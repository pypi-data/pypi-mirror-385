# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import collections.abc
import datetime
import logging
import uuid
import warnings
from collections.abc import Callable, Hashable, Iterable, Mapping, Sequence
from itertools import groupby
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal, TypeAlias, cast

import deprecat
import numpy
import xarray
from dask import array as da
from odc.geo import CRS, XY, Resolution, res_, resyx_, yx_
from odc.geo.geobox import GeoBox, GeoboxTiles
from odc.geo.geom import Geometry, bbox_union, box, intersects
from odc.geo.warp import Resampling
from odc.geo.xr import xr_coords
from typing_extensions import override
from xarray.core.coordinates import DataArrayCoordinates

from datacube.cfg import GeneralisedCfg, GeneralisedEnv, GeneralisedRawCfg, ODCConfig
from datacube.model import Dataset, ExtraDimensions, ExtraDimensionSlices, Measurement
from datacube.model.utils import xr_apply
from datacube.storage import BandInfo, reproject_and_fuse
from datacube.utils import ignore_exceptions_if
from datacube.utils.dates import normalise_dt

if TYPE_CHECKING:
    from odc.geo.crs import MaybeCRS
    from pandas import DataFrame

    from datacube.model import GridSpec
    from datacube.utils.geometry import GeoBox as LegacyGeoBox

from ..drivers import new_datasource
from ..index import Index, extract_geom_from_query, index_connect
from ..migration import ODC2DeprecationWarning
from ..model import QueryField
from ..storage._load import FuserFunction, ProgressFunction
from .query import GroupBy, Query, query_group_by

_LOG: logging.Logger = logging.getLogger(__name__)


DataFrameLike: TypeAlias = list[dict[str, str | int | float | None]]


class TerminateCurrentLoad(Exception):  # noqa: N818
    """This exception is raised by user code from `progress_cbk`
    to terminate currently running `.load`
    """

    pass


