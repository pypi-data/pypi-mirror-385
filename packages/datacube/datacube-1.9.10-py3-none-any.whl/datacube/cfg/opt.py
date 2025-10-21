# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0

import os
import warnings
from typing import TYPE_CHECKING, Any
from urllib.parse import quote_plus, urlparse

from typing_extensions import override

from ..migration import ODC2DeprecationWarning
from .exceptions import ConfigException
from .utils import check_valid_option

if TYPE_CHECKING:
    from .api import ODCEnvironment


_DEFAULT_IAM_TIMEOUT = 600
_DEFAULT_CONN_TIMEOUT = 60
_DEFAULT_HOSTNAME = "localhost"
_DEFAULT_DATABASE = "datacube"

try:
    import pwd

    _DEFAULT_DB_USER: str | None = pwd.getpwuid(os.geteuid()).pw_name
except (ImportError, KeyError):
    # No default on Windows and some other systems
    _DEFAULT_DB_USER = None


class ODCOptionHandler:
    """
    Base option handler class.  Sufficient for basic option with no validation.

    Smarter or more specialised option handlers extend this class.
    """

    # If overridden by subclass to False, then no environment variable overrides apply.
    allow_envvar_lookup: bool = True

    def __init__(
        self,
        name: str,
        env: "ODCEnvironment",
        default: Any = None,
        legacy_env_aliases=None,
    ) -> None:
        """
        :param name: Name of the option
        :param env: The ODCEnvironment the option is being read from
        :param default: The default value if not specified in the config file
        :param legacy_env_aliases:  Any legacy (pre odc-1.9) environment variable aliases for the option
        """
        check_valid_option(name)
        self.name: str = name
        self.env: ODCEnvironment = env
        self.default: Any = default
        if legacy_env_aliases:
            self.legacy_env_aliases = legacy_env_aliases
        else:
            self.legacy_env_aliases = []

    def validate_and_normalise(self, value: Any) -> Any:
        """
        Given a value read from a raw dictionary, return a normalised form.

        Subclasses should replace and call this implementation through super() for default handling.
        :param value: The value read from the raw dictionary (None if not present)
        :return: the normalised value.
        """
        if self.default is not None and value is None:
            return self.default
        return value

    def handle_dependent_options(self, value: Any) -> None:
        """
        Default implementation is no-op

        In subclasses:
        If the value of this option implies that dependent OptionHandlers should be run, they
        should be constructed here, and appended to self.env._option_handlers  (See examples below)

        :param value: The normalised value, as returned by validate_and_normalise
        :return: None
        """
        pass

    def get_val_from_environment(self) -> str | None:
        """
        Handle environment lookups.

        1. Returns None unless self.allow_envvar_lookups and self.env._allow_envvar_overrides are both set.
        2. Check canonical envvar name first.  E.g. option "bar" in environment "foo" -> $ODC_FOO_BAR
        3. Check canonical envvar name for any alias environments that point to this one.
        4. Check any legacy envvar names, and raise warnings if found.
        5. Check global envvar name, denoted by "all" instead of an environment name

        :return: First environment variable with non-empty value, or None if none found.
        """
        if self.allow_envvar_lookup and self.env._allow_envvar_overrides:
            canonical_name = f"odc_{self.env._name}_{self.name}".upper()
            for env_name in self.env.get_all_aliases():
                envvar_name = f"odc_{env_name}_{self.name}".upper()
                if val := os.environ.get(envvar_name):
                    return val
            for envvar_name in self.legacy_env_aliases:
                if val := os.environ.get(envvar_name):
                    warnings.warn(
                        f"Config being passed in by legacy environment variable ${envvar_name}. "
                        f"Please use ${canonical_name} instead.",
                        ODC2DeprecationWarning,
                        stacklevel=3,
                    )
                    return val
            global_name = f"odc_all_{self.name}".upper()
            if val := os.environ.get(global_name):
                return val
        return None


class AliasOptionHandler(ODCOptionHandler):
    """
    Alias option is handled at the environment level.
    """

    allow_envvar_lookup: bool = False

    @override
    def validate_and_normalise(self, value: Any) -> Any:
        if value is None:
            return None
        raise ConfigException(
            "Illegal attempt to directly access alias environment"
            " - use the ODCConfig object to resolve the environment"
        )


class IndexDriverOptionHandler(ODCOptionHandler):
    """
    Index Driver option.  Must be a valid index driver name, and index drivers may support further configuration.

    Example implementation for Postgresql/Postgis-based index drivers shown below.
    """

    @override
    def validate_and_normalise(self, value: Any) -> Any:
        value = super().validate_and_normalise(value)
        from datacube.drivers.indexes import index_drivers

        drivers = index_drivers()
        if value not in drivers:
            raise ConfigException(
                f"Unknown index driver: {value} - Try one of {','.join(sorted(drivers))}"
            )
        return value

    @override
    def handle_dependent_options(self, value: Any) -> None:
        # Get driver-specific config options
        from datacube.drivers.indexes import index_driver_by_name

        driver = index_driver_by_name(value)
        assert driver is not None
        for option in driver.get_config_option_handlers(self.env):
            self.env._option_handlers.append(option)


