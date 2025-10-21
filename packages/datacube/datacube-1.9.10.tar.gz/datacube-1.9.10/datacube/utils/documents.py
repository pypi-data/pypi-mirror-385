# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Functions for working with YAML documents and configurations
"""

from __future__ import annotations

import collections.abc
import gzip
import json
import logging
import math
from collections import OrderedDict
from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from copy import deepcopy
from io import TextIOWrapper
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import UUID

import numpy
import toolz
import yaml
from typing_extensions import override

from datacube.utils.changes import Offset

# Compatibility-imports to preserve the API.
from datacube.utils.json_types import JsonAtom, JsonDict, JsonLike  # noqa: F401

if TYPE_CHECKING:
    from datacube.model import Field

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader  # type: ignore[assignment]

from datacube.utils.generic import map_with_lookahead
from datacube.utils.uris import as_url, mk_part_uri, uri_to_local_path

_LOG: logging.Logger = logging.getLogger(__name__)


@contextmanager
def _open_from_s3(url: str):
    o = urlparse(url)
    if o.scheme != "s3":
        raise RuntimeError("Abort abort I don't know how to open non s3 urls")

    from .aws import s3_open

    yield s3_open(url)


def _open_with_urllib(url: str | Request):
    return urlopen(url)


_PROTOCOL_OPENERS = {
    "s3": _open_from_s3,
    "ftp": _open_with_urllib,
    "http": _open_with_urllib,
    "https": _open_with_urllib,
    "file": _open_with_urllib,
}


def load_from_yaml(handle: TextIOWrapper, parse_dates: bool = False) -> Generator[dict]:
    loader = SafeLoader if parse_dates else NoDatesSafeLoader
    yield from yaml.load_all(handle, Loader=loader)


def parse_yaml(doc: str | bytes) -> Mapping[str, Any]:
    """Convert a single document yaml string into a parsed document"""
    return yaml.load(doc, Loader=SafeLoader)


def load_from_json(handle) -> Generator[dict]:
    yield json.load(handle)


def load_from_netcdf(path: Path) -> Generator[dict]:
    for doc in read_strings_from_netcdf(path, variable="dataset"):
        yield yaml.load(doc, Loader=NoDatesSafeLoader)


_PARSERS: dict[
    str, Callable[[str], Generator[dict]] | Callable[[TextIOWrapper], Generator[dict]]
] = {
    ".yaml": load_from_yaml,
    ".yml": load_from_yaml,
    ".json": load_from_json,
}


def load_documents(path: str) -> Generator[dict]:
    """
    Load document/s from the specified path.

    At the moment can handle:

     - JSON and YAML locally and remotely.
     - Compressed JSON and YAML locally
     - Data Cube Dataset Documents inside local NetCDF files.

    :param path: path or URI to load documents from
    :return: generator of dicts
    """
    path = str(path)
    url = as_url(path)
    scheme = urlparse(url).scheme
    compressed = url[-3:] == ".gz"

    if scheme == "file" and path[-3:] == ".nc":
        local_path = uri_to_local_path(url)
        assert local_path is not None
        yield from load_from_netcdf(local_path)
    else:
        with _PROTOCOL_OPENERS[scheme](url) as fh:
            if compressed:
                fh = gzip.open(fh)
                path = path[:-3]

            suffix = Path(path).suffix

            parser = _PARSERS[suffix]

            yield from parser(fh)


def read_documents(*paths, uri: bool = False) -> Generator[tuple[str, dict]]:
    """
    Read and parse documents from the filesystem or remote URLs (yaml or json).

    Note that a single yaml file can contain multiple documents.

    This function will load any dates in the documents as strings. In
    Data Cube we store JSONB in PostgreSQL and it will turn our dates
    into strings anyway.

    :param uri: When True yield URIs instead of Paths
    :param paths: input Paths or URIs
    """

    def process_file(path: str) -> Generator[tuple[str, dict]]:
        docs = load_documents(path)

        if not uri:
            for doc in docs:
                yield path, doc
        else:
            url = as_url(path)

            def add_uri_no_part(x: tuple) -> tuple:
                _, doc = x
                return url, doc

            def add_uri_with_part(x: tuple) -> tuple:
                idx, doc = x
                return mk_part_uri(url, idx), doc

            yield from map_with_lookahead(
                enumerate(docs), if_one=add_uri_no_part, if_many=add_uri_with_part
            )

    for p in paths:
        try:
            yield from process_file(p)
        except InvalidDocException as e:
            raise e
        except (yaml.YAMLError, ValueError) as e:
            raise InvalidDocException(f"Failed to load {p}: {e}") from None
        except Exception as e:
            raise InvalidDocException(f"Failed to load {p}: {e}") from None


def parse_doc_stream(
    doc_stream: Sequence[tuple[str, str | bytes]],
    on_error: Callable[[str, str | bytes, Exception], None] | None = None,
    transform: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
) -> Generator[tuple[str, Mapping[str, Any] | None]]:
    """
    Parse a stream of (filename, document body) tuples

    The document bodies are interpreted as either YAML or JSON depending on the filename suffix
    and turned into dictionary structures.

    If any error occurs while parsing, the ``on_error`` callback is run, and None is returned
    instead of a dictionary.

    :param doc_stream: sequence of tuples consisting of uri and document body
    :param on_error: error callback that gets the uri, doc, and exception as parameters
    :param transform: if given, transforms the parsed document

    """
    for uri, doc in doc_stream:
        try:
            metadata = json.loads(doc) if uri.endswith(".json") else parse_yaml(doc)
            if transform is not None:
                metadata = transform(metadata)
        except Exception as e:  # pylint: disable=broad-except
            if on_error is not None:
                on_error(uri, doc, e)
            metadata = None
        yield uri, metadata


def netcdf_extract_string(chars) -> str:
    """
    Convert netcdf S|U chars to Unicode string.
    """
    import netCDF4

    if isinstance(chars, str):
        return chars

    chars = netCDF4.chartostring(chars)
    if chars.dtype.kind == "U":
        return str(chars)
    return str(numpy.char.decode(chars))


def read_strings_from_netcdf(path: str | PathLike[str], variable) -> Generator[str]:
    """
    Load all the string encoded data from a variable in a NetCDF file.

    By 'string', the CF conventions mean ascii.

    Useful for loading dataset metadata information.
    """
    import netCDF4

    with netCDF4.Dataset(str(path)) as ds:
        for chars in ds[variable]:
            yield netcdf_extract_string(chars)


def validate_document(
    document,
    schema: Mapping[str, Any],
    schema_folder: str | PathLike[str] | None = None,
) -> None:
    import jsonschema
    import referencing
    from referencing import Resource
    from referencing.exceptions import NoSuchResource
    from referencing.jsonschema import DRAFT4
    from referencing.typing import URI

    # Allow schemas to reference other schemas in the given folder.
    def doc_reference(uri: URI) -> Resource:
        assert schema_folder is not None
        path = Path(schema_folder).joinpath(uri)
        if not path.exists():
            raise NoSuchResource(f"Reference not found: {uri}")
        referenced_schema = next(iter(read_documents(path)))[1]
        return DRAFT4.create_resource(referenced_schema)

    try:
        registry = (
            referencing.Registry()
            if schema_folder is None
            else referencing.Registry(retrieve=doc_reference)  # type: ignore[call-arg]
        )
        jsonschema.Draft4Validator.check_schema(schema)
        validator = jsonschema.Draft4Validator(schema, registry=registry)
        validator.validate(document)
    except jsonschema.ValidationError as e:
        raise InvalidDocException(e) from None


_DOCUMENT_EXTENSIONS = (".yaml", ".yml", ".json", ".nc")
_COMPRESSION_EXTENSIONS = ("", ".gz")
_ALL_SUPPORTED_EXTENSIONS: tuple[str, ...] = tuple(
    doc_type + compression_type
    for doc_type in _DOCUMENT_EXTENSIONS
    for compression_type in _COMPRESSION_EXTENSIONS
)


def is_supported_document_type(path: Path | str) -> bool:
    """
    Does a document path look like a supported type?
    """
    return any(
        str(path).lower().endswith(suffix) for suffix in _ALL_SUPPORTED_EXTENSIONS
    )


class NoDatesSafeLoader(SafeLoader):  # pylint: disable=too-many-ancestors
    @classmethod
    def remove_implicit_resolver(cls, tag_to_remove) -> None:
        """
        Removes implicit resolvers for a particular tag

        Takes care not to modify resolvers in super classes.

        We want to load datetimes as strings, not dates. We go on to
        serialise as json which doesn't have the advanced types of
        yaml, and leads to slightly different objects down the track.
        """
        if "yaml_implicit_resolvers" not in cls.__dict__:
            cls.yaml_implicit_resolvers = cls.yaml_implicit_resolvers.copy()

        for first_letter, mappings in cls.yaml_implicit_resolvers.items():
            cls.yaml_implicit_resolvers[first_letter] = [
                (tag, regexp) for tag, regexp in mappings if tag != tag_to_remove
            ]


NoDatesSafeLoader.remove_implicit_resolver("tag:yaml.org,2002:timestamp")


class InvalidDocException(Exception):  # noqa: N818
    pass


class UnknownMetadataType(InvalidDocException):
    """
    Specific exception to raise on a product with an unknown metadata type
    """

    pass


def get_doc_offset(offset: Sequence[str | int], document: dict, default=None):
    return toolz.get_in(offset, document, default=default)


def documents_equal(d1: str | float | list | dict, d2) -> bool:
    if d1.__class__ != d2.__class__:
        return False
    if isinstance(d1, str):
        return d1 == d2
    if isinstance(d1, dict):
        if set(d1.keys()) != set(d2.keys()):
            return False
        return all(documents_equal(d1[k], d2[k]) for k in d1)
    if isinstance(d1, list):
        if len(d1) != len(d2):
            return False
        return all(documents_equal(d1[i], d2[i]) for i in range(len(d1)))
    if isinstance(d1, float):
        if math.isnan(d1) and math.isnan(d2):
            return True
        return math.isclose(d1, d2, abs_tol=1e-10)
    return d1 == d2


def transform_object_tree(f, o, key_transform=lambda k: k):
    """
    Apply a function (f) on all the values in the given document tree (o), returning a new document of
    the results.

    Recurses through container types (dicts, lists, tuples).

    Returns a new instance (deep copy) without modifying the original.

    :param f: Function to apply on values.
    :param o: document/object
    :param key_transform: Optional function to apply on any dictionary keys.
    """

    def recur(o_):
        return transform_object_tree(f, o_, key_transform=key_transform)

    if isinstance(o, OrderedDict):
        return OrderedDict((key_transform(k), recur(v)) for k, v in o.items())
    if isinstance(o, dict):
        return {key_transform(k): recur(v) for k, v in o.items()}
    if isinstance(o, list):
        return [recur(v) for v in o]
    if isinstance(o, tuple):
        return tuple(recur(v) for v in o)
    return f(o)


def metadata_subset(element, document, full_recursion: bool = False) -> bool:
    """
    Recursively check if one metadata document/object is a subset of another

    full_recursion=False emulates the jsonb "contains" operator used by the postgis and postgres driver.
        (This is used by the in-memory driver to implement search_by_metadata.)

    full_recursion=True allows arbitrary depth matching.

    :param element: The document/object to search for
    :param document: The document/object to search in
    :return: True if element is a subset of document
    """
    if isinstance(element, dict) and isinstance(document, dict):
        matches = True
        for k in element:
            if k not in document or not metadata_subset(
                element[k], document[k], full_recursion=full_recursion
            ):
                matches = False
                break
        if matches:
            return True
        if full_recursion:
            for k in document:
                if metadata_subset(element, document[k], full_recursion=full_recursion):
                    return True
    elif isinstance(document, dict) and full_recursion:
        for k in document:
            if metadata_subset(element, document[k], full_recursion=full_recursion):
                return True
    elif isinstance(element, list | tuple):
        matches = True
        for i in element:
            if not metadata_subset(i, document, full_recursion=full_recursion):
                matches = False
                break
        if matches:
            return True
    elif isinstance(document, list | tuple):
        for i in document:
            if full_recursion:
                if metadata_subset(element, i, full_recursion=full_recursion):
                    return True
            else:
                if element == i:
                    return True
    else:
        return element == document
    return False


class SimpleDocNav:
    """
    Allows navigation of Dataset metadata document lineage tree without
    creating full Dataset objects.

    This has the assumption that a dictionary of source datasets is
    found at the offset ``lineage -> source_datasets`` inside each
    dataset dictionary.
    """

    def __init__(
        self, doc: dict[str, Any], sources_path: Sequence[str] | None = None
    ) -> None:
        if not isinstance(doc, collections.abc.Mapping):
            raise ValueError("SimpleDocNav requires a Mapping")

        self._doc = doc
        self._doc_without = None
        self._sources_path = (
            sources_path if sources_path else ("lineage", "source_datasets")
        )
        self._sources = None
        self._doc_uuid: UUID | None = None

    # FIXME: despite the type signature, this returns a Mapping.
    @property
    def doc(self) -> dict[str, Any]:
        return self._doc

    @property
    def doc_without_lineage_sources(self):
        if self._doc_without is None:
            self._doc_without = toolz.assoc_in(self._doc, self._sources_path, {})

        return self._doc_without

    @property
    def id(self) -> UUID | None:
        if not self._doc_uuid:
            doc_id = self._doc.get("id", None)
            if doc_id:
                self._doc_uuid = doc_id if isinstance(doc_id, UUID) else UUID(doc_id)
        return self._doc_uuid

    @property
    def sources(self):
        if self._sources is None:
            # sources aren't expected to be embedded documents anymore
            self._sources = {
                k: SimpleDocNav(v) if isinstance(v, collections.abc.Mapping) else v
                for k, v in get_doc_offset(self._sources_path, self._doc, {}).items()
            }
        return self._sources

    @property
    def sources_path(self) -> Sequence[str]:
        return self._sources_path

    @property
    def location(self):
        return self._doc.get("location", None)

    def without_location(self) -> SimpleDocNav:
        if self.location is None:
            return self
        return SimpleDocNav(toolz.dissoc(self._doc, "location"))


def _set_doc_offset(offset: list[str | int], document: dict, value) -> None:
    read_offset = offset[:-1]
    sub_doc = get_doc_offset(read_offset, document, {})
    sub_doc[offset[-1]] = value


class DocReader:
    def __init__(
        self,
        type_definition: Mapping[str, list[str]],
        search_fields: Mapping[str, Field],
        doc: Mapping[str, Field],
    ) -> None:
        self.__dict__["_doc"] = doc

        # The user-configurable search fields for this dataset type.
        self.__dict__["_search_fields"] = {
            name: field
            for name, field in search_fields.items()
            if hasattr(field, "extract")
        }

        # The field offsets that the datacube itself understands: id, format, sources etc.
        # (See the metadata-type-schema.yaml or the comments in default-metadata-types.yaml)
        # Search field offsets take priority over Native Fields.
        self.__dict__["_system_offsets"] = {
            name: offset
            for name, offset in type_definition.items()
            if name != "search_fields"
        }

    def __getattr__(self, name: str):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(
            f"Unknown field {name!r}. Expected one of {list(self.fields.keys())!r}"
        )

    @override
    def __setattr__(self, name: str, val) -> None:
        offset = self._system_offsets.get(name)
        if offset is None:
            raise AttributeError(
                f"Unknown field offset {name!r}. Expected one of {list(self.system_fields.keys())!r}"
            )
        return _set_doc_offset(offset, self._doc, val)

    @override
    def __dir__(self) -> list:
        return list(self.fields)

    @property
    def doc(self):
        return self.__dict__["_doc"]

    @property
    def search_fields(self):
        return {
            name: field.extract(self.__dict__["_doc"])
            for name, field in self._search_fields.items()
            if name not in self.system_fields and field.can_extract
        }

    @property
    def system_fields(self):
        return {
            name: get_doc_offset(field, self.__dict__["_doc"])
            for name, field in self._system_offsets.items()
        }

    @property
    def fields(self) -> dict[str, Any]:
        return {**self.system_fields, **self.search_fields}


def without_lineage_sources(
    doc: dict[str, Any], spec, inplace: bool = False
) -> dict[str, Any]:
    """Replace lineage.source_datasets with {}

    :param doc: parsed yaml/json document describing dataset
    :param spec: Product or MetadataType according to which `doc` to be interpreted
    :param inplace: If True modify `doc` in place
    """
    if not inplace:
        doc = deepcopy(doc)

    doc_view = spec.dataset_reader(doc)

    if "sources" in doc_view.fields:
        if doc_view.sources is not None:
            doc_view.sources = {}
        # lineage has not been remapped
        elif "lineage" in doc:
            doc["lineage"] = {}
    # 'sources' path isn't defined
    elif "lineage" in doc:
        doc["lineage"] = {}

    return doc


def schema_validated(schema: Path):
    """
    Decorate a class to enable validating its definition against a JSON Schema file.

    Adds a self.validate() method which takes a dict used to populate the instantiated class.

    :param schema: filename of the json schema, relative to `SCHEMA_PATH`
    :return: wrapped class
    """

    def validate(cls, document) -> None:
        return validate_document(document, cls.schema, schema.parent)

    def decorate(cls):
        cls.schema = next(iter(read_documents(schema)))[1]
        cls.validate = classmethod(validate)
        return cls

    return decorate


def _readable_offset(offset: Offset) -> str:
    return ".".join(map(str, offset))