class Datacube:
    """
    Interface to search, read and write a datacube.
    """

    def __init__(
        self,
        index: Index | None = None,
        config: GeneralisedCfg | None = None,
        env: GeneralisedEnv | None = None,
        raw_config: GeneralisedRawCfg | None = None,
        app: str | None = None,
        validate_connection: bool = True,
    ) -> None:
        """
        Create an interface for the query and storage access.

        :param index: The database index to use. If provided, config, app, env and raw_config should all be None.

        :param config: One of:
            - None (Use provided ODCEnvironment or Index, or perform default config loading.)
            - An ODCConfig object
            - A file system path pointing to the location of the config file.
            - A list of file system paths to search for config files. The first readable file found will be used.
            If an index or an explicit ODCEnvironment is supplied, config and raw_config should be None.

        :param env: The datacube environment to use.
            Either an explicit ODCEnvironment object, or a str which is a section name in the loaded config file.

            Defaults to 'default'. Falls back to 'datacube' with a deprecation warning if config file does not
            contain a 'default' section.

            Allows you to have multiple datacube instances in one configuration, specified on load,
            e.g. 'dev', 'test' or 'landsat', 'modis' etc.

            If env is an ODCEnvironment object, config and index should both None.

        :param raw_config: Explicit configuration to use.  Either as a string (serialised in ini or yaml format) or
            a dictionary (deserialised).  If provided, config should be None.
            If an index or an explicit ODCEnvironment is supplied, config and raw_config should be None.

        :param app: A short, alphanumeric name to identify this application.

            The application name is used to track down problems with database queries, so it is strongly
            advised that be used.  Should be None if an index is supplied.

        :param validate_connection: Check that the database connection is available and valid.
            Defaults to True. Ignored if index is passed.
        """
        # Validate arguments

        if index is not None:
            # If an explicit index is provided, all other index-creation arguments should be None.
            should_be_none: list[str] = []
            if config is not None:
                should_be_none.append("config")
            if raw_config is not None:
                should_be_none.append("raw_config")
            if app is not None:
                should_be_none.append("app")
            if env is not None:
                should_be_none.append("env")
            if should_be_none:
                raise ValueError(
                    f"When an explicit index is provided, these arguments should be None: {','.join(should_be_none)}"
                )
            # Explicit index passed in?  Use it.
            self.index = index
            return

        # Obtain an ODCEnvironment object:
        cfg_env = ODCConfig.get_environment(
            env=env, config=config, raw_config=raw_config
        )

        self.index = index_connect(
            cfg_env, application_name=app, validate_connection=validate_connection
        )

    def list_products(
        self, with_pandas: bool = True, dataset_count: bool = False
    ) -> DataFrame | DataFrameLike:
        """
        List all products in the datacube. This will produce a ``pandas.DataFrame``
        or list of dicts containing useful information about each product, including:

            'name'
            'description'
            'license'
            'default_crs' or 'grid_spec.crs'
            'default_resolution' or 'grid_spec.crs'
            'dataset_count' (optional)

        :param with_pandas:
            Return the list as a Pandas DataFrame. Defaults to True.  If False, return a list of dicts.

        :param dataset_count:
            Return a "dataset_count" column containing the number of datasets
            for each product. This can take several minutes on large datacubes.
            Defaults to False.

        :return: A table or list of every product in the datacube.
        """

        def _get_non_default(product, col):
            load_hints = product.load_hints()
            if load_hints:
                if col == "crs":
                    return load_hints.get("output_crs", None)
                return load_hints.get(col, None)
            return getattr(product.grid_spec, col, None)

        # Read properties from each datacube product
        cols = [
            "name",
            "description",
            "license",
            "default_crs",
            "default_resolution",
        ]
        rows = [
            [
                (
                    getattr(pr, col, None)
                    # if 'default_crs' and 'default_resolution' are not None
                    # return 'default_crs' and 'default_resolution'
                    if getattr(pr, col, None) or "default" not in col
                    # else get crs and resolution from load_hints or grid_spec
                    # as per output_geobox() handling logic
                    else _get_non_default(pr, col.replace("default_", ""))
                )
                for col in cols
            ]
            for pr in self.index.products.get_all()
        ]

        # Optionally compute dataset count for each product and add to row/cols
        # Product lists are sorted by product name to ensure 1:1 match
        if dataset_count:
            # Load counts
            counts = [(p.name, c) for p, c in self.index.datasets.count_by_product()]

            # Sort both rows and counts by product name
            from operator import itemgetter

            rows = sorted(rows, key=itemgetter(0))
            counts = sorted(counts, key=itemgetter(0))

            # Add sorted count to each existing row
            rows = [[*row, count[1]] for row, count in zip(rows, counts)]
            cols += ["dataset_count"]

        # If pandas not requested, return list of dicts
        if not with_pandas:
            return [dict(zip(cols, row)) for row in rows]

        # Return pandas dataframe with each product as a row
        import pandas

        return pandas.DataFrame(rows, columns=cols).set_index("name", drop=False)

    @deprecat.deprecat(
        deprecated_args={
            "show_archived": {
                "reason": "The show_archived argument has never done anything and will be removed in future.",
                "version": "1.9.0",
                "category": ODC2DeprecationWarning,
            }
        }
    )
    def list_measurements(
        self, show_archived: bool = False, with_pandas: bool = True
    ) -> DataFrame | DataFrameLike:
        """
        List measurements for each product

        :param show_archived: include archived products in the result.
        :param with_pandas: return the list as a Pandas DataFrame, otherwise as a list of dict. (defaults to True)
        """
        measurements = self._list_measurements()
        if not with_pandas:
            return measurements

        import pandas

        return pandas.DataFrame.from_records(measurements).set_index(
            ["product", "measurement"]
        )

    def _list_measurements(self) -> list[dict[str, Any]]:
        measurements = []
        dts = self.index.products.get_all()
        for dt in dts:
            if dt.measurements:
                for name, measurement in dt.measurements.items():
                    row = {
                        "product": dt.name,
                        "measurement": name,
                    }
                    if "attrs" in measurement:
                        row.update(measurement["attrs"])
                    row.update({k: v for k, v in measurement.items() if k != "attrs"})
                    measurements.append(row)
        return measurements

    #: pylint: disable=too-many-arguments, too-many-locals
    def load(
        self,
        product: str | None = None,
        measurements: str | list[str] | None = None,
        output_crs: MaybeCRS = None,
        resolution: (
            int
            | float
            | tuple[int | float, int | float]
            | list[int | float]
            | Resolution
            | None
        ) = None,
        resampling: Resampling | dict[str, Resampling] | None = None,
        align: XY[float] | Iterable[float] | None = None,
        skip_broken_datasets: bool | None = None,
        dask_chunks: Mapping[str, int | Literal["auto"]] | None = None,
        like: GeoBox | xarray.Dataset | xarray.DataArray | None = None,
        fuse_func: FuserFunction | Mapping[str, FuserFunction | None] | None = None,
        datasets: Sequence[Dataset] | None = None,
        dataset_predicate: Callable[[Dataset], bool] | None = None,
        progress_cbk: ProgressFunction | None = None,
        patch_url: Callable[[str], str] | None = None,
        limit: int | None = None,
        driver: Any | None = None,
        **query: QueryField,
    ) -> xarray.Dataset:
        # Ruff reformats the legal resampling values into a tuple, so disable
        # formatting for this code block.
        # fmt: off
        r"""
        Load data as an ``xarray.Dataset`` object.
        Each measurement will be a data variable in the :class:`xarray.Dataset`.

        See the `xarray documentation <https://xarray.pydata.org/en/stable/data-structures.html>`_ for usage of the
        :class:`xarray.Dataset` and :class:`xarray.DataArray` objects.

        **Product and Measurements**

            A product can be specified using the product name::

                product = "ls5_ndvi_albers"

            See :meth:`list_products` for the list of products with their names and properties.

            A product name MUST be supplied unless search is bypassed all together by supplying an explicit
            list of datasets.

            The ``measurements`` argument is a list of measurement names, as listed in :meth:`list_measurements`.
            If not provided, all measurements for the product will be returned::

                measurements = ["red", "nir", "swir2"]

        **Dimensions**

            Spatial dimensions can be specified using the ``longitude``/``latitude`` and ``x``/``y`` fields.

            The CRS of this query is assumed to be WGS84/EPSG:4326 unless the ``crs`` field is supplied,
            even if the stored data is in another projection or the ``output_crs`` is specified.
            The dimensions ``longitude``/``latitude`` and ``x``/``y`` can be used interchangeably::

                latitude=(-34.5, -35.2), longitude=(148.3, 148.7)

            or::

                x=(1516200, 1541300), y=(-3867375, -3867350), crs="EPSG:3577"

            You can also specify a polygon with an arbitrary CRS (in e.g. the native CRS)::

                geopolygon = polygon(coords, crs="EPSG:3577")

            Or an iterable of polygons (search is done against the union of all polygons)::

                geopolygon = [poly1, poly2, poly3, ....]

            You can also pass a WKT string, or a GeoJSON string or any other object that can be passed to the
            :class:`odc.geo.Geometry` constructor, or an iterable of any of the above.

            Performance and accuracy of geopolygon queries may vary depending on the index driver in use and the CRS.

            The ``time`` dimension can be specified using a single or tuple of datetime objects or strings with
            ``YYYY-MM-DD hh:mm:ss`` format. Data will be loaded inclusive of the start and finish times.
            A ``None`` value in the range indicates an open range, with the provided date serving as either the
            upper or lower bound. E.g.::

                time = ("2000-01-01", "2001-12-31")
                time = ("2000-01", "2001-12")
                time = ("2000", "2001")
                time = "2000"
                time = ("2000", None)  # all data from 2000 onward
                time = (None, "2000")  # all data up to and including 2000

            For 3D datasets, where the product definition contains an ``extra_dimension`` specification,
            these dimensions can be queried using that dimension's name. E.g.::

                z = (10, 30)

            or::

                z = 5

            or::

                wvl = (560.3, 820.5)

            For EO-specific datasets that are based around scenes, the time dimension can be reduced to the day level,
            using solar day to keep scenes together::

                group_by = "solar_day"

            For data that has different values for the scene overlap that requires more complex rules for combining
            data, a function can be provided to the merging into a single time slice.

            See :func:`datacube.helpers.ga_pq_fuser` for an example implementation.
            See :func:`datacube.api.query.query_group_by` for ``group_by`` built-in functions.


        **Output**

            To reproject or resample data, supply the ``output_crs``, ``resolution``, ``resampling`` and ``align``
            fields.

            By default, the resampling method is ``nearest``. However, any stored overview layers may be used
            when down-sampling, which may override (or hybridise) the choice of resampling method.

            To reproject data to 30 m resolution for EPSG:3577::

                dc.load(
                    product="ls5_nbar_albers",
                    x=(148.15, 148.2),
                    y=(-35.15, -35.2),
                    time=("1990", "1991"),
                    output_crs="EPSG:3577",
                    resolution=30,
                    resampling="cubic",
                )

            odc-geo style xy objects are preferred for passing in resolution and align pairs to avoid x/y ordering
            ambiguity.

        :param product:
            The name of the product to be loaded. Either ``product`` or ``datasets`` must be supplied

        :param measurements:
            Measurements name or list of names to be included, as listed in :meth:`list_measurements`.
            These will be loaded as individual ``xr.DataArray`` variables in
            the output ``xarray.Dataset`` object.

            If a list is specified, the measurements will be returned in the order requested.
            By default, all available measurements are included.

        :param output_crs:
            The CRS of the returned data, for example ``EPSG:3577``.
            If no CRS is supplied, the CRS of the stored data is used if available.

            Any form that can be converted to a CRS by odc-geo is accepted.

            This differs from the ``crs`` parameter described above, which is used to define the CRS
            of the coordinates in the query itself.

        :param resolution:
            The spatial resolution of the returned data. If using square pixels with an inverted Y axis, it
            should be provided as an int or float. If not, it should be provided as an odc-geo XY object
            to avoid coordinate-order ambiguity.  If passed as a tuple, y,x order is assumed for backwards
            compatibility.

            Units are in the coordinate space of ``output_crs``. This includes the direction (as indicated by
            a positive or negative number).

        :param resampling:
            The resampling method to use if re-projection is required. This could be a string or
            a dictionary mapping band name to resampling mode. When using a dict use ``'\*'`` to
            indicate "apply to all other bands", for example ``{'\*': 'cubic', 'fmask': 'nearest'}`` would
            use ``cubic`` for all bands except ``fmask`` for which ``nearest`` will be used.

            Valid values are::

               "nearest", "average", "bilinear", "cubic", "cubic_spline",
               "lanczos", "mode", "gauss", "max", "min", "med", "q1", "q3",

            Default is to use ``nearest`` for all bands.

            .. seealso::
               :meth:`load_data`

        :param align:
            Load data such that point 'align' lies on the pixel boundary.  A pair of floats between 0 and 1.

            An odc-geo XY object is preferred to avoid coordinate-order ambiguity.  If passed as a tuple, x,y
            order is assumed for backwards compatibility.

            Default is ``(0, 0)``

        :param skip_broken_datasets:
            Optional. If this is True, then don't break when failing to load a broken dataset.
            If None, the value will come from the environment variable of the same name.
            Default is False.

        :param dask_chunks:
            If the data should be lazily loaded using :class:`dask.array.Array`,
            specify the chunking size in each output dimension.

            See the documentation on using `xarray with dask <https://xarray.pydata.org/en/stable/dask.html>`_
            for more information.

        :param like:
            Use the output of a previous :meth:`load()` to load data into the same spatial grid and
            resolution (i.e. :class:`odc.geo.geobox.GeoBox` or an xarray `Dataset` or `DataArray`).
            E.g.::

                pq = dc.load(product="ls5_pq_albers", like=nbar_dataset)

        :param fuse_func: Function used to fuse/combine/reduce data with the ``group_by`` parameter. By default,
            data is simply copied over the top of each other in a relatively undefined manner. This function can
            perform a specific combining step. This can be a dictionary if different
            fusers are needed per band (similar format to the resampling dict described above).

        :param datasets: Optional. If this is a non-empty list of :class:`datacube.model.Dataset` objects,
            these will be loaded instead of performing a database lookup.

        :param dataset_predicate: Optional. A function that can be passed to restrict loaded datasets. A
            predicate function should take a :class:`datacube.model.Dataset` object (e.g. as returned from
            :meth:`find_datasets`) and return a boolean.

            For example, loaded data could be filtered to January observations only by passing the following
            predicate function that returns True for datasets acquired in January::

                def filter_jan(dataset):
                    return dataset.time.begin.month == 1

            .

        :param progress_cbk: ``Int, Int -> None``,
            if supplied will be called for every file read with ``files_processed_so_far, total_files``. This is
            only applicable to non-lazy loads, ignored when using dask.

        :param patch_url: if supplied, will be used to patch/sign the url(s), as required to access some
            commercial archives (e.g. Microsoft Planetary Computer).

        :param limit: Optional. If provided, limit the maximum number of datasets returned. Useful for
            testing and debugging. Can also be provided via the ``dc_load_limit`` config option.

        :param driver: Optional. If provided, use the specified driver to load the data.

        :param query: Search parameters for products and dimension ranges as described above.
            For example: ``'x', 'y', 'time', 'crs'``.

        :return: Requested data in a :class:`xarray.Dataset`
        """
        # fmt: on
        if product is None and datasets is None:
            raise ValueError("Must specify a product or supply datasets")

        if datasets is None:
            assert product is not None  # For type checker
            if limit is None:
                # check if a value was provided via the envvar
                limit = self.index.environment["dc_load_limit"]
            datasets = self.find_datasets(
                ensure_location=True,
                dataset_predicate=dataset_predicate,
                like=like,
                limit=limit,
                product=product,
                **query,
            )
        elif isinstance(datasets, collections.abc.Iterator):
            datasets = list(datasets)

        if len(datasets) == 0:
            return xarray.Dataset()

        ds, *_ = datasets
        datacube_product = ds.product

        # Retrieve extra_dimension from product definition
        extra_dims: ExtraDimensions | None = None
        if datacube_product:
            extra_dims = datacube_product.extra_dimensions

            # Extract extra_dims slice information
            extra_dims_slice: ExtraDimensionSlices = {
                k: v  # type: ignore[misc]
                for k, v in query.items()
                if v is not None and k in extra_dims.dims
            }
            extra_dims = extra_dims[extra_dims_slice]
            # Check if empty
            if extra_dims.has_empty_dim():
                return xarray.Dataset()

        if isinstance(resolution, tuple | list):
            resolution = _handle_legacy_resolution(resolution)

        load_hints = datacube_product.load_hints()
        grid_spec = None if load_hints is not None else datacube_product.grid_spec

        geobox = output_geobox(
            like=like,
            output_crs=output_crs,
            resolution=resolution,
            align=align,
            grid_spec=grid_spec,
            load_hints=load_hints,
            datasets=datasets,
            geopolygon=cast(Geometry | None, query.pop("geopolygon", None)),
            **query,
        )
        group_by = query_group_by(**query)  # type: ignore[arg-type]
        grouped = self.group_datasets(datasets, group_by)

        measurement_dicts = datacube_product.lookup_measurements(measurements)

        if skip_broken_datasets is None:
            # default to value from env var, which defaults to False
            skip_broken_datasets = self.index.environment["skip_broken_datasets"]

        return self.load_data(
            grouped,
            geobox,
            measurement_dicts,
            resampling=resampling,
            fuse_func=fuse_func,
            dask_chunks=dask_chunks,
            skip_broken_datasets=skip_broken_datasets,
            progress_cbk=progress_cbk,
            extra_dims=extra_dims,
            patch_url=patch_url,
            driver=driver,
        )

    def find_datasets(
        self,
        ensure_location: bool = False,
        dataset_predicate: Callable[[Dataset], bool] | None = None,
        like: GeoBox | xarray.Dataset | xarray.DataArray | None = None,
        limit: int | None = None,
        **search_terms: QueryField,
    ) -> list[Dataset]:
        """
        Search the index and return all datasets for a product matching the search terms.

        :param ensure_location: only return datasets that have locations
        :param dataset_predicate: an optional predicate to filter datasets
        :param like:
            Use the output of a previous :meth:`load()` to load data into the same spatial grid and
            resolution (i.e. :class:`odc.geo.geobox.GeoBox` or an xarray `Dataset` or `DataArray`).
            E.g.::

                pq = dc.load(product="ls5_pq_albers", like=nbar_dataset)

        :param limit: if provided, limit the maximum number of datasets returned
        :param search_terms: see :class:`datacube.api.query.Query`
        :return: list of datasets

        .. seealso:: :meth:`group_datasets` :meth:`load_data` :meth:`find_datasets_lazy`
        """
        return list(
            self.find_datasets_lazy(
                limit=limit,
                ensure_location=ensure_location,
                dataset_predicate=dataset_predicate,
                like=like,
                **search_terms,
            )
        )

    def find_datasets_lazy(
        self,
        limit: int | None = None,
        ensure_location: bool = False,
        dataset_predicate: Callable[[Dataset], bool] | None = None,
        like: GeoBox | xarray.Dataset | xarray.DataArray | None = None,
        **kwargs: QueryField,
    ) -> Iterable[Dataset]:
        """
        Find datasets matching query.

        :param limit: if provided, limit the maximum number of datasets returned
        :param ensure_location: only return datasets that have locations
        :param dataset_predicate: an optional predicate to filter datasets
        :param like:
            Use the output of a previous :meth:`load()` to load data into the same spatial grid and
            resolution (i.e. :class:`odc.geo.geobox.GeoBox` or an xarray `Dataset` or `DataArray`).
            E.g.::

                pq = dc.load(product='ls5_pq_albers', like=nbar_dataset)
        :param kwargs: see :class:`datacube.api.query.Query`
        :return: iterator of datasets

        .. seealso:: :meth:`group_datasets` :meth:`load_data` :meth:`find_datasets`
        """
        query = Query(self.index, like=like, **kwargs)  # type: ignore[arg-type]
        if not query.product:
            raise ValueError("must specify a product")

        datasets = self.index.datasets.search(limit=limit, **query.search_terms)

        if query.geopolygon is not None and not self.index.supports_spatial_indexes:
            datasets = select_datasets_inside_polygon(datasets, query.geopolygon)

        if ensure_location:
            datasets = (dataset for dataset in datasets if dataset.uri)

        # If a predicate function is provided, use this to filter datasets before load
        if dataset_predicate is not None:
            datasets = (dataset for dataset in datasets if dataset_predicate(dataset))

        return datasets

    @staticmethod
    def group_datasets(
        datasets: Iterable[Dataset],
        group_by: Literal["time", "solar_day"] | GroupBy,
    ) -> xarray.DataArray:
        """
        Group datasets along defined non-spatial dimensions (i.e. time).

        :param datasets: a list of datasets, typically from :meth:`find_datasets`
        :param group_by: Contains:
            - a function that returns a label for a dataset
            - name of the new dimension
            - unit for the new dimension
            - function to sort by before grouping

        .. seealso:: :meth:`find_datasets`, :meth:`load_data`, :meth:`query_group_by`
        """
        if isinstance(group_by, str):
            group_by = query_group_by(group_by=group_by)

        def ds_sorter(ds: Dataset) -> Any:
            return group_by.sort_key(ds), getattr(ds, "id", 0)

        def norm_axis_value(x: Any) -> Any:
            if isinstance(x, datetime.datetime):
                # For datetime we convert to UTC, then strip timezone info
                # to avoid numpy/pandas warning about timezones
                return numpy.datetime64(normalise_dt(x), "ns")
            return x

        def mk_group(group: Iterable[Dataset]) -> tuple[Any, Iterable[Dataset]]:
            dss = tuple(sorted(group, key=ds_sorter))
            return norm_axis_value(group_by.group_key(dss)), dss

        datasets = sorted(datasets, key=group_by.group_by_func)

        groups = [
            mk_group(group) for _, group in groupby(datasets, group_by.group_by_func)
        ]

        groups.sort(key=lambda x: x[0])

        coords = numpy.asarray([coord for coord, _ in groups])
        data = numpy.empty(len(coords), dtype=object)
        for i, (_, dss) in enumerate(groups):
            data[i] = dss

        sources = xarray.DataArray(data, dims=[group_by.dimension], coords=[coords])
        if coords.dtype.kind == "M":
            # skip units for time dimensions as it breaks .to_netcdf(..) functionality #972
            sources[group_by.dimension].attrs["units"] = group_by.units

        return sources

    @staticmethod
    def create_storage(
        coords: DataArrayCoordinates | None,
        geobox: GeoBox | xarray.Dataset | xarray.DataArray,
        measurements: list[Measurement],
        data_func: (
            Callable[[Measurement, tuple[int, ...]], numpy.ndarray] | None
        ) = None,
        extra_dims: ExtraDimensions | None = None,
    ) -> xarray.Dataset:
        """
        Create a :class:`xarray.Dataset` and (optionally) fill it with data.

        This function makes the in memory storage structure to hold datacube data.

        :param coords:
            DataArrayCoordinates defining the dimensions not specified by `geobox`

        :param geobox:
            A GeoBox defining the output spatial projection and resolution

        :param measurements:
            list of :class:`datacube.model.Measurement`

        :param data_func: Callable `Measurement -> np.ndarray`
            function to fill the storage with data. It is called once for each measurement, with the measurement
            as an argument. It should return an appropriately shaped numpy array. If not provided memory is
            allocated and filled with `nodata` value defined on a given Measurement.

        :param extra_dims:
            A ExtraDimensions describing any additional dimensions on top of (t, y, x)


        .. seealso:: :meth:`find_datasets` :meth:`group_datasets`
        """
        from collections import OrderedDict
        from copy import deepcopy

        spatial_ref = "spatial_ref"

        def empty_func(m: Measurement, shape: tuple[int, ...]) -> numpy.ndarray:
            return numpy.full(shape, m.nodata, dtype=m.dtype)

        geobox = _normalise_geobox(geobox)

        crs_attrs = {}
        if geobox.crs is not None:
            crs_attrs["crs"] = str(geobox.crs)
            crs_attrs["grid_mapping"] = spatial_ref

        # Assumptions
        #  - 3D dims must fit between (t) and (y, x) or (lat, lon)

        # 2D defaults
        if isinstance(coords, dict):
            warnings.warn(
                "The coords argument to Datacube.create_storage is now expected "
                "as a DataArrayCoordinates object or None instead of a dict.",
                ODC2DeprecationWarning,
                stacklevel=2,
            )
            coords = None if coords == {} else DataArrayCoordinates(*coords.values())

        dims_default = (() if coords is None else coords.dims) + geobox.dimensions
        shape_default = (
            ()
            if coords is None
            else tuple(c.size for k, c in coords.items() if k in dims_default)
        ) + geobox.shape.yx
        coords_default: OrderedDict[str, xarray.DataArray] = OrderedDict()
        if coords is not None:
            coords_default.update([(str(k), v) for k, v in coords.items()])
        coords_default.update(
            [(str(k), v) for k, v in xr_coords(geobox, spatial_ref).items()]
        )

        arrays = []
        ds_coords = deepcopy(coords_default)

        for m in measurements:
            if "extra_dim" not in m:
                # 2D default case
                arrays.append((m, shape_default, coords_default, dims_default))
            elif extra_dims:
                # 3D case
                name = m.extra_dim
                new_dims = (*dims_default[:1], name, *dims_default[1:])
                new_coords = deepcopy(coords_default)
                new_coords[name] = extra_dims._coords[name].copy()
                new_coords[name].attrs.update(crs_attrs)
                ds_coords.update(new_coords)

                new_shape = (
                    *shape_default[:1],
                    len(new_coords[name].values),
                    *shape_default[1:],
                )
                arrays.append((m, new_shape, new_coords, new_dims))

        data_func = data_func or (lambda m, shape: empty_func(m, shape))

        def mk_data_var(
            m: Measurement,
            shape: tuple[int, ...],
            coords: OrderedDict[str, xarray.DataArray],
            dims: tuple[Hashable, ...],
            data_func: Callable[[Measurement, tuple[int, ...]], numpy.ndarray],
        ) -> xarray.DataArray:
            data = data_func(m, shape)
            attrs = dict(**m.dataarray_attrs(), **crs_attrs)
            return xarray.DataArray(
                data, name=m.name, coords=coords, dims=dims, attrs=attrs
            )

        return xarray.Dataset(
            {
                m.name: mk_data_var(m, shape, coords, dims, data_func)
                for m, shape, coords, dims in arrays
            },
            coords=ds_coords,
            attrs=crs_attrs,
        )

    @staticmethod
    def _dask_load(
        sources: xarray.DataArray,
        geobox: GeoBox,
        measurements: list[Measurement],
        dask_chunks: Mapping[str, int | Literal["auto"]],
        skip_broken_datasets: bool = False,
        extra_dims: ExtraDimensions | None = None,
        patch_url: Callable[[str], str] | None = None,
    ) -> xarray.Dataset:
        chunk_sizes = _calculate_chunk_sizes(sources, geobox, dask_chunks, extra_dims)
        needed_irr_chunks = chunk_sizes[0]
        if extra_dims:
            extra_dim_chunks = chunk_sizes[1]
        grid_chunks = chunk_sizes[-1]
        gbt = GeoboxTiles(geobox, grid_chunks)
        dsk = {}

        def chunk_datasets(dss, gbt):
            out = {}
            for ds in dss:
                dsk[_tokenize_dataset(ds)] = ds
                for idx in gbt.tiles(ds.extent):
                    out.setdefault(idx, []).append(ds)
            return out

        chunked_srcs = xr_apply(
            sources, lambda _, dss: chunk_datasets(dss, gbt), dtype=object
        )

        def data_func(measurement, shape):
            if "extra_dim" in measurement:
                chunks = needed_irr_chunks + extra_dim_chunks + grid_chunks
            else:
                chunks = needed_irr_chunks + grid_chunks
            return _make_dask_array(
                chunked_srcs,
                dsk,
                gbt,
                measurement,
                chunks=chunks,
                skip_broken_datasets=skip_broken_datasets,
                extra_dims=extra_dims,
                patch_url=patch_url,
            )

        return Datacube.create_storage(
            sources.coords, geobox, measurements, data_func, extra_dims
        )

    @staticmethod
    def _xr_load(
        sources: xarray.DataArray,
        geobox: GeoBox,
        measurements: list[Measurement],
        skip_broken_datasets: bool = False,
        progress_cbk: ProgressFunction | None = None,
        extra_dims: ExtraDimensions | None = None,
        patch_url: Callable[[str], str] | None = None,
    ) -> xarray.Dataset:
        def mk_cbk(cbk: ProgressFunction | None) -> ProgressFunction | None:
            if cbk is None:
                return None
            n = 0
            t_size = sum(len(x) for x in sources.values.ravel())
            n_total = 0
            for m in measurements:
                if "extra_dim" in m:
                    assert extra_dims is not None  # for type-checker
                    index_subset = extra_dims.measurements_slice(m.extra_dim)
                    n_total += t_size * len(
                        m.extra_dim.get("measurement_map")[index_subset]
                    )
                else:
                    n_total += t_size

            def _cbk(_a: int, _b: int) -> Any | None:
                nonlocal n
                n += 1
                return cbk(n, n_total)

            return _cbk

        data = Datacube.create_storage(
            sources.coords, geobox, measurements, extra_dims=extra_dims
        )
        _cbk = mk_cbk(progress_cbk)

        # Create a list of read IO operations
        read_ios = []
        for index, datasets in numpy.ndenumerate(sources.values):
            for m in measurements:
                if "extra_dim" in m:
                    # When we want to support 3D native reads, we can start by replacing the for loop with
                    # read_ios.append(((index + extra_dim_index), (datasets, m, index_subset)))
                    assert extra_dims is not None  # for type-checker
                    index_subset = extra_dims.measurements_index(m.extra_dim)
                    for result_index, extra_dim_index in enumerate(
                        range(*index_subset)
                    ):
                        read_ios.append(
                            (((*index, result_index)), (datasets, m, extra_dim_index))
                        )
                else:
                    # Get extra_dim index if available
                    extra_dim_index = m.get("extra_dim_index", None)
                    read_ios.append((index, (datasets, m, extra_dim_index)))

        # Perform the read IO operations
        for index, (datasets, m, extra_dim_index) in read_ios:
            data_slice = data[m.name].values[index]
            try:
                _fuse_measurement(
                    data_slice,
                    datasets,
                    geobox,
                    m,
                    skip_broken_datasets=skip_broken_datasets,
                    progress_cbk=_cbk,
                    extra_dim_index=extra_dim_index,
                    patch_url=patch_url,
                )
            except (TerminateCurrentLoad, KeyboardInterrupt):
                data.attrs["dc_partial_load"] = True
                return data

        return data

    @staticmethod
    def load_data(
        sources: xarray.DataArray,
        geobox: GeoBox | xarray.Dataset | xarray.DataArray,
        measurements: Mapping[str, Measurement] | list[Measurement],
        resampling: Resampling | dict[str, Resampling] | None = None,
        fuse_func: FuserFunction | Mapping[str, FuserFunction | None] | None = None,
        dask_chunks: Mapping[str, int | Literal["auto"]] | None = None,
        skip_broken_datasets: bool = False,
        progress_cbk: ProgressFunction | None = None,
        extra_dims: ExtraDimensions | None = None,
        patch_url: Callable[[str], str] | None = None,
        driver: Any | None = None,
        **extra,
    ) -> xarray.Dataset:
        """
        Load data from :meth:`group_datasets` into an :class:`xarray.Dataset`.

        :param sources:
            DataArray holding a list of :class:`datacube.model.Dataset`, grouped along the time dimension

        :param geobox:
            A GeoBox defining the output spatial projection and resolution

        :param measurements:
            list of `Measurement` objects

        :param resampling:
            The resampling method to use if re-projection is required. This could be a string or
            a dictionary mapping band name to resampling mode. When using a dict use ``'*'`` to
            indicate "apply to all other bands", for example ``{'*': 'cubic', 'fmask': 'nearest'}`` would
            use `cubic` for all bands except ``fmask`` for which `nearest` will be used.

            Valid values are: ``'nearest', 'cubic', 'bilinear', 'cubic_spline', 'lanczos', 'average',
            'mode', 'gauss',  'max', 'min', 'med', 'q1', 'q3'``

            Default is to use ``nearest`` for all bands.

        :param fuse_func:
            function to merge successive arrays as an output. Can be a dictionary just like resampling.

        :param dask_chunks:
            If provided, the data will be loaded on demand using :class:`dask.array.Array`.
            Should be a dictionary specifying the chunking size for each output dimension.
            Unspecified dimensions will be auto-guessed, currently this means use chunk size of 1 for non-spatial
            dimensions and use whole dimension (no chunking unless specified) for spatial dimensions.

            See the documentation on using `xarray with dask <https://xarray.pydata.org/en/stable/dask.html>`_
            for more information.

        :param skip_broken_datasets: do not include broken datasets in the result.

        :param progress_cbk: Int, Int -> None
            if supplied will be called for every file read with `files_processed_so_far, total_files`. This is
            only applicable to non-lazy loads, ignored when using dask.

        :param extra_dims:
            A ExtraDimensions describing any additional dimensions on top of (t, y, x)

        :param patch_url:
            if supplied, will be used to patch/sign the url(s), as required to access some commercial archives.

        :param driver:
            Optional. If provided, use the specified driver to load the data.


        .. seealso:: :meth:`find_datasets` :meth:`group_datasets`
        """
        measurements = per_band_load_data_settings(
            measurements, resampling=resampling, fuse_func=fuse_func
        )

        geobox = _normalise_geobox(geobox)

        if driver is not None:
            from ..storage._loader import driver_based_load

            return driver_based_load(
                driver,
                sources,
                geobox,
                measurements,
                dask_chunks,
                skip_broken_datasets=skip_broken_datasets,
                extra_dims=extra_dims,
                patch_url=patch_url,
            )

        if dask_chunks is not None:
            return Datacube._dask_load(
                sources,
                geobox,
                measurements,
                dask_chunks,
                skip_broken_datasets=skip_broken_datasets,
                extra_dims=extra_dims,
                patch_url=patch_url,
            )
        return Datacube._xr_load(
            sources,
            geobox,
            measurements,
            skip_broken_datasets=skip_broken_datasets,
            progress_cbk=progress_cbk,
            extra_dims=extra_dims,
            patch_url=patch_url,
        )

    @override
    def __str__(self) -> str:
        return f"Datacube<index={self.index!r}>"

    @override
    def __repr__(self) -> str:
        return self.__str__()

    def close(self) -> None:
        """
        Close any open connections
        """
        self.index.close()

    def __enter__(self) -> Datacube:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