class IntOptionHandler(ODCOptionHandler):
    """
    Require an integer value, with optional min and max vals.
    """

    def __init__(
        self, *args, minval: int | None = None, maxval: int | None = None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.minval = minval
        self.maxval = maxval

    @override
    def validate_and_normalise(self, value: Any) -> Any:
        # Call super() to get handle default value
        value = super().validate_and_normalise(value)
        if value is None:
            return value
        try:
            ival = int(value)
        except ValueError:
            raise ConfigException(
                f"Config option {self.name} must be an integer"
            ) from None
        if self.minval is not None and ival < self.minval:
            raise ConfigException(
                f"Config option {self.name} must be at least {self.minval}"
            )
        if self.maxval is not None and ival > self.maxval:
            raise ConfigException(
                f"Config option {self.name} must not be greater than {self.maxval}"
            )
        return ival


class BoolOptionHandler(ODCOptionHandler):
    """
    Handle config option expecting a boolean value
    """

    @override
    def validate_and_normalise(self, value: Any) -> Any:
        value = super().validate_and_normalise(value)
        if isinstance(value, bool):
            return value
        return isinstance(value, str) and value.lower() == "true"


class IAMAuthenticationOptionHandler(ODCOptionHandler):
    """
    A simple boolean, compatible with the historic behaviour of the IAM Authentication on/off option.

    y/yes (case-insensitive): True
    Anything else: False

    If true, adds an IAM Timeout Option to the Environment.
    """

    @override
    def validate_and_normalise(self, value: Any) -> Any:
        if isinstance(value, bool):
            return value
        return isinstance(value, str) and value.lower() in ("y", "yes")

    @override
    def handle_dependent_options(self, value: Any) -> None:
        if value:
            self.env._option_handlers.append(
                IntOptionHandler(
                    "db_iam_timeout",
                    self.env,
                    default=_DEFAULT_IAM_TIMEOUT,
                    legacy_env_aliases=["DATACUBE_IAM_TIMEOUT"],
                    minval=1,
                )
            )


class PostgresURLOptionHandler(ODCOptionHandler):
    @override
    def validate_and_normalise(self, value: Any) -> Any:
        if not value:
            return None
        components = urlparse(value)
        # Check URL scheme is postgresql:
        if (
            components.scheme != "postgresql"
            and not value.startswith("postgresql+psycopg2://")
            and not value.startswith("postgresql+psycopg://")
        ):
            raise ConfigException("Database URL is not a postgresql connection URL")
        # Don't bother splitting up the url, we'd just have to put it back together again later
        return value

    @override
    def handle_dependent_options(self, value: Any) -> None:
        if value is None:
            handlers: tuple[ODCOptionHandler, ...] = (
                ODCOptionHandler(
                    "db_username",
                    self.env,
                    legacy_env_aliases=["DB_USERNAME"],
                    default=_DEFAULT_DB_USER,
                ),
                ODCOptionHandler(
                    "db_password", self.env, legacy_env_aliases=["DB_PASSWORD"]
                ),
                ODCOptionHandler(
                    "db_hostname",
                    self.env,
                    legacy_env_aliases=["DB_HOSTNAME"],
                    default=_DEFAULT_HOSTNAME,
                ),
                IntOptionHandler(
                    "db_port",
                    self.env,
                    default=5432,
                    legacy_env_aliases=["DB_PORT"],
                    minval=1,
                    maxval=65535,
                ),
                ODCOptionHandler(
                    "db_database",
                    self.env,
                    legacy_env_aliases=["DB_DATABASE"],
                    default=_DEFAULT_DATABASE,
                ),
            )
        else:
            # These pseudo-handlers extract the equivalent config from the url returned by this handler.
            handlers = (
                PostgresURLPartHandler(self, "username", "db_username", self.env),
                PostgresURLPartHandler(self, "password", "db_password", self.env),
                PostgresURLPartHandler(self, "hostname", "db_hostname", self.env),
                PostgresURLPartHandler(self, "port", "db_port", self.env),
                PostgresURLPartHandler(self, "path", "db_database", self.env),
            )

        for handler in handlers:
            self.env._option_handlers.append(handler)


class PostgresURLPartHandler(ODCOptionHandler):
    def __init__(
        self,
        urlhandler: PostgresURLOptionHandler,
        urlpart: str,
        name: str,
        env: "ODCEnvironment",
    ) -> None:
        self.urlhandler = urlhandler
        self.urlpart = urlpart
        super().__init__(name, env)

    @override
    def validate_and_normalise(self, value: Any) -> Any:
        url = self.env._normalised[self.urlhandler.name]
        purl = urlparse(url)
        part = getattr(purl, self.urlpart)
        if self.urlpart == "path" and part.startswith("/"):
            # Remove leading slash
            return str(part)[1:]
        return part

    @override
    def get_val_from_environment(self) -> str | None:
        # Never read from environment - take from URL, wherever it came from
        return None


def config_options_for_psql_driver(env: "ODCEnvironment") -> list[ODCOptionHandler]:
    """
    Config options for shared use by postgres-based index drivers
    (i.e. postgres and postgis drivers)
    """
    return [
        PostgresURLOptionHandler("db_url", env, legacy_env_aliases=["DATACUBE_DB_URL"]),
        IAMAuthenticationOptionHandler(
            "db_iam_authentication",
            env,
            legacy_env_aliases=["DATACUBE_IAM_AUTHENTICATION"],
        ),
        IntOptionHandler(
            "db_connection_timeout", env, default=_DEFAULT_CONN_TIMEOUT, minval=1
        ),
    ]


def psql_url_from_config(env: "ODCEnvironment"):
    if env.db_url:
        return env.db_url
    if not env.db_database:
        raise ConfigException(f"No database name supplied for environment {env._name}")
    url = f"postgresql+psycopg{'' if env.psycopg_version == 3 else '2'}://"
    if env.db_username:
        if env.db_password:
            escaped_password = quote_plus(env.db_password)
            url += f"{env.db_username}:{escaped_password}@"
        else:
            url += f"{env.db_username}@"
    url += f"{env.db_hostname}:{env.db_port}/{env.db_database}"
    return url
