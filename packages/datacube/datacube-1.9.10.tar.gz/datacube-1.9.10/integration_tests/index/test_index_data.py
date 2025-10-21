# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Test database methods.

Integration tests: these depend on a local Postgres instance.
"""

import copy
import datetime
from pathlib import Path
from uuid import UUID

import pytest

from datacube.index import Index
from datacube.index.eo3 import prep_eo3
from datacube.index.exceptions import MissingRecordError
from datacube.model import Dataset, MetadataType, Product
from datacube.testutils import suppress_deprecations
from datacube.utils.json_types import JsonDict

_telemetry_uuid = UUID("4ec8fe97-e8b9-11e4-87ff-1040f381a756")
_telemetry_dataset = {
    "product_type": "satellite_telemetry_data",
    "checksum_path": "package.sha1",
    "id": str(_telemetry_uuid),
    "ga_label": "LS8_OLITIRS_STD-MD_P00_LC81160740742015089ASA00_"
    "116_074_20150330T022553Z20150330T022657",
    "ga_level": "P00",
    "size_bytes": 637660782,
    "platform": {"code": "LANDSAT_8"},
    # We're unlikely to have extent info for a raw dataset, we'll use it for search tests.
    "extent": {
        "center_dt": datetime.datetime(2014, 7, 26, 23, 49, 0, 343853).isoformat(),
        "coord": {
            "ll": {"lat": -31.33333, "lon": 149.78434},
            "lr": {"lat": -31.37116, "lon": 152.20094},
            "ul": {"lat": -29.23394, "lon": 149.85216},
            "ur": {"lat": -29.26873, "lon": 152.21782},
        },
    },
    "creation_dt": datetime.datetime(2015, 4, 22, 6, 32, 4).isoformat(),
    "instrument": {"name": "OLI_TIRS"},
    "format": {"name": "MD"},
    "lineage": {"source_datasets": {}, "blah": float("NaN")},
}

_pseudo_telemetry_dataset_type: JsonDict = {
    "name": "ls8_telemetry",
    "description": "LS8 test",
    "metadata": {
        "product_type": "satellite_telemetry_data",
        "platform": {"code": "LANDSAT_8"},
        "format": {"name": "MD"},
    },
    "metadata_type": "eo",
}


def test_archive_datasets(index: Index, ls8_eo3_dataset) -> None:
    datasets = list(index.datasets.search())
    assert len(datasets) == 1
    assert not datasets[0].is_archived

    index.datasets.archive([ls8_eo3_dataset.id])
    datasets = list(index.datasets.search())
    assert len(datasets) == 0

    # The model should show it as archived now.
    indexed_dataset = index.datasets.get(ls8_eo3_dataset.id)
    assert indexed_dataset is not None
    assert indexed_dataset.is_archived

    index.datasets.restore([ls8_eo3_dataset.id])
    datasets = list(index.datasets.search())
    assert len(datasets) == 1

    # And now active
    indexed_dataset = index.datasets.get(ls8_eo3_dataset.id)
    assert indexed_dataset is not None
    assert not indexed_dataset.is_archived


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_archive_less_mature(
    index: Index, final_dataset, nrt_dataset, ds_no_region
) -> None:
    # case 1: add nrt then final; nrt should get archived
    index.datasets.add(nrt_dataset, with_lineage=False, archive_less_mature=True)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    index.datasets.add(final_dataset, with_lineage=False, archive_less_mature=True)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert d.is_archived
    d = index.datasets.get(final_dataset.id)
    assert d is not None
    assert not d.is_archived

    # case 2: purge nrt; re-add with final already there
    index.datasets.purge([nrt_dataset.id])
    assert index.datasets.get(nrt_dataset.id) is None
    with pytest.raises(ValueError):
        # should error as more mature version of dataset already exists
        index.datasets.add(nrt_dataset, with_lineage=False, archive_less_mature=True)

    # case 3: re-index final; nrt should still get archived
    assert index.datasets.get(final_dataset.id) is not None
    index.datasets.add(nrt_dataset, with_lineage=False)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    index.datasets.add(final_dataset, with_lineage=False, archive_less_mature=True)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert d.is_archived


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_cannot_search_for_less_mature(index: Index, nrt_dataset, ds_no_region) -> None:
    # if a dataset is missing a property required for finding less mature datasets,
    # it should error
    index.datasets.add(nrt_dataset, with_lineage=False, archive_less_mature=0)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    assert ds_no_region.metadata.region_code is None
    with pytest.raises(ValueError, match="region_code"):
        index.datasets.add(ds_no_region, with_lineage=False, archive_less_mature=0)


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_archive_less_mature_approx_timestamp(
    index: Index, ga_s2am_ard3_final, ga_s2am_ard3_interim
) -> None:
    # test archive_less_mature where there's a slight difference in timestamps
    index.datasets.add(ga_s2am_ard3_interim, with_lineage=False)
    d = index.datasets.get(ga_s2am_ard3_interim.id)
    assert d is not None
    assert not d.is_archived
    index.datasets.add(ga_s2am_ard3_final, with_lineage=False, archive_less_mature=True)
    d = index.datasets.get(ga_s2am_ard3_interim.id)
    assert d is not None
    assert d.is_archived
    d = index.datasets.get(ga_s2am_ard3_final.id)
    assert d is not None
    assert not d.is_archived


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_dont_archive_less_mature(index: Index, final_dataset, nrt_dataset) -> None:
    # ensure datasets aren't archive if no archive_less_mature value is provided
    index.datasets.add(nrt_dataset, with_lineage=False)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    index.datasets.add(final_dataset, with_lineage=False, archive_less_mature=None)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    d = index.datasets.get(final_dataset.id)
    assert d is not None
    assert not d.is_archived


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_archive_less_mature_bool(index: Index, final_dataset, nrt_dataset) -> None:
    # if archive_less_mature value gets passed as a bool via an outdated script
    index.datasets.add(nrt_dataset, with_lineage=False)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    index.datasets.add(final_dataset, with_lineage=False, archive_less_mature=False)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    d = index.datasets.get(final_dataset.id)
    assert d is not None
    assert not d.is_archived


def test_purge_datasets(index: Index, ls8_eo3_dataset) -> None:
    assert index.datasets.has(ls8_eo3_dataset.id)
    datasets = list(index.datasets.search())
    assert len(datasets) == 1
    assert not datasets[0].is_archived

    # Archive dataset
    index.datasets.archive([ls8_eo3_dataset.id])
    datasets = list(index.datasets.search())
    assert len(datasets) == 0

    # The model should show it as archived now.
    indexed_dataset = index.datasets.get(ls8_eo3_dataset.id)
    assert indexed_dataset is not None
    assert indexed_dataset.is_archived

    # Purge dataset
    index.datasets.purge([ls8_eo3_dataset.id])
    assert index.datasets.get(ls8_eo3_dataset.id) is None


def test_purge_datasets_cli(index: Index, ls8_eo3_dataset, clirunner) -> None:
    dsid = ls8_eo3_dataset.id

    # Attempt to purge non-archived dataset should fail
    runner = clirunner(["dataset", "purge", str(dsid)])
    assert "could not be purged" in runner.output
    assert str(dsid) in runner.output
    assert "0 of 1 datasets purged" in runner.output

    # Archive dataset
    index.datasets.archive([dsid])
    indexed_dataset = index.datasets.get(dsid)
    assert indexed_dataset is not None
    assert indexed_dataset.is_archived

    # Test CLI dry run
    clirunner(["dataset", "purge", "--dry-run", str(dsid)])
    indexed_dataset = index.datasets.get(dsid)
    assert indexed_dataset is not None
    assert indexed_dataset.is_archived

    # Test CLI purge
    clirunner(["dataset", "purge", str(dsid)])
    assert index.datasets.get(dsid) is None

    # Attempt to purge non-existent dataset should fail
    clirunner(["dataset", "purge", str(dsid)], expect_success=False)


def test_purge_all_datasets_cli(
    index: Index, cfg_env, ls8_eo3_dataset, clirunner
) -> None:
    dsid = ls8_eo3_dataset.id

    # archive all datasets
    clirunner(["dataset", "archive", "--all"])

    indexed_dataset = index.datasets.get(dsid)
    assert indexed_dataset is not None
    assert indexed_dataset.is_archived

    # Restore all datasets
    clirunner(["dataset", "restore", "--all"])
    indexed_dataset = index.datasets.get(dsid)
    assert indexed_dataset is not None
    assert not indexed_dataset.is_archived

    # Archive again
    clirunner(["dataset", "archive", "--all"])

    # and purge
    clirunner(["dataset", "purge", "--all"])
    assert index.datasets.get(dsid) is None


def test_index_duplicate_dataset(index: Index, cfg_env, ls8_eo3_dataset) -> None:
    product = ls8_eo3_dataset.product
    dsid = ls8_eo3_dataset.id
    assert index.datasets.has(dsid)

    # Insert again.
    ds = Dataset(product, ls8_eo3_dataset.metadata_doc, uri=ls8_eo3_dataset.uri)
    index.datasets.add(ds, with_lineage=False)

    assert index.datasets.has(dsid)


def test_has_dataset(index: Index, ls8_eo3_dataset: Dataset) -> None:
    assert index.datasets.has(ls8_eo3_dataset.id)
    assert index.datasets.has(str(ls8_eo3_dataset.id))

    assert not index.datasets.has(UUID("f226a278-e422-11e6-b501-185e0f80a5c0"))
    assert not index.datasets.has("f226a278-e422-11e6-b501-185e0f80a5c0")

    assert index.datasets.bulk_has(
        [ls8_eo3_dataset.id, UUID("f226a278-e422-11e6-b501-185e0f80a5c0")]
    ) == [True, False]
    assert index.datasets.bulk_has(
        [str(ls8_eo3_dataset.id), "f226a278-e422-11e6-b501-185e0f80a5c0"]
    ) == [True, False]


def test_get_dataset(index: Index, ls8_eo3_dataset: Dataset) -> None:
    assert index.datasets.has(ls8_eo3_dataset.id)
    assert index.datasets.has(str(ls8_eo3_dataset.id))

    assert index.datasets.bulk_has(
        [ls8_eo3_dataset.id, "f226a278-e422-11e6-b501-185e0f80a5c0"]
    ) == [True, False]

    for tr in (lambda x: x, lambda x: str(x)):
        ds = index.datasets.get(tr(ls8_eo3_dataset.id))
        assert ds is not None
        assert ds.id == ls8_eo3_dataset.id

        (ds,) = index.datasets.bulk_get([tr(ls8_eo3_dataset.id)])
        assert ds.id == ls8_eo3_dataset.id

    assert (
        index.datasets.bulk_get(
            [
                "f226a278-e422-11e6-b501-185e0f80a5c0",
                "f226a278-e422-11e6-b501-185e0f80a5c1",
            ]
        )
        == []
    )


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_add_dataset_no_product_id(
    index: Index, extended_eo3_metadata_type, ls8_eo3_product, eo3_ls8_dataset_doc
) -> None:
    product_no_id = Product(extended_eo3_metadata_type, ls8_eo3_product.definition)
    assert product_no_id.id is None
    dataset_doc, _ = eo3_ls8_dataset_doc
    dataset = Dataset(product_no_id, prep_eo3(dataset_doc))
    assert index.datasets.add(dataset, with_lineage=False)


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_transactions_api_ctx_mgr(
    index: Index,
    extended_eo3_metadata_type_doc,
    ls8_eo3_product,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
):
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(index, products=[ls8_eo3_product.name], verify_lineage=False)
    ds1, _ = resolver(*eo3_ls8_dataset_doc)
    assert ds1 is not None
    ds2, _ = resolver(*eo3_ls8_dataset2_doc)
    assert ds2 is not None
    with pytest.raises(Exception) as e:  # noqa: SIM117
        with index.transaction() as trans:
            assert index.datasets.get(ds1.id) is None
            index.datasets.add(ds1, with_lineage=False)
            assert index.datasets.get(ds1.id) is not None
            raise Exception("Rollback!")
    assert "Rollback!" in str(e.value)
    assert index.datasets.get(ds1.id) is None
    with index.transaction() as trans:
        assert index.datasets.get(ds1.id) is None
        index.datasets.add(ds1, with_lineage=False)
        assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds1.id) is not None
    with index.transaction() as trans:
        index.datasets.add(ds2, with_lineage=False)
        assert index.datasets.get(ds2.id) is not None
        raise trans.rollback_exception("Rollback")
    assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds2.id) is None


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_transactions_api_ctx_mgr_nested(
    index: Index,
    extended_eo3_metadata_type_doc,
    ls8_eo3_product,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
):
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(index, products=[ls8_eo3_product.name], verify_lineage=False)
    ds1, _ = resolver(*eo3_ls8_dataset_doc)
    assert ds1 is not None
    ds2, _ = resolver(*eo3_ls8_dataset2_doc)
    assert ds2 is not None
    with pytest.raises(Exception) as e:  # noqa: SIM117
        with index.transaction():
            with index.transaction() as trans:
                assert index.datasets.get(ds1.id) is None
                index.datasets.add(ds1, False)
                assert index.datasets.get(ds1.id) is not None
                raise Exception("Rollback!")
    assert "Rollback!" in str(e.value)
    assert index.datasets.get(ds1.id) is None
    with index.transaction():  # noqa: SIM117
        with index.transaction() as trans:
            assert index.datasets.get(ds1.id) is None
            index.datasets.add(ds1, False)
            assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds1.id) is not None
    with index.transaction():  # noqa: SIM117
        with index.transaction() as trans:
            index.datasets.add(ds2, False)
            assert index.datasets.get(ds2.id) is not None
            raise trans.rollback_exception("Rollback")
    assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds2.id) is None


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_transactions_api_manual(
    index: Index,
    extended_eo3_metadata_type_doc,
    ls8_eo3_product,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
) -> None:
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(index, products=[ls8_eo3_product.name], verify_lineage=False)
    ds1, _ = resolver(*eo3_ls8_dataset_doc)
    ds2, _ = resolver(*eo3_ls8_dataset2_doc)
    assert ds1 is not None
    assert ds2 is not None
    trans = index.transaction()
    index.datasets.add(ds1, False)
    assert index.datasets.get(ds1.id) is not None
    trans.begin()
    index.datasets.add(ds2, False)
    assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds2.id) is not None
    trans.rollback()
    assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds2.id) is None
    trans.begin()
    index.datasets.add(ds2, False)
    trans.commit()
    assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds2.id) is not None


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_transactions_api_hybrid(
    index: Index,
    extended_eo3_metadata_type_doc,
    ls8_eo3_product,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
) -> None:
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(index, products=[ls8_eo3_product.name], verify_lineage=False)
    ds1, _ = resolver(*eo3_ls8_dataset_doc)
    assert ds1 is not None
    ds2, _ = resolver(*eo3_ls8_dataset2_doc)
    assert ds2 is not None
    with index.transaction() as trans:
        assert index.datasets.get(ds1.id) is None
        index.datasets.add(ds1, False)
        assert index.datasets.get(ds1.id) is not None
        trans.rollback()
        assert index.datasets.get(ds1.id) is None
        trans.begin()
        assert index.datasets.get(ds1.id) is None
        index.datasets.add(ds1, False)
        assert index.datasets.get(ds1.id) is not None
        trans.commit()
        assert index.datasets.get(ds1.id) is not None
        trans.begin()
        index.datasets.add(ds2, False)
        assert index.datasets.get(ds2.id) is not None
        trans.rollback()
    assert index.datasets.get(ds1.id) is not None
    assert index.datasets.get(ds2.id) is None


def test_get_missing_things(index: Index) -> None:
    """
    The get(id) methods should return None if the object doesn't exist.
    """
    uuid_ = UUID("18474b58-c8a6-11e6-a4b3-185e0f80a5c0")
    missing_thing = index.datasets.get(uuid_, include_sources=False)
    assert missing_thing is None, "get() should return none when it doesn't exist"

    if index.supports_lineage and not index.supports_external_lineage:
        missing_thing = index.datasets.get(uuid_, include_sources=True)
        assert missing_thing is None, "get() should return none when it doesn't exist"

    # Max SmallInteger: https://www.postgresql.org/docs/17/datatype-numeric.html
    id_ = 32767
    missing_thing = index.metadata_types.get(id_)
    assert missing_thing is None, "get() should return none when it doesn't exist"

    missing_thing = index.products.get(id_)
    assert missing_thing is None, "get() should return none when it doesn't exist"


@pytest.mark.parametrize("datacube_env_name", ("datacube", "datacube3"))
def test_index_dataset_with_sources(index: Index, default_metadata_type) -> None:
    type_ = index.products.add_document(_pseudo_telemetry_dataset_type)

    parent_doc = _telemetry_dataset.copy()
    parent = Dataset(type_, parent_doc, None, sources={})
    child_doc = _telemetry_dataset.copy()
    child_doc["lineage"] = {"source_datasets": {"source": _telemetry_dataset}}
    child_doc["id"] = "051a003f-5bba-43c7-b5f1-7f1da3ae9cfb"
    child = Dataset(type_, child_doc, sources={"source": parent})

    with pytest.raises(MissingRecordError):
        index.datasets.add(child, with_lineage=False)

    index.datasets.add(child)
    assert index.datasets.get(parent.id)
    assert index.datasets.get(child.id)

    assert len(list(index.datasets.bulk_get([parent.id, child.id]))) == 2

    index.datasets.add(child, with_lineage=False)
    index.datasets.add(child, with_lineage=True)

    parent_doc["platform"] = {"code": "LANDSAT_9"}
    index.datasets.add(child, with_lineage=True)
    index.datasets.add(child, with_lineage=False)


@pytest.mark.parametrize("datacube_env_name", ("postgis", "postgis3"))
@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_index_dataset_with_lineage(
    index: Index, ds_with_lineage, ls8_eo3_dataset
) -> None:
    assert ds_with_lineage.source_tree
    index.datasets.add(ds_with_lineage)
    sources = index.lineage.get_source_tree(ds_with_lineage.id).children
    assert sources is not None
    assert len(sources["ard"]) == 1
    assert sources["ard"][0].dataset_id == ls8_eo3_dataset.id
    assert index.datasets.get(ds_with_lineage.id)


@pytest.mark.parametrize("datacube_env_name", ("datacube", "datacube3"))
def test_index_dataset_with_location(
    index: Index, default_metadata_type: MetadataType
) -> None:
    first_file = Path("/tmp/first/something.yaml").absolute()
    second_file = Path("/tmp/second/something.yaml").absolute()

    product = index.products.add_document(_pseudo_telemetry_dataset_type)
    assert product is not None
    dataset = Dataset(product, _telemetry_dataset, uri=first_file.as_uri(), sources={})
    index.datasets.add(dataset)
    stored = index.datasets.get(dataset.id)
    assert stored is not None
    assert stored.id == _telemetry_uuid
    # TODO: Dataset types?
    assert stored.product.id == product.id
    assert stored.metadata_type.id == default_metadata_type.id
    assert stored.local_path == Path(first_file)

    # Ingesting again should have no effect.
    index.datasets.add(dataset)
    stored = index.datasets.get(dataset.id)
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert len(locations) == 1
    # Remove the location
    with suppress_deprecations():
        was_removed = index.datasets.remove_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert was_removed
    with suppress_deprecations():
        was_removed = index.datasets.remove_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert not was_removed
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert len(locations) == 0
    # Re-add the location
    with suppress_deprecations():
        was_added = index.datasets.add_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert was_added
    with suppress_deprecations():
        was_added = index.datasets.add_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert not was_added
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert len(locations) == 1

    # A rough date is ok: 1:01 beforehand just in case someone runs this during daylight savings time conversion :)
    # (any UTC conversion errors will be off by much more than this for PST/AEST)
    before_archival_dt = utc_now() - datetime.timedelta(hours=1, minutes=1)

    with suppress_deprecations():
        was_archived = index.datasets.archive_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert was_archived
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert locations == []
    with suppress_deprecations():
        locations = index.datasets.get_archived_locations(
            dataset.id
        )  # Test of deprecated method
    assert locations == [first_file.as_uri()]

    # It should return the time archived.
    with suppress_deprecations():
        location_times = index.datasets.get_archived_location_times(
            dataset.id
        )  # Test of deprecated method
    assert len(location_times) == 1
    location, archived_time = location_times[0]
    assert location == first_file.as_uri()
    assert utc_now() > archived_time > before_archival_dt

    with suppress_deprecations():
        was_restored = index.datasets.restore_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert was_restored
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert len(locations) == 1

    # Indexing with a new path should NOT add the second one.
    dataset._uris = [second_file.as_uri()]
    index.datasets.add(dataset)
    stored = index.datasets.get(dataset.id)
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert len(locations) == 1

    # Add location manually instead
    with suppress_deprecations():
        index.datasets.add_location(
            dataset.id, second_file.as_uri()
        )  # Test of deprecated method
        stored = index.datasets.get(dataset.id)
        assert stored is not None
    assert len(stored._uris) == 2

    # Newest to oldest.
    assert stored._uris == [second_file.as_uri(), first_file.as_uri()]
    # And the second one is newer, so it should be returned as the default local path:
    assert stored.local_path == Path(second_file)

    # Can archive and restore the first file, and location order is preserved
    with suppress_deprecations():
        was_archived = index.datasets.archive_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert was_archived
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert locations == [second_file.as_uri()]
    with suppress_deprecations():
        was_restored = index.datasets.restore_location(
            dataset.id, first_file.as_uri()
        )  # Test of deprecated method
    assert was_restored
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert locations == [second_file.as_uri(), first_file.as_uri()]

    # Can archive and restore the second file, and location order is preserved
    with suppress_deprecations():
        was_archived = index.datasets.archive_location(
            dataset.id, second_file.as_uri()
        )  # Test of deprecated method
    assert was_archived
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert locations == [first_file.as_uri()]
    with suppress_deprecations():
        was_restored = index.datasets.restore_location(
            dataset.id, second_file.as_uri()
        )  # Test of deprecated method
    assert was_restored
    with suppress_deprecations():
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert locations == [second_file.as_uri(), first_file.as_uri()]

    # Indexing again without location should have no effect.
    dataset._uris = []
    with suppress_deprecations():
        index.datasets.add(dataset)
        stored = index.datasets.get(dataset.id)
        assert stored is not None
        locations = index.datasets.get_locations(
            dataset.id
        )  # Test of deprecated method
    assert len(locations) == 2
    # Newest to oldest.
    assert locations == [second_file.as_uri(), first_file.as_uri()]
    # And the second one is newer, so it should be returned as the default local path:
    assert stored.local_path == Path(second_file)

    # Check order of uris is preserved when indexing with more than one
    second_ds_doc = copy.deepcopy(_telemetry_dataset)
    test_uuid = "366f32d8-e1f8-11e6-94b4-185e0f80a589"
    second_ds_doc["id"] = test_uuid
    with suppress_deprecations():
        index.datasets.add(
            Dataset(  # Test deprecated behaviour
                product, second_ds_doc, uris=["file:///a", "file:///b"], sources={}
            )
        )

    # test order using get_locations function
    with suppress_deprecations():
        # Test of deprecated method
        assert index.datasets.get_locations(test_uuid) == [
            "file:///a",
            "file:///b",
        ]

        # test order using datasets.get(), it has custom query as it turns out
        d = index.datasets.get(test_uuid)
        assert d is not None
        assert d._uris == [
            "file:///a",
            "file:///b",
        ]

        # test update, this should prepend file:///c, file:///d to the existing list
        index.datasets.update(
            Dataset(  # Test of deprecated functionality
                product,
                second_ds_doc,
                uris=["file:///a", "file:///c", "file:///d"],
                sources={},
            )
        )
        assert index.datasets.get_locations(test_uuid) == [  # Test of deprecated method
            "file:///c",
            "file:///d",
            "file:///a",
            "file:///b",
        ]
        d = index.datasets.get(test_uuid)
        assert d is not None
        assert d.uris == [  # Test of deprecated functionality
            "file:///c",
            "file:///d",
            "file:///a",
            "file:///b",
        ]

    # Ability to get datasets for a location
    # Add a second dataset with a different location (to catch lack of joins, filtering etc)
    second_ds_doc = copy.deepcopy(_telemetry_dataset)
    second_ds_doc["id"] = "366f32d8-e1f8-11e6-94b4-185e0f80a5c0"
    index.datasets.add(
        Dataset(product, second_ds_doc, uri=second_file.as_uri(), sources={})
    )
    for mode in ("exact", "prefix", None):
        with suppress_deprecations():
            dataset_ids = [
                d.id
                for d in index.datasets.get_datasets_for_location(
                    first_file.as_uri(), mode=mode
                )
            ]
        assert dataset_ids == [dataset.id]

    assert (
        list(
            index.datasets.get_datasets_for_location(first_file.as_uri() + "#part=100")
        )
        == []
    )

    with pytest.raises(ValueError):
        list(
            index.datasets.get_datasets_for_location(
                first_file.as_uri(), mode="nosuchmode"
            )
        )


def utc_now():
    return datetime.datetime.now(datetime.UTC)


def test_bulk_reads_transaction(
    index,
    extended_eo3_metadata_type_doc,
    ls8_eo3_product,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
) -> None:
    with pytest.raises(ValueError) as e:  # noqa: SIM117
        with index.datasets._db_connection() as conn:
            conn.bulk_simple_dataset_search(batch_size=2)
    assert "within a transaction" in str(e.value)
