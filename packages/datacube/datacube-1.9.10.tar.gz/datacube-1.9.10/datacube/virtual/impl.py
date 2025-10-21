# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Implementation of virtual products. Provides an interface for the products in the datacube
to query and to load data, and combinators to combine multiple products into "virtual"
products implementing the same interface.
"""

import uuid
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Hashable, Iterable, Iterator, Mapping, Sequence
from collections.abc import Mapping as TypeMapping
from typing import Any, cast

import dask.array
import numpy
import xarray
import yaml
from dask.core import flatten
from odc.geo.geobox import GeoBox, GeoboxTiles, geobox_union_conservative
from odc.geo.math import is_affine_st
from odc.geo.overlap import compute_reproject_roi
from odc.geo.warp import resampling_s2rio, rio_reproject
from odc.geo.xr import xr_coords
from typing_extensions import override

from datacube import Datacube
from datacube.api.core import output_geobox, per_band_load_data_settings
from datacube.api.query import Query, query_group_by
from datacube.index import Index
from datacube.model import Measurement, Product
from datacube.model.utils import SafeDumper, xr_apply, xr_iter
from datacube.testutils.io import native_geobox

from .utils import (
    merge_dicts,
    merge_search_terms,
    qualified_name,
    reject_keys,
    select_keys,
    select_unique,
)


class VirtualProductException(Exception):  # noqa: N818
    """Raised if the construction of the virtual product cannot be validated."""


class VirtualDatasetBag:
    """Result of `VirtualProduct.query`."""

    def __init__(self, bag, geopolygon, product_definitions) -> None:
        self.bag = bag
        self.geopolygon = geopolygon
        self.product_definitions = product_definitions

    def contained_datasets(self):
        def worker(bag):
            if isinstance(bag, Sequence):
                for child in bag:
                    yield child

            elif isinstance(bag, Mapping):
                # there should only be one key (collate or juxtapose)
                for key in bag:
                    # bag[key] should be a list
                    for child in bag[key]:
                        yield from worker(child)

            else:
                raise VirtualProductException("unexpected bag")

        return worker(self.bag)

    def explode(self) -> Iterator:
        def worker(bag):
            if isinstance(bag, Sequence):
                for child in bag:
                    yield [child]

            elif isinstance(bag, Mapping):
                if "juxtapose" in bag:
                    # too hard, giving up
                    raise NotImplementedError

                for index, child_bag in enumerate(bag["collate"]):
                    for child in worker(child_bag):
                        yield {
                            "collate": [
                                child if i == index else []
                                for i, _ in enumerate(bag["collate"])
                            ]
                        }

            else:
                raise VirtualProductException("unexpected bag")

        for child in worker(self.bag):
            yield VirtualDatasetBag(child, self.geopolygon, self.product_definitions)

    @override
    def __repr__(self) -> str:
        return f"<VirtualDatasetBag of {len(list(self.contained_datasets()))} datacube datasets>"


class VirtualDatasetBox:
    """Result of `VirtualProduct.group`."""

    def __init__(
        self, box, geobox, load_natively, product_definitions, geopolygon=None
    ) -> None:
        if not load_natively and geobox is None:
            raise VirtualProductException("VirtualDatasetBox has no geobox")
        if not load_natively and geopolygon is not None:
            raise VirtualProductException("unexpected geopolygon for VirtualDatasetBox")

        self.box = box
        self.geobox = geobox
        self.load_natively = load_natively
        self.product_definitions = product_definitions
        self.geopolygon = geopolygon

    @override
    def __repr__(self) -> str:
        if not self.load_natively:
            return f"<VirtualDatasetBox of shape {dict(zip(self.dims, self.shape))}>"

        return "<natively loaded VirtualDatasetBox>"

    @property
    def dims(self):
        """
        Names of the dimensions, e.g., ``('time', 'y', 'x')``.
        :return: tuple(str)
        """
        if self.load_natively:
            raise VirtualProductException("dims requires known geobox")

        return self.box.dims + self.geobox.dimensions

    @property
    def shape(self):
        """
        Lengths of each dimension, e.g., ``(285, 4000, 4000)``.
        :return: tuple(int)
        """
        if self.load_natively:
            raise VirtualProductException("shape requires known geobox")

        return self.box.shape + self.geobox.shape

    def __getitem__(self, chunk) -> "VirtualDatasetBox":
        if self.load_natively:
            raise VirtualProductException("slicing requires known geobox")

        # TODO implement this properly
        box = self.box

        return VirtualDatasetBox(
            _fast_slice(box, chunk[: len(box.shape)]),
            self.geobox[chunk[len(box.shape) :]],
            self.load_natively,
            self.product_definitions,
            geopolygon=self.geopolygon,
        )

    def map(self, func, dtype: str = "O") -> "VirtualDatasetBox":
        return VirtualDatasetBox(
            xr_apply(self.box, func, dtype=dtype),
            self.geobox,
            self.load_natively,
            self.product_definitions,
            geopolygon=self.geopolygon,
        )

    def filter(self, predicate) -> "VirtualDatasetBox":
        mask = self.map(predicate, dtype="bool")

        # NOTE: this could possibly result in an empty box
        return VirtualDatasetBox(
            self.box[mask.box],
            self.geobox,
            self.load_natively,
            self.product_definitions,
            geopolygon=self.geopolygon,
        )

    def split(self, dim: str = "time"):
        box = self.box

        [length] = box[dim].shape
        for i in range(length):
            yield VirtualDatasetBox(
                box.isel(**{dim: slice(i, i + 1)}),
                self.geobox,
                self.load_natively,
                self.product_definitions,
                geopolygon=self.geopolygon,
            )

    def input_datasets(self):
        def traverse(entry):
            if isinstance(entry, Mapping):
                if "collate" in entry:
                    _, child = entry["collate"]
                    yield from traverse(child)
                elif "juxtapose" in entry:
                    for child in entry["juxtapose"]:
                        yield from traverse(child)
                else:
                    raise VirtualProductException("malformed box")

            elif isinstance(entry, Sequence):
                yield from entry

            elif isinstance(entry, VirtualDatasetBox):
                for _, _, child in xr_iter(entry.input_datasets()):
                    yield from child

            else:
                raise VirtualProductException("malformed box")

        def worker(index: Index, entry):
            return set(traverse(entry))

        return self.map(worker).box


class Transformation(ABC):
    """
    A user-defined on-the-fly data transformation.

    The data coming in and out of the `compute` method are `xarray.Dataset` objects.
    The measurements are stored as `xarray.DataArray` objects inside it.

    The `measurements` method transforms the dictionary mapping measurement names
    to `datacube.model.Measurement` objects describing the input data
    into a dictionary describing the measurements of the output data
    produced by the `compute` method.
    """

    @abstractmethod
    def measurements(self, input_measurements) -> dict[str, Measurement]:
        """
        Returns the dictionary describing the output measurements from this transformation.
        Assumes the `data` provided to `compute` will have measurements
        given by the dictionary `input_measurements`.
        """

    @abstractmethod
    def compute(self, data):
        """
        Perform computation on `data` that results in an `xarray.Dataset`
        having measurements reported by the `measurements` method.
        """


class VirtualProduct(Mapping):
    """
    A recipe for combining loaded data from multiple datacube products.

    Basic combinators are:
        - product: an existing datacube product
        - transform: on-the-fly computation on data being loaded
        - collate: stack observations from products with the same set of measurements
        - juxtapose: put measurements from different products side-by-side
        - aggregate: take (non-spatial) statistics of grouped data
        - reproject: on-the-fly reprojection of raster data
    """

    _GEOBOX_KEYS = {"output_crs", "resolution", "align"}
    _GROUPING_KEYS = {"group_by"}
    _LOAD_KEYS = {
        "measurements",
        "fuse_func",
        "resampling",
        "dask_chunks",
        "like",
        "skip_broken_datasets",
    }
    _ADDITIONAL_SEARCH_KEYS = {"dataset_predicate", "ensure_location"}

    _NON_QUERY_KEYS = _GEOBOX_KEYS | _GROUPING_KEYS | _LOAD_KEYS

    # helper methods

    @override
    def __getitem__(self, key):
        return self._settings[key]

    @override
    def __len__(self) -> int:
        return len(self._settings)

    @override
    def __iter__(self) -> Iterator:
        return iter(self._settings)

    @staticmethod
    def _assert(cond, msg) -> None:
        if not cond:
            raise VirtualProductException(msg)

    # public interface

    def __init__(self, settings: dict[str, Any]) -> None:
        """
        :param settings: validated and reference-resolved recipe
        """
        self._settings = settings

    def output_measurements(
        self, product_definitions: dict[str, Product]
    ) -> dict[str, Measurement]:
        """
        A dictionary mapping names to measurement metadata.
        :param product_definitions: a dictionary mapping product names to products (`Product` objects)
        """
        raise NotImplementedError

    def query(self, dc: Datacube, **search_terms: dict[str, Any]) -> VirtualDatasetBag:
        """Collection of datasets that match the query."""
        raise NotImplementedError

    # no index access below this line

    def group(
        self, datasets: VirtualDatasetBag, **group_settings: dict[str, Any]
    ) -> VirtualDatasetBox:
        """
        Datasets grouped by their timestamps.
        :param datasets: the `VirtualDatasetBag` to fetch data from
        """
        raise NotImplementedError

    def fetch(
        self, grouped: VirtualDatasetBox, **load_settings: dict[str, Any]
    ) -> xarray.Dataset:
        """Convert grouped datasets to `xarray.Dataset`."""
        raise NotImplementedError

    @override
    def __repr__(self) -> str:
        return yaml.dump(
            self._reconstruct(),  # type: ignore[attr-defined]
            Dumper=SafeDumper,
            default_flow_style=False,
            indent=2,
        )

    def load(self, dc: Datacube, **query: dict[str, Any]) -> xarray.Dataset:
        """Mimic `datacube.Datacube.load`. For illustrative purposes. May be removed in the future."""
        datasets = self.query(dc, **query)
        grouped = self.group(datasets, **query)
        return self.fetch(grouped, **query)


class Product(VirtualProduct):  # type: ignore[no-redef]
    """An existing datacube product."""

    # TODO: We have ODC model Products throughout this source file as type hints.  Are the Product type hints in this
    #       module after this definition this class or the normal Product model class?
    #       Either this class should be renamed or Product imported as e.g. OdcProduct

    @property
    def _product(self):
        """The name of an existing datacube product."""
        return self["product"]

    def _reconstruct(self) -> dict:
        return {
            key: value
            if key not in ["fuse_func", "dataset_predicate"]
            else qualified_name(value)
            for key, value in self.items()
        }

    @override
    def output_measurements(  # type: ignore[override]
        self,
        product_definitions: TypeMapping[str, Product],
        measurements: list[str] | None = None,
    ) -> TypeMapping[str, Measurement]:
        self._assert(
            self._product in product_definitions,
            f"product {self._product} not found in definitions",
        )

        if measurements is None:
            measurements = self.get("measurements")

        product = product_definitions[self._product]
        return product.lookup_measurements(measurements)

    @override
    def query(self, dc: Datacube, **search_terms: dict[str, Any]) -> VirtualDatasetBag:
        product = dc.index.products.get_by_name(self._product)
        if product is None:
            raise VirtualProductException(f"could not find product {self._product}")

        merged_terms = merge_search_terms(
            reject_keys(self, self._NON_QUERY_KEYS),
            reject_keys(search_terms, self._NON_QUERY_KEYS),
        )

        query = Query(
            dc.index, **reject_keys(merged_terms, self._ADDITIONAL_SEARCH_KEYS)
        )
        self._assert(
            query.product == self._product,
            f"query for {self._product} returned another product {query.product}",
        )

        return VirtualDatasetBag(
            dc.find_datasets(**merged_terms), query.geopolygon, {product.name: product}
        )

    @override
    def group(
        self, datasets: VirtualDatasetBag, **group_settings: dict[str, Any]
    ) -> VirtualDatasetBox:
        geopolygon = datasets.geopolygon
        selected = list(datasets.bag)

        # geobox
        merged = merge_search_terms(self, group_settings)

        try:
            if isinstance(merged.get("like"), GeoBox):
                geobox = merged["like"]
            else:
                geobox = output_geobox(
                    datasets=selected,
                    grid_spec=datasets.product_definitions[self._product].grid_spec,
                    geopolygon=geopolygon,
                    **select_keys(merged, self._GEOBOX_KEYS),
                )
            load_natively = False

        except ValueError:
            # we are not calculating geoboxes here for the moment
            # since it may require filesystem access
            # in ODC 2.0 the dataset should know the information required
            geobox = None
            load_natively = True

        # group by time
        group_query = query_group_by(**select_keys(merged, self._GROUPING_KEYS))

        # information needed for Datacube.load_data
        return VirtualDatasetBox(
            Datacube.group_datasets(selected, group_query),
            geobox,
            load_natively,
            datasets.product_definitions,
            geopolygon=None if not load_natively else geopolygon,
        )

    @override
    def fetch(
        self, grouped: VirtualDatasetBox, **load_settings: dict[str, Any]
    ) -> xarray.Dataset:
        """Convert grouped datasets to `xarray.Dataset`."""

        load_keys = self._LOAD_KEYS - {"measurements"}
        merged = merge_search_terms(
            select_keys(self, load_keys), select_keys(load_settings, load_keys)
        )

        product = grouped.product_definitions[self._product]

        if "measurements" in self and "measurements" in load_settings:
            for measurement in load_settings["measurements"]:
                self._assert(
                    measurement in self["measurements"],
                    f"{measurement} not found in {self._product}",
                )

        measurement_dicts = self.output_measurements(
            grouped.product_definitions,
            cast(list[str], load_settings.get("measurements")),
        )

        if grouped.load_natively:
            canonical_names = [
                product.canonical_measurement(measurement)
                for measurement in measurement_dicts
            ]
            dataset_geobox = geobox_union_conservative(
                [
                    native_geobox(
                        ds, measurements=canonical_names, basis=merged.get("like")
                    )
                    for ds in grouped.box.sum().item()
                ]
            )

            if grouped.geopolygon is not None:
                reproject_roi = compute_reproject_roi(
                    dataset_geobox,
                    GeoBox.from_geopolygon(
                        grouped.geopolygon,
                        crs=dataset_geobox.crs,
                        align=dataset_geobox.alignment,
                        resolution=dataset_geobox.resolution,
                    ),
                )

                assert reproject_roi.transform.linear is not None  # for type checker.
                self._assert(
                    is_affine_st(reproject_roi.transform.linear),
                    "native load is not axis-aligned",
                )
                self._assert(
                    numpy.isclose(reproject_roi.scale, 1.0),
                    "native load should not require scaling",
                )

                geobox = dataset_geobox[reproject_roi.roi_src]
            else:
                geobox = dataset_geobox
        else:
            geobox = grouped.geobox

        return Datacube.load_data(
            grouped.box,
            geobox,
            list(measurement_dicts.values()),
            fuse_func=merged.get("fuse_func"),
            dask_chunks=merged.get("dask_chunks"),
            skip_broken_datasets=merged.get("skip_broken_datasets", False),
            resampling=merged.get("resampling", "nearest"),
        )


class Transform(VirtualProduct):
    """An on-the-fly transformation."""

    @property
    def _transformation(self) -> Transformation:
        """The `Transformation` object associated with a transform product."""
        cls = self["transform"]

        try:
            obj = cls(
                **{
                    key: value
                    for key, value in self.items()
                    if key not in ["transform", "input"]
                }
            )
        except TypeError:
            raise VirtualProductException(
                f"transformation {cls} could not be instantiated"
            ) from None

        self._assert(
            isinstance(obj, Transformation), f"not a transformation object: {obj}"
        )

        return cast(Transformation, obj)

    @property
    def _input(self) -> VirtualProduct:
        """The input product of a transform product."""
        return from_validated_recipe(self["input"])

    def _reconstruct(self) -> dict[str, Any]:
        # pylint: disable=protected-access
        return dict(
            transform=qualified_name(self["transform"]),
            input=self._input._reconstruct(),  # type: ignore[attr-defined]
            **reject_keys(self, ["input", "transform"]),
        )

    @override
    def output_measurements(
        self, product_definitions: dict[str, Product]
    ) -> dict[str, Measurement]:
        input_measurements = self._input.output_measurements(product_definitions)

        return self._transformation.measurements(input_measurements)

    @override
    def query(self, dc: Datacube, **search_terms: dict[str, Any]) -> VirtualDatasetBag:
        return self._input.query(dc, **search_terms)

    @override
    def group(
        self, datasets: VirtualDatasetBag, **group_settings: dict[str, Any]
    ) -> VirtualDatasetBox:
        return self._input.group(datasets, **group_settings)

    @override
    def fetch(
        self, grouped: VirtualDatasetBox, **load_settings: dict[str, Any]
    ) -> xarray.Dataset:
        input_data = self._input.fetch(grouped, **load_settings)
        output_data = self._transformation.compute(input_data)
        output_data.attrs["crs"] = input_data.attrs["crs"]
        for data_var in output_data.data_vars:
            output_data[data_var].attrs["crs"] = input_data.attrs["crs"]
        return output_data


class Aggregate(VirtualProduct):
    """A (non-spatial) statistic of grouped data."""

    @property
    def _statistic(self) -> Transformation:
        """The `Transformation` object associated with an aggregate product."""
        cls = self["aggregate"]

        try:
            obj = cls(
                **{
                    key: value
                    for key, value in self.items()
                    if key not in ["aggregate", "input", "group_by"]
                }
            )
        except TypeError:
            raise VirtualProductException(
                f"transformation {cls} could not be instantiated"
            ) from None

        self._assert(
            isinstance(obj, Transformation), f"not a transformation object: {obj}"
        )

        return cast(Transformation, obj)

    @property
    def _input(self) -> VirtualProduct:
        """The input product of a transform product."""
        return from_validated_recipe(self["input"])

    def _reconstruct(self) -> dict[str, Any]:
        # pylint: disable=protected-access
        return dict(
            aggregate=qualified_name(self["aggregate"]),
            group_by=qualified_name(self["group_by"]),
            input=self._input._reconstruct(),  # type: ignore[attr-defined]
            **reject_keys(self, ["input", "aggregate", "group_by"]),
        )

    @override
    def output_measurements(
        self, product_definitions: dict[str, Product]
    ) -> dict[str, Measurement]:
        input_measurements = self._input.output_measurements(product_definitions)

        return self._statistic.measurements(input_measurements)

    @override
    def query(self, dc: Datacube, **search_terms: dict[str, Any]) -> VirtualDatasetBag:
        return self._input.query(dc, **search_terms)

    @override
    def group(
        self, datasets: VirtualDatasetBag, **group_settings: dict[str, Any]
    ) -> VirtualDatasetBox:
        grouped = self._input.group(datasets, **group_settings)
        dim = self.get("dim", "time")

        def to_box(value):
            return xarray.DataArray(
                [
                    VirtualDatasetBox(
                        value,
                        grouped.geobox,
                        grouped.load_natively,
                        grouped.product_definitions,
                        geopolygon=grouped.geopolygon,
                    )
                ],
                dims=["_fake_"],
            )

        # TODO: use a proper `GroupBy` object instead
        result = (
            grouped.box.groupby(self["group_by"](grouped.box[dim]), squeeze=False)
            .apply(to_box)
            .squeeze("_fake_")
        )
        result[dim].attrs.update(grouped.box[dim].attrs)

        return VirtualDatasetBox(
            result,
            grouped.geobox,
            grouped.load_natively,
            grouped.product_definitions,
            geopolygon=grouped.geopolygon,
        )

    @override
    def fetch(
        self, grouped: VirtualDatasetBox, **load_settings: dict[str, Any]
    ) -> xarray.Dataset:
        dim = self.get("dim", "time")

        def xr_map(array, func):
            # convenient function close to `xr_apply` in spirit
            coords = {key: value.values for key, value in array.coords.items()}
            for i in numpy.ndindex(array.shape):
                yield func(
                    {key: value[i] for key, value in coords.items()}, array.values[i]
                )

        def statistic(coords, value):
            data = self._input.fetch(value, **load_settings)
            result = self._statistic.compute(data)
            result.coords[dim] = coords[dim]
            return result.drop_indexes(dim, errors="ignore")

        groups = list(xr_map(grouped.box, statistic))
        result = xarray.concat(groups, dim=dim).assign_attrs(
            **select_unique([g.attrs for g in groups])
        )
        result.coords[dim].attrs.update(grouped.box[dim].attrs)
        return result


class Collate(VirtualProduct):
    """Stack observations from products with the same set of measurements."""

    @property
    def _children(self) -> list[VirtualProduct]:
        """The children of a collate product."""
        return [from_validated_recipe(child) for child in self["collate"]]

    def _reconstruct(self):
        # pylint: disable=protected-access
        children = [child._reconstruct() for child in self._children]
        return dict(collate=children, **reject_keys(self, ["collate"]))

    @override
    def output_measurements(
        self, product_definitions: dict[str, Product]
    ) -> dict[str, Measurement]:
        input_measurement_list = [
            child.output_measurements(product_definitions) for child in self._children
        ]

        first, *rest = input_measurement_list

        for child in rest:
            self._assert(
                set(child) == set(first),
                "child datasets do not all have the same set of measurements",
            )

        name = self.get("index_measurement_name")
        if name is None:
            return first

        self._assert(
            name not in first, f"source index measurement '{name}' already present"
        )

        first.update({name: Measurement(name=name, dtype="int8", nodata=-1, units="1")})
        return first

    @override
    def query(self, dc: Datacube, **search_terms: dict[str, Any]) -> VirtualDatasetBag:
        result = [child.query(dc, **search_terms) for child in self._children]

        return VirtualDatasetBag(
            {"collate": [datasets.bag for datasets in result]},
            select_unique([datasets.geopolygon for datasets in result]),
            merge_dicts([datasets.product_definitions for datasets in result]),
        )

    @override
    def group(
        self, datasets: VirtualDatasetBag, **group_settings: dict[str, Any]
    ) -> VirtualDatasetBox:
        self._assert(
            "collate" in datasets.bag
            and len(datasets.bag["collate"]) == len(self._children),
            "invalid dataset bag",
        )

        def build(source_index, product, dataset_bag):
            grouped = product.group(
                VirtualDatasetBag(
                    dataset_bag, datasets.geopolygon, datasets.product_definitions
                ),
                **group_settings,
            )

            def tag(_, value):
                return {"collate": (source_index, value)}

            return grouped.map(tag)

        groups = [
            build(source_index, product, dataset_bag)
            for source_index, (product, dataset_bag) in enumerate(
                zip(self._children, datasets.bag["collate"])
            )
        ]

        dim = self.get("dim", "time")
        return VirtualDatasetBox(
            xarray.concat(
                [grouped.box for grouped in groups if grouped.box.shape[0] > 0], dim=dim
            ).sortby(dim),
            select_unique([grouped.geobox for grouped in groups]),
            select_unique([grouped.load_natively for grouped in groups]),
            merge_dicts([grouped.product_definitions for grouped in groups]),
            geopolygon=select_unique([grouped.geopolygon for grouped in groups]),
        )

    @override
    def fetch(
        self, grouped: VirtualDatasetBox, **load_settings: dict[str, Any]
    ) -> xarray.Dataset:
        def is_from(source_index):
            def result(_, value):
                self._assert("collate" in value, "malformed dataset box in collate")
                return value["collate"][0] == source_index

            return result

        def strip_source(_, value):
            return value["collate"][1]

        def fetch_child(child, source_index, r):
            if any(x == 0 for x in r.box.shape):
                # empty raster
                return None
            result = child.fetch(r, **load_settings)
            name = self.get("index_measurement_name")

            if name is None:
                return result

            # implication for dask?
            measurement = Measurement(name=name, dtype="int8", nodata=-1, units="1")
            shape = select_unique([result[band].shape for band in result.data_vars])
            array = numpy.full(shape, source_index, dtype=measurement.dtype)
            first = result[next(iter(result.data_vars))]
            result[name] = xarray.DataArray(
                array, dims=first.dims, coords=first.coords, name=name
            ).assign_attrs(units=measurement.units, nodata=measurement.nodata)
            return result

        groups = [
            fetch_child(
                child,
                source_index,
                grouped.filter(is_from(source_index)).map(strip_source),
            )
            for source_index, child in enumerate(self._children)
        ]

        non_empty = [g for g in groups if g is not None]

        dim = self.get("dim", "time")

        result = (
            xarray.concat(non_empty, dim=dim)
            .sortby(dim)
            .assign_attrs(**select_unique([g.attrs for g in non_empty]))
        )

        # concat and sortby mess up chunking
        if (
            "dask_chunks" not in load_settings
            or dim not in load_settings["dask_chunks"]
        ):
            return result
        return result.apply(
            lambda x: x.chunk({dim: load_settings["dask_chunks"][dim]}), keep_attrs=True
        )


class Juxtapose(VirtualProduct):
    """Put measurements from different products side-by-side."""

    @property
    def _children(self) -> list[VirtualProduct]:
        """The children of a juxtapose product."""
        return [from_validated_recipe(child) for child in self["juxtapose"]]

    def _reconstruct(self):
        # pylint: disable=protected-access
        children = [child._reconstruct() for child in self._children]
        return dict(juxtapose=children, **reject_keys(self, ["juxtapose"]))

    @override
    def output_measurements(
        self, product_definitions: dict[str, Product]
    ) -> dict[str, Measurement]:
        input_measurement_list = [
            child.output_measurements(product_definitions) for child in self._children
        ]

        result = cast(dict[str, Measurement], {})
        for measurements in input_measurement_list:
            common = set(result) & set(measurements)
            self._assert(not common, f"common measurements {common} between children")

            result.update(measurements)

        return result

    @override
    def query(self, dc: Datacube, **search_terms: dict[str, Any]) -> VirtualDatasetBag:
        result = [child.query(dc, **search_terms) for child in self._children]

        return VirtualDatasetBag(
            {"juxtapose": [datasets.bag for datasets in result]},
            select_unique([datasets.geopolygon for datasets in result]),
            merge_dicts([datasets.product_definitions for datasets in result]),
        )

    @override
    def group(
        self, datasets: VirtualDatasetBag, **group_settings: dict[str, Any]
    ) -> VirtualDatasetBox:
        self._assert(
            "juxtapose" in datasets.bag
            and len(datasets.bag["juxtapose"]) == len(self._children),
            "invalid dataset bag",
        )

        groups = [
            product.group(
                VirtualDatasetBag(
                    dataset_bag, datasets.geopolygon, datasets.product_definitions
                ),
                **group_settings,
            )
            for product, dataset_bag in zip(self._children, datasets.bag["juxtapose"])
        ]

        aligned_boxes = xarray.align(*[grouped.box for grouped in groups])

        def tuplify(indexes, _):
            return {"juxtapose": [box.sel(**indexes).item() for box in aligned_boxes]}

        return VirtualDatasetBox(
            xr_apply(aligned_boxes[0], tuplify),
            select_unique([grouped.geobox for grouped in groups]),
            select_unique([grouped.load_natively for grouped in groups]),
            merge_dicts([grouped.product_definitions for grouped in groups]),
            geopolygon=select_unique([grouped.geopolygon for grouped in groups]),
        )

    @override
    def fetch(
        self, grouped: VirtualDatasetBox, **load_settings: dict[str, Any]
    ) -> xarray.Dataset:
        def select_child(source_index):
            def result(_, value):
                self._assert("juxtapose" in value, "malformed dataset box in juxtapose")
                return value["juxtapose"][source_index]

            return result

        def fetch_recipe(source_index):
            child_groups = grouped.map(select_child(source_index))
            return VirtualDatasetBox(
                child_groups.box,
                grouped.geobox,
                grouped.load_natively,
                grouped.product_definitions,
                geopolygon=grouped.geopolygon,
            )

        groups = [
            child.fetch(fetch_recipe(source_index), **load_settings)
            for source_index, child in enumerate(self._children)
        ]

        return xarray.merge(groups).assign_attrs(
            **select_unique([g.attrs for g in groups])
        )


class Reproject(VirtualProduct):
    """
    On-the-fly reprojection of raster data.
    """

    @property
    def _input(self) -> "VirtualProduct":
        """The input product of a transform product."""
        return from_validated_recipe(self["input"])

    def _reconstruct(self) -> dict[str, Any]:
        # pylint: disable=protected-access
        return dict(
            input=self._input._reconstruct(),  # type: ignore[attr-defined]
            **reject_keys(self, ["input"]),
        )

    @override
    def output_measurements(
        self, product_definitions: dict[str, Product]
    ) -> dict[str, Measurement]:
        """
        A dictionary mapping names to measurement metadata.
        :param product_definitions: a dictionary mapping product names to products (`Product` objects)
        """
        return self._input.output_measurements(product_definitions)

    @override
    def query(self, dc: Datacube, **search_terms: dict[str, Any]) -> VirtualDatasetBag:
        """Collection of datasets that match the query."""
        return self._input.query(dc, **reject_keys(search_terms, self._GEOBOX_KEYS))

    @override
    def group(
        self, datasets: VirtualDatasetBag, **group_settings: dict[str, Any]
    ) -> VirtualDatasetBox:
        """
        Datasets grouped by their timestamps.
        :param datasets: the `VirtualDatasetBag` to fetch data from
        """
        geopolygon = datasets.geopolygon

        merged = merge_search_terms(self, group_settings)
        selected = list(datasets.contained_datasets()) if geopolygon is None else None

        geobox = output_geobox(
            datasets=selected,
            output_crs=self["reproject"]["output_crs"],
            resolution=self["reproject"]["resolution"],
            align=self["reproject"].get("align"),
            geopolygon=geopolygon,
        )

        # load natively
        input_box = self._input.group(
            datasets, **reject_keys(merged, self._GEOBOX_KEYS)
        )

        return VirtualDatasetBox(
            input_box.box,
            geobox,
            True,
            datasets.product_definitions,
            geopolygon=geopolygon,
        )

    @override
    def fetch(
        self, grouped: VirtualDatasetBox, **load_settings: dict[str, Any]
    ) -> xarray.Dataset:
        """Convert grouped datasets to `xarray.Dataset`."""
        from collections import OrderedDict

        spatial_ref = "spatial_ref"

        geobox = grouped.geobox

        measurements = self.output_measurements(grouped.product_definitions)

        band_settings = dict(
            zip(
                list(measurements),
                per_band_load_data_settings(
                    measurements, resampling=self.get("resampling", "nearest")
                ),
            )
        )

        boxes = [
            VirtualDatasetBox(
                box_slice.box,
                None,
                True,
                box_slice.product_definitions,
                geopolygon=geobox.extent,
            )
            for box_slice in grouped.split()
        ]

        dask_chunks = load_settings.get("dask_chunks")
        if dask_chunks is None:
            rasters = [self._input.fetch(box, **load_settings) for box in boxes]
        else:
            rasters = [
                self._input.fetch(
                    box,
                    dask_chunks={
                        key: 1 for key in dask_chunks if key not in geobox.dims
                    },
                    **reject_keys(load_settings, ["dask_chunks"]),
                )
                for box in boxes
            ]

        result = xarray.Dataset()
        result.coords["time"] = grouped.box.coords["time"]

        coords: Mapping[Hashable, xarray.DataArray] = OrderedDict(
            [(str(k), v) for k, v in xr_coords(geobox, spatial_ref).items()]
        )
        result.coords.update(coords)

        for measurement in measurements:
            result[measurement] = xarray.concat(
                [
                    reproject_band(
                        raster[measurement],
                        geobox,
                        band_settings[measurement]["resampling_method"],
                        grouped.box.dims + geobox.dims,
                        dask_chunks,
                    )
                    for raster in rasters
                ],
                dim="time",
            )

        result.attrs["crs"] = geobox.crs
        return result


def reproject_band(
    band, geobox, resampling, dims: str | Iterable[Hashable], dask_chunks=None
) -> xarray.DataArray:
    """Reproject a single measurement to the geobox."""
    if not hasattr(band.data, "dask") or dask_chunks is None:
        data = reproject_array(
            band.data, band.nodata, band.odc.geobox, geobox, resampling
        )
        return wrap_in_dataarray(data, band, geobox, dims)

    dask_name = f"warp_{band.name}-{uuid.uuid4().hex}"
    dependencies = [band.data]

    spatial_chunks = tuple(
        dask_chunks.get(k, geobox.shape[i]) for i, k in enumerate(geobox.dims)
    )

    gt = GeoboxTiles(geobox, spatial_chunks)
    new_layer: dict[tuple[Hashable, xarray.DataArray], Any] = {}

    for tile_index in numpy.ndindex(gt.shape):  # type: ignore[call-overload]
        sub_geobox = gt[tile_index]
        # find the input array slice from the output geobox
        reproject_roi = compute_reproject_roi(band.odc.geobox, sub_geobox, padding=1)

        # find the chunk from the input array with the slice index
        subset_band = band[(..., *reproject_roi.roi_src)].chunk(-1)

        if min(subset_band.shape) == 0:
            # pad the empty chunk
            new_layer[(dask_name, *tile_index)] = (
                numpy.full,
                sub_geobox.shape,
                band.nodata,
                band.dtype,
            )
        else:
            # next 3 lines to generate the new graph
            dependencies.append(subset_band.data)
            # get the input dask array for the function `reproject_array`
            band_key = next(iter(flatten(subset_band.data.__dask_keys__())))
            # generate a new layer of dask graph with reproject
            new_layer[(dask_name, *tile_index)] = (
                reproject_array,
                band_key,
                band.nodata,
                subset_band.geobox,
                sub_geobox,
                resampling,
            )

    # create a new graph with the additional layer and pack the graph into dask.array
    # since only regular chunking is allowed at the higher level dask.array interface,
    # to manipulate the graph seems to be the easiest way to obtain a dask.array with irregular chunks after reproject
    data = dask.array.Array(
        band.data.dask.from_collections(
            dask_name, new_layer, dependencies=dependencies
        ),
        dask_name,
        chunks=spatial_chunks,
        dtype=band.dtype,
        shape=gt.base.shape,
    )

    return wrap_in_dataarray(data, band, geobox, dims)


def reproject_array(src, nodata, s_geobox, d_geobox, resampling):
    """Reproject a numpy array."""
    # add time dimension to the shape to match src dims if needed
    dst_shape = (1, *d_geobox.shape) if src.ndim == 3 else d_geobox.shape
    dst = numpy.full(dst_shape, fill_value=nodata, dtype=src.dtype)
    rio_reproject(
        src=src,
        dst=dst,
        s_gbox=s_geobox,
        d_gbox=d_geobox,  # TODO: rename s_gbox and d_gbox once odc-geo has been updated
        resampling=resampling_s2rio(resampling),
        src_nodata=nodata,
        dst_nodata=nodata,
    )
    return dst


def wrap_in_dataarray(
    reprojected_data, src_band, dst_geobox, dims: str | Iterable[Hashable]
) -> xarray.DataArray:
    """Wrap the reproject numpy array in a `xarray.DataArray` with relevant metadata."""
    non_spatial_shape = src_band.shape[:-2]
    assert all(x == 1 for x in non_spatial_shape)

    result = xarray.DataArray(
        data=reprojected_data.reshape(non_spatial_shape + dst_geobox.shape),
        dims=dims,
        attrs=src_band.attrs,
    )
    result.coords["time"] = src_band.coords["time"]

    for name, coord in dst_geobox.coordinates.items():
        result.coords[name] = (
            name,
            coord.values,
            {"units": coord.units, "resolution": coord.resolution},
        )

    result.attrs["crs"] = dst_geobox.crs
    return result


def virtual_product_kind(recipe: Mapping[str, Any]) -> str:
    """One of product, transform, collate, juxtapose, aggregate, or reproject."""
    candidates = [
        key
        for key in list(recipe)
        if key
        in ["product", "transform", "collate", "juxtapose", "aggregate", "reproject"]
    ]
    if len(candidates) > 1:
        raise VirtualProductException(f"ambiguous kind in recipe: {recipe}")
    if len(candidates) < 1:
        raise VirtualProductException(
            f"virtual product kind not specified in recipe: {recipe}"
        )
    return candidates[0]


def from_validated_recipe(recipe: Mapping[str, Any]) -> VirtualProduct:
    lookup = {
        "product": Product,
        "transform": Transform,
        "collate": Collate,
        "juxtapose": Juxtapose,
        "aggregate": Aggregate,
        "reproject": Reproject,
    }
    return lookup[virtual_product_kind(recipe)](recipe)


def _fast_slice(array, indexers) -> xarray.DataArray:
    data = array.values[indexers]
    dims = [
        dim for dim, indexer in zip(array.dims, indexers) if isinstance(indexer, slice)
    ]
    coords = OrderedDict(
        (
            dim,
            xarray.Variable(
                (dim,),
                array.coords[dim].values[indexer],
                attrs=array.coords[dim].attrs,
                fastpath=True,
            ),
        )
        for dim, indexer in zip(array.dims, indexers)
        if isinstance(indexer, slice)
    )
    return xarray.DataArray(data, dims=dims, coords=coords, attrs=array.attrs)
