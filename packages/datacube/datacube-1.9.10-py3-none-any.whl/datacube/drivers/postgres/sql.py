# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Custom types for postgres & sqlalchemy
"""

import warnings

from sqlalchemy import TIMESTAMP, Connection, inspect, text
from sqlalchemy.dialects.postgresql.ranges import AbstractRange, Range
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.expression import ClauseElement, Executable
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.types import Double

SCHEMA_NAME = "agdc"


class CreateView(Executable, ClauseElement):
    inherit_cache = True

    def __init__(self, name: str, select) -> None:
        self.name = name
        self.select = select


@compiles(CreateView)
def visit_create_view(element, compiler, **kw) -> str:
    return f"CREATE VIEW {element.name} AS {compiler.process(element.select, literal_binds=True)}"


UPDATE_TIMESTAMP_SQL: str = f"""
create or replace function {SCHEMA_NAME}.set_row_update_time()
returns trigger as $$
begin
  new.updated = now();
  return new;
end;
$$ language plpgsql;
"""

UPDATE_COLUMN_MIGRATE_SQL_TEMPLATE = """
alter table {schema}.{table} add column if not exists updated
timestamptz default now();
"""

UPDATE_COLUMN_INDEX_SQL_TEMPLATE = """
create index if not exists ix_{table}_updated
on {schema}.{table}(updated);
"""

ADDED_COLUMN_MIGRATE_SQL_TEMPLATE = """
alter table {schema}.{table} add column if not exists added
timestamptz default now();
"""

ADDED_COLUMN_INDEX_SQL_TEMPLATE = """
create index if not exists ix_{table}_added
on {schema}.{table}(added);
"""

INSTALL_TRIGGER_SQL_TEMPLATE = [
    "drop trigger if exists row_update_time_{table} on {schema}.{table}",
    """
    create trigger row_update_time_{table}
    before update on {schema}.{table}
    for each row
    execute procedure {schema}.set_row_update_time();
    """,
]

TYPES_INIT_SQL: list[str] = [
    f"""
    create or replace function {SCHEMA_NAME}.common_timestamp(text)
    returns timestamp with time zone as $$
    select ($1)::timestamp at time zone 'utc';
    $$ language sql immutable returns null on null input;
    """,
    f"""
    create type {SCHEMA_NAME}.float8range as range (
        subtype = float8,
        subtype_diff = float8mi
    )
    """,
]


# pylint: disable=abstract-method
class FLOAT8RANGE(AbstractRange[Range[Double]]):
    __visit_name__ = "FLOAT8RANGE"


@compiles(FLOAT8RANGE)
def visit_float8range(element, compiler, **kw) -> str:
    return "FLOAT8RANGE"


# Register the function with SQLAlchemy.
# pylint: disable=too-many-ancestors
class CommonTimestamp(GenericFunction):
    type = TIMESTAMP(timezone=True)
    package = "agdc"
    identifier = "common_timestamp"
    inherit_cache = False

    name = "common_timestamp"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.packagenames = (f"{SCHEMA_NAME}",)


# pylint: disable=too-many-ancestors
class Float8Range(GenericFunction):
    type = FLOAT8RANGE  # type: ignore[assignment]
    package = "agdc"
    identifier = "float8range"
    inherit_cache = False

    name = "float8range"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.packagenames = (f"{SCHEMA_NAME}",)


class PGNAME(sqltypes.Text):
    """Postgres 'NAME' type."""

    __visit_name__ = "NAME"


@compiles(PGNAME)
def visit_name(element, compiler, **kw) -> str:
    return "NAME"


def pg_exists(conn, name: str) -> bool:
    """
    Does a postgres object exist?
    """
    return conn.execute(text(f"SELECT to_regclass('{name}')")).scalar() is not None


def pg_column_exists(
    conn: Connection, table: str, column: str, schema: str | None = SCHEMA_NAME
) -> bool:
    """
    Does a table column exist?
    """
    if table.startswith((f"{SCHEMA_NAME}.", f"'{SCHEMA_NAME}.", f'"{SCHEMA_NAME}.')):
        warnings.warn(
            f"Call pg_column_exists with a table name without {SCHEMA_NAME}.",
            stacklevel=2,
        )
        table = table.replace(f"{SCHEMA_NAME}.", "")
    return column in [x.get("name") for x in inspect(conn).get_columns(table, schema)]


def escape_pg_identifier(conn, name: str):
    """
    Escape identifiers (tables, fields, roles, etc) for inclusion in SQL statements.

    psycopg2 can safely merge query arguments, but cannot do the same for dynamically
    generating queries.

    See http://initd.org/psycopg/docs/sql.html for more information.
    """
    # New (2.7+) versions of psycopg2 have function: extensions.quote_ident()
    # But it's too bleeding edge right now. We'll ask the server to escape instead, as
    # these are not performance sensitive.
    return conn.execute(text(f"select quote_ident('{name}')")).scalar()