def per_band_load_data_settings(
    measurements: list[Measurement] | Mapping[str, Measurement],
    resampling: Resampling | Mapping[str, Resampling] | None = None,
    fuse_func: FuserFunction | Mapping[str, FuserFunction | None] | None = None,
) -> list[Measurement]:
    def with_resampling(m, resampling, default=None):
        m = m.copy()
        m["resampling_method"] = resampling.get(m.name, default)
        return m

    def with_fuser(m, fuser, default=None):
        m = m.copy()
        m["fuser"] = fuser.get(m.name, default)
        return m

    if resampling is not None and not isinstance(resampling, dict):
        resampling = {"*": resampling}

    if fuse_func is None or callable(fuse_func):
        fuse_func = {"*": fuse_func}

    if isinstance(measurements, dict):
        measurements = list(measurements.values())

    if resampling is not None:
        measurements = [
            with_resampling(m, resampling, default=resampling.get("*"))
            for m in measurements
        ]

    if fuse_func is not None:
        measurements = [
            with_fuser(m, fuse_func, default=fuse_func.get("*")) for m in measurements
        ]

    return measurements


def output_geobox(
    like: GeoBox | LegacyGeoBox | xarray.Dataset | xarray.DataArray | None = None,
    output_crs: Any = None,
    resolution: (
        int
        | float
        | Resolution
        | tuple[int | float, int | float]
        | list[int | float]
        | None
    ) = None,
    align: XY[float] | Iterable[float] | None = None,
    grid_spec: GridSpec | None = None,
    load_hints: Mapping[str, Any] | None = None,
    datasets: Iterable[Dataset] | None = None,
    geopolygon: Geometry | None = None,
    **query: QueryField,
) -> GeoBox:
    """Configure output geobox from user provided output specs."""

    if like is not None:
        assert output_crs is None, "'like' and 'output_crs' are not supported together"
        assert resolution is None, "'like' and 'resolution' are not supported together"
        assert align is None, "'like' and 'align' are not supported together"
        return _normalise_geobox(like)

    if load_hints:
        if output_crs is None:
            output_crs = load_hints.get("output_crs", None)

        if resolution is None:
            resolution = load_hints.get("resolution", None)

        if align is None:
            align = load_hints.get("align", None)

    if output_crs is not None:
        if resolution is None:
            raise ValueError("Must specify 'resolution' when specifying 'output_crs'")
        crs = CRS(output_crs)
    elif grid_spec is not None:
        # specification from grid_spec
        crs = grid_spec.crs
        if resolution is None:
            resolution = grid_spec.resolution
        align = align or grid_spec.alignment
    else:
        raise ValueError(
            "Product has no default CRS.\nMust specify 'output_crs' and 'resolution'"
        )

    # Try figuring out bounds
    #  1. Explicitly defined with geopolygon
    #  2. Extracted from x=,y=
    #  3. Computed from dataset footprints
    #  4. fail with ValueError
    if geopolygon is None:
        geopolygon = extract_geom_from_query(**query)

        if geopolygon is None:
            if datasets is None:
                raise ValueError("Bounds are not specified")

            geopolygon = get_bounds(datasets, crs)

    if isinstance(resolution, tuple | list):
        resolution = _handle_legacy_resolution(resolution)

    if align is not None:
        align = yx_(align)

    return GeoBox.from_geopolygon(geopolygon, resolution, crs, align)


