# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Access methods for indexing datasets & products.
"""

import logging

from datacube.cfg import ODCConfig, ODCEnvironment

from .abstract import AbstractIndex as Index

_LOG: logging.Logger = logging.getLogger(__name__)


def index_connect(
    config_env: ODCEnvironment | None = None,
    application_name: str | None = None,
    validate_connection: bool = True,
) -> Index:
    """
    Create a Data Cube Index (as per config)

    It contains all the required connection parameters, but doesn't actually
    check that the server is available.

    :param config_env: Config environment to use. (optional)
    :param application_name: A short, alphanumeric name to identify this application.
    :param validate_connection: Validate database connection and schema immediately
    :raises datacube.index.Exceptions.IndexSetupError:
    """
    from datacube.drivers import index_driver_by_name

    if config_env is None:
        config_env = ODCConfig()[None]

    driver_name = config_env.index_driver
    index_driver = index_driver_by_name(driver_name)
    # No need to check for missing index driver - already checked during config parsing.
    assert index_driver is not None
    return index_driver.connect_to_index(
        config_env,
        application_name=application_name,
        validate_connection=validate_connection,
    )
