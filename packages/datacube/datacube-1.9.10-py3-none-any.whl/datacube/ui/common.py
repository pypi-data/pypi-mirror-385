# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Common methods for UI code.
"""

from collections.abc import Generator, Iterable
from pathlib import Path

from toolz.functoolz import identity

from datacube.utils import (
    InvalidDocException,
    SimpleDocNav,
    is_supported_document_type,
    is_url,
    read_documents,
)


def get_metadata_path(possible_path: str | Path) -> str:
    """
    Find a metadata path for a given input/dataset path.

    Needs to handle local files as well as remote URLs
    """
    # We require exact URLs, lets skip any sort of fancy investigation and mapping
    if isinstance(possible_path, str) and is_url(possible_path):
        return possible_path

    dataset_path = Path(possible_path)

    # They may have given us a metadata file directly.
    if dataset_path.is_file() and is_supported_document_type(dataset_path):
        return str(dataset_path)

    # Otherwise there may be a sibling file with appended suffix '.agdc-md.yaml'.
    expected_name = dataset_path.parent.joinpath(f"{dataset_path.name}.agdc-md")
    found = _find_any_metadata_suffix(expected_name)
    if found:
        return str(found)

    # Otherwise if it's a directory, there may be an 'agdc-metadata.yaml' file describing all contained datasets.
    if dataset_path.is_dir():
        expected_name = dataset_path.joinpath("agdc-metadata")
        found = _find_any_metadata_suffix(expected_name)
        if found:
            return str(found)

    if is_supported_document_type(dataset_path):
        raise ValueError(f"No such file {dataset_path}")
    raise ValueError(f"No supported metadata docs found for dataset {dataset_path}")


def _find_any_metadata_suffix(path: Path) -> Path | None:
    """
    Find any supported metadata files that exist with the given file path stem.
    (supported suffixes are tried on the name)

    Eg. searching for '/tmp/ga-metadata' will find if any files such as '/tmp/ga-metadata.yaml' or
    '/tmp/ga-metadata.json', or '/tmp/ga-metadata.yaml.gz' etc that exist: any suffix supported by read_documents()
    """
    existing_paths = list(
        filter(is_supported_document_type, path.parent.glob(path.name + "*"))
    )
    if not existing_paths:
        return None

    if len(existing_paths) > 1:
        raise ValueError(f"Multiple matched metadata files: {existing_paths!r}")

    return existing_paths[0]


def ui_path_doc_stream(
    paths: Iterable[str | Path], logger=None, uri: bool = True, raw: bool = False
) -> Generator[tuple[str, SimpleDocNav | dict]]:
    """Given a stream of URLs, or Paths that could be directories, generate a stream of
    (path, doc) tuples.

    For every path:
    1. If directory find the metadata file or log error if not found

    2. Load all documents from that path and return one at a time (parsing
    errors are logged, but processing should continue)

    :param paths: Filesystem paths

    :param logger: Logger to use to report errors

    :param uri: If True return path in uri format, else return it as filesystem path

    :param raw: By default docs are wrapped in :class:`SimpleDocNav`, but you can
    instead request them to be raw dictionaries
    """

    def _resolve_doc_files(paths: Iterable[str | Path]) -> Generator[str]:
        for p in paths:
            try:
                yield get_metadata_path(p)
            except ValueError as e:
                if logger is not None:
                    logger.error(str(e))

    def _path_doc_stream(
        files, uri: bool = True, raw: bool = False
    ) -> Generator[tuple[str, SimpleDocNav | dict]]:
        maybe_wrap = identity if raw else SimpleDocNav

        for fname in files:
            try:
                for p, doc in read_documents(fname, uri=uri):
                    yield p, maybe_wrap(doc)

            except InvalidDocException:
                if logger is not None:
                    logger.error("Failed reading documents from %s", str(fname))

    yield from _path_doc_stream(_resolve_doc_files(paths), uri=uri, raw=raw)