def select_datasets_inside_polygon(
    datasets: Iterable[Dataset], polygon: Geometry
) -> Iterable[Dataset]:
    # Check against the bounding box of the original scene, can throw away some portions
    # (Only needed for index drivers without spatial index support)
    query_crs = polygon.crs
    for dataset in datasets:
        if dataset.extent and intersects(
            polygon, dataset.extent.to_crs(query_crs, resolution="auto")
        ):
            yield dataset


def fuse_lazy(
    datasets: Iterable[Dataset],
    geobox: GeoBox,
    measurement: Measurement,
    skip_broken_datasets: bool = False,
    prepend_dims: int = 0,
    extra_dim_index: int | None = None,
    patch_url: Callable[[str], str] | None = None,
) -> numpy.ndarray:
    prepend_shape = (1,) * prepend_dims
    data = numpy.full(geobox.shape, measurement.nodata, dtype=measurement.dtype)
    _fuse_measurement(
        data,
        datasets,
        geobox,
        measurement,
        skip_broken_datasets=skip_broken_datasets,
        extra_dim_index=extra_dim_index,
        patch_url=patch_url,
    )
    return data.reshape(prepend_shape + geobox.shape)


def _fuse_measurement(
    dest: numpy.ndarray,
    datasets: Iterable[Dataset],
    geobox: GeoBox,
    measurement: Measurement,
    skip_broken_datasets: bool = False,
    progress_cbk: ProgressFunction | None = None,
    extra_dim_index: int | None = None,
    patch_url: Callable[[str], str] | None = None,
) -> None:
    srcs = []
    for ds in datasets:
        src = None
        with ignore_exceptions_if(skip_broken_datasets):
            src = new_datasource(BandInfo(ds, measurement.name, patch_url=patch_url))

        if src is None:
            if not skip_broken_datasets:
                raise ValueError(f"Failed to load dataset: {ds.id}")
        else:
            srcs.append(src)

    reproject_and_fuse(
        srcs,
        dest,
        geobox,
        dest.dtype.type(measurement.nodata),
        resampling=measurement.get("resampling_method", "nearest"),
        fuse_func=measurement.get("fuser", None),
        skip_broken_datasets=skip_broken_datasets,
        progress_cbk=progress_cbk,
        extra_dim_index=extra_dim_index,
    )


