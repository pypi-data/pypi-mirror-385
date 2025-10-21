# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Core classes used across modules.
"""

from __future__ import annotations

import logging
import math
from collections import OrderedDict
from collections.abc import Callable, Generator, Iterable, Iterator, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, TypeAlias
from urllib.parse import urlparse
from uuid import UUID

from affine import Affine
from typing_extensions import override

from datacube.utils import (
    DocReader,
    cached_property,
    parse_time,
    schema_validated,
    uri_to_local_path,
    without_lineage_sources,
)

from ._base import Not, QueryDict, QueryField, Range, ranges_overlap  # noqa: F401
from .eo3 import validate_eo3_compatible_type
from .fields import Field, get_dataset_fields
from .lineage import (
    InconsistentLineageException,
    LineageDirection,
    LineageRelation,
    LineageTree,
)

__all__ = [
    "Dataset",
    "ExtraDimensions",
    "Field",
    "GridSpec",
    "InconsistentLineageException",
    "LineageDirection",
    "LineageRelation",
    "LineageTree",
    "Measurement",
    "MetadataType",
    "Product",
    "QueryDict",
    "QueryField",
    "Range",
    "get_dataset_fields",
    "metadata_from_doc",
    "ranges_overlap",
]

import contextlib

from deprecat import deprecat
from odc.geo import (
    CRS,
    BoundingBox,
    Geometry,
    Resolution,
    SomeShape,
    res_,
    resyx_,
    wh_,
    yx_,
)
from odc.geo.geobox import GeoBox
from odc.geo.geom import intersects, polygon
from odc.geo.gridspec import GridSpec as GeoGridSpec
from odc.stac.model import RasterCollectionMetadata

from datacube.migration import ODC2DeprecationWarning

from ..utils.uris import pick_uri

_LOG: logging.Logger = logging.getLogger(__name__)

DEFAULT_SPATIAL_DIMS = ("y", "x")  # Used when product lacks grid_spec

SCHEMA_PATH: Path = Path(__file__).parent / "schema"


# TODO: Multi-dimension code is has incomplete type hints and significant type issues that will require attention


class Dataset:
    """
    A Dataset. A container of metadata, and refers typically to a multi-band raster on disk.

    Most important parts are the metadata_doc and uri.

    Dataset objects should be constructed by an index driver, or with the
    datacube.index.hl.Doc2Dataset

    :param metadata_doc: the document (typically a parsed JSON/YAML)
    :param uris: All active uris for the dataset
    """

    @deprecat(
        deprecated_args={
            "uris": {
                "version": "1.9",
                "reason": "Multiple locations per dataset are deprecated - prefer passing single uri to uri argument",
            }
        }
    )
    def __init__(
        self,
        product: Product,
        metadata_doc: dict[str, Any],
        uris: list[str] | None = None,
        uri: str | None = None,
        sources: Mapping[str, Dataset] | None = None,
        indexed_by: str | None = None,
        indexed_time: datetime | None = None,
        archived_time: datetime | None = None,
        source_tree: LineageTree | None = None,
        derived_tree: LineageTree | None = None,
    ) -> None:
        self.product = product

        #: The document describing the dataset as a dictionary. It is often serialised as YAML on disk
        #: or inside a NetCDF file, and as JSON-B inside the database index.
        self.metadata_doc = metadata_doc

        # Multiple locations are now deprecated as per EP13.
        # 1.9: Store legacy location lists in a hidden _uris attribute.
        # 2.0: Remove _uris, only use uri
        #: Active URIs in order from newest to oldest
        if uri:
            # Single URI - preferred
            self._uris = [uri]
            self.uri: str | None = uri
        elif uris:
            # Multiple URIs - deprecated/legacy
            self._uris = uris
            self.uri = uris[0]
        else:
            # No URI.  May be useful to support non-raster datasets.
            self._uris = []
            self.uri = None

        #: The datasets that this dataset is derived from (if requested on load).
        self.sources = sources

        if self.sources is not None and self.metadata.sources is not None:
            assert set(self.metadata.sources.keys()) == set(self.sources.keys())

        self.source_tree = source_tree
        self.derived_tree = derived_tree

        #: The User who indexed this dataset
        self.indexed_by = indexed_by
        self.indexed_time = indexed_time
        # When the dataset was archived. Null if not archived.
        self.archived_time = archived_time

    @property
    @deprecat(
        reason="Multiple locations are now deprecated. Please use the 'uri' attribute instead.",
        version="1.9.0",
        category=ODC2DeprecationWarning,
    )
    def uris(self) -> Sequence[str]:
        """
        List of active locations, newest to oldest.

        Multiple locations are deprecated, please use 'uri'.
        """
        return self._uris

    def legacy_uri(self, schema: str | None = None):
        """
        This is a 1.9-2.0 transitional method and will be removed in 2.0.

        If the dataset has only one location, it returns that uri, but if the dataset has multiple locations,
        it calls various deprecated methods to achieve the legacy behaviour.  It is intended for
        internal core use only.

        :param schema:
        :return:
        """
        n_locs = len(self._uris)
        if n_locs <= 1:
            return self.uri
        return pick_uri(self._uris, schema)

    def has_multiple_uris(self) -> bool:
        """
        This is a 1.9-2.0 transitional method and will be removed in 2.0.

        Returns true if the dataset has multiple locations.

        Allows checking for multiple locations without tripping a deprecation warning.
        """
        return len(self._uris) > 1

    @property
    @deprecat(
        reason="The 'type' attribute has been deprecated. Please use the 'product' attribute instead.",
        version="1.9.0",
        category=ODC2DeprecationWarning,
    )
    def type(self) -> Product:
        # For compatibility
        return self.product

    @property
    def is_eo3(self) -> bool:
        from datacube.index.eo3 import is_doc_eo3

        return is_doc_eo3(self.metadata_doc)

    @property
    def metadata_type(self) -> MetadataType:
        return self.product.metadata_type

    @property
    def local_uri(self) -> str | None:
        """
        Return the uri if it is local, or None.

        Legacy behaviour: The latest local file uri, if any.
        """
        if not self._uris:
            return None

        local_uris = [uri for uri in self._uris if uri.startswith("file:")]
        if local_uris:
            return local_uris[0]

        return None

    @property
    def local_path(self) -> Path | None:
        """
        A path to this dataset on the local filesystem (if available).
        """
        return uri_to_local_path(self.local_uri)

    @property
    def id(self) -> UUID:
        """UUID of a dataset"""
        # This is a string in a raw document.
        return UUID(self.metadata.id)

    @property
    def managed(self) -> bool:
        return self.product.managed

    @property
    def format(self) -> str:
        return self.metadata.format

    @property
    def uri_scheme(self) -> str:
        if not self._uris:
            return ""

        url = urlparse(self.uri)
        if url.scheme == "":
            return "file"
        return str(url.scheme)

    @property
    def measurements(self) -> dict[str, Any]:
        # It's an optional field in documents.
        # Dictionary of key -> measurement descriptor
        metadata = self.metadata
        if not hasattr(metadata, "measurements"):
            return {}
        return metadata.measurements

    @cached_property
    def center_time(self) -> datetime | None:
        """mid-point of time range"""
        time = self.time
        if time is None:
            return None
        return time.begin + (time.end - time.begin) // 2

    @property
    def time(self) -> Range | None:
        try:
            time = self.metadata.time
            return Range(parse_time(time.begin), parse_time(time.end))
        except AttributeError:
            return None

    @cached_property
    def key_time(self) -> datetime | None:
        if "key_time" in self.metadata.fields:
            return self.metadata.key_time

        # Existing datasets are already using the computed "center_time" for their storage index key
        # if 'center_time' in self.metadata.fields:
        #     return self.metadata.center_time

        return self.center_time

    @property
    def bounds(self) -> BoundingBox | None:
        """:returns: bounding box of the dataset in the native crs"""
        gs = self._gs
        if gs is None:
            return None

        bounds = gs["geo_ref_points"]
        return BoundingBox(
            left=min(bounds["ur"]["x"], bounds["ll"]["x"]),
            right=max(bounds["ur"]["x"], bounds["ll"]["x"]),
            top=max(bounds["ur"]["y"], bounds["ll"]["y"]),
            bottom=min(bounds["ur"]["y"], bounds["ll"]["y"]),
            crs=self.crs,
        )

    @property
    def transform(self) -> Affine | None:
        geo = self._gs
        if geo is None:
            return None

        bounds = geo.get("geo_ref_points")
        if bounds is None:
            return None

        return Affine(
            bounds["lr"]["x"] - bounds["ul"]["x"],
            0,
            bounds["ul"]["x"],
            0,
            bounds["lr"]["y"] - bounds["ul"]["y"],
            bounds["ul"]["y"],
        )

    @property
    def is_archived(self) -> bool:
        """
        Is this dataset archived?

        (an archived dataset is one that is not intended to be used by users anymore: eg. it has been
        replaced by another dataset. It will not show up in search results, but still exists in the
        system via provenance chains or through id lookup.)
        """
        return self.archived_time is not None

    @property
    @deprecat(
        reason="The 'is_active' attribute has been deprecated. Please use 'is_archived' instead.",
        version="1.9.0",
        category=ODC2DeprecationWarning,
    )
    def is_active(self) -> bool:
        """
        Is this dataset active?

        (ie. dataset hasn't been archived)
        """
        return not self.is_archived

    @property
    def _gs(self) -> dict[str, Any] | None:
        try:
            return self.metadata.grid_spatial
        except AttributeError:
            return None

    @property
    def crs(self) -> CRS | None:
        """Return CRS if available"""
        projection = self._gs

        if not projection:
            return None

        crs = projection.get("spatial_reference", None)
        if crs:
            return CRS(str(crs))
        return None

    @cached_property
    def extent(self) -> Geometry | None:
        """:returns: valid extent of the dataset or None"""

        def xytuple(obj: dict) -> tuple[float, float]:
            return obj["x"], obj["y"]

        # If no projection or crs, they have no extent.
        projection = self._gs
        if not projection:
            return None
        crs = self.crs
        if not crs:
            _LOG.debug("No CRS, assuming no extent (dataset %s)", self.id)
            return None

        valid_data = projection.get("valid_data")
        geo_ref_points = projection.get("geo_ref_points")
        if valid_data:
            return Geometry(valid_data, crs=crs)
        if geo_ref_points:
            return polygon(
                [
                    xytuple(geo_ref_points[key])
                    for key in ("ll", "ul", "ur", "lr", "ll")
                ],
                crs=crs,
            )

        return None

    @property
    def accessories(self) -> dict[str, Any]:
        return self.metadata_doc.get("accessories", {})

    @property
    def grids(self) -> dict[str, Any]:
        return self.metadata_doc["grids"]

    @property
    def properties(self) -> dict[str, Any]:
        return self.metadata_doc["properties"]

    @override
    def __eq__(self, other) -> bool:
        if isinstance(other, Dataset):
            return self.id == other.id
        return False

    @override
    def __hash__(self) -> int:
        return hash(self.id)

    @override
    def __str__(self) -> str:
        str_loc = "not available" if not self.uri else self.uri
        return f"Dataset <id={self.id} product={self.product.name} location={str_loc}>"

    @override
    def __repr__(self) -> str:
        return self.__str__()

    @property
    def metadata(self) -> DocReader:
        return self.metadata_type.dataset_reader(self.metadata_doc)

    def metadata_doc_without_lineage(self) -> dict[str, Any]:
        """Return metadata document without nested lineage datasets"""
        return without_lineage_sources(self.metadata_doc, self.metadata_type)


class Measurement:
    """
    Describes a single data variable of a Product or Dataset.

    Must include, which can be used when loading and interpreting data:

     - name
     - dtype - eg: int8, int16, float32
     - nodata - What value represent No Data
     - units

    Attributes can be accessed using ``dict []`` syntax.

    Can also include attributes like alternative names 'aliases', and spectral and bit flags
    definitions to aid with interpreting the data.
    """

    REQUIRED_KEYS = ("name", "dtype", "nodata", "units")
    OPTIONAL_KEYS = (
        "aliases",
        "spectral_definition",
        "flags_definition",
        "scale_factor",
        "add_offset",
        "extra_dim",
        "dims",
    )
    ATTR_SKIP = [
        "name",
        "dtype",
        "aliases",
        "resampling_method",
        "fuser",
        "extra_dim",
        "dims",
        "extra_dim_index",
    ]

    def __init__(self, canonical_name: str | None = None, *args, **kwargs) -> None:
        self._data = {}

        missing_keys = set(self.REQUIRED_KEYS) - set(kwargs)
        if missing_keys:
            raise ValueError(f"Measurement required keys missing: {missing_keys}")

        canonical_name_tmp = canonical_name or kwargs.get("name")
        assert canonical_name_tmp is not None
        self.canonical_name: str = canonical_name_tmp

        # Handle positional arguments (e.g., Measurement([('a', 1), ('b', 2)]))
        if args:
            if len(args) == 1:
                raise TypeError("Measurement() takes at most 1 positional argument")
            arg = args[0]
            if isinstance(arg, dict):
                self._data = arg.copy()  # Copy the dict to avoid modifying the original
            elif hasattr(arg, "__iter__"):  # Handle iterables like lists of tuples
                for key, value in arg:
                    self[key] = value  # Use self.__setitem__ for assignment
            else:
                raise TypeError("Measurement() argument must be a dict or iterable")
        self.update(kwargs)

    def __getattr__(self, key: str) -> Any:
        """Allow access to items as attributes."""
        if key == "_data":
            # return self._data
            raise AttributeError("Measurement() object has no attribute '_data'")
        return self._data.get(key)

    def __getitem__(self, key):
        """
        Retrieves the value associated with the given key.
        """
        return self._data[key]

    def __setitem__(self, key, value) -> None:
        """
        Sets the value associated with the given key.
        """
        self._data[key] = value

    def __delitem__(self, key) -> None:
        if key in self.REQUIRED_KEYS:
            raise KeyError(f"Measurement() requires key {key}")
        del self._data[key]

    def __contains__(self, key) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator:
        return iter(self._data)

    @override
    def __str__(self) -> str:
        return repr(self)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def setdefault(self, key, default=None):
        return self._data.setdefault(key, default)

    def pop(self, key, default=None):
        """
        Removes the key and returns its value from the dictionary or a default value if the key is not found.
        """
        if key in self.REQUIRED_KEYS:
            raise KeyError(f"Measurement() requires key {key}")
        return self._data.pop(key, default)

    def update(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise TypeError("update() takes at most 1 positional argument")
            arg = args[0]
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self[key] = value
            elif hasattr(arg, "__iter__"):
                for key, value in arg:
                    self[key] = value
            else:
                raise TypeError("update() argument must be a dict or iterable")

        for key, value in kwargs.items():
            self[key] = value

    @override
    def __eq__(self, other) -> bool:
        return isinstance(other, Measurement) and self._data == other._data

    @override
    def __hash__(self) -> int:
        return hash(self._data)

    @override
    def __repr__(self) -> str:
        return f"Measurement({self._data!r})"

    def copy(self) -> Measurement:
        """Required as the super class `dict` method returns a `dict`
        and does not preserve Measurement class"""
        return Measurement(**self._data)

    def dataarray_attrs(self) -> dict[str, Any]:
        """This returns attributes filtered for display in a dataarray."""
        return {key: value for key, value in self.items() if key not in self.ATTR_SKIP}

    def __getstate__(self):
        state = {**self._data}
        state["canonical_name"] = self.canonical_name
        return state

    def __setstate__(self, state):
        self.__init__(**state)


@schema_validated(SCHEMA_PATH / "metadata-type-schema.yaml")
class MetadataType:
    """Metadata Type definition"""

    def __init__(
        self,
        definition: Mapping[str, Any],
        search_field_extractor: Callable[[Mapping[str, Any]], Mapping[str, Field]]
        | None = None,
        id_: int | None = None,
    ) -> None:
        # Build fields using a named extractor function for pickleability
        if search_field_extractor is None:
            search_field_extractor = get_dataset_fields
        self.definition = definition
        self.search_field_extractor = search_field_extractor
        self.dataset_fields = self.search_field_extractor(self.definition)
        self.id = id_

    @property
    def name(self) -> str:
        return self.definition.get("name", None)

    @property
    def description(self) -> str:
        return self.definition.get("description", None)

    def dataset_reader(self, dataset_doc: Mapping[str, Field]) -> DocReader:
        return DocReader(self.definition["dataset"], self.dataset_fields, dataset_doc)

    @classmethod
    def validate_eo3(cls, doc) -> None:
        cls.validate(doc)  # type: ignore[attr-defined]
        validate_eo3_compatible_type(doc)

    # Fields defined using SQLAlchemy ORM are not pickleable,
    # so use a named (and therefore pickleable) extraction function
    def __getstate__(self) -> Mapping[str, Any]:
        return {
            "definition": self.definition,
            "id": self.id,
            "search_field_extractor": self.search_field_extractor,
        }

    def __setstate__(self, state: Mapping[str, Any]) -> None:
        self.definition = state["definition"]
        self.id = state["id"]
        self.search_field_extractor = state["search_field_extractor"]
        self.dataset_fields = self.search_field_extractor(self.definition)

    @override
    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True

        if self.__class__ != other.__class__:
            return False

        return self.name == other.name

    @override
    def __str__(self) -> str:
        return f"MetadataType(name={self.name!r}, id_={self.id!r})"

    @override
    def __repr__(self) -> str:
        return str(self)


@schema_validated(SCHEMA_PATH / "dataset-type-schema.yaml")
class Product:
    """
    Product definition

    :param metadata_type:
    :param definition:
    """

    def __init__(
        self,
        metadata_type: MetadataType,
        definition: Mapping[str, Any],
        id_: int | None = None,
        stac: RasterCollectionMetadata | None = None,
    ) -> None:
        self.id = id_
        self.metadata_type = metadata_type
        #: product definition document
        self.definition = definition
        self._extra_dimensions: Mapping[str, Any] | None = None
        self._canonical_measurements: Mapping[str, Measurement] | None = None
        self._all_measurements: dict[str, Measurement] | None = None
        self._load_hints: dict[str, Any] | None = None

        # Used for mapping between STAC Collections and Products.
        self._stac = stac

    def _resolve_aliases(self) -> dict[str, Measurement]:
        if self._all_measurements is not None:
            return self._all_measurements
        mm = self.measurements
        oo = {}

        for m in mm.values():
            oo[m.name] = m
            for alias in m.get("aliases", []):
                # TODO: check for duplicates
                # if alias is in oo already -- bad
                m_alias = dict(**m)
                m_alias.update(name=alias, canonical_name=m.name)
                oo[alias] = Measurement(**m_alias)

        self._all_measurements = oo
        return self._all_measurements

    @property
    def stac(self) -> RasterCollectionMetadata | None:
        return self._stac

    @property
    def name(self) -> str:
        return self.definition["name"]

    @property
    def description(self) -> str:
        return self.definition.get("description", None)

    @property
    def license(self) -> str:
        return self.definition.get("license", None)

    @property
    def managed(self) -> bool:
        return self.definition.get("managed", False)

    @property
    def metadata_doc(self) -> Mapping[str, Any]:
        return self.definition["metadata"]

    @property
    def metadata(self) -> DocReader:
        return self.metadata_type.dataset_reader(self.metadata_doc)

    @property
    def fields(self) -> dict[str, Any]:
        return self.metadata_type.dataset_reader(self.metadata_doc).fields

    @property
    def measurements(self) -> Mapping[str, Measurement]:
        """
        Dictionary of measurements in this product
        """
        # from copy import deepcopy
        if self._canonical_measurements is None:

            def fix_nodata(m: dict[str, Any]) -> dict[str, Any]:
                nodata = m.get("nodata")
                if isinstance(nodata, str):
                    m = dict(**m)
                    m["nodata"] = float(nodata)
                return m

            self._canonical_measurements = OrderedDict(
                (m["name"], Measurement(**fix_nodata(m)))
                for m in self.definition.get("measurements", {})
            )

        return self._canonical_measurements

    @property
    def dimensions(self) -> tuple[str, str, str]:
        """
        List of dimension labels for data in this product
        """
        spatial_dims = (
            DEFAULT_SPATIAL_DIMS
            if self.grid_spec is None
            else self.grid_spec.dimensions
        )

        return ("time", *spatial_dims)

    @property
    def extra_dimensions(self) -> ExtraDimensions:
        """
        Dictionary of metadata for the third dimension.
        """
        if self._extra_dimensions is None:
            self._extra_dimensions = OrderedDict(
                (d["name"], d) for d in self.definition.get("extra_dimensions", [])
            )
        return ExtraDimensions(self._extra_dimensions)

    @cached_property
    def grid_spec(self) -> GridSpec | GeoGridSpec | None:
        """
        Grid specification for this product
        """
        storage = self.definition.get("storage")
        if storage is None:
            return None

        crs = storage.get("crs")
        if crs is None:
            return None

        crs = CRS(str(crs).strip())

        def extract_point(name: str):
            xx = storage.get(name, None)
            # Else-branch has type "int | None".
            return (
                tuple(xx[dim] for dim in crs.dimensions) if isinstance(xx, dict) else xx
            )

        # extract both tile_size and tile_shape for backwards compatibility
        gs_params = {
            name: extract_point(name)
            for name in ("tile_size", "tile_shape", "resolution", "origin")
        }

        complete = gs_params["resolution"] is not None and (
            gs_params["tile_size"] or gs_params["tile_shape"]
        )
        if not complete:
            return None

        if gs_params["tile_shape"] is not None:
            # convert origin to XY
            if isinstance(gs_params["origin"], tuple):
                gs_params["origin"] = yx_(gs_params["origin"])

            if isinstance(gs_params["resolution"], tuple):
                gs_params["resolution"] = resyx_(*gs_params["resolution"])
            else:
                gs_params["resolution"] = res_(gs_params["resolution"])

            del gs_params["tile_size"]
            return GeoGridSpec(crs=crs, **gs_params)

        del gs_params["tile_shape"]
        return GridSpec(crs=crs, **gs_params)

    @staticmethod
    def validate_extra_dims(definition: Mapping[str, Any]) -> None:
        """Validate 3D metadata in the product definition.

        Perform some basic checks for validity of the 3D dataset product definition:
          - Checks extra_dimensions section exists
          - For each 3D measurement, check if the required dimension is defined
          - If the 3D spectral_definition is defined:
            - Check there's one entry per coordinate.
            - Check that wavelength and response are the same length.

        :param definition: Dimension definition dict, typically retrieved from the product definition's
            `extra_dimensions` field.
        """
        # Dict of extra dimensions names and values in the product definition
        defined_extra_dimensions = OrderedDict(
            (d.get("name"), d.get("values"))
            for d in definition.get("extra_dimensions", [])
        )

        for m in definition.get("measurements", []):
            # Skip if not a 3D measurement
            if "extra_dim" not in m:
                continue

            # Found 3D measurement, check if extra_dimension is defined.
            if len(defined_extra_dimensions) == 0:
                raise ValueError(
                    "extra_dimensions is not defined. 3D measurements require extra_dimensions "
                    "to be defined for the dimension"
                )

            dim_name = m.get("extra_dim")

            # Check extra dimension is defined
            if dim_name not in defined_extra_dimensions:
                raise ValueError(
                    f"Dimension {dim_name} is not defined in extra_dimensions"
                )

            if "spectral_definition" in m:
                spectral_definitions = m.get("spectral_definition", [])
                # Check spectral_definition of expected length
                if len(defined_extra_dimensions[dim_name]) != len(spectral_definitions):
                    raise ValueError(
                        f"spectral_definition should be the same length as values for extra_dim {m.get('extra_dim')}"
                    )

                # Check each spectral_definition has the same length for wavelength and response if both exists
                for idx, spectral_definition in enumerate(spectral_definitions):
                    if (
                        "wavelength" in spectral_definition
                        and "response" in spectral_definition
                    ) and len(spectral_definition.get("wavelength")) != len(
                        spectral_definition.get("response")
                    ):
                        raise ValueError(
                            "spectral_definition_map: wavelength should be the same length as response "
                            f"in the product definition for spectral definition at index {idx}."
                        )

    def canonical_measurement(self, measurement: str) -> str:
        """resolve measurement alias into canonical name"""
        m = self._resolve_aliases().get(measurement, None)
        if m is None:
            raise ValueError(f"No such band/alias {measurement}")

        return m.canonical_name

    def lookup_measurements(
        self, measurements: Iterable[str] | str | None = None
    ) -> Mapping[str, Measurement]:
        """
        Find measurements by name

        :param measurements: list of measurement names or a single measurement name, or None to get all
        """
        if measurements is None:
            return self.measurements
        if isinstance(measurements, str):
            measurements = [measurements]

        mm = self._resolve_aliases()
        return OrderedDict((m, mm[m]) for m in measurements)

    def _extract_load_hints(self) -> dict[str, Any] | None:
        _load = self.definition.get("load")
        if _load is None:
            # Check for partial "storage" definition
            storage = self.definition.get("storage", {})

            if "crs" in storage and "resolution" in storage:
                if "tile_size" in storage or "tile_shape" in storage:
                    # Fully defined GridSpec, ignore it
                    return None

                # TODO: warn user to use `load:` instead of `storage:`??
                _load = storage
            else:
                return None

        crs = CRS(_load["crs"])

        def extract_point(name: str):
            xx = _load.get(name, None)
            # Else-branch has type "int | None".
            return (
                tuple(xx[dim] for dim in crs.dimensions) if isinstance(xx, dict) else xx
            )

        params = {name: extract_point(name) for name in ("resolution", "align")}
        params = {name: v for name, v in params.items() if v is not None}

        if "resolution" in params:
            params["resolution"] = resyx_(*params["resolution"])

        return dict(crs=crs, **params)

    @property
    def default_crs(self) -> CRS | None:
        return self.load_hints().get("output_crs", None)

    @property
    def default_resolution(self) -> Resolution | None:
        return self.load_hints().get("resolution", None)

    @property
    def default_align(self) -> tuple[float, float] | None:
        return self.load_hints().get("align", None)

    def load_hints(self) -> dict[str, Any]:
        """
        Returns dictionary with keys compatible with ``dc.load(..)`` named arguments:

          output_crs - CRS
          resolution - Tuple[float, float]
          align      - Tuple[float, float] (if defined)

        Returns {} if load hints are not defined on this product, or defined with errors.
        """
        if self._load_hints is not None:
            return self._load_hints

        hints = None
        with contextlib.suppress(Exception):
            hints = self._extract_load_hints()

        if hints is None:
            self._load_hints = {}
        else:
            crs = hints.pop("crs")
            self._load_hints = dict(output_crs=crs, **hints)

        return self._load_hints

    def dataset_reader(self, dataset_doc: Mapping[str, Field]) -> DocReader:
        return self.metadata_type.dataset_reader(dataset_doc)

    def to_dict(self) -> Mapping[str, Any]:
        """
        Convert to a dictionary representation of the available fields
        """
        row = dict(**self.fields)
        row.update(
            id=self.id,
            name=self.name,
            license=self.license,
            description=self.description,
        )

        if self.grid_spec is not None:
            if isinstance(self.grid_spec, GeoGridSpec):
                tile_shape: SomeShape = self.grid_spec.tile_shape
            else:
                tile_shape = self.grid_spec.tile_resolution
            row.update(
                {
                    "crs": str(self.grid_spec.crs),
                    "spatial_dimensions": self.grid_spec.dimensions,
                    "tile_shape": tile_shape,
                    "resolution": self.grid_spec.resolution,
                }
            )
        return row

    @override
    def __str__(self) -> str:
        return f"Product(name={self.name!r}, id_={self.id!r})"

    @override
    def __repr__(self) -> str:
        return self.__str__()

    # Types are uniquely identifiable by name:

    @override
    def __eq__(self, other) -> bool:
        if self is other:
            return True

        if self.__class__ != other.__class__:
            return False

        return self.name == other.name

    @override
    def __hash__(self) -> int:
        return hash(self.name)


# Type alias for backwards compatibility
DatasetType = Product


@deprecat(
    reason="This version of GridSpec has been deprecated. Please use the GridSpec class defined in odc-geo.\n"
    "Note that in odc-geo GridSpec, tile_size has been renamed tile_shape and should be provided in pixels, "
    "resolution is expected in (X, Y) order or simply X if using square pixels with inverted Y axis, "
    "and origin (if provided) must be an instance of odc.geo.XY",
    version="1.9.0",
    category=ODC2DeprecationWarning,
)
class GridSpec:
    """
    Definition for a regular spatial grid

        >>> gs = GridSpec(
        ...     crs=CRS("EPSG:4326"),
        ...     tile_size=(1, 1),
        ...     resolution=(-0.1, 0.1),
        ...     origin=(-50.05, 139.95),
        ... )
        >>> gs.tile_resolution
        (10, 10)
        >>> list(gs.tiles(BoundingBox(140, -50, 141.5, -48.5)))
        [((0, 0), GeoBox((10, 10), Affine(0.1, 0.0, 139.95,
               0.0, -0.1, -49.05), CRS('EPSG:4326'))), ((1, 0), GeoBox((10, 10), Affine(0.1, 0.0, 140.95,
               0.0, -0.1, -49.05), CRS('EPSG:4326'))), ((0, 1), GeoBox((10, 10), Affine(0.1, 0.0, 139.95,
               0.0, -0.1, -48.05), CRS('EPSG:4326'))), ((1, 1), GeoBox((10, 10), Affine(0.1, 0.0, 140.95,
               0.0, -0.1, -48.05), CRS('EPSG:4326')))]

    :param crs: Coordinate System used to define the grid
    :param tile_size: (Y, X) size of each tile, in CRS units
    :param resolution: (Y, X) size of each data point in the grid, in CRS units. Y will
        usually be negative.
    :param origin: (Y, X) coordinates of a corner of the (0,0) tile in CRS units. default is (0.0, 0.0)
    """

    def __init__(
        self,
        crs: CRS,
        tile_size: tuple[float, float],
        resolution: tuple[float, float],
        origin: tuple[float, float] | None = None,
    ) -> None:
        self.crs = crs
        self.tile_size = tile_size
        self.resolution = resolution
        self.origin = origin or (0.0, 0.0)

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GridSpec):
            return False

        return (
            self.crs == other.crs
            and self.tile_size == other.tile_size
            and self.resolution == other.resolution
            and self.origin == other.origin
        )

    @property
    def dimensions(self) -> tuple[str, str]:
        """
        List of dimension names of the grid spec
        """
        return self.crs.dimensions

    @property
    def alignment(self) -> tuple[float, float]:
        """
        Pixel boundary alignment
        """
        y, x = (orig % abs(res) for orig, res in zip(self.origin, self.resolution))
        return y, x

    @property
    def tile_resolution(self) -> tuple[int, int]:
        """
        Tile size in pixels in CRS dimension order (Usually y,x or lat,lon)
        """
        y, x = (int(abs(ts / res)) for ts, res in zip(self.tile_size, self.resolution))
        return y, x

    def tile_coords(self, tile_index: tuple[int, int]) -> tuple[float, float]:
        """
        Coordinate of the top-left corner of the tile in (Y,X) order

        :param tile_index: in X,Y order
        """

        def coord(index: int, resolution: float, size: float, origin: float) -> float:
            return (index + (1 if resolution < 0 < size else 0)) * size + origin

        y, x = (
            coord(index, res, size, origin)
            for index, res, size, origin in zip(
                tile_index[::-1], self.resolution, self.tile_size, self.origin
            )
        )
        return y, x

    def tile_geobox(self, tile_index: tuple[int, int]) -> GeoBox:
        """
        Tile geobox.

        :param tile_index:
        """
        res_y, res_x = self.resolution
        y, x = self.tile_coords(tile_index)
        h, w = self.tile_resolution
        return GeoBox(
            crs=self.crs, affine=Affine(res_x, 0.0, x, 0.0, res_y, y), shape=wh_(w, h)
        )

    def tiles(
        self, bounds: BoundingBox, geobox_cache: dict | None = None
    ) -> Generator[tuple[tuple[int, int], GeoBox]]:
        """
        Returns an iterator of tile_index, :py:class:`GeoBox` tuples across
        the grid and overlapping with the specified `bounds` rectangle.

        .. note::

           Grid cells are referenced by coordinates `(x, y)`, which is the opposite to the usual CRS
           dimension order.

        :param bounds: Boundary coordinates of the required grid
        :param geobox_cache: Optional cache to reuse geoboxes instead of creating new one each time
        :return: iterator of grid cells with :py:class:`GeoBox` tiles
        """

        def geobox(tile_index: tuple[int, int]) -> GeoBox:
            if geobox_cache is None:
                return self.tile_geobox(tile_index)

            gbox = geobox_cache.get(tile_index)
            if gbox is None:
                gbox = self.tile_geobox(tile_index)
                geobox_cache[tile_index] = gbox
            return gbox

        tile_size_y, tile_size_x = self.tile_size
        tile_origin_y, tile_origin_x = self.origin
        for y in GridSpec.grid_range(
            bounds.bottom - tile_origin_y, bounds.top - tile_origin_y, tile_size_y
        ):
            for x in GridSpec.grid_range(
                bounds.left - tile_origin_x, bounds.right - tile_origin_x, tile_size_x
            ):
                tile_index = (x, y)
                yield tile_index, geobox(tile_index)

    def tiles_from_geopolygon(
        self,
        geopolygon: Geometry,
        tile_buffer: tuple[float, float] | None = None,
        geobox_cache: dict | None = None,
    ) -> Generator[tuple[tuple[int, int], GeoBox]]:
        """
        Returns an iterator of tile_index, :py:class:`GeoBox` tuples across
        the grid and overlapping with the specified `geopolygon`.

        .. note::

           Grid cells are referenced by coordinates `(x, y)`, which is the opposite to the usual CRS
           dimension order.

        :param geopolygon: Polygon to tile
        :param tile_buffer: Optional <float,float> tuple, (extra padding for the query
                            in native units of this GridSpec)
        :param geobox_cache: Optional cache to reuse geoboxes instead of creating new one each time
        :return: iterator of grid cells with :py:class:`GeoBox` tiles
        """
        geopolygon = geopolygon.to_crs(self.crs)
        bbox = geopolygon.boundingbox
        bbox = bbox.buffered(*tile_buffer) if tile_buffer else bbox

        for tile_index, tile_geobox in self.tiles(bbox, geobox_cache):
            tile_geobox = (
                tile_geobox.buffered(*tile_buffer) if tile_buffer else tile_geobox
            )

            if intersects(tile_geobox.extent, geopolygon):
                yield tile_index, tile_geobox

    @staticmethod
    def grid_range(lower: float, upper: float, step: float) -> range:
        """
        Returns the indices along a 1D scale.

        Used for producing 2D grid indices.

        >>> list(GridSpec.grid_range(-4.0, -1.0, 3.0))
        [-2, -1]
        >>> list(GridSpec.grid_range(1.0, 4.0, -3.0))
        [-2, -1]
        >>> list(GridSpec.grid_range(-3.0, 0.0, 3.0))
        [-1]
        >>> list(GridSpec.grid_range(-2.0, 1.0, 3.0))
        [-1, 0]
        >>> list(GridSpec.grid_range(-1.0, 2.0, 3.0))
        [-1, 0]
        >>> list(GridSpec.grid_range(0.0, 3.0, 3.0))
        [0]
        >>> list(GridSpec.grid_range(1.0, 4.0, 3.0))
        [0, 1]
        """
        if step < 0.0:
            lower, upper, step = -upper, -lower, -step
        assert step > 0.0
        return range(math.floor(lower / step), math.ceil(upper / step))

    @override
    def __str__(self) -> str:
        return f"GridSpec(crs={self.crs}, tile_size={self.tile_size}, resolution={self.resolution})"

    @override
    def __repr__(self) -> str:
        return self.__str__()


def metadata_from_doc(doc: Mapping[str, Any]) -> MetadataType:
    """Construct MetadataType that is not tied to any particular db index. This is
    useful when there is a need to interpret dataset metadata documents
    according to metadata spec.
    """
    MetadataType.validate(doc)  # type: ignore[attr-defined]
    return MetadataType(doc)


ExtraDimensionSlices: TypeAlias = dict[str, float | tuple[float, float]]


class ExtraDimensions:
    """
    Definition for the additional dimensions between (t) and (y, x)

    It allows the creation of a subsetted ExtraDimensions that contains slicing information relative to
    the original dimension coordinates.
    """

    def __init__(self, extra_dim: Mapping[str, Any]) -> None:
        """Init function

        :param extra_dim: Dimension definition dict, typically retrieved from the product definition's
            `extra_dimensions` field.
        """
        import xarray

        # Dict of information about each dimension
        self._dims = extra_dim
        # Dimension slices that results in this ExtraDimensions object
        self._dim_slice = {
            name: (0, len(dim["values"])) for name, dim in extra_dim.items()
        }
        # Coordinate information
        self._coords = {
            name: xarray.DataArray(
                data=dim["values"],
                coords={name: dim["values"]},
                dims=(name,),
                name=name,
            ).astype(dim["dtype"])
            for name, dim in extra_dim.items()
        }

    def has_empty_dim(self) -> bool:
        """Return True if ExtraDimensions has an empty dimension, otherwise False.

        :return: A boolean if ExtraDimensions has an empty dimension, otherwise False.
        """
        return any(value.shape[0] == 0 for value in self._coords.values())

    def __getitem__(self, dim_slices: ExtraDimensionSlices) -> ExtraDimensions:
        """Return a ExtraDimensions subsetted by dim_slices

        :param dim_slices: Dict of dimension slices to subset by.
        :return: An ExtraDimensions object subsetted by `dim_slices`
        """
        # Check all dimensions specified in dim_slices exists
        unknown_keys = set(dim_slices.keys()) - set(self._dims.keys())
        if unknown_keys:
            raise KeyError(f"Found unknown keys {unknown_keys} in dim_slices")

        from copy import deepcopy

        ed = ExtraDimensions(deepcopy(self._dims))
        ed._dim_slice = self._dim_slice

        # Convert to integer index
        for dim_name, dim_slice in dim_slices.items():
            dim_slices[dim_name] = self.coord_slice(dim_name, dim_slice)

        for dim_name, dim_slice in dim_slices.items():
            # Adjust slices relative to original.
            if dim_name in ed._dim_slice:
                ed._dim_slice[dim_name] = (  # type: ignore[assignment]
                    ed._dim_slice[dim_name][0] + dim_slice[0],  # type: ignore[index]
                    ed._dim_slice[dim_name][0] + dim_slice[1],  # type: ignore[index]
                )

            # Subset dimension values.
            if dim_name in ed._dims:
                ed._dims[dim_name]["values"] = ed._dims[dim_name]["values"][
                    slice(*dim_slice)  # type: ignore[misc]
                ]

            # Subset dimension coordinates.
            if dim_name in ed._coords:
                slice_dict = {k: slice(*v) for k, v in dim_slices.items()}  # type: ignore[misc]
                ed._coords[dim_name] = ed._coords[dim_name].isel(slice_dict)

        return ed

    @property
    def dims(self) -> Mapping[str, dict]:
        """Returns stored dimension information

        :return: A dict of information about each dimension
        """
        return self._dims

    @property
    def dim_slice(self) -> Mapping[str, tuple[int, int]]:
        """Returns dimension slice for this ExtraDimensions object

        :return: A dict of dimension slices that results in this ExtraDimensions object
        """
        return self._dim_slice

    def measurements_values(self, dim: str) -> list[Any]:
        """Returns the dimension values after slicing

        :param dim: The name of the dimension
        :return: A list of dimension values for the requested dimension.
        """
        if dim not in self._dims:
            raise ValueError(f"Dimension {dim} not found.")
        return self._dims[dim]["values"]

    def measurements_slice(self, dim: str) -> slice:
        """Returns the index for slicing on a dimension

        :param dim: The name of the dimension
        :return: A slice for the requested dimension.
        """
        dim_slice = self.measurements_index(dim)
        return slice(*dim_slice)

    def measurements_index(self, dim: str) -> tuple[int, int]:
        """Returns the index for slicing on a dimension as a tuple.

        :param dim: The name of the dimension
        :return: A tuple for the requested dimension.
        """
        if dim not in self._dim_slice:
            raise ValueError(f"Dimension {dim} not found.")

        return self._dim_slice[dim]

    def index_of(self, dim: str, value: Any) -> int:
        """Find index for value in the dimension dim

        :param dim: The name of the dimension
        :param value: The coordinate value.
        :return: The integer index of `value`
        """
        if dim not in self._coords:
            raise ValueError(f"Dimension {dim} not found.")
        return self._coords[dim].searchsorted(value)

    def coord_slice(
        self, dim: str, coord_range: float | tuple[float, float]
    ) -> tuple[int, int]:
        """Returns the Integer index for a coordinate (min, max) range.

        :param dim: The name of the dimension
        :param coord_range: The coordinate range.
        :return: A tuple containing the integer indexes of `coord_range`.
        """
        # Convert to Tuple if it's an int or float
        if isinstance(coord_range, int | float):
            coord_range = (coord_range, coord_range)

        start_index = self.index_of(dim, coord_range[0])
        stop_index = self.index_of(dim, coord_range[1] + 1)
        return start_index, stop_index

    def chunk_size(self) -> tuple[tuple[str, ...], tuple[int, ...]]:
        """Returns the names and shapes of dimensions in dimension order

        :return: A tuple containing the names and max sizes of each dimension
        """
        names = ()
        shapes = ()
        if self.dims is not None:
            for dim in self.dims.values():
                name = dim.get("name")
                names += (name,)  # type: ignore[assignment]
                shapes += (len(self.measurements_values(name)),)  # type: ignore[assignment,arg-type]
        return names, shapes

    @override
    def __str__(self) -> str:
        return (
            f"ExtraDimensions(extra_dim={dict(self._dims)}, dim_slice={self._dim_slice} "
            f"coords={self._coords})"
        )

    @override
    def __repr__(self) -> str:
        return self.__str__()
