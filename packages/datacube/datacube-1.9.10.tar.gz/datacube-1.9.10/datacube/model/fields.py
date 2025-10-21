# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""Non-db specific implementation of metadata search fields.

This allows extraction of fields of interest from dataset metadata document.
"""

import decimal
from collections.abc import Callable, Mapping
from typing import Any, Generic, Literal, TypeAlias, get_args

import toolz
from typing_extensions import override

from datacube.utils import parse_time

from ._base import OrderedT, Range

# Allowed values for field 'type' (specified in a metadata type document)
_AVAILABLE_TYPES: TypeAlias = Literal[
    # Unrestricted type - handy for dynamically creating fields from offsets, e.g. for search_returning()
    "any",
    "numeric-range",
    "double-range",
    "integer-range",
    "datetime-range",
    "string",
    "numeric",
    "double",
    "integer",
    "boolean",
    "datetime",
    # For backwards compatibility (alias for numeric-range)
    "float-range",
]
_AVAILABLE_TYPE_NAMES: tuple[_AVAILABLE_TYPES, ...] = get_args(_AVAILABLE_TYPES)


class Expression:
    # No properties at the moment. These are built and returned by the
    # DB driver (from Field methods), so they're mostly an opaque token.

    # A simple equals implementation for comparison in test code.
    @override
    def __eq__(self, other) -> bool:
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__

    def evaluate(self, ctx):
        raise NotImplementedError()


class SimpleEqualsExpression(Expression):
    def __init__(self, field, value) -> None:
        self.field = field
        self.value = value

    @override
    def evaluate(self, ctx):
        return self.field.extract(ctx) == self.value


class Field:
    """
    A searchable field within a dataset/storage metadata document.
    """

    # type of field.
    # If type is not specified, the field is a string
    type_name: _AVAILABLE_TYPES = "string"

    def __init__(self, name: str, description: str) -> None:
        self.name = name

        self.description = description

        # Does selecting this affect the output rows?
        # (eg. Does this join other tables that aren't 1:1 with datasets.)
        self.affects_row_selection = False
        # FIXME: Remove assert in 2.0.
        assert self.type_name in _AVAILABLE_TYPE_NAMES, (
            f"Invalid type name {self.type_name}"
        )

    @override
    def __eq__(self, value) -> Expression:  # type: ignore[override]
        """
        Is this field equal to a value?

        this returns an Expression object (hence type ignore above)
        """
        raise NotImplementedError("equals expression")

    def between(self, low, high) -> Expression:
        """
        Is this field in a range?
        """
        raise NotImplementedError("between expression")

    # Should be True if value can be extracted from a dataset metadata document with the extract method
    can_extract: bool = False

    def extract(self, doc):
        raise NotImplementedError(f"extract for {self.name}")


class SimpleField(Field):
    def __init__(
        self,
        offset: list[str | int],
        converter: type | Callable[[Any], Any],
        type_name: _AVAILABLE_TYPES,
        name: str = "",
        description: str = "",
    ) -> None:
        self._offset = offset
        self._converter = converter
        self.type_name = type_name
        super().__init__(name, description)

    @override
    def __eq__(self, value) -> Expression:  # type: ignore[override]
        return SimpleEqualsExpression(self, value)

    can_extract = True

    @override
    def extract(self, doc):
        v = toolz.get_in(self._offset, doc, default=None)
        if v is None:
            return None
        return self._converter(v)


class RangeField(Generic[OrderedT], Field):
    def __init__(
        self,
        min_offset,
        max_offset,
        base_converter: type | Callable[[Any], OrderedT],
        type_name: _AVAILABLE_TYPES,
        name: str = "",
        description: str = "",
    ) -> None:
        self.type_name = type_name
        self._converter = base_converter
        self._min_offset = min_offset
        self._max_offset = max_offset
        super().__init__(name, description)

    can_extract = True

    @override
    def extract(self, doc) -> Range | None:
        def extract_raw(paths) -> list[OrderedT]:
            vv = [toolz.get_in(p, doc, default=None) for p in paths]
            return [self._converter(v) for v in vv if v is not None]

        v_min = extract_raw(self._min_offset)
        v_max = extract_raw(self._max_offset)

        v_min = None if len(v_min) == 0 else min(v_min)
        v_max = None if len(v_max) == 0 else max(v_max)

        if v_min is None and v_max is None:
            return None

        return Range(v_min, v_max)


def parse_search_field(
    doc: Mapping[str, Any], name: str = ""
) -> RangeField | SimpleField:
    parsers: dict[str, type | Callable[[Any], Any]] = {
        "string": str,
        "double": float,
        "integer": int,
        "boolean": bool,
        "numeric": decimal.Decimal,
        "datetime": parse_time,
        "object": lambda x: x,
    }
    _type = doc.get("type", "string")

    if _type in parsers:
        offset = doc.get("offset", None)
        if offset is None:
            raise ValueError("Missing offset")

        return SimpleField(
            offset,
            parsers[_type],
            _type,
            name=name,
            description=doc.get("description", ""),
        )

    if not _type.endswith("-range"):
        raise ValueError("Unsupported search field type: " + str(_type))

    raw_type = _type.split("-")[0]

    if (
        raw_type == "float"
    ):  # float-range is supposed to be supported, but not just float?
        raw_type = "numeric"
        _type = "numeric-range"

    if raw_type not in parsers:
        raise ValueError("Unsupported search field type: " + str(_type))

    min_offset = doc.get("min_offset", None)
    max_offset = doc.get("max_offset", None)

    if min_offset is None or max_offset is None:
        raise ValueError("Need to specify both min_offset and max_offset")

    return RangeField(
        min_offset,
        max_offset,
        parsers[raw_type],
        _type,
        name=name,
        description=doc.get("description", ""),
    )


def get_dataset_fields(metadata_definition: Mapping[str, Any]) -> dict[str, Field]:
    """Construct search fields dictionary not tied to any specific db
    implementation.
    """
    fields = toolz.get_in(["dataset", "search_fields"], metadata_definition, {})
    return {n: parse_search_field(doc, name=n) for n, doc in fields.items()}