def get_bounds(datasets: Iterable[Dataset], crs: CRS) -> Geometry:
    bbox = bbox_union(ds.extent.to_crs(crs).boundingbox for ds in datasets if ds.extent)
    return box(*bbox, crs=crs)  # type: ignore[misc]


def _calculate_chunk_sizes(
    sources: xarray.DataArray,
    geobox: GeoBox,
    dask_chunks: Mapping[str, int | Literal["auto"]],
    extra_dims: ExtraDimensions | None = None,
) -> tuple[tuple, ...]:
    extra_dim_names: tuple[str, ...] = ()
    extra_dim_shapes: tuple[int, ...] = ()
    if extra_dims is not None:
        extra_dim_names, extra_dim_shapes = extra_dims.chunk_size()

    valid_keys = (
        tuple(str(dim) for dim in sources.dims) + extra_dim_names + geobox.dimensions
    )
    bad_keys = dask_chunks.keys() - set(valid_keys)
    if bad_keys:
        raise KeyError(
            f"Unknown dask_chunk dimension {bad_keys}. Valid dimensions are: {valid_keys}"
        )

    chunk_maxsz = dict(
        zip(
            sources.dims + extra_dim_names + geobox.dimensions,
            sources.shape + extra_dim_shapes + geobox.shape,
        )
    )

    # defaults: 1 for non-spatial, whole dimension for Y/X
    chunk_defaults = dict(
        [(dim, 1) for dim in sources.dims]
        + [(dim, 1) for dim in extra_dim_names]
        + [(dim, -1) for dim in geobox.dimensions]
    )

    def _resolve(k, v: str | int | None) -> int:
        if v is None or v == "auto":
            v = _resolve(k, chunk_defaults[k])

        if isinstance(v, int):
            if v < 0:
                return chunk_maxsz[k]
            return v
        raise ValueError("Chunk should be one of int|'auto'")

    irr_chunks = tuple(_resolve(dim, dask_chunks.get(str(dim))) for dim in sources.dims)
    extra_dim_chunks = tuple(
        _resolve(dim, dask_chunks.get(str(dim))) for dim in extra_dim_names
    )
    grid_chunks = tuple(
        _resolve(dim, dask_chunks.get(str(dim))) for dim in geobox.dimensions
    )

    if extra_dim_chunks:
        return irr_chunks, extra_dim_chunks, grid_chunks
    return irr_chunks, grid_chunks


