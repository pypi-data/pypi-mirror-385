# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from datacube.index import Index


@pytest.mark.parametrize("datacube_env_name", ("postgis", "postgis3"))
def test_cli_spatial_indexes(index: Index, clirunner) -> None:
    runner = clirunner(["spindex", "list"], verbose_flag=False)
    assert "EPSG:4326" in runner.output
    assert "EPSG:3577" not in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["spindex", "create", "epsg:3577"], verbose_flag=False)
    assert runner.exit_code == 0, f"Output: {runner.output}"

    # Double creation succeeds silently
    runner = clirunner(["spindex", "create", "3577"], verbose_flag=False)
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["spindex", "update", "3577"], verbose_flag=False)
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["spindex", "update", "EPSG:3857"], verbose_flag=False, expect_success=False
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["spindex", "list"], verbose_flag=False)
    assert "EPSG:4326" in runner.output
    assert "EPSG:3577" in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["spindex", "drop", "3577"], verbose_flag=False, expect_success=False
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"
    runner = clirunner(["spindex", "drop", "--force", "3577"], verbose_flag=False)
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["spindex", "list"], verbose_flag=False)
    assert "EPSG:4326" in runner.output
    assert "EPSG:3577" not in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    # Drop non-existent spindex ignored.
    runner = clirunner(["spindex", "drop", "--force", "3577"], verbose_flag=False)
    assert runner.exit_code == 0, f"Output: {runner.output}"


@pytest.mark.parametrize("datacube_env_name", ("postgis", "postgis3"))
def test_cli_spatial_index_create_and_update(index: Index, clirunner) -> None:
    runner = clirunner(["spindex", "list"], verbose_flag=False)
    assert "EPSG:4326" in runner.output
    assert "EPSG:3577" not in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["spindex", "create", "--update", "3577"], verbose_flag=False)
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["spindex", "list"], verbose_flag=False)
    assert "EPSG:4326" in runner.output
    assert "EPSG:3577" in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["spindex", "drop", "3577"], verbose_flag=False, expect_success=False
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"
    runner = clirunner(["spindex", "drop", "--force", "3577"], verbose_flag=False)
    assert runner.exit_code == 0, f"Output: {runner.output}"


@pytest.mark.parametrize("datacube_env_name", ("datacube", "datacube3"))
def test_cli_spatial_indexes_on_non_supporting_index(index: Index, clirunner) -> None:
    runner = clirunner(["spindex", "list"], verbose_flag=False, expect_success=False)
    assert "does not support spatial indexes" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["spindex", "create", "3577"], verbose_flag=False, expect_success=False
    )
    assert "does not support spatial indexes" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["spindex", "update", "3577"], verbose_flag=False, expect_success=False
    )
    assert "does not support spatial indexes" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["spindex", "drop", "3577"], verbose_flag=False, expect_success=False
    )
    assert "does not support spatial indexes" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"


@pytest.mark.parametrize("datacube_env_name", ("postgis", "postgis3"))
def test_cli_spatial_indexes_no_srids(index: Index, clirunner) -> None:
    runner = clirunner(["spindex", "create"], verbose_flag=False, expect_success=False)
    assert "Must supply at least one CRS" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["spindex", "update"], verbose_flag=False, expect_success=False)
    assert "Must supply at least one CRS" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["spindex", "drop"], verbose_flag=False, expect_success=False)
    assert "Must supply at least one CRS" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"


@pytest.mark.parametrize("datacube_env_name", ("postgis", "postgis3"))
def test_cli_spatial_indexes_bad_srid(index: Index, clirunner) -> None:
    runner = clirunner(
        ["spindex", "create", "1"], verbose_flag=False, expect_success=False
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"
    runner = clirunner(
        ["spindex", "create", "--update", "1"], verbose_flag=False, expect_success=False
    )
    assert "Skipping update" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"
    runner = clirunner(
        ["spindex", "update", "1"], verbose_flag=False, expect_success=False
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"
    runner = clirunner(
        ["spindex", "drop", "1"], verbose_flag=False, expect_success=False
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"
