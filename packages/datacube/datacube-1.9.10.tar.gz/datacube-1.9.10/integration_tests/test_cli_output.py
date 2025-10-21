# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
import pytest


def test_cli_product_subcommand(index_empty, clirunner, dataset_add_configs) -> None:
    runner = clirunner(["product", "update"], verbose_flag=False, expect_success=False)
    assert "Usage:  [OPTIONS] [FILES]" in runner.output
    assert "Update existing products." in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["product", "update", dataset_add_configs.empty_file],
        verbose_flag=False,
        expect_success=False,
    )
    assert "All files are empty, exit" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["product", "add"], verbose_flag=False, expect_success=False)
    assert "Usage:  [OPTIONS] [FILES]" in runner.output
    assert "Add or update products in" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["product", "list"], verbose_flag=False)
    assert "Usage:  [OPTIONS] [FILES]" not in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["product", "show", "ga_ls8c_ard_3"], verbose_flag=False, expect_success=False
    )
    assert "No products" not in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["product", "add", dataset_add_configs.empty_file],
        verbose_flag=False,
        expect_success=False,
    )
    assert "All files are empty, exit" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["product", "delete"], verbose_flag=False, expect_success=False)
    assert "Usage:  [OPTIONS] [PRODUCT_NAMES]" in runner.output
    assert "Delete products" in runner.output

    runner = clirunner(
        ["product", "delete", "ga_ls8c_ard_3"], verbose_flag=False, expect_success=False
    )
    assert '"ga_ls8c_ard_3" is not a valid Product name' in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"