def _tokenize_dataset(dataset: Dataset) -> str:
    return f"dataset-{dataset.id.hex}"


# pylint: disable=too-many-locals
def _make_dask_array(
    chunked_srcs: xarray.DataArray,
    dsk,
    gbt,
    measurement: Measurement,
    chunks,
    skip_broken_datasets: bool = False,
    extra_dims: ExtraDimensions | None = None,
    patch_url: Callable[[str], str] | None = None,
):
    dsk = dsk.copy()  # this contains mapping from dataset id to dataset object

    token = uuid.uuid4().hex
    dsk_name = f"dc_load_{measurement.name}-{token}"

    needed_irr_chunks, grid_chunks = chunks[:-2], chunks[-2:]
    actual_irr_chunks = (1,) * len(needed_irr_chunks)

    # we can have up to 4 empty chunk shapes: whole, right edge, bottom edge and
    # bottom right corner
    #  W R
    #  B BR
    empties: dict[tuple[int, int], str] = {}

    def _mk_empty(shape: tuple[int, int]) -> str:
        name = empties.get(shape)
        if name is not None:
            return name

        name = "empty_{}x{}-{token}".format(*shape, token=token)
        dsk[name] = (
            numpy.full,
            actual_irr_chunks + shape,
            measurement.nodata,
            measurement.dtype,
        )
        empties[shape] = name

        return name

    for irr_index, tiled_dss in numpy.ndenumerate(chunked_srcs.values):
        key_prefix = (dsk_name, *irr_index)

        # all spatial chunks
        for idx in numpy.ndindex(gbt.shape.shape):
            dss = tiled_dss.get(idx, None)

            if dss is None:
                val3d = _mk_empty(gbt.chunk_shape(idx).yx)
                # 3D case
                if "extra_dim" in measurement:
                    assert extra_dims is not None  # For type checker
                    index_subset = extra_dims.measurements_index(measurement.extra_dim)
                    for result_index, _ in numpy.ndenumerate(range(*index_subset)):
                        dsk[key_prefix + result_index + idx] = val3d
                else:
                    dsk[key_prefix + idx] = val3d
            else:
                val = (
                    fuse_lazy,
                    [_tokenize_dataset(ds) for ds in dss],
                    gbt[idx],
                    measurement,
                    skip_broken_datasets,
                    len(needed_irr_chunks),
                )

                # 3D case
                if "extra_dim" in measurement:
                    # Do extra_dim subsetting here
                    assert extra_dims is not None  # For type checker
                    index_subset = extra_dims.measurements_index(measurement.extra_dim)
                    for result_index, extra_dim_index in enumerate(
                        range(*index_subset)
                    ):
                        dsk[(*key_prefix, result_index, *idx)] = (
                            *val,
                            extra_dim_index,
                            patch_url,
                        )
                else:
                    # Get extra_dim index if available
                    extra_dim_index = measurement.get("extra_dim_index", None)
                    dsk[key_prefix + idx] = (*val, extra_dim_index, patch_url)

    y_shapes = [grid_chunks[0]] * gbt.shape[0]
    x_shapes = [grid_chunks[1]] * gbt.shape[1]

    y_shapes[-1], x_shapes[-1] = gbt.chunk_shape(tuple(n - 1 for n in gbt.shape))

    extra_dim_shape: tuple = ()
    if "extra_dim" in measurement:
        assert extra_dims is not None  # For type checker
        dim_name = measurement.extra_dim
        extra_dim_shape += (len(extra_dims.measurements_values(dim_name)),)

    data = da.Array(
        dsk,
        dsk_name,
        chunks=(*actual_irr_chunks, tuple(y_shapes), tuple(x_shapes)),
        dtype=measurement.dtype,
        shape=(chunked_srcs.shape + extra_dim_shape + gbt.base.shape),
    )

    if needed_irr_chunks != actual_irr_chunks:
        data = data.rechunk(chunks=chunks)
    return data


