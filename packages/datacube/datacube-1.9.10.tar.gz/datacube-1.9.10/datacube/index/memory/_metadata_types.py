# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
import logging
from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any, cast

from typing_extensions import override

from datacube.index.abstract import (
    AbstractMetadataTypeResource,
    default_metadata_type_docs,
)
from datacube.index.memory._fields import get_dataset_fields
from datacube.model import MetadataType
from datacube.utils import _readable_offset, changes, jsonify_document
from datacube.utils.changes import (
    AllowPolicy,
    Change,
    Offset,
    check_doc_unchanged,
    get_doc_changes,
)
from datacube.utils.documents import JsonDict

_LOG: logging.Logger = logging.getLogger(__name__)


class MetadataTypeResource(AbstractMetadataTypeResource):
    def __init__(self) -> None:
        self.by_id: dict = {}
        self.by_name: dict = {}
        self.next_id = 1
        for doc in default_metadata_type_docs():
            self.add(self.from_doc(doc))

    @override
    def from_doc(self, definition: JsonDict) -> MetadataType:
        MetadataType.validate(definition)  # type: ignore[attr-defined]
        return self._make(definition)

    @override
    def add(
        self, metadata_type: MetadataType, allow_table_lock: bool = False
    ) -> MetadataType:
        MetadataType.validate(metadata_type.definition)  # type: ignore[attr-defined]
        if metadata_type.name in self.by_name:
            # Error unless it's the exact same metadata_type
            _LOG.warning("Metadata Type exists, checking for differences")
            check_doc_unchanged(
                self.by_name[metadata_type.name].definition,
                jsonify_document(metadata_type.definition),
                f"Metadata Type {metadata_type.name}",
            )
        else:
            persisted = self._make(
                jsonify_document(metadata_type.definition), id_=self.next_id
            )
            self.next_id += 1
            self.by_id[persisted.id] = persisted
            self.by_name[persisted.name] = persisted
        return cast(MetadataType, self.get_by_name(metadata_type.name))

    @override
    def can_update(
        self, metadata_type: MetadataType, allow_unsafe_updates: bool = False
    ) -> tuple[bool, Iterable[Change], Iterable[Change]]:
        MetadataType.validate(metadata_type.definition)  # type: ignore[attr-defined]
        existing = self.get_by_name(metadata_type.name)
        if not existing:
            raise ValueError(
                f"Unknown metadata type {metadata_type.name}, cannot update - add first"
            )
        updates_allowed: Mapping[Offset, AllowPolicy] = {
            ("description",): changes.allow_any,
            # You can add new fields safely but not modify existing ones.
            ("dataset",): changes.allow_extension,
            ("dataset", "search_fields"): changes.allow_extension,
        }

        doc_changes = get_doc_changes(
            existing.definition, jsonify_document(metadata_type.definition)
        )
        good_changes, bad_changes = changes.classify_changes(
            doc_changes, updates_allowed
        )
        for offset, old_val, new_val in good_changes:
            _LOG.info(
                "Safe change in %s from %r to %r",
                _readable_offset(offset),
                old_val,
                new_val,
            )

        for offset, old_val, new_val in bad_changes:
            _LOG.warning(
                "Unsafe change in %s from %r to %r",
                _readable_offset(offset),
                old_val,
                new_val,
            )

        return ((allow_unsafe_updates or not bad_changes), good_changes, bad_changes)

    @override
    def update(
        self,
        metadata_type: MetadataType,
        allow_unsafe_updates: bool = False,
        allow_table_lock: bool = False,
    ) -> MetadataType:
        can_update, safe_changes, unsafe_changes = self.can_update(
            metadata_type, allow_unsafe_updates
        )

        if not safe_changes and not unsafe_changes:
            _LOG.warning(f"No changes detected for metadata type {metadata_type.name}")
            return self.get_by_name_unsafe(metadata_type.name)

        if not can_update:
            errs = ", ".join(_readable_offset(change[0]) for change in unsafe_changes)
            raise ValueError(f"Unsafe changes in {metadata_type.name}: {errs}")

        _LOG.info(f"Updating metadata type {metadata_type.name}")

        persisted = self.clone(metadata_type)
        self.by_id[metadata_type.id] = persisted
        self.by_name[metadata_type.name] = persisted
        return persisted

    @override
    def get_unsafe(self, id_: int) -> MetadataType:
        return self.clone(self.by_id[id_])

    @override
    def get_by_name_unsafe(self, name: str) -> MetadataType:
        return self.clone(self.by_name[name])

    @override
    def check_field_indexes(
        self,
        allow_table_lock: bool = False,
        rebuild_views: bool = False,
        rebuild_indexes: bool = False,
    ) -> None:
        # Cannot implement this method without separating index implementation into
        # separate layer from the API Resource implementations.
        pass

    @override
    def get_all(self) -> Iterable[MetadataType]:
        return (self.clone(mdt) for mdt in self.by_id.values())

    @staticmethod
    def _make(definition: Mapping[str, Any], id_=None) -> MetadataType:
        # Note this is an index-specific implementation of get_dataset_fields, not the default
        return MetadataType(
            definition, search_field_extractor=get_dataset_fields, id_=id_
        )

    @staticmethod
    def clone(orig: MetadataType) -> MetadataType:
        return MetadataTypeResource._make(deepcopy(orig.definition), id_=orig.id)
