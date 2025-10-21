# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
import csv
import logging
import sys
from collections import OrderedDict
from collections.abc import Iterable, Sequence

import click
import yaml
import yaml.resolver

from datacube.cfg import ODCEnvironment
from datacube.index import Index
from datacube.index.abstract import AbstractIndex
from datacube.ui import click as ui
from datacube.ui.click import cli
from datacube.utils import gen_password
from datacube.utils.serialise import SafeDatacubeDumper

_LOG: logging.Logger = logging.getLogger("datacube-user")
USER_ROLES = ("user", "manage", "admin")


@cli.group(name="user", help="User management commands")
def user_cmd() -> None:
    pass


def build_user_list(index: Index) -> Sequence[OrderedDict[str, str | None]]:
    lstdct = []
    for role, user, description in index.users.list_users():
        info = OrderedDict(
            (("role", role), ("user", user), ("description", description))
        )
        lstdct.append(info)
    return lstdct


def _write_csv(index: Iterable[dict[str, str | None]]) -> None:
    writer = csv.DictWriter(
        sys.stdout, ["role", "user", "description"], extrasaction="ignore"
    )
    writer.writeheader()

    def add_first_role(row: dict[str, str | None]) -> dict[str, str | None]:
        roles_ = row["role"]
        row["role"] = roles_ if roles_ else None
        return row

    writer.writerows(add_first_role(row) for row in index)


def _write_yaml(index: Iterable[dict[str, str | None]]) -> str | bytes | None:
    """
    Dump yaml data with support for OrderedDicts.

    Allows for better human-readability of output: such as dataset ID field first, sources last.

    (Ordered dicts are output identically to normal yaml dicts: their order is purely for readability)
    """
    return yaml.dump_all(
        index, sys.stdout, SafeDatacubeDumper, default_flow_style=False, indent=4
    )


_OUTPUT_WRITERS = {
    "csv": _write_csv,
    "yaml": _write_yaml,
}


@user_cmd.command("list")
@click.option(
    "-f",
    help="Output format",
    type=click.Choice(list(_OUTPUT_WRITERS)),
    default="yaml",
    show_default=True,
)
@ui.pass_index()
def list_users(index: Index, f: str) -> None:
    """
    List users
    """
    _OUTPUT_WRITERS[f](build_user_list(index))


@user_cmd.command("grant")
@click.argument("role", type=click.Choice(USER_ROLES), nargs=1)
@click.argument("users", nargs=-1)
@ui.pass_index()
def grant(index: Index, role: str, users: Iterable[str]) -> None:
    """
    Grant a role to users
    """
    index.users.grant_role(role, *users)


@user_cmd.command("create")
@click.argument("role", type=click.Choice(USER_ROLES), nargs=1)
@click.argument("user", nargs=1)
@click.option("--description")
@ui.pass_index()
@ui.pass_config
def create_user(
    cfg_env: ODCEnvironment,
    index: AbstractIndex,
    role: str,
    user: str,
    description: str,
) -> None:
    """
    Create a User
    """
    password = gen_password(12)
    index.users.create_user(user, password, role, description=description)

    click.echo(
        "{host}:{port}:*:{username}:{password}".format(
            host=index.url_parts.hostname or "localhost",
            port=index.url_parts.port,
            username=user,
            password=password,
        )
    )


@user_cmd.command("delete")
@click.argument("users", nargs=-1)
@ui.pass_index()
@ui.pass_config
def delete_user(config, index: Index, users: str) -> None:
    """
    Delete a User
    """
    index.users.delete_user(*users)
