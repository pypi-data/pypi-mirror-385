# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Common methods for index integration tests.
"""

import itertools
import os
import warnings
from collections.abc import Generator, Iterable, Sequence
from copy import copy, deepcopy
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from uuid import UUID, uuid4

import pytest
import yaml
from antimeridian import FixWindingWarning
from click.testing import CliRunner, Result
from hypothesis import HealthCheck, settings
from sqlalchemy import text

import datacube.scripts.cli_app
import datacube.utils
from datacube import Datacube
from datacube.cfg import ODCConfig, ODCEnvironment, psql_url_from_config
from datacube.drivers.postgis import PostGisDb
from datacube.drivers.postgis import _core as pgis_core
from datacube.drivers.postgres import PostgresDb
from datacube.drivers.postgres import _core as pgres_core
from datacube.index import Index, index_connect
from datacube.index.abstract import AbstractIndex, default_metadata_type_docs
from datacube.model import Dataset, LineageDirection, LineageTree, MetadataType, Product
from datacube.utils import SimpleDocNav, read_documents
from integration_tests.utils import (
    GEOTIFF,
    _make_geotiffs,
    _make_ls5_scene_datasets,
    load_test_products,
    load_yaml_file,
)

_SINGLE_RUN_CONFIG_TEMPLATE = """

