# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Common datatypes for DB drivers.
"""

from datetime import date, datetime, time, timezone

from typing_extensions import override

from datacube.model import Not, QueryField, Range
from datacube.model.fields import Expression, Field

__all__ = [
    "Expression",
    "Field",
    "OrExpression",
    "UnknownFieldError",
    "as_expression",
    "to_expressions",
]


class UnknownFieldError(Exception):
    pass


class OrExpression(Expression):
    def __init__(self, *exprs) -> None:
        super().__init__()
        self.exprs = exprs
        # Or expressions built by dc.load are always made up of simple expressions that share the same field.
        self.field = exprs[0].field

    @override
    def evaluate(self, ctx) -> bool:
        return any(expr.evaluate(ctx) for expr in self.exprs)


class NotExpression(Expression):
    def __init__(self, expr) -> None:
        super().__init__()
        self.expr = expr
        self.field = expr.field

    @override
    def evaluate(self, ctx) -> bool:
        return not self.expr.evaluate(ctx)


def as_expression(field: Field, value: QueryField) -> Expression:
    """
    Convert a single field/value to expression, following the "simple" conventions.
    """
    if isinstance(value, Range):
        return field.between(value.begin, value.end)
    if isinstance(value, list):
        return OrExpression(*(as_expression(field, val) for val in value))
    if isinstance(value, Not):
        return NotExpression(as_expression(field, value.value))
    # Treat a date (day) as a time range.
    if isinstance(value, date) and not isinstance(value, datetime):
        return as_expression(
            field,
            Range(
                datetime.combine(value, time.min.replace(tzinfo=timezone.utc)),
                datetime.combine(value, time.max.replace(tzinfo=timezone.utc)),
            ),
        )
    return field == value


def _to_expression(get_field, name: str, value) -> Expression:
    field = get_field(name)
    if field is None:
        raise UnknownFieldError(f"Unknown field {name!r}")

    return as_expression(field, value)


def to_expressions(get_field, **query) -> list[Expression]:
    """
    Convert a simple query (dict of param names and values) to expression objects.
    """
    return [_to_expression(get_field, name, value) for name, value in query.items()]
