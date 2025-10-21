# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0

# We often have one-arg-per column, so these checks aren't so useful.
# pylint: disable=too-many-arguments,too-many-public-methods

# SQLAlchemy queries require "column == None", not "column is None" due to operator overloading:
# pylint: disable=singleton-comparison

"""
Postgres connection and setup
"""

import json
import logging
import re
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Connection, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL as EngineUrl  # noqa: N811
from typing_extensions import override

import datacube
from datacube.index.exceptions import IndexSetupError
from datacube.model import Field
from datacube.utils import jsonify_document

from ...cfg import ODCEnvironment, psql_url_from_config
from . import _api, _core

_LIB_ID: str = "odc-" + str(datacube.__version__)

_LOG: logging.Logger = logging.getLogger(__name__)


class PostgresDb:
    """
    A thin database access api.

    It exists so that higher level modules are not tied to SQLAlchemy, connections or specifics of database-access.

    (and can be unit tested without any actual databases)

    Thread safe: the only shared state is the (thread-safe) sqlalchemy connection pool.

    But not multiprocess safe once the first connections are made! A connection must not be shared between multiple
    processes. You can call close() before forking if you know no other threads currently hold connections,
    or else use a separate instance of this class in each process.
    """

    driver_name = "postgres"  # Mostly to support parametrised tests

    def __init__(self, engine) -> None:
        # We don't recommend using this constructor directly as it may change.
        # Use static methods PostgresDb.create() or PostgresDb.from_config()
        self._engine = engine

    @classmethod
    def from_config(
        cls,
        config_env: ODCEnvironment,
        application_name: str | None = None,
        validate_connection: bool = True,
    ) -> "PostgresDb":
        app_name = cls._expand_app_name(application_name)

        return PostgresDb.create(
            config_env, application_name=app_name, validate=validate_connection
        )

    @classmethod
    def create(
        cls,
        config_env: ODCEnvironment,
        application_name: str | None = None,
        validate: bool = True,
    ) -> "PostgresDb":
        url = psql_url_from_config(config_env)
        engine = cls._create_engine(
            url,
            application_name,
            config_env.db_iam_authentication,
            config_env.db_iam_timeout if config_env.db_iam_authentication else 600,
            config_env.db_connection_timeout,
        )
        if validate:
            if not _core.database_exists(engine):
                raise IndexSetupError(
                    "\n\nNo DB schema exists. Have you run init?\n\t{init_command}".format(
                        init_command="datacube system init"
                    )
                )

            if not _core.schema_is_latest(engine):
                raise IndexSetupError(
                    "\n\nDB schema is out of date. "
                    "An administrator must run init:\n\t{init_command}".format(
                        init_command="datacube -v system init"
                    )
                )
        return PostgresDb(engine)

    @staticmethod
    def _create_engine(
        url: str | EngineUrl,
        application_name: str | None = None,
        iam_rds_auth: bool = False,
        iam_rds_timeout: float | int = 600,
        pool_timeout: int = 60,
    ) -> Engine:
        connect_args: dict[str, Any] = {"application_name": application_name}
        if str(url).startswith("postgresql+psycopg://"):
            try:
                from psycopg import ClientCursor
            except ImportError:
                raise IndexSetupError(
                    "psycopg is required to work with the database. "
                    "Please install the psycopg package manually."
                ) from None
            connect_args["cursor_factory"] = ClientCursor
        try:
            engine = create_engine(
                url,
                echo=False,
                echo_pool=False,
                # 'AUTOCOMMIT' here means READ-COMMITTED isolation level with autocommit on.
                # When a transaction is needed we will do an explicit begin/commit.
                isolation_level="AUTOCOMMIT",
                json_serializer=_to_json,
                # If a connection is idle for this many seconds, SQLAlchemy will renew it rather
                # than assuming it's still open. Allows servers to close idle connections without clients
                # getting errors.
                pool_recycle=pool_timeout,
                connect_args=connect_args,
            )
        except ModuleNotFoundError:
            raise IndexSetupError(
                "psycopg2 is required to work with the database. "
                "Please install the [postgres] or [test] dependencies, "
                "or manually install psycopg2 or psycopg2-binary."
            ) from None

        if iam_rds_auth:
            from datacube.utils.aws import obtain_new_iam_auth_token

            handle_dynamic_token_authentication(
                engine, obtain_new_iam_auth_token, timeout=iam_rds_timeout, url=url
            )

        return engine

    @property
    def url(self) -> EngineUrl:
        return self._engine.url

    def close(self) -> None:
        """
        Close any idle connections in the pool.

        This is good practice if you are keeping this object in scope
        but won't be using it for a while.

        Connections should not be shared between processes, so this should be called
        before forking if the same instance will be used.

        (connections are normally closed automatically when this object is
         garbage collected)
        """
        self._engine.dispose()

    @classmethod
    def _expand_app_name(cls, application_name: str | None) -> str:
        """
        >>> PostgresDb._expand_app_name(None)  # doctest: +ELLIPSIS
        'odc-...'
        >>> PostgresDb._expand_app_name("")  # doctest: +ELLIPSIS
        'odc-...'
        >>> PostgresDb._expand_app_name("cli")  # doctest: +ELLIPSIS
        'cli odc-...'
        >>> PostgresDb._expand_app_name("a b.c/d")
        'a-b-c-d odc-...'
        >>> PostgresDb._expand_app_name(5)
        Traceback (most recent call last):
        ...
        TypeError: Application name must be a string
        """
        full_name = _LIB_ID
        if application_name:
            if not isinstance(application_name, str):
                raise TypeError("Application name must be a string")

            full_name = re.sub("[^0-9a-zA-Z]+", "-", application_name) + " " + full_name

        if len(full_name) > 64:
            _LOG.warning(
                "Application name is too long: Truncating to %s chars",
                (64 - len(_LIB_ID) - 1),
            )
        return full_name[-64:]

    def init(self, with_permissions: bool = True) -> bool:
        """
        Init a new database (if not already set up).

        :return: If it was newly created.
        """
        is_new = _core.ensure_db(self._engine, with_permissions=with_permissions)
        if not is_new:
            _core.update_schema(self._engine)

        return is_new

    @contextmanager
    def _connect(self) -> Generator[_api.PostgresDbAPI]:
        """
        Borrow a connection from the pool.

        The name connect() is misleading: it will not create a new connection if one is already available in the pool.

        Callers should minimise the amount of time they hold onto their connections. If they're doing anything between
        calls to the DB (such as opening files, or waiting on user input), it's better to return the connection
        to the pool beforehand.

        The connection can raise errors if not following this advice ("server closed the connection unexpectedly"),
        as some servers will aggressively close idle connections (e.g. DEA's NCI servers). It also prevents the
        connection from being reused while borrowed.

        Low level context manager, use <index_resource>._db_connection instead
        """
        with self._engine.connect().execution_options(
            isolation_level="AUTOCOMMIT", preserve_rowcount=True
        ) as connection:
            try:
                yield _api.PostgresDbAPI(connection)
            finally:
                connection.close()

    def give_me_a_connection(self) -> Connection:
        return self._engine.connect()

    @classmethod
    def get_dataset_fields(
        cls, metadata_type_definition: Mapping[str, Any]
    ) -> Mapping[str, Field]:
        return _api.get_dataset_fields(metadata_type_definition)

    @override
    def __repr__(self) -> str:
        return f"PostgresDb<engine={self._engine!r}>"


def handle_dynamic_token_authentication(
    engine: Engine, new_token: Callable[..., str], timeout: float | int = 600, **kwargs
) -> None:
    last_token: list[str | None] = [None]
    last_token_time = [0.0]

    @event.listens_for(engine, "do_connect")
    def override_new_connection(dialect, conn_rec, cargs, cparams) -> None:
        # Handle IAM authentication
        # Importing here because the function `clock_gettime` is not available on Windows
        # which shouldn't be a problem, because boto3 auth is mostly used on AWS.
        from time import CLOCK_REALTIME, clock_gettime

        now = clock_gettime(CLOCK_REALTIME)
        if now - last_token_time[0] > timeout:
            last_token[0] = new_token(**kwargs)
            last_token_time[0] = now
        cparams["password"] = last_token[0]


def _to_json(o) -> str:
    # Postgres <=9.5 doesn't support NaN and Infinity
    fixedup = jsonify_document(o)
    return json.dumps(fixedup, default=_json_fallback)


def _json_fallback(obj: Any) -> None:
    """Fallback json serialiser."""
    raise TypeError(f"Type not serializable: {type(obj)}")
