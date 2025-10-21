# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Low level config path resolution, loading and multi-format parsing functions.

The default search path and default config also live here.
"""

from __future__ import annotations

import os
import warnings
from enum import Enum
from os import PathLike
from os.path import expanduser
from typing import TYPE_CHECKING

from datacube.cfg.exceptions import ConfigException
from datacube.cfg.utils import ConfigDict, SemaphoreCallback, smells_like_ini
from datacube.migration import ODC2DeprecationWarning

if TYPE_CHECKING:
    from datacube.cfg.api import GeneralisedPath

_DEFAULT_CONFIG_SEARCH_PATH: list[str] = [
    "datacube.conf",  # i.e. in the current working directory.
    expanduser("~/.datacube.conf"),  # i.e. in user's home directory.
    # Check if we are running under a Windows and use Windowsy default paths?
    "/etc/default/datacube.conf",  # Preferred location for global config file
    "/etc/datacube.conf",  # Legacy location for global config file
]

_DEFAULT_CONF = """
default:
   db_hostname: ''
   db_database: datacube
   index_driver: default
   db_connection_timeout: 60
"""


def find_config(
    paths_in: GeneralisedPath | None,
    default_cb: SemaphoreCallback | None = None,
) -> str:
    """
    Given a file system path, or a list of file system paths, return the contents of the first file
    in the list that can be read as a string.

    If "None" is passed in the default config search path is used:

        "datacube.conf"               (i.e. 'datacube.conf' in the current working directory.)
        "~/.datacube.conf"            (i.e. '.datacube.conf' in the user's home directory.)
        "/etc/default/datacube.conf"  (Preferred location for global config file)
        "/etc/datacube.conf"          (Legacy location for global config file)

    If a path or list of paths was passed in, AND no readable file could be found, a ConfigException is raised.
    If None was passed in, AND no readable file could be found, a default configuration text is returned.

    :param paths_in: A file system path, or a list of file system paths, or None.
    :param default_cb: A default semaphore callback object, or None.
    :return: The contents of the first readable file found.
    """
    using_default_paths: bool = False
    paths: list[str | PathLike] = []
    if paths_in is None:
        if os.environ.get("ODC_CONFIG_PATH"):
            paths.extend(os.environ["ODC_CONFIG_PATH"].split(":"))
        elif os.environ.get("DATACUBE_CONFIG_PATH"):
            warnings.warn(
                "Datacube config path being determined by legacy $DATACUBE_CONFIG_PATH environment variable. "
                "This environment variable is deprecated and the behaviour of it has changed somewhat since datacube "
                "1.8.x.   Please refer to the documentation for details and switch to $ODC_CONFIG_PATH",
                ODC2DeprecationWarning,
                stacklevel=2,
            )
            paths.extend(os.environ["DATACUBE_CONFIG_PATH"].split(":"))
        else:
            paths.extend(_DEFAULT_CONFIG_SEARCH_PATH)
            using_default_paths = True
    elif isinstance(paths_in, str | PathLike):
        paths.append(paths_in)
    else:
        paths.extend(paths_in)

    for path in paths:
        try:
            with open(path) as fp:
                return fp.read()
        except OSError:
            continue

    if using_default_paths:
        if default_cb is not None:
            default_cb()
        return _DEFAULT_CONF

    raise ConfigException("No configuration file found in the provided locations")


class CfgFormat(Enum):
    """
    An Enum class for config file formats.
    """

    AUTO = 0  # Format unspecified - autodetect
    INI = 1
    YAML = 2
    JSON = 2  # JSON is a subset of YAML


def parse_text(cfg_text: str, fmt: CfgFormat = CfgFormat.AUTO) -> ConfigDict:
    """
    Parse a string of text in INI, JSON or YAML format into a raw dictionary.

    Raises a ConfigException if the file cannot be parsed.

    :param cfg_text: Configuration string in INI, YAML or JSON format
    :param fmt: Whether to use the ini or yaml/json parser. Autodetects file format by default.
    :return: A raw config dictionary
    """
    raw_config = {}
    if fmt == fmt.INI or (fmt == fmt.AUTO and smells_like_ini(cfg_text)):
        # INI parsing
        import configparser

        try:
            ini_config = configparser.ConfigParser()
            ini_config.read_string(cfg_text)
            for section in ini_config.sections():
                sect = {}
                for key, value in ini_config.items(section):
                    sect[key] = value

                raw_config[section] = sect
        except configparser.Error as e:
            raise ConfigException(f"Invalid INI file: {e}") from None
    else:
        # YAML/JSON parsing
        import yaml

        try:
            raw_config = yaml.load(cfg_text, Loader=yaml.Loader)
        except yaml.parser.ParserError as e:
            raise ConfigException(f"Invalid YAML file:{e}") from None

    return raw_config