def _handle_legacy_resolution(
    resolution: tuple[int | float, int | float] | list[int | float],
) -> int | float | Resolution | None:
    warnings.warn(
        "The use of tuples or lists for resolution is deprecated. "
        "Square resolutions can be provided as an int or float, "
        "or axis order can be specified with odc.geo.resxy_ or odc.geo.resyx_. "
        "Legacy resolution formats are assumed to use (y, x) ordering.",
        ODC2DeprecationWarning,
        stacklevel=2,
    )
    if not len(resolution):
        _LOG.warning("Empty resolution value. Ignoring")
        return None
    if len(resolution) == 1:
        return resolution[0]
    if len(resolution) > 2:
        raise ValueError("Resolution cannot have more than 2 dimensions.")
    if resolution[0] == -resolution[1]:
        return res_(resolution[1])
    return resyx_(*resolution)


def _normalise_geobox(
    gbox: GeoBox | LegacyGeoBox | xarray.Dataset | xarray.DataArray,
) -> GeoBox:
    """Retain support for legacy geoboxes by converting them to odc.geo GeoBoxes."""
    if isinstance(gbox, GeoBox):
        # Is already a GeoBox
        return gbox

    if isinstance(gbox, xarray.Dataset | xarray.DataArray):
        # Is an Xarray object
        return gbox.odc.geobox

    # Is a legacy GeoBox: convert to odc.geo.geobox.GeoBox.
    warnings.warn(
        "The use of datacube.utils.geometry.GeoBox objects is deprecated, "
        "and support will be removed in a future release.\n"
        "Now converting to an odc.geo GeoBox.",
        ODC2DeprecationWarning,
        stacklevel=3,
    )
    crs = None if gbox.crs is None else gbox.crs._str
    return GeoBox(shape=gbox.shape, affine=gbox.affine, crs=crs)