"""
INTEGRATION_TESTS_DIR = Path(__file__).parent

_EXAMPLE_LS5_NBAR_DATASET_FILE = INTEGRATION_TESTS_DIR / "example-ls5-nbar.yaml"

#: Number of time slices to create in sample data
NUM_TIME_SLICES = 3

PROJECT_ROOT = Path(__file__).parents[1]
CONFIG_SAMPLES = PROJECT_ROOT / "docs" / "source" / "config_samples"

CONFIG_FILE_PATHS = [
    os.path.expanduser("~/.datacube_integration.conf"),
    str(INTEGRATION_TESTS_DIR / "integration.conf"),
]

# Configure Hypothesis to allow slower tests, because we're testing datasets
# and disk IO rather than scalar values in memory.  Ask @Zac-HD for details.
settings.register_profile(
    "opendatacube",
    deadline=5000,
    max_examples=10,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("opendatacube")

EO3_TESTDIR = INTEGRATION_TESTS_DIR / "data" / "eo3"


def get_eo3_test_data_doc(path: str | Path) -> dict:
    from datacube.utils import read_documents

    for _, doc in read_documents(EO3_TESTDIR / path):
        return doc
    pytest.fail(f"No document found for {EO3_TESTDIR / path}", False)


@pytest.fixture
def ext_eo3_mdt_path() -> str:
    return str(EO3_TESTDIR / "eo3_landsat_ard.odc-type.yaml")


@pytest.fixture
def eo3_product_paths() -> list[str]:
    return [
        str(EO3_TESTDIR / "ard_ls8.odc-product.yaml"),
        str(EO3_TESTDIR / "ga_ls_wo_3.odc-product.yaml"),
        str(EO3_TESTDIR / "s2_africa_product.yaml"),
    ]


@pytest.fixture
def eo3_dataset_paths() -> list[str]:
    return [
        str(EO3_TESTDIR / "ls8_dataset.yaml"),
        str(EO3_TESTDIR / "ls8_dataset2.yaml"),
        str(EO3_TESTDIR / "ls8_dataset3.yaml"),
        str(EO3_TESTDIR / "ls8_dataset4.yaml"),
        str(EO3_TESTDIR / "wo_dataset.yaml"),
        str(EO3_TESTDIR / "s2_africa_dataset.yaml"),
        str(EO3_TESTDIR / "s2_africa_dataset2.yaml"),
    ]


@pytest.fixture
def eo3_dataset_update_path() -> str:
    return str(EO3_TESTDIR / "ls8_dataset_update.yaml")


@pytest.fixture
def dataset_with_lineage_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("wo_ds_with_lineage.odc-metadata.yaml"),
        "s3://dea-public-data/derivative/ga_ls_wo_3/1-6-0/090/086/2016/05/12/"
        "ga_ls_wo_3_090086_2016-05-12_final.stac-item.json",
    )


@pytest.fixture
def eo3_ls8_dataset_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("ls8_dataset.yaml"),
        "s3://dea-public-data/baseline/ga_ls8c_ard_3/090/086/2016/05/12/"
        "ga_ls8c_ard_3-0-0_090086_2016-05-12_final.stac-item.json",
    )


@pytest.fixture
def eo3_ls8_dataset2_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("ls8_dataset2.yaml"),
        "s3://dea-public-data/baseline/ga_ls8c_ard_3/090/086/2016/05/28/"
        "ga_ls8c_ard_3-0-0_090086_2016-05-28_final.stac-item.json",
    )


@pytest.fixture
def eo3_ls8_dataset3_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("ls8_dataset3.yaml"),
        "s3://dea-public-data/baseline/ga_ls8c_ard_3/101/077/2013/04/04/"
        "ga_ls8c_ard_3-0-0_101077_2013-04-04_final.stac-item.json",
    )


@pytest.fixture
def eo3_ls8_dataset4_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("ls8_dataset4.yaml"),
        "s3://dea-public-data/baseline/ga_ls8c_ard_3/101/077/2013/07/21/"
        "ga_ls8c_ard_3-0-0_101077_2013-07-21_final.stac-item.json",
    )


@pytest.fixture
def eo3_wo_dataset_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("wo_dataset.yaml"),
        "s3://dea-public-data/derivative/ga_ls_wo_3/1-6-0/090/086/2016/05/12/"
        "ga_ls_wo_3_090086_2016-05-12_final.stac-item.json",
    )


@pytest.fixture
def eo3_africa_dataset_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("s2_africa_dataset.yaml"),
        "s3://deafrica-sentinel-2/sentinel-s2-l2a-cogs/37/M/CQ/"
        "2022/8/S2A_37MCQ_20220808_0_L2A/S2A_37MCQ_20220808_0_L2A.json",
    )


@pytest.fixture
def eo3_africa_dataset2_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("s2_africa_dataset2.yaml"),
        "s3://deafrica-sentinel-2/sentinel-s2-l2a-cogs/39/M/XR/"
        "2020/9/S2A_39MXR_20200909_0_L2A/S2A_39MXR_20200909_0_L2A.json",
    )


@pytest.fixture
def s1_dataset_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("ga_s1_vertical_dualpol.yaml"),
        "https://deant-data-public-dev.s3.ap-southeast-2.amazonaws.com/"
        "experimental_for_inland_water_team/s1_rtc_c1/t045_095837_iw1/2020/1/10/metadata.json",
    )


@pytest.fixture
def datasets_with_unembedded_lineage_doc() -> list[tuple[dict, str]]:
    return [
        (
            get_eo3_test_data_doc("ls8_dataset.yaml"),
            "s3://dea-public-data/baseline/ga_ls8c_ard_3/090/086/2016/05/12/"
            "ga_ls8c_ard_3-0-0_090086_2016-05-12_final.stac-item.json",
        ),
        (
            get_eo3_test_data_doc("wo_dataset.yaml"),
            "s3://dea-public-data/derivative/ga_ls_wo_3/1-6-0/090/086/2016/05/12/"
            "ga_ls_wo_3_090086_2016-05-12_final.stac-item.json",
        ),
    ]


@pytest.fixture
def extended_eo3_metadata_type_doc() -> dict:
    return get_eo3_test_data_doc("eo3_landsat_ard.odc-type.yaml")


@pytest.fixture
def eo3_sentinel_metadata_type_doc() -> dict:
    return get_eo3_test_data_doc("eo3_sentinel_ard.odc-type.yaml")


@pytest.fixture
def eo3_s1_metadata_type_doc() -> dict:
    return get_eo3_test_data_doc("eo3_s1_ard.odc-type.yaml")


@pytest.fixture
def extended_eo3_product_doc() -> dict:
    return get_eo3_test_data_doc("ard_ls8.odc-product.yaml")


@pytest.fixture
def base_eo3_product_doc() -> dict:
    return get_eo3_test_data_doc("ga_ls_wo_3.odc-product.yaml")


@pytest.fixture
def africa_s2_product_doc() -> dict:
    return get_eo3_test_data_doc("s2_africa_product.yaml")


@pytest.fixture
def s2_ard_product_doc() -> dict:
    return get_eo3_test_data_doc("ga_s2am_ard_3.odc-product.yaml")


@pytest.fixture
def s1_product_doc() -> dict:
    return get_eo3_test_data_doc("ga_s1_vertical_dualpol.odc-product.yaml")


@pytest.fixture
def final_dataset_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("final_dataset.yaml"),
        "s3://dea-public-data/baseline/ga_ls8c_ard_3/090/086/2023/04/30"
        "ga_ls8c_ard_3-2-1_090086_2023-04-30_final.stac-item.json",
    )


@pytest.fixture
def nrt_dataset_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("nrt_dataset.yaml"),
        "s3://dea-public-data/baseline/ga_ls8c_ard_3/090/086/2023/04/30_nrt"
        "ga_ls8c_ard_3-2-1_090086_2023-04-30_nrt.stac-item.json",
    )


@pytest.fixture
def ga_s2am_ard_3_interim_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("ga_s2am_ard_3_interim.yaml"),
        "s3://dea-public-data/baseline/ga_s2am_ard_3/53/JNN/2021/07/24_interim"
        "20230222T235626/ga_s2am_ard_3-2-1_53JNN_2021-07-24_interim.odc-metadata.yaml",
    )


@pytest.fixture
def ga_s2am_ard_3_final_doc() -> tuple[dict, str]:
    return (
        get_eo3_test_data_doc("ga_s2am_ard_3_final.yaml"),
        "s3://dea-public-data/baseline/ga_s2am_ard_3/53/JNN/2021/07/24"
        "20210724T023436/ga_s2am_ard_3-2-1_53JNN_2021-07-24_final.odc-metadata.yaml",
    )


def doc_to_ds(
    index: Index,
    product_name: str,
    ds_doc: SimpleDocNav | dict[str, Any],
    ds_path: str,
    src_tree=None,
    derived_tree=None,
) -> Dataset:
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(index, products=[product_name], verify_lineage=False)
    ds, err = resolver(ds_doc, ds_path)
    assert err is None and ds is not None
    if src_tree is not None:
        ds.source_tree = src_tree
    if derived_tree is not None:
        ds.derived_tree = derived_tree
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FixWindingWarning)
        index.datasets.add(ds, with_lineage=index.supports_lineage)
    return index.datasets.get_unsafe(ds.id)


def doc_to_ds_no_add(index: Index, product_name: str, ds_doc, ds_path) -> Dataset:
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(index, products=[product_name], verify_lineage=False)
    ds, err = resolver(ds_doc, ds_path)
    assert err is None and ds is not None
    return ds


@pytest.fixture
def extended_eo3_metadata_type(
    index: Index, extended_eo3_metadata_type_doc
) -> MetadataType:
    return index.metadata_types.add(
        index.metadata_types.from_doc(extended_eo3_metadata_type_doc)
    )


@pytest.fixture
def eo3_sentinel_metadata_type(
    index: Index, eo3_sentinel_metadata_type_doc
) -> MetadataType:
    return index.metadata_types.add(
        index.metadata_types.from_doc(eo3_sentinel_metadata_type_doc)
    )


@pytest.fixture
def eo3_s1_metadata_type(index: Index, eo3_s1_metadata_type_doc) -> MetadataType:
    return index.metadata_types.add(
        index.metadata_types.from_doc(eo3_s1_metadata_type_doc)
    )


@pytest.fixture
def ls8_eo3_product(
    index: Index, extended_eo3_metadata_type, extended_eo3_product_doc
) -> Product:
    p = index.products.add_document(extended_eo3_product_doc)
    assert p is not None
    return p


@pytest.fixture
def wo_eo3_product(index: Index, base_eo3_product_doc) -> Product:
    p = index.products.add_document(base_eo3_product_doc)
    assert p is not None
    return p


@pytest.fixture
def africa_s2_eo3_product(index: Index, africa_s2_product_doc) -> Product:
    p = index.products.add_document(africa_s2_product_doc)
    assert p is not None
    return p


@pytest.fixture
def ga_s2am_ard_3_product(
    index: Index, eo3_sentinel_metadata_type, s2_ard_product_doc
) -> Product:
    p = index.products.add_document(s2_ard_product_doc)
    assert p is not None
    return p


@pytest.fixture
def ga_s1_product(index: Index, eo3_s1_metadata_type, s1_product_doc) -> Product:
    p = index.products.add_document(s1_product_doc)
    assert p is not None
    return p


@pytest.fixture
def eo3_products(
    index: Index,
    extended_eo3_metadata_type,
    ls8_eo3_product,
    wo_eo3_product,
    africa_s2_eo3_product,
):
    return [africa_s2_eo3_product, ls8_eo3_product, wo_eo3_product]


@pytest.fixture
def ls8_eo3_dataset(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, eo3_ls8_dataset_doc
) -> Dataset:
    return doc_to_ds(index, ls8_eo3_product.name, *eo3_ls8_dataset_doc)


@pytest.fixture
def ls8_eo3_dataset2(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, eo3_ls8_dataset2_doc
) -> Dataset:
    return doc_to_ds(index, ls8_eo3_product.name, *eo3_ls8_dataset2_doc)


@pytest.fixture
def ls8_eo3_dataset3(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, eo3_ls8_dataset3_doc
) -> Dataset:
    return doc_to_ds(index, ls8_eo3_product.name, *eo3_ls8_dataset3_doc)


@pytest.fixture
def ls8_eo3_dataset4(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, eo3_ls8_dataset4_doc
) -> Dataset:
    return doc_to_ds(index, ls8_eo3_product.name, *eo3_ls8_dataset4_doc)


@pytest.fixture
def wo_eo3_dataset(
    index: Index, wo_eo3_product, eo3_wo_dataset_doc, ls8_eo3_dataset
) -> Dataset:
    return doc_to_ds(index, wo_eo3_product.name, *eo3_wo_dataset_doc)


@pytest.fixture
def africa_eo3_dataset(
    index: Index, africa_s2_eo3_product, eo3_africa_dataset_doc
) -> Dataset:
    return doc_to_ds(index, africa_s2_eo3_product.name, *eo3_africa_dataset_doc)


@pytest.fixture
def africa_eo3_dataset2(
    index: Index, africa_s2_eo3_product, eo3_africa_dataset2_doc
) -> Dataset:
    return doc_to_ds(index, africa_s2_eo3_product.name, *eo3_africa_dataset2_doc)


@pytest.fixture
def nrt_dataset(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, nrt_dataset_doc
) -> Dataset:
    return doc_to_ds_no_add(index, ls8_eo3_product.name, *nrt_dataset_doc)


@pytest.fixture
def final_dataset(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, final_dataset_doc
) -> Dataset:
    return doc_to_ds_no_add(index, ls8_eo3_product.name, *final_dataset_doc)


@pytest.fixture
def ds_no_region(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, final_dataset_doc
) -> Dataset:
    doc_no_region = deepcopy(final_dataset_doc)
    doc_no_region[0]["properties"]["odc:region_code"] = None
    return doc_to_ds_no_add(index, ls8_eo3_product.name, *doc_no_region)


@pytest.fixture
def ds_with_lineage(index: Index, wo_eo3_product, eo3_wo_dataset_doc) -> Dataset:
    doc, path = eo3_wo_dataset_doc
    return doc_to_ds_no_add(index, wo_eo3_product.name, doc, path)


@pytest.fixture
def ga_s2am_ard3_final(
    index: Index,
    eo3_sentinel_metadata_type,
    ga_s2am_ard_3_product,
    ga_s2am_ard_3_final_doc,
) -> Dataset:
    return doc_to_ds_no_add(index, ga_s2am_ard_3_product.name, *ga_s2am_ard_3_final_doc)


@pytest.fixture
def ga_s2am_ard3_interim(
    index: Index,
    eo3_sentinel_metadata_type,
    ga_s2am_ard_3_product,
    ga_s2am_ard_3_interim_doc,
) -> Dataset:
    return doc_to_ds_no_add(
        index, ga_s2am_ard_3_product.name, *ga_s2am_ard_3_interim_doc
    )


@pytest.fixture
def s1_eo3_dataset(
    index: Index, eo3_s1_metadata_type, ga_s1_product, s1_dataset_doc
) -> Dataset:
    return doc_to_ds(index, ga_s1_product.name, *s1_dataset_doc)


@pytest.fixture
def mem_index_fresh(in_memory_config) -> Generator[Datacube]:
    with Datacube(env=in_memory_config) as dc:
        yield dc


@pytest.fixture
def mem_index_eo3(
    mem_index_fresh,
    extended_eo3_metadata_type_doc,
    extended_eo3_product_doc,
    base_eo3_product_doc,
):
    mem_index_fresh.index.metadata_types.add(
        mem_index_fresh.index.metadata_types.from_doc(extended_eo3_metadata_type_doc)
    )
    mem_index_fresh.index.products.add_document(base_eo3_product_doc)
    mem_index_fresh.index.products.add_document(extended_eo3_product_doc)
    return mem_index_fresh


@pytest.fixture
def mem_eo3_data(mem_index_eo3, datasets_with_unembedded_lineage_doc):
    (doc_ls8, loc_ls8), (doc_wo, loc_wo) = datasets_with_unembedded_lineage_doc
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(mem_index_eo3.index)
    ds_ls8, _ = resolver(doc_ls8, loc_ls8)
    mem_index_eo3.index.datasets.add(ds_ls8)
    ds_wo, _ = resolver(doc_wo, loc_wo)
    mem_index_eo3.index.datasets.add(ds_wo)
    return mem_index_eo3, ds_ls8.id, ds_wo.id


@pytest.fixture(scope="module", params=["datacube", "postgis", "datacube3", "postgis3"])
def datacube_env_name(request) -> str:
    return request.param


@pytest.fixture(
    params=[
        ("datacube", "postgis"),
        ("postgis", "datacube"),
        ("postgis", "datacube3"),
        ("postgis3", "datacube"),
    ]
)
def datacube_env_name_pair(request) -> tuple[str, str]:
    return request.param


@pytest.fixture
def odc_config() -> ODCConfig:
    return ODCConfig(paths=CONFIG_FILE_PATHS)


@pytest.fixture
def cfg_env(odc_config: ODCConfig, datacube_env_name: str) -> ODCEnvironment:
    """Provides a :class:`ODCEnvironment` configured with suitable config file paths."""
    return odc_config[datacube_env_name]


@pytest.fixture
def cfg_env_pair(
    odc_config: ODCConfig, datacube_env_name_pair: tuple[str, str]
) -> tuple[ODCEnvironment, ...]:
    """Provides a pair of :class:`ODCEnvironment` configured with suitable config file paths."""
    return tuple(odc_config[env] for env in datacube_env_name_pair)


@pytest.fixture
def null_config(odc_config: ODCConfig) -> ODCEnvironment:
    """Provides a :class:`ODCEnvironment` configured with null index driver"""
    return odc_config["nulldriver"]


@pytest.fixture
def in_memory_config(odc_config: ODCConfig) -> ODCEnvironment:
    """Provides a :class:`ODCEnvironment` configured with memory index driver"""
    return odc_config["localmemory"]


def reset_db(cfg_env: ODCEnvironment, tz=None) -> PostgresDb | PostGisDb:
    from urllib.parse import urlparse

    url = psql_url_from_config(cfg_env)
    url_components = urlparse(url)
    db_name = url_components.path[1:]
    if cfg_env._name in ("datacube", "default", "postgres", "datacube3"):
        db: PostgresDb | PostGisDb = PostgresDb.from_config(
            cfg_env, application_name="test-run", validate_connection=False
        )
        # Drop tables so our tests have a clean db.
        # with db.begin() as c:  # Creates a new PostgresDbAPI, by passing a new connection to it
        with db._engine.connect() as connection:
            pgres_core.drop_schema(connection)
            if tz:
                connection.execute(
                    text(f"alter database {db_name} set timezone = {tz!r}")
                )
        # We need to run this as well, I think because SQLAlchemy grabs them into it's MetaData,
        # and attempts to recreate them. WTF TODO FIX
        remove_postgres_dynamic_indexes()
    else:
        db = PostGisDb.from_config(
            cfg_env, application_name="test-run", validate_connection=False
        )
        with db._engine.connect() as connection:
            pgis_core.drop_schema(connection)
            if tz:
                connection.execute(
                    text(f"alter database {db_name} set timezone = {tz!r}")
                )
        remove_postgis_dynamic_indexes()
    return db


def cleanup_db(cfg_env: ODCEnvironment, db: PostgresDb | PostGisDb) -> None:
    with db._engine.connect() as connection:
        if cfg_env._name in ("datacube", "default", "postgres", "datacube3"):
            pgres_core.drop_schema(connection)
        else:
            pgis_core.drop_schema(connection)
    db.close()


@pytest.fixture(params=["America/Los_Angeles", "UTC"])
def uninitialised_postgres_db(
    cfg_env: ODCEnvironment, request
) -> Generator[PostgresDb | PostGisDb]:
    """
    Return a connection to an empty PostgreSQL or PostGIS database
    """
    # Setup
    timezone = request.param
    db = reset_db(cfg_env, timezone)

    yield db

    # Cleanup
    cleanup_db(cfg_env, db)


@pytest.fixture
def uninitialised_postgres_db_pair(
    cfg_env_pair: tuple[ODCEnvironment, ...],
) -> Generator[tuple[PostgresDb | PostGisDb, ...]]:
    """
    Return a pair of connections to empty PostgreSQL or PostGIS databases
    """
    dbs = tuple(reset_db(cfg_env) for cfg_env in cfg_env_pair)

    yield dbs

    for local_cfg, db in zip(cfg_env_pair, dbs):
        cleanup_db(local_cfg, db)


@pytest.fixture
def index(
    cfg_env: ODCEnvironment, uninitialised_postgres_db: PostGisDb | PostgresDb
) -> Generator[AbstractIndex]:
    index = index_connect(cfg_env, validate_connection=False)
    index.init_db()
    yield index
    del index


@pytest.fixture
def index_pair_populated_empty(
    cfg_env_pair: tuple[ODCEnvironment, ...],
    uninitialised_postgres_db_pair,
    extended_eo3_metadata_type_doc,
    base_eo3_product_doc,
    extended_eo3_product_doc,
    africa_s2_product_doc,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
    eo3_ls8_dataset3_doc,
    eo3_ls8_dataset4_doc,
    eo3_wo_dataset_doc,
    eo3_africa_dataset_doc,
    eo3_africa_dataset2_doc,
) -> Generator[tuple]:
    populated_cfg, empty_cfg = cfg_env_pair
    populated_idx = index_connect(populated_cfg, validate_connection=False)
    empty_idx = index_connect(empty_cfg, validate_connection=False)
    populated_idx.init_db()
    empty_idx.init_db(with_default_types=False)
    assert list(empty_idx.products.get_all()) == []
    assert list(populated_idx.products.get_all()) == []
    # Populate the populated index
    populated_idx.metadata_types.add(
        populated_idx.metadata_types.from_doc(extended_eo3_metadata_type_doc)
    )
    for prod_doc in (
        base_eo3_product_doc,
        extended_eo3_product_doc,
        africa_s2_product_doc,
    ):
        populated_idx.products.add_document(prod_doc)
    for ds_doc, ds_path in (
        eo3_ls8_dataset_doc,
        eo3_ls8_dataset2_doc,
        eo3_ls8_dataset3_doc,
        eo3_ls8_dataset4_doc,
        eo3_wo_dataset_doc,
        eo3_africa_dataset_doc,
        eo3_africa_dataset2_doc,
    ):
        doc_to_ds(populated_idx, ds_doc["product"]["name"], ds_doc, ds_path)
    assert list(populated_idx.products.get_all()) != list(empty_idx.products.get_all())
    assert list(empty_idx.products.get_all()) == []
    assert list(populated_idx.products.get_all()) != []

    yield populated_idx, empty_idx

    del populated_idx
    del empty_idx


@pytest.fixture
def index_empty(
    cfg_env: ODCEnvironment, uninitialised_postgres_db: PostGisDb | PostgresDb
) -> Generator[Index]:
    index = index_connect(cfg_env, validate_connection=False)
    index.init_db(with_default_types=False)
    yield index
    del index


def remove_postgres_dynamic_indexes() -> None:
    """
    Clear any dynamically created postgresql indexes from the schema.
    """
    # Our normal indexes start with "ix_", dynamic indexes with "dix_"
    for table in pgres_core.METADATA.tables.values():
        table.indexes.intersection_update(
            [
                i
                for i in table.indexes
                if i.name is not None and not i.name.startswith("dix_")
            ]
        )


def remove_postgis_dynamic_indexes() -> None:
    """
    Clear any dynamically created postgis indexes from the schema.
    """
    # Our normal indexes start with "ix_", dynamic indexes with "dix_"
    # for table in pgis_core.METADATA.tables.values():
    #    table.indexes.intersection_update([i for i in table.indexes if not i.name.startswith('dix_')])
    # Dynamic indexes disabled.


@pytest.fixture
def ls5_telem_doc(ga_metadata_type) -> dict[str, str | dict[str, str | dict[str, str]]]:
    return {
        "name": "ls5_telem_test",
        "description": "LS5 Test",
        "license": "CC-BY-4.0",
        "metadata": {
            "platform": {"code": "LANDSAT_5"},
            "product_type": "satellite_telemetry_data",
            "ga_level": "P00",
            "format": {"name": "RCC"},
        },
        "metadata_type": ga_metadata_type.name,
    }


@pytest.fixture
def ls5_telem_type(index: Index, ls5_telem_doc) -> Product:
    p = index.products.add_document(ls5_telem_doc)
    assert p is not None
    return p


@pytest.fixture(scope="session")
def geotiffs(tmpdir_factory) -> list[dict[str, str | UUID | dict]]:
    """Create test geotiffs and corresponding yamls.

    We create one yaml per time slice, itself comprising one geotiff
    per band, each with specific custom data that can be later
    tested. These are meant to be used by all tests in the current
    session, by way of symlinking the yamls and tiffs returned by this
    fixture, in order to save disk space (and potentially generation
    time).

    The yamls are customised versions of
    :ref:`_EXAMPLE_LS5_NBAR_DATASET_FILE` shifted by 24h and with
    spatial coords reflecting the size of the test geotiff, defined in
    :ref:`GEOTIFF`.

    :param tmpdir_factory: pytest tmp dir factory.
    :return: List of dictionaries like::

        {
            "day": ...,  # compact day string, e.g. `19900302`
            "uuid": ...,  # a unique UUID for this dataset (i.e. specific day)
            "path": ...,  # path to the yaml ingestion file
            "tiffs": ...,  # list of paths to the actual geotiffs in that dataset, one per band.
        }
    """
    tiffs_dir = tmpdir_factory.mktemp("tiffs")

    config = load_yaml_file(_EXAMPLE_LS5_NBAR_DATASET_FILE)[0]

    # Customise the spatial coordinates
    ul = GEOTIFF["ul"]
    lr = {
        dim: ul[dim] + GEOTIFF["shape"][dim] * GEOTIFF["pixel_size"][dim]
        for dim in ("x", "y")
    }
    config["grid_spatial"]["projection"]["geo_ref_points"] = {
        "ul": ul,
        "ur": {"x": lr["x"], "y": ul["y"]},
        "ll": {"x": ul["x"], "y": lr["y"]},
        "lr": lr,
    }
    # Generate the custom geotiff yamls
    return [
        _make_tiffs_and_yamls(tiffs_dir, config, day_offset)
        for day_offset in range(NUM_TIME_SLICES)
    ]


def _make_tiffs_and_yamls(
    tiffs_dir: str, config: dict, day_offset: int
) -> dict[str, str | UUID | dict]:
    """Make a custom yaml and tiff for a day offset.

    :param tiffs_dir: The base path to receive the tiffs.
    :param config: The yaml config to be cloned and altered.
    :param day_offset: how many days to offset the original yaml by.
    """
    config = deepcopy(config)

    # Increment all dates by the day_offset
    delta = timedelta(days=day_offset)
    day_orig = config["acquisition"]["aos"].strftime("%Y%m%d")
    config["acquisition"]["aos"] += delta
    config["acquisition"]["los"] += delta
    config["extent"]["from_dt"] += delta
    config["extent"]["center_dt"] += delta
    config["extent"]["to_dt"] += delta
    day = config["acquisition"]["aos"].strftime("%Y%m%d")

    # Set the main UUID and assign random UUIDs where needed
    uuid = uuid4()
    config["id"] = str(uuid)
    level1 = config["lineage"]["source_datasets"]["level1"]
    level1["id"] = str(uuid4())
    level1["lineage"]["source_datasets"]["satellite_telemetry_data"]["id"] = str(
        uuid4()
    )

    # Alter band data
    bands = config["image"]["bands"]
    for band in bands:
        # Copy dict to avoid aliases in yaml output (for better legibility)
        bands[band]["shape"] = copy(GEOTIFF["shape"])
        bands[band]["cell_size"] = {
            dim: abs(GEOTIFF["pixel_size"][dim]) for dim in ("x", "y")
        }
        bands[band]["path"] = (
            bands[band]["path"].replace("product/", "").replace(day_orig, day)
        )

    dest_path = str(tiffs_dir.join(f"agdc-metadata_{day}.yaml"))
    with open(dest_path, "w") as dest_yaml:
        yaml.dump(config, dest_yaml)
    return {
        "day": day,
        "uuid": uuid,
        "path": dest_path,
        "tiffs": _make_geotiffs(tiffs_dir, day_offset),  # make 1 geotiff per band
    }


@pytest.fixture
def example_ls5_dataset_path(example_ls5_dataset_paths):
    """Create a single sample raw observation (dataset + geotiff)."""
    return next(iter(example_ls5_dataset_paths.values()))


@pytest.fixture
def example_ls5_dataset_paths(tmpdir, geotiffs: list) -> dict:
    """Create sample raw observations (dataset + geotiff).

    This fixture should be used by eah test requiring a set of
    observations over multiple time slices. The actual geotiffs and
    corresponding yamls are symlinks to a set created for the whole
    test session, in order to save disk and time.

    :param tmpdir: The temp directory in which to create the datasets.
    :param geotiffs: List of session geotiffs and yamls, to be
      linked from this unique observation set sample.
    :return: Dict of directories containing each observation,
      indexed by dataset UUID.
    """
    return _make_ls5_scene_datasets(geotiffs, tmpdir)


@pytest.fixture
def default_metadata_type_doc() -> dict:
    return next(doc for doc in default_metadata_type_docs() if doc["name"] == "eo")


@pytest.fixture
def eo3_metadata_type_docs(eo3_base_metadata_type_doc, extended_eo3_metadata_type_doc):
    return [eo3_base_metadata_type_doc, extended_eo3_metadata_type_doc]


@pytest.fixture
def eo3_base_metadata_type_doc():
    return next(doc for doc in default_metadata_type_docs() if doc["name"] == "eo3")


@pytest.fixture
def telemetry_metadata_type_doc() -> dict:
    return next(
        doc for doc in default_metadata_type_docs() if doc["name"] == "telemetry"
    )


@pytest.fixture
def ga_metadata_type_doc() -> dict:
    _FULL_EO_METADATA = Path(__file__).parent.joinpath("extensive-eo-metadata.yaml")  # noqa: N806
    return next(read_documents(_FULL_EO_METADATA))[1]


@pytest.fixture
def default_metadata_types(
    index: Index, eo3_metadata_type_docs
) -> Iterable[MetadataType]:
    """Inserts the default metadata types into the Index"""
    type_docs = (
        default_metadata_type_docs()
        if index.supports_legacy
        else eo3_metadata_type_docs
    )
    for d in type_docs:
        index.metadata_types.add(index.metadata_types.from_doc(d))
    return index.metadata_types.get_all()


@pytest.fixture
def ga_metadata_type(index: Index, ga_metadata_type_doc) -> MetadataType:
    return index.metadata_types.add(index.metadata_types.from_doc(ga_metadata_type_doc))


@pytest.fixture
def default_metadata_type(index: Index, default_metadata_types) -> MetadataType:
    m = index.metadata_types.get_by_name("eo" if index.supports_legacy else "eo3")
    assert m is not None
    return m


@pytest.fixture
def telemetry_metadata_type(index: Index, default_metadata_types) -> MetadataType:
    m = index.metadata_types.get_by_name("telemetry")
    assert m is not None
    return m


@pytest.fixture
def indexed_ls5_scene_products(index: Index, ga_metadata_type) -> list[Product]:
    """Add Landsat 5 scene Products into the Index"""
    products = load_test_products(
        CONFIG_SAMPLES / "dataset_types" / "ls5_scenes.yaml",
        # Use our larger metadata type with a more diverse set of field types.
        metadata_type=ga_metadata_type,
    )

    types = []
    for product in products:
        p = index.products.add_document(product)
        assert p is not None
        types.append(p)

    return types


@pytest.fixture
def example_ls5_nbar_metadata_doc() -> list:
    return load_yaml_file(_EXAMPLE_LS5_NBAR_DATASET_FILE)[0]


@pytest.fixture
def clirunner(datacube_env_name: str):
    def _run_cli(
        opts: Sequence[str],
        catch_exceptions: bool = False,
        expect_success: bool = True,
        cli_method=datacube.scripts.cli_app.cli,
        skip_env: bool = False,
        skip_config_paths: bool = False,
        verbose_flag: Literal[False] | str = "-v",
    ) -> Result:
        # If raw config passed in, skip default test config
        exe_opts: list[str] = (
            []
            if skip_config_paths
            else list(itertools.chain(*(("--config", f) for f in CONFIG_FILE_PATHS)))
        )
        if not skip_env:
            exe_opts += ["--env", datacube_env_name]
        if verbose_flag:
            exe_opts.append(verbose_flag)
        exe_opts.extend(opts)

        result = CliRunner().invoke(
            cli_method, exe_opts, catch_exceptions=catch_exceptions
        )
        if expect_success:
            assert result.exit_code == 0, (
                f"Error for {opts!r}. output: {result.output!r}"
            )
        return result

    return _run_cli


@pytest.fixture
def clirunner_raw():
    def _run_cli(
        opts: Sequence[str],
        catch_exceptions: bool = False,
        expect_success: bool = True,
        cli_method=datacube.scripts.cli_app.cli,
        verbose_flag: Literal[False] | str = "-v",
    ) -> Result:
        exe_opts = []
        if verbose_flag:
            exe_opts.append(verbose_flag)
        exe_opts.extend(opts)

        runner = CliRunner()
        result = runner.invoke(cli_method, exe_opts, catch_exceptions=catch_exceptions)
        if expect_success:
            assert result.exit_code == 0, (
                f"Error for {opts!r}. output: {result.output!r}"
            )
        return result

    return _run_cli


@pytest.fixture
def dataset_add_configs():
    B = INTEGRATION_TESTS_DIR / "data" / "dataset_add"
    return SimpleNamespace(
        metadata=str(B / "metadata.yml"),
        products=str(B / "products.yml"),
        datasets_bad1=str(B / "datasets_bad1.yml"),
        datasets_no_id=str(B / "datasets_no_id.yml"),
        datasets_eo3=str(B / "datasets_eo3.yml"),
        datasets_eo3_updated=str(B / "datasets_eo3_updated.yml"),
        datasets=str(B / "datasets.yml"),
        empty_file=str(B / "empty_file.yml"),
    )


@pytest.fixture
def src_tree_ids() -> dict[str, UUID]:
    return {
        "root": uuid4(),
        "ard1": uuid4(),
        "ard2": uuid4(),
        "l1_1": uuid4(),
        "l1_2": uuid4(),
        "l1_3": uuid4(),
        "l1_4": uuid4(),
        "l1_5": uuid4(),
        "l1_6": uuid4(),
        "atmos": uuid4(),
        "atmos_parent": uuid4(),
    }


@pytest.fixture
def src_lineage_tree(
    src_tree_ids: dict[str, UUID],
) -> tuple[LineageTree, dict[str, UUID]]:
    ids = src_tree_ids
    direction = LineageDirection.SOURCES
    return LineageTree(
        dataset_id=ids["root"],
        direction=direction,
        children={
            "ard": [
                LineageTree(
                    dataset_id=ids["ard1"],
                    direction=direction,
                    children={
                        "l1": [
                            LineageTree(
                                dataset_id=ids["l1_1"],
                                direction=direction,
                                home="level1",
                                children={},
                            ),
                            LineageTree(
                                dataset_id=ids["l1_2"],
                                direction=direction,
                                home="level1",
                                children={},
                            ),
                            LineageTree(
                                dataset_id=ids["l1_3"],
                                direction=direction,
                                home="level1",
                                children={},
                            ),
                        ],
                        "atmos_corr": [
                            LineageTree(
                                dataset_id=ids["atmos"],
                                direction=direction,
                                home="anciliary",
                                children=None,
                            )
                        ],
                    },
                ),
                LineageTree(
                    dataset_id=ids["ard2"],
                    direction=direction,
                    children={
                        "l1": [
                            LineageTree(
                                dataset_id=ids["l1_4"],
                                direction=direction,
                                home="level1",
                                children={},
                            ),
                            LineageTree(
                                dataset_id=ids["l1_5"],
                                direction=direction,
                                home="level1",
                                children={},
                            ),
                            LineageTree(
                                dataset_id=ids["l1_6"],
                                direction=direction,
                                home="level1",
                                children={},
                            ),
                        ],
                        "atmos_corr": [
                            LineageTree(
                                dataset_id=ids["atmos"],
                                direction=direction,
                                home="anciliary",
                                children={
                                    "preatmos": [
                                        LineageTree(
                                            dataset_id=ids["atmos_parent"],
                                            direction=direction,
                                            home="anciliary",
                                            children={},
                                        )
                                    ]
                                },
                            )
                        ],
                    },
                ),
            ]
        },
    ), ids


@pytest.fixture
def compatible_derived_tree(
    src_tree_ids: dict[str, UUID],
) -> tuple[LineageTree, dict[str, UUID]]:
    ids = src_tree_ids.copy()
    ids.update(
        {
            "atmos_grandparent": uuid4(),
            "ard3": uuid4(),
            "ard4": uuid4(),
            "leaf_1": uuid4(),
            "leaf_2": uuid4(),
            "leaf_3": uuid4(),
            "child_of_root": uuid4(),
            "grandchild_of_root": uuid4(),
        }
    )
    tree = LineageTree(
        dataset_id=ids["atmos_grandparent"],
        direction=LineageDirection.DERIVED,
        home="steves_basement",
        children={
            "spam": [
                LineageTree(
                    dataset_id=ids["atmos_parent"],
                    direction=LineageDirection.DERIVED,
                    home="anciliary",
                    children={
                        "preatmos": [
                            LineageTree(
                                dataset_id=ids["atmos"],
                                direction=LineageDirection.DERIVED,
                                home="anciliary",
                                children={
                                    "atmos_corr": [
                                        LineageTree(
                                            dataset_id=ids["ard1"],
                                            direction=LineageDirection.DERIVED,
                                            home="ard",
                                            children={
                                                "ard": [
                                                    LineageTree(
                                                        dataset_id=ids["root"],
                                                        direction=LineageDirection.DERIVED,
                                                        home="extensions",
                                                        children={
                                                            "dra": [
                                                                LineageTree(
                                                                    dataset_id=ids[
                                                                        "child_of_root"
                                                                    ],
                                                                    direction=LineageDirection.DERIVED,
                                                                    home="extensions",
                                                                    children={
                                                                        "rad": [
                                                                            LineageTree(
                                                                                dataset_id=ids[
                                                                                    "grandchild_of_root"
                                                                                ],
                                                                                direction=LineageDirection.DERIVED,
                                                                                home="extensions",
                                                                                children={},
                                                                            )
                                                                        ]
                                                                    },
                                                                )
                                                            ]
                                                        },
                                                    ),
                                                    LineageTree(
                                                        dataset_id=ids["leaf_1"],
                                                        direction=LineageDirection.DERIVED,
                                                        home="extensions",
                                                        children={},
                                                    ),
                                                ]
                                            },
                                        ),
                                        LineageTree(
                                            dataset_id=ids["ard2"],
                                            direction=LineageDirection.DERIVED,
                                            home="ard",
                                            children={},
                                        ),
                                        LineageTree(
                                            dataset_id=ids["ard3"],
                                            direction=LineageDirection.DERIVED,
                                            home="ard",
                                            children={
                                                "ard": [
                                                    LineageTree(
                                                        dataset_id=ids["leaf_2"],
                                                        direction=LineageDirection.DERIVED,
                                                        home="extensions",
                                                        children={},
                                                    ),
                                                    LineageTree(
                                                        dataset_id=ids["leaf_3"],
                                                        direction=LineageDirection.DERIVED,
                                                        home="extensions",
                                                        children={},
                                                    ),
                                                ]
                                            },
                                        ),
                                        LineageTree(
                                            dataset_id=ids["ard4"],
                                            direction=LineageDirection.DERIVED,
                                            home="ard",
                                            children={},
                                        ),
                                    ]
                                },
                            )
                        ]
                    },
                )
            ]
        },
    )
    return tree, ids


@pytest.fixture
def dataset_with_external_lineage(
    index: Index,
    src_lineage_tree: tuple[LineageTree, dict[str, UUID]],
    compatible_derived_tree: tuple[LineageTree, dict[str, UUID]],
    ls8_eo3_product,
    eo3_ls8_dataset_doc,
) -> tuple[Dataset, LineageTree, LineageTree, dict[str, UUID]]:
    src_tree, _ = src_lineage_tree
    derived_tree, ids = compatible_derived_tree
    eo3_ls8_dataset_doc[0]["id"] = ids["root"]
    dataset = doc_to_ds(
        index,
        ls8_eo3_product.name,
        *eo3_ls8_dataset_doc,
        src_tree=src_tree,  # type: ignore[misc]
        derived_tree=derived_tree,
    )
    return dataset, src_tree, derived_tree, ids