def test_cli_metadata_subcommand(index_empty, clirunner, dataset_add_configs) -> None:
    runner = clirunner(["metadata", "update"], verbose_flag=False, expect_success=False)
    assert "Usage:  [OPTIONS] [FILES]" in runner.output
    assert "Update existing metadata types." in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["metadata", "update", dataset_add_configs.empty_file],
        verbose_flag=False,
        expect_success=False,
    )
    assert "All files are empty, exit" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["metadata", "add"], verbose_flag=False, expect_success=False)
    assert "Usage:  [OPTIONS] [FILES]" in runner.output
    assert "Add or update metadata types in" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["metadata", "add", dataset_add_configs.empty_file],
        verbose_flag=False,
        expect_success=False,
    )
    assert "All files are empty, exit" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_cli_dataset_subcommand(
    index,
    clirunner,
    extended_eo3_metadata_type,
    ls8_eo3_product,
    wo_eo3_product,
    africa_s2_eo3_product,
    eo3_dataset_paths,
) -> None:
    # Tests with no datasets in db
    runner = clirunner(["dataset", "add"], verbose_flag=False, expect_success=False)
    assert (
        "Indexing datasets  [####################################]  100%"
        not in runner.output
    )
    assert "Usage:  [OPTIONS] [DATASET_PATHS]" in runner.output
    assert "Add datasets" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["dataset", "update"], verbose_flag=False, expect_success=False)
    assert "0 successful, 0 failed" not in runner.output
    assert "Usage:  [OPTIONS] [DATASET_PATHS]" in runner.output
    assert "Update datasets" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["dataset", "info"], verbose_flag=False, expect_success=False)
    assert "Usage:  [OPTIONS] [IDS]" in runner.output
    assert "Display dataset information" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "uri-search"], verbose_flag=False, expect_success=False
    )
    assert "Usage:  [OPTIONS] [PATHS]" in runner.output
    assert "Search by dataset locations" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    # Insert datasets
    for path in eo3_dataset_paths:
        clirunner(["dataset", "add", "--ignore-lineage", path])

    runner = clirunner(
        ["dataset", "find-duplicates"], verbose_flag=False, expect_success=False
    )
    assert "Error: must provide field names to match on" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "find-duplicates", "region_code", "fake_field"],
        verbose_flag=False,
        expect_success=False,
    )
    assert (
        "Error: no products found with fields region_code, fake_field" in runner.output
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        [
            "dataset",
            "find-duplicates",
            "region_code",
            "landsat_scene_id",
            "-p",
            "ga_ls8c_ard_3",
            "-p",
            "ga_ls_wo_3",
        ],
        verbose_flag=False,
        expect_success=False,
    )
    assert (
        "Error: specified products ga_ls_wo_3 do not contain all required fields"
        in runner.output
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "find-duplicates", "region_code", "uri"], verbose_flag=False
    )
    assert "No potential duplicates found." in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "find-duplicates", "region_code", "dataset_maturity"],
        verbose_flag=False,
    )
    assert "No potential duplicates found." not in runner.output
    assert "region_code: 090086\ndataset_maturity: final" in runner.output
    assert "region_code: '101077'\ndataset_maturity: final" in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "count", "--count-only", "ga_ls8c_ard_3", "ga_ls_wo_3"],
        verbose_flag=False,
    )
    assert runner.output == "5\n"
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "count", "ga_ls8c_ard_3", "ga_ls_wo_3"], verbose_flag=False
    )
    assert "product: ga_ls8c_ard_3\ncount: 4" in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "count", "ga_ls8c_ard_3", "--query", 'region_code="090086"'],
        verbose_flag=False,
    )
    assert "count: 2" in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "count", "--count-only", "--period", "1 month", "ga_ls8c_ard_3"],
        verbose_flag=False,
        expect_success=False,
    )
    assert (
        "Error: cannot return total count when requesting time slicing" in runner.output
    )
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        [
            "dataset",
            "count",
            "--period",
            "1 year",
            "--query",
            "time in [2013-01-01, 2017-01-01]",
            "ga_ls8c_ard_3",
        ],
        verbose_flag=False,
    )
    assert "time: '2013-01-01'\ncount: 2" in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    clirunner(
        ["dataset", "archive", "c21648b1-a6fa-4de0-9dc3-9c445d8b295a"],
        verbose_flag=False,
    )
    runner = clirunner(["dataset", "count", "ga_ls8c_ard_3"], verbose_flag=False)
    assert "count: 3" in runner.output
    runner = clirunner(
        ["dataset", "count", "--status", "all", "ga_ls8c_ard_3"], verbose_flag=False
    )
    assert "count: 4" in runner.output
    runner = clirunner(
        ["dataset", "count", "--status", "archived", "ga_ls8c_ard_3"],
        verbose_flag=False,
    )
    assert "count: 1" in runner.output

    runner = clirunner(
        ["dataset", "search", "foo"], verbose_flag=False, expect_success=False
    )
    assert "Invalid expression" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(
        ["dataset", "search", "product=ga_ls8c_ard_3", 'region_code="090086"'],
        verbose_flag=False,
    )
    assert "id: 4a30d008-4e82-4d67-99af-28bc1629f766" in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["dataset", "archive"], verbose_flag=False, expect_success=False)
    assert "Completed dataset archival." not in runner.output
    assert "Usage:  [OPTIONS] [IDS]" in runner.output
    assert "Archive datasets" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["dataset", "archive", "--all"], verbose_flag=False)
    assert "Archiving dataset:" in runner.output
    assert "Completed dataset archival." in runner.output
    assert "Usage:  [OPTIONS] [IDS]" not in runner.output
    assert "Archive datasets" not in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["dataset", "restore"], verbose_flag=False, expect_success=False)
    assert "Usage:  [OPTIONS] [IDS]" in runner.output
    assert "Restore datasets" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["dataset", "restore", "--all"], verbose_flag=False)
    assert "restoring" in runner.output
    assert "Usage:  [OPTIONS] [IDS]" not in runner.output
    assert "Restore datasets" not in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"

    runner = clirunner(["dataset", "purge"], verbose_flag=False, expect_success=False)
    assert "Completed dataset purge." not in runner.output
    assert "Usage:  [OPTIONS] [IDS]" in runner.output
    assert "Purge archived datasets" in runner.output
    assert runner.exit_code == 1, f"Output: {runner.output}"

    runner = clirunner(["dataset", "purge", "--all"], verbose_flag=False)
    assert "Completed dataset purge." in runner.output
    assert "Usage:  [OPTIONS] [IDS]" not in runner.output
    assert runner.exit_code == 0, f"Output: {runner.output}"


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_read_and_update_metadata_product_dataset_command(
    index,
    clirunner,
    ext_eo3_mdt_path,
    eo3_product_paths,
    eo3_dataset_paths,
    eo3_dataset_update_path,
) -> None:
    clirunner(["metadata", "add", ext_eo3_mdt_path])
    rerun_add = clirunner(["metadata", "add", ext_eo3_mdt_path])
    assert "WARNING Metadata Type" in rerun_add.output
    assert "is already in the database" in rerun_add.output

    update = clirunner(["metadata", "update", ext_eo3_mdt_path])
    assert "WARNING No changes detected for metadata type" in update.output

    for prod_path in eo3_product_paths:
        clirunner(["product", "add", prod_path])
        rerun_add = clirunner(["product", "add", prod_path])
        assert "WARNING Product" in rerun_add.output
        assert "is already in the database" in rerun_add.output

        update = clirunner(["product", "update", prod_path])
        assert "WARNING No changes detected for product" in update.output

    # Update before add
    for ds_path in eo3_dataset_paths:
        update = clirunner(["dataset", "update", ds_path])
        assert "No such dataset in the database" in update.output
        assert "Failure while processing" in update.output

        clirunner(["dataset", "add", "--ignore-lineage", ds_path])
        rerun_add = clirunner(["dataset", "add", "--ignore-lineage", ds_path])
        assert "WARNING Dataset" in rerun_add.output
        assert "is already in the database" in rerun_add.output

    update = clirunner(["dataset", "update", eo3_dataset_update_path])
    assert "Unsafe changes in" in update.output
    assert "0 successful, 1 failed" in update.output

    update = clirunner(
        [
            "dataset",
            "update",
            "--allow-any",
            "properties.datetime",
            eo3_dataset_update_path,
        ]
    )
    assert "1 successful, 0 failed" in update.output
