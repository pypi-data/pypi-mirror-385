# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Build and index fields within documents.
"""

from collections import namedtuple
from collections.abc import Callable, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, cast, func
from sqlalchemy.dialects import postgresql as postgres
from sqlalchemy.dialects.postgresql import INT4RANGE, INTERVAL, NUMRANGE, TSTZRANGE
from sqlalchemy.sql import ColumnElement
from typing_extensions import override

from datacube import utils
from datacube.model import Range
from datacube.model.fields import _AVAILABLE_TYPES, Expression, Field
from datacube.utils import get_doc_offset
from datacube.utils.changes import Offset
from datacube.utils.dates import tz_aware

from .sql import FLOAT8RANGE


class PgField(Field):
    """
    Postgres implementation of a searchable field. May be a value inside
    a JSONB column.
    """

    def __init__(
        self, name: str, description: str, alchemy_column: ColumnElement, indexed: bool
    ) -> None:
        super().__init__(name, description)

        # The underlying SQLAlchemy column. (eg. DATASET.c.metadata)
        self.alchemy_column = alchemy_column
        self.indexed = indexed

    @property
    def required_alchemy_table(self):
        return self.alchemy_column.table

    @property
    def alchemy_expression(self):
        """
        Get an SQLAlchemy expression for accessing this field.
        :return:
        """
        raise NotImplementedError("alchemy expression")

    @property
    def sql_expression(self):
        """
        Get the raw SQL expression for this field as a string.
        """
        return str(
            self.alchemy_expression.compile(
                dialect=postgres.dialect(), compile_kwargs={"literal_binds": True}
            )
        )

    @property
    def postgres_index_type(self) -> str | None:
        return "btree"

    @override
    def __eq__(self, value) -> Expression:  # type: ignore[override]
        return EqualsExpression(self, value)

    @override
    def between(self, low, high) -> Expression:
        raise NotImplementedError("between expression")


class NativeField(PgField):
    """
    Fields hard-coded into the schema. (not user configurable)
    """

    def __init__(
        self,
        name: str,
        description: str,
        alchemy_column,
        alchemy_expression=None,
        # Should this be selected by default when selecting all fields?
        affects_row_selection: bool = False,
    ) -> None:
        super().__init__(name, description, alchemy_column, False)
        self._expression = alchemy_expression
        self.affects_row_selection = affects_row_selection

    @property
    @override
    def alchemy_expression(self):
        expression = (
            self._expression if self._expression is not None else self.alchemy_column
        )
        return expression.label(self.name)

    @property
    @override
    def postgres_index_type(self) -> str | None:
        # Don't add extra indexes for native fields.
        return None


class PgDocField(PgField):
    """
    A field extracted from inside a (jsonb) document.
    """

    def value_to_alchemy(self, value):
        """
        Wrap the given value with any necessary type casts/conversions for this field.

        Overridden by other classes as needed.
        """
        # Default do nothing (eg. string datatypes)
        return value

    def parse_value(self, value):
        """
        Parse the value from a string. May be overridden by subclasses.
        """
        return value

    def _alchemy_offset_value(
        self,
        doc_offsets: Sequence[Offset],
        agg_function: Callable[[Any], ColumnElement],
    ) -> ColumnElement:
        """
        Get an sqlalchemy value for the given offsets of this field's sqlalchemy column.
        If there are multiple they will be combined using the given aggregate function.

        Offsets can either be single:
            ('platform', 'code')
        Or multiple:
            (('platform', 'code'), ('satellite', 'name'))

        In the latter case, the multiple values are combined using the given aggregate function
        (defaults to using coalesce: grab the first non-null value)
        """
        if not doc_offsets:
            raise ValueError("Value requires at least one offset")

        if isinstance(doc_offsets[0], str):
            # It's a single offset.
            doc_offsets = [doc_offsets]

        alchemy_values = [
            self.value_to_alchemy(self.alchemy_column[offset].astext)
            for offset in doc_offsets
        ]
        # If there's multiple fields, we aggregate them (eg. "min()"). Otherwise use the one.
        return (
            agg_function(*alchemy_values)
            if len(alchemy_values) > 1
            else alchemy_values[0]
        )

    def _extract_offset_value(self, doc, doc_offsets, agg_function):
        """
        Extract a value for the given document offsets.

        Same as _alchemy_offset_value(), but returns the value instead of an sqlalchemy expression to calc the value.
        """
        if not doc_offsets:
            raise ValueError("Value requires at least one offset")

        if isinstance(doc_offsets[0], str):
            # It's a single offset.
            doc_offsets = [doc_offsets]

        values = (get_doc_offset(offset, doc) for offset in doc_offsets)
        values = [self.parse_value(v) for v in values if v is not None]

        if not values:
            return None
        if len(values) == 1:
            return values[0]
        return agg_function(*values)


class SimpleDocField(PgDocField):
    """
    A field with a single value (e.g. String, int) calculated as an offset inside
    a (jsonb) document.
    """

    def __init__(
        self,
        name: str,
        description: str,
        alchemy_column,
        indexed: bool,
        offset: Offset | Sequence[Offset] | None = None,
        selection: str = "first",
    ) -> None:
        super().__init__(name, description, alchemy_column, indexed)
        self.offset = offset
        if selection not in SELECTION_TYPES:
            raise ValueError(
                f"Unknown field selection type {selection}. Expected one of: {(SELECTION_TYPES,)!r}"
            )
        self.aggregation = SELECTION_TYPES[selection]

    @property
    @override
    def alchemy_expression(self):
        return self._alchemy_offset_value(self.offset, self.aggregation.pg_calc).label(
            self.name
        )

    @override
    def __eq__(self, value) -> Expression:  # type: ignore[override]
        return EqualsExpression(self, value)

    @override
    def between(self, low, high) -> Expression:
        raise NotImplementedError("Simple field between expression")

    can_extract = True

    @override
    def extract(self, doc):
        return self._extract_offset_value(doc, self.offset, self.aggregation.calc)

    def evaluate(self, ctx):
        return self.extract(ctx)


class IntDocField(SimpleDocField):
    type_name: _AVAILABLE_TYPES = "integer"

    @override
    def value_to_alchemy(self, value):
        return cast(value, postgres.INTEGER)

    @override
    def between(self, low, high) -> "ValueBetweenExpression":
        return ValueBetweenExpression(self, low, high)

    @override
    def parse_value(self, value) -> int:
        return int(value)


class BoolDocField(SimpleDocField):
    type_name: _AVAILABLE_TYPES = "boolean"

    @override
    def value_to_alchemy(self, value):
        return cast(value, postgres.BOOLEAN)

    @override
    def parse_value(self, value) -> bool:
        if value.lower() == "false":
            return False
        if value.lower() == "true":
            return True
        return bool(value)


class NumericDocField(SimpleDocField):
    type_name: _AVAILABLE_TYPES = "numeric"

    @override
    def value_to_alchemy(self, value):
        return cast(value, postgres.NUMERIC)

    @override
    def between(self, low, high) -> "ValueBetweenExpression":
        return ValueBetweenExpression(self, low, high)

    @override
    def parse_value(self, value) -> Decimal:
        return Decimal(value)


class DoubleDocField(SimpleDocField):
    type_name: _AVAILABLE_TYPES = "double"

    @override
    def value_to_alchemy(self, value):
        return cast(value, postgres.DOUBLE_PRECISION)

    @override
    def between(self, low, high) -> "ValueBetweenExpression":
        return ValueBetweenExpression(self, low, high)

    @override
    def parse_value(self, value) -> float:
        return float(value)


class DateDocField(SimpleDocField):
    type_name: _AVAILABLE_TYPES = "datetime"

    @override
    def value_to_alchemy(
        self, value: datetime | date | str | ColumnElement
    ) -> datetime | date | str | ColumnElement:
        """
        Wrap a value as needed for this field type.
        """
        if isinstance(value, datetime):
            return tz_aware(value)
        # SQLAlchemy expression or string are parsed in pg as dates.
        if isinstance(value, ColumnElement | str):
            return func.agdc.common_timestamp(value)
        raise ValueError(f"Value not readable as date: {value!r}")

    @override
    def between(self, low, high) -> "ValueBetweenExpression":
        return ValueBetweenExpression(self, low, high)

    @override
    def parse_value(self, value: datetime | str) -> datetime:
        return utils.parse_time(value)

    @property
    def day(self) -> NativeField:
        """Get field truncated to the day"""
        return NativeField(
            f"{self.name}_day",
            f"Day of {self.description}",
            self.alchemy_column,
            alchemy_expression=cast(
                func.date_trunc("day", self.alchemy_expression), postgres.TIMESTAMP
            ),
        )


class RangeDocField(PgDocField):
    """
    A range of values. Has min and max values, which may be calculated from multiple
    values in the document.
    """

    FIELD_CLASS = SimpleDocField

    def __init__(
        self,
        name: str,
        description: str,
        alchemy_column,
        indexed: bool,
        min_offset=None,
        max_offset=None,
    ) -> None:
        super().__init__(name, description, alchemy_column, indexed)
        self.lower = self.FIELD_CLASS(
            name + "_lower",
            description,
            alchemy_column,
            indexed=False,
            offset=min_offset,
            selection="least",
        )
        self.greater = self.FIELD_CLASS(
            name + "_greater",
            description,
            alchemy_column,
            indexed=False,
            offset=max_offset,
            selection="greatest",
        )

    @override
    def value_to_alchemy(self, value):
        raise NotImplementedError("range type")

    @property
    @override
    def postgres_index_type(self) -> str:
        return "gist"

    @property
    @override
    def alchemy_expression(self):
        return self.value_to_alchemy(
            (self.lower.alchemy_expression, self.greater.alchemy_expression)
        ).label(self.name)

    @override
    def __eq__(self, value) -> Expression:  # type: ignore[override]
        # Lower and higher are interchangeable here: they're the same type.
        casted_val = self.lower.value_to_alchemy(value)
        return RangeContainsExpression(self, casted_val)

    can_extract = True

    @override
    def extract(self, doc) -> Range | None:
        min_val = self.lower.extract(doc)
        max_val = self.greater.extract(doc)
        if not min_val and not max_val:
            return None
        return Range(min_val, max_val)


class NumericRangeDocField(RangeDocField):
    FIELD_CLASS = NumericDocField
    type_name: _AVAILABLE_TYPES = "numeric-range"

    @override
    def value_to_alchemy(self, value):
        low, high = value
        return func.numrange(
            low,
            high,
            # Inclusive on both sides.
            "[]",
            type_=NUMRANGE,
        )

    @override
    def between(self, low, high) -> Expression:
        return RangeBetweenExpression(self, low, high, _range_class=postgres.Range)


class IntRangeDocField(RangeDocField):
    FIELD_CLASS = IntDocField
    type_name: _AVAILABLE_TYPES = "integer-range"

    @override
    def value_to_alchemy(self, value):
        low, high = value
        return func.numrange(
            low,
            high,
            # Inclusive on both sides.
            "[]",
            type_=INT4RANGE,
        )

    @override
    def between(self, low, high) -> Expression:
        return RangeBetweenExpression(self, low, high, _range_class=postgres.Range)


class DoubleRangeDocField(RangeDocField):
    FIELD_CLASS = DoubleDocField
    type_name: _AVAILABLE_TYPES = "double-range"

    @override
    def value_to_alchemy(self, value):
        low, high = value
        return func.agdc.float8range(
            low,
            high,
            # Inclusive on both sides.
            "[]",
            type_=FLOAT8RANGE,
        )

    @override
    def between(self, low, high) -> Expression:
        return RangeBetweenExpression(
            self, low, high, _range_class=func.agdc.float8range
        )


class DateRangeDocField(RangeDocField):
    FIELD_CLASS = DateDocField
    type_name: _AVAILABLE_TYPES = "datetime-range"

    @override
    def value_to_alchemy(self, value):
        low, high = value
        return func.tstzrange(
            low,
            high,
            # Inclusive on both sides.
            "[]",
            type_=TSTZRANGE,
        )

    @override
    def between(self, low: datetime, high: datetime) -> Expression:
        low = _number_implies_year(low)
        high = _number_implies_year(high)

        if isinstance(low, datetime) and isinstance(high, datetime):
            return RangeBetweenExpression(
                self, tz_aware(low), tz_aware(high), _range_class=postgres.Range
            )
        raise ValueError(
            "Unknown comparison type for date range: "
            f"expecting datetimes, got: ({low!r}, {high!r})"
        )

    @property
    def expression_with_leniency(self):
        return func.tstzrange(
            self.lower.alchemy_expression - cast("500 milliseconds", INTERVAL),
            self.greater.alchemy_expression + cast("500 milliseconds", INTERVAL),
            # Inclusive on both sides.
            "[]",
            type_=TSTZRANGE,
        )


def _number_implies_year(v: int | datetime) -> datetime:
    """
    >>> _number_implies_year(1994)
    datetime.datetime(1994, 1, 1, 0, 0)
    >>> _number_implies_year(datetime(1994, 4, 4))
    datetime.datetime(1994, 4, 4, 0, 0)
    """
    if isinstance(v, int):
        return datetime(v, 1, 1)
    # The expression module parses all number ranges as floats.
    if isinstance(v, float):
        return datetime(int(v), 1, 1)

    return v


class PgExpression(Expression):
    def __init__(self, field: PgField) -> None:
        super().__init__()
        self.field = field

    @property
    def alchemy_expression(self):
        """
        Get an SQLAlchemy expression for accessing this field.
        """
        raise NotImplementedError("alchemy expression")


class ValueBetweenExpression(PgExpression):
    def __init__(self, field: PgField, low_value, high_value) -> None:
        super().__init__(field)
        self.low_value = low_value
        self.high_value = high_value

    @property
    @override
    def alchemy_expression(self):
        if self.low_value is not None and self.high_value is not None:
            return and_(
                self.field.alchemy_expression >= self.low_value,
                self.field.alchemy_expression < self.high_value,
            )
        if self.low_value is not None:
            return self.field.alchemy_expression >= self.low_value
        if self.high_value is not None:
            return self.field.alchemy_expression < self.high_value

        raise ValueError("Expect at least one of [low,high] to be set")


class RangeBetweenExpression(PgExpression):
    def __init__(self, field: PgField, low_value, high_value, _range_class) -> None:
        super().__init__(field)
        self.low_value = low_value
        self.high_value = high_value
        self._range_class = _range_class

    @property
    @override
    def alchemy_expression(self):
        return self.field.alchemy_expression.overlaps(
            self._range_class(self.low_value, self.high_value, bounds="[]")
        )


class RangeContainsExpression(PgExpression):
    def __init__(self, field: PgField, value) -> None:
        super().__init__(field)
        self.value = value

    @property
    @override
    def alchemy_expression(self):
        return self.field.alchemy_expression.contains(self.value)


class EqualsExpression(PgExpression):
    def __init__(self, field: PgField, value) -> None:
        super().__init__(field)
        self.value = value

    @property
    @override
    def alchemy_expression(self):
        return self.field.alchemy_expression == self.value

    @override
    def evaluate(self, ctx):
        return self.field.evaluate(ctx) == self.value


def parse_fields(doc: dict[str, Any], table_column) -> dict[str, PgField]:
    """
    Parse a field spec document into objects.

    Example document:

    ::

        {
            # Field name:
            "lat": {
                # Field type & properties.
                "type": "float-range",
                "min_offset": [
                    # Offsets within a dataset document for this field.
                    ["extent", "coord", "ul", "lat"],
                    ["extent", "coord", "ll", "lat"],
                ],
                "max_offset": [
                    ["extent", "coord", "ur", "lat"],
                    ["extent", "coord", "lr", "lat"],
                ],
            }
        }

    :param table_column: SQLAlchemy jsonb column for the document we're reading fields from.
    """
    # Implementations of fields for this driver
    types = {
        SimpleDocField,
        IntDocField,
        BoolDocField,
        DoubleDocField,
        DateDocField,
        NumericRangeDocField,
        IntRangeDocField,
        DoubleRangeDocField,
        DateRangeDocField,
    }
    type_map = {f.type_name: f for f in types}
    # An alias for backwards compatibility
    type_map["float-range"] = NumericRangeDocField

    # No later field should have overridden string
    assert type_map["string"] == SimpleDocField

    def _get_field(name: str, descriptor: dict, column) -> PgField:
        """
        :param column: SQLAlchemy table column
        """
        ctorargs = descriptor.copy()
        type_name = ctorargs.pop("type", "string")
        description = ctorargs.pop("description", None)
        indexed_val = ctorargs.pop("indexed", "true")
        indexed = (
            indexed_val.lower() == "true"
            if isinstance(indexed_val, str)
            else indexed_val
        )

        field_class = type_map.get(type_name)
        if not field_class:
            raise ValueError(
                f"Field {name!r} has unknown type {type_name!r}."
                f" Available types are: {list(type_map.keys())!r}"
            )
        try:
            return field_class(name, description, column, indexed, **ctorargs)
        except TypeError as e:
            raise RuntimeError(
                f"Field {name} has unexpected argument for a {type_name}", e
            ) from None

    return {
        name: _get_field(name, descriptor, table_column)
        for name, descriptor in doc.items()
    }


def _coalesce(*values):
    """
    Return first non-none value.
    Return None if all values are None, or there are no values passed in.

    >>> _coalesce(1, 2)
    1
    >>> _coalesce(None, 2, 3)
    2
    >>> _coalesce(None, None, 3, None, 5)
    3
    """
    for v in values:
        if v is not None:
            return v
    return None


# How to choose/combine multiple doc values.
ValueAggregation = namedtuple("ValueAggregation", ("calc", "pg_calc"))
SELECTION_TYPES = {
    # First non-null
    "first": ValueAggregation(_coalesce, func.coalesce),
    # min/max
    "least": ValueAggregation(min, func.least),
    "greatest": ValueAggregation(max, func.greatest),
}
