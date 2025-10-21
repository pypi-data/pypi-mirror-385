# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Module
"""

import logging
import random
from pathlib import Path

import pytest

EXAMPLE_DATASET_TYPE_DOCS = list(
    map(
        str,
        Path(__file__)
        .parent.parent.joinpath("docs", "source", "config_samples", "dataset_types")
        .glob("**/*.yaml"),
    )
)
assert len(EXAMPLE_DATASET_TYPE_DOCS) > 0

# Documents that shouldn't be accepted as mapping docs.
INVALID_MAPPING_DOCS = list(
    map(str, Path(__file__).parent.parent.joinpath("docs").glob("*"))
)
assert len(INVALID_MAPPING_DOCS) > 0


def _dataset_type_count(index):
    with index._active_connection() as connection:
        return len(list(connection.get_all_products()))


def test_add_example_dataset_types(
    clirunner, index, default_metadata_type, eo3_product_paths, ext_eo3_mdt_path
) -> None:
    """
    Add example mapping docs, to ensure they're valid and up-to-date.

    We add them all to a single database to check for things like duplicate ids.
    """
    existing_mappings = _dataset_type_count(index)

    if index.supports_legacy:
        # Legacy EO test examples
        print(f"{existing_mappings} mappings")
        for mapping_path in EXAMPLE_DATASET_TYPE_DOCS:
            print(f"Adding mapping {mapping_path}")

            result = clirunner(["-v", "product", "add", mapping_path])
            assert result.exit_code == 0, f"Output: {result.output}"

            mappings_count = _dataset_type_count(index)
            assert mappings_count > existing_mappings, (
                "Mapping document was not added: " + str(mapping_path)
            )
            existing_mappings = mappings_count

        result = clirunner(["-v", "metadata", "show", "-f", "json", "eo"])
        assert result.exit_code == 0, f"Output: {result.output}"

    # EO3 test examples
    result = clirunner(["-v", "metadata", "add", ext_eo3_mdt_path])
    assert result.exit_code == 0, f"Output: {result.output}"

    for path in eo3_product_paths:
        result = clirunner(["-v", "product", "add", path])
        assert result.exit_code == 0, f"Output: {result.output}"

        mappings_count = _dataset_type_count(index)
        assert mappings_count > existing_mappings, (
            "Mapping document was not added: " + str(path)
        )
        existing_mappings = mappings_count

    result = clirunner(["-v", "metadata", "show", "-f", "json", "eo3"])
    assert result.exit_code == 0, f"Output: {result.output}"

    result = clirunner(["-v", "metadata", "list"])
    assert result.exit_code == 0, f"Output: {result.output}"

    result = clirunner(["-v", "metadata", "show"])
    assert result.exit_code == 0, f"Output: {result.output}"

    result = clirunner(["-v", "product", "list"])
    assert result.exit_code == 0, f"Output: {result.output}"

    expect_result = 0 if existing_mappings > 0 else 1
    result = clirunner(["-v", "product", "show"], expect_success=(expect_result == 0))
    assert result.exit_code == expect_result

    if existing_mappings > 1:
        result = clirunner(
            ["-v", "product", "show", "-f", "json"], expect_success=False
        )
        assert result.exit_code == 1, f"Output: {result.output}"

        result = clirunner(["-v", "product", "show", "-f", "json", "ga_ls8c_ard_3"])
        assert result.exit_code == 0, f"Output: {result.output}"

        result = clirunner(["-v", "product", "show", "-f", "yaml", "ga_ls8c_ard_3"])
        assert result.exit_code == 0, f"Output: {result.output}"


def test_error_returned_on_invalid(clirunner, index) -> None:
    assert _dataset_type_count(index) == 0

    for mapping_path in INVALID_MAPPING_DOCS:
        result = clirunner(
            ["product", "add", mapping_path],
            # TODO: Make this false when the cli is updated to print errors (rather than uncaught exceptions).
            catch_exceptions=True,
            expect_success=False,
        )
        assert result.exit_code != 0, "Success return code for invalid document."
        assert _dataset_type_count(index) == 0, "Invalid document was added to DB"


def test_config_check(clirunner, index, cfg_env) -> None:
    # This is not a very thorough check, we just check to see that
    # it prints something vaguely related and does not error-out.
    result = clirunner(["system", "check"])

    assert cfg_env["db_hostname"] in result.output
    assert cfg_env["db_username"] in result.output
    assert str(cfg_env["skip_broken_datasets"]) in result.output
    assert str(cfg_env["dc_load_limit"]) in result.output


def test_list_users_does_not_fail(clirunner, cfg_env, index) -> None:
    # We don't want to make assumptions about available users during test runs.
    # (They are host-global, not specific to the database)
    # So we're just checking that it doesn't fail (and the SQL etc is well formed)
    result = clirunner(["user", "list"])
    assert result.exit_code == 0, f"Output: {result.output}"


def test_db_init_noop(clirunner, cfg_env, ls8_eo3_product) -> None:
    # Run on an existing database.
    result = clirunner(["-v", "system", "init"])
    assert "Updated." in result.output
    # It should not rebuild indexes by default
    assert f"Dropping index: dix_{ls8_eo3_product.name}" not in result.output

    result = clirunner(["metadata", "list"])
    assert "eo3 " in result.output


def test_db_init_rebuild(clirunner, cfg_env, ls8_eo3_product) -> None:
    if cfg_env._name in ("datacube", "datacube3"):
        from datacube.drivers.postgres import _dynamic
        from datacube.drivers.postgres.sql import SCHEMA_NAME

        # Set field creation logging to debug since we assert on debug output.
        _dynamic._LOG.setLevel(logging.DEBUG)
    # Run on an existing database.
    result = clirunner(["-v", "-E", cfg_env._name, "system", "init", "--rebuild"])
    assert "Updated." in result.output
    # These debug log messages are not present in the Postgis driver.
    if cfg_env._name in ("datacube", "datacube3"):
        # It should have recreated views and indexes.
        assert f"Dropping index: dix_{ls8_eo3_product.name}" in result.output
        assert f"Creating index: dix_{ls8_eo3_product.name}" in result.output
        assert (
            f"Dropping view: {SCHEMA_NAME}.dv_{ls8_eo3_product.name}_dataset"
            in result.output
        )
        assert (
            f"Creating view: {SCHEMA_NAME}.dv_{ls8_eo3_product.name}_dataset"
            in result.output
        )


def test_db_init(clirunner, index) -> None:
    if index._db.driver_name == "postgis":
        from datacube.drivers.postgis._core import drop_schema, has_schema
    else:
        from datacube.drivers.postgres._core import drop_schema, has_schema

    with index._db._connect() as connection:
        drop_schema(connection._connection)

        assert not has_schema(index._db._engine)

    # Run on an empty database.
    if index._db.driver_name == "postgis":
        result = clirunner(["-E", "postgis", "system", "init"])
    else:
        result = clirunner(["system", "init"])

    assert "Created." in result.output

    with index._db._connect() as connection:
        assert has_schema(index._db._engine)


def test_add_no_such_product(clirunner, index) -> None:
    result = clirunner(
        ["dataset", "add", "--dtype", "no_such_product", "/tmp"], expect_success=False
    )
    assert result.exit_code != 0, f"Output: {result.output}"
    assert "DEPRECATED option detected" in result.output
    assert "ERROR Supplied product name" in result.output


@pytest.fixture(
    params=[
        ('test_"user"_{n}', None),
        ('test_"user"_{n}', "Test user description"),
        # Test that names are escaped
        ('test_user_"invalid+_chars_{n}', None),
        ("test_user_invalid_desc_{n}", "Invalid \"' chars in description"),
    ]
)
def example_user(clirunner, index, request):
    username, description = request.param

    username = username.format(n=random.randint(111111, 999999))

    # test_roles = (user_name for role_name, user_name, desc in roles if user_name.startswith('test_'))
    with index._db._connect() as connection:
        users = (user_name for role_name, user_name, desc in connection.list_users())
        if username in users:
            connection.drop_users([username])

    # No user exists.
    assert_no_user(clirunner, username)

    yield username, description

    with index._db._connect() as connection:
        users = (user_name for role_name, user_name, desc in connection.list_users())
        if username in users:
            connection.drop_users([username])


def test_user_creation(clirunner, example_user) -> None:
    """
    Add a user, grant them, delete them.

    This test requires role creation privileges on the PostgreSQL instance used for testing...
    """
    username, user_description = example_user

    # Create them
    args = ["user", "create", "user", username]
    if user_description:
        args.extend(["--description", user_description])
    clirunner(args)
    assert_user_with_role(clirunner, "ingest", username)

    # Grant them 'manage' permission
    clirunner(["user", "grant", "manage", username])
    assert_user_with_role(clirunner, "manage", username)

    # Delete them
    clirunner(["user", "delete", username])
    assert_no_user(clirunner, username)


def assert_user_with_role(clirunner, role, user_name: str) -> None:
    result = clirunner(["user", "list"])
    assert "{}{}".format("user: ", user_name) in result.output


def assert_no_user(clirunner, username: str) -> None:
    result = clirunner(["user", "list"])
    assert username not in result.output
