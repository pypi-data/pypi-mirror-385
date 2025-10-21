# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
import datetime
from uuid import uuid4

import pytest

import datacube.index.memory.index
from datacube import Datacube
from datacube.cfg import ODCEnvironment
from datacube.model import Range
from datacube.testutils import gen_dataset_test_dag, suppress_deprecations
from datacube.utils import InvalidDocException, SimpleDocNav, read_documents


def test_init_memory(in_memory_config: ODCEnvironment) -> None:
    from datacube.drivers.indexes import index_cache

    idxs = index_cache()
    assert "default" in idxs._drivers
    assert "memory" in idxs._drivers
    with Datacube(env=in_memory_config, validate_connection=True) as dc:
        assert dc.index.url == "memory"
        assert dc.index.environment.index_driver == "memory"


def test_mem_user_resource(mem_index_fresh: Datacube) -> None:
    # Test default user
    assert mem_index_fresh.index.users.list_users() == [
        ("local_user", "localuser", "Default user")
    ]
    # Test create_user success
    mem_index_fresh.index.users.create_user(
        "test_user_1", "password123", "odc_user", "Test1"
    )
    mem_index_fresh.index.users.create_user(
        "test_user_2", "password123", "agdc_user", "Test2"
    )
    users = mem_index_fresh.index.users.list_users()
    assert ("local_user", "localuser", "Default user") in users
    assert ("odc_user", "test_user_1", "Test1") in users
    assert ("agdc_user", "test_user_2", "Test2") in users
    # Test create_user errors

    with pytest.raises(ValueError) as e:
        mem_index_fresh.index.users.create_user(
            "test_user_2", "password123", "agdc_user", "Test2"
        )
    assert "User test_user_2 already exists" in str(e.value)
    with pytest.raises(ValueError) as e:
        mem_index_fresh.index.users.create_user(
            "test_user_3", "password123", "omg_user", "Test3"
        )
    assert "omg_user is not a known role" in str(e.value)
    # Test grant_role success
    mem_index_fresh.index.users.grant_role("agdc_admin", "test_user_1", "test_user_2")
    # Roles can be granted multiple times.
    mem_index_fresh.index.users.grant_role("agdc_admin", "test_user_1", "test_user_2")
    # Test grant_role errors
    with pytest.raises(ValueError) as e:
        mem_index_fresh.index.users.grant_role(
            "omg_admin", "test_user_1", "test_user_2"
        )
    assert "omg_admin is not a known role" in str(e.value)
    with pytest.raises(ValueError) as e:
        mem_index_fresh.index.users.grant_role(
            "odc_admin", "test_user_1", "test_user_3"
        )
    assert "test_user_3 is not a known username" in str(e.value)
    # Test delete_user errors
    with pytest.raises(ValueError) as e:
        mem_index_fresh.index.users.delete_user(
            "test_user_1", "test_user_2", "test_user_3"
        )
    assert "test_user_3 is not a known username" in str(e.value)
    # Confirm one error means no users deleted
    users = mem_index_fresh.index.users.list_users()
    assert ("odc_user", "test_user_1", "Test1") in users
    # Confirm delete error success
    mem_index_fresh.index.users.delete_user("test_user_1", "test_user_2")
    assert mem_index_fresh.index.users.list_users() == [
        ("local_user", "localuser", "Default user")
    ]


def test_mem_metadatatype_resource(mem_index_fresh: Datacube) -> None:
    assert isinstance(mem_index_fresh.index, datacube.index.memory.index.Index)
    assert len(mem_index_fresh.index.metadata_types.by_id) == len(
        mem_index_fresh.index.metadata_types.by_name
    )
    assert len(list(mem_index_fresh.index.metadata_types.get_all())) == 3
    mdt = mem_index_fresh.index.metadata_types.get(1)
    assert mdt is not None and mdt.id == 1
    eo3 = mem_index_fresh.index.metadata_types.get_by_name("eo3")
    assert eo3 is not None and eo3.name == "eo3"
    # Verify we cannot mess with the cache
    eo3.definition["description"] = "foo"  # type: ignore[index]
    eo3.definition["dataset"]["measurements"] = ["over_here", "measurements"]
    eo3_fresh = mem_index_fresh.index.metadata_types.get_by_name("eo3")
    assert eo3_fresh is not None
    assert eo3.description != eo3_fresh.description
    assert (
        eo3.definition["dataset"]["measurements"]
        != eo3_fresh.definition["dataset"]["measurements"]
    )
    # Updating measurements definition is not safe
    with pytest.raises(ValueError):
        mem_index_fresh.index.metadata_types.update(eo3)
    # Updating descriptions is safe.
    eo3_fresh.definition["description"] = "New description"  # type: ignore[index]
    mem_index_fresh.index.metadata_types.update(eo3_fresh)
    eo3_fresher = mem_index_fresh.index.metadata_types.get_by_name("eo3")
    assert eo3_fresher is not None
    assert eo3_fresher.description == eo3_fresh.description
    # Check get_with_fields
    platform_mdts = list(
        mem_index_fresh.index.metadata_types.get_with_fields(["platform"])
    )
    assert len(platform_mdts) == 3
    assert eo3 in platform_mdts
    ptype_mdts = list(
        mem_index_fresh.index.metadata_types.get_with_fields(
            ["platform", "product_type"]
        )
    )
    assert len(ptype_mdts) == 2
    assert eo3 not in ptype_mdts
    pfam_mdts = list(
        mem_index_fresh.index.metadata_types.get_with_fields(
            ["platform", "product_family"]
        )
    )
    assert pfam_mdts == [eo3]


def test_mem_product_resource(
    mem_index_fresh: Datacube,
    extended_eo3_metadata_type_doc,
    extended_eo3_product_doc,
    base_eo3_product_doc,
) -> None:
    assert isinstance(mem_index_fresh.index, datacube.index.memory.index.Index)
    eo3 = mem_index_fresh.index.metadata_types.get_by_name("eo3")
    assert eo3 is not None
    # Test Empty index works as expected:
    assert (
        list(mem_index_fresh.index.products.get_with_fields(("measurements", "extent")))
        == []
    )
    assert list(mem_index_fresh.index.products.search_robust()) == []
    assert list(mem_index_fresh.index.products.get_with_types([eo3])) == []
    assert mem_index_fresh.index.products.get_by_name("product1") is None
    # Add an e03 product doc
    wo_prod = mem_index_fresh.index.products.add_document(base_eo3_product_doc)
    assert wo_prod is not None
    assert wo_prod.name == "ga_ls_wo_3"
    p = mem_index_fresh.index.products.get_by_name("ga_ls_wo_3")
    assert p is not None
    assert p.name == "ga_ls_wo_3"
    # Attempt to add a product without a metadata type
    with pytest.raises(InvalidDocException):
        ls8_prod = mem_index_fresh.index.products.add_document(extended_eo3_product_doc)
    # Add extended eo3 metadatatype
    eo3ext = mem_index_fresh.index.metadata_types.from_doc(
        extended_eo3_metadata_type_doc
    )
    mem_index_fresh.index.metadata_types.add(eo3ext)
    # Add an extended eo3 product doc
    ls8_prod = mem_index_fresh.index.products.add_document(extended_eo3_product_doc)
    assert ls8_prod is not None
    assert ls8_prod.name == "ga_ls8c_ard_3"
    p = mem_index_fresh.index.products.get_by_name("ga_ls8c_ard_3")
    assert p is not None
    assert p.name == "ga_ls8c_ard_3"
    assert list(mem_index_fresh.index.products.get_with_types([eo3ext])) == [ls8_prod]
    # Verify we cannot mess with the cache
    ls8_prod.definition["description"] = "foo"  # type: ignore[index]
    ls8_prod.definition["measurements"][0]["name"] = "blueish"
    ls8_fresh = mem_index_fresh.index.products.get_by_name("ga_ls8c_ard_3")
    assert ls8_fresh is not None
    assert ls8_prod.description != ls8_fresh.description
    assert (
        ls8_prod.definition["measurements"][0]["name"]
        != ls8_fresh.definition["measurements"][0]["name"]
    )
    # Updating measurements definition is not safe
    with pytest.raises(ValueError):
        mem_index_fresh.index.products.update(ls8_prod)
    # Updating descriptions is safe.
    ls8_fresh.definition["description"] = "New description"  # type: ignore[index]
    mem_index_fresh.index.products.update(ls8_fresh)
    ls8_fresher = mem_index_fresh.index.products.get_by_name("ga_ls8c_ard_3")
    assert ls8_fresher is not None
    assert ls8_fresher.description == ls8_fresh.description
    # Test get_with_fields
    assert (
        len(
            list(
                mem_index_fresh.index.products.get_with_fields(
                    ("platform", "product_family")
                )
            )
        )
        == 2
    )
    assert (
        len(
            list(
                mem_index_fresh.index.products.get_with_fields(
                    ("platform", "eo_sun_elevation")
                )
            )
        )
        == 1
    )
    # Test search_robust
    search_results = list(
        mem_index_fresh.index.products.search_robust(region_code="my_backyard")
    )
    assert len(search_results) == 2
    for _, unmatched in search_results:
        assert "region_code" in unmatched
    search_results = list(
        mem_index_fresh.index.products.search_robust(product_family="the_simpsons")
    )
    assert len(search_results) == 0
    search_results = list(
        mem_index_fresh.index.products.search_robust(platform="landsat-8")
    )
    assert len(search_results) == 2
    for prod, unmatched in search_results:
        if prod.name == "ga_ls8c_ard_3":
            assert unmatched == {}
        else:
            assert unmatched["platform"] == "landsat-8"
    # Test search_by_metadata
    lds = list(
        mem_index_fresh.index.products.search_by_metadata({"product_family": "ard"})
    )
    assert len(lds) == 0
    lds = list(
        mem_index_fresh.index.products.search_by_metadata({"odc:product_family": "ard"})
    )
    assert len(lds) == 1
    lds = list(
        mem_index_fresh.index.products.search_by_metadata({"platform": "landsat-8"})
    )
    assert len(lds) == 0
    lds = list(
        mem_index_fresh.index.products.search_by_metadata({"eo:platform": "landsat-8"})
    )
    assert len(lds) == 1
    # Test delete
    mem_index_fresh.index.products.delete([ls8_fresh])
    assert mem_index_fresh.index.products.get_by_name("ga_ls8c_ard_3") is None


# Hand crafted tests with recent real-world eo3 examples
def test_mem_dataset_add_eo3(
    mem_index_eo3: Datacube,
    dataset_with_lineage_doc,
    datasets_with_unembedded_lineage_doc,
) -> None:
    dc = mem_index_eo3
    assert list(dc.index.datasets.get_all_dataset_ids(True)) == []
    assert list(dc.index.datasets.get_all_dataset_ids(False)) == []
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(dc.index)
    with pytest.raises(ValueError) as e:
        _, _ = resolver(dataset_with_lineage_doc[0], dataset_with_lineage_doc[1])
    assert "Embedded lineage not supported for eo3 metadata types" in str(e.value)
    (doc_ls8, loc_ls8), (doc_wo, _) = datasets_with_unembedded_lineage_doc
    assert not dc.index.datasets.has(doc_ls8["id"])
    assert not dc.index.datasets.has(doc_wo["id"])
    assert list(dc.index.datasets.bulk_has((doc_ls8["id"], doc_wo["id"]))) == [
        False,
        False,
    ]

    ds, err = resolver(doc_ls8, loc_ls8)
    assert err is None
    assert ds is not None
    dc.index.datasets.add(ds)
    assert dc.index.datasets.has(doc_ls8["id"])
    ls8_ds = dc.index.datasets.get(doc_ls8["id"], include_sources=True)
    assert ls8_ds is not None
    ds, err = resolver(
        datasets_with_unembedded_lineage_doc[1][0],
        datasets_with_unembedded_lineage_doc[1][1],
    )
    assert err is None
    assert ds is not None
    dc.index.datasets.add(ds)
    assert list(dc.index.datasets.bulk_has((doc_ls8["id"], doc_wo["id"]))) == [
        True,
        True,
    ]


def test_mem_ds_lineage(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    wo_ds = dc.index.datasets.get(wo_id, include_sources=True)
    ls8_ds = wo_ds.sources["ard"]
    assert ls8_ds.id == ls8_id
    wo_ds = dc.index.datasets.get(wo_ds.id, include_sources=False)
    assert not wo_ds.sources
    assert dc.index.datasets.bulk_get((wo_ds.id, ls8_id))
    derived = list(dc.index.datasets.get_derived(ls8_id))
    assert len(derived) == 1
    assert derived[0].id == wo_id
    assert "cloud_cover" in dc.index.products.get_field_names(ls8_ds.product)


def test_mem_ds_search_dups(mem_eo3_data: tuple) -> None:
    dc, ls8_id, _ = mem_eo3_data
    ls8_ds = dc.index.datasets.get(ls8_id)
    dup_results = dc.index.datasets.search_product_duplicates(
        ls8_ds.product, "cloud_cover", "dataset_maturity"
    )
    assert len(dup_results) == 0


def test_mem_ds_locations(mem_eo3_data: tuple) -> None:
    dc, ls8_id, _ = mem_eo3_data
    before_test = datetime.datetime.now()
    ls8ds = dc.index.datasets.get(ls8_id)
    with suppress_deprecations():
        dc.index.datasets.add_location(
            ls8_id, "file:///test_loc_1"
        )  # Test of deprecated method
        assert ls8ds.uri == dc.index.datasets.get_location(ls8_id)
        assert "file:///test_loc_1" in dc.index.datasets.get_locations(
            ls8_id
        )  # Test of deprecated method
        assert (
            list(dc.index.datasets.get_archived_locations(ls8_id)) == []
        )  # Test of deprecated method
        dc.index.datasets.archive_location(
            ls8_id, "file:///test_loc_1"
        )  # Test of deprecated method
        assert "file:///test_loc_1" not in dc.index.datasets.get_locations(
            ls8_id
        )  # Test of deprecated method
        assert "file:///test_loc_1" in dc.index.datasets.get_archived_locations(
            ls8_id
        )  # Test of deprecated method
        found = False
        for loc, dt in dc.index.datasets.get_archived_location_times(
            ls8_id
        ):  # Test of deprecated method
            if loc == "file:///test_loc_1":
                found = True
                assert dt >= before_test
                break
        assert found
        assert dc.index.datasets.restore_location(
            ls8_id, "file:///test_loc_1"
        )  # Test of deprecated method
        assert "file:///test_loc_1" in dc.index.datasets.get_locations(
            ls8_id
        )  # Test of deprecated method
        assert (
            list(dc.index.datasets.get_archived_locations(ls8_id)) == []
        )  # Test of deprecated method
        assert (
            next(
                iter(
                    dc.index.datasets.get_datasets_for_location(
                        "file:///test_loc_1", "exact"
                    )
                )
            ).id
            == ls8_id
        )
        assert dc.index.datasets.remove_location(
            ls8_id, "file:///test_loc_1"
        )  # Test of deprecated method
        assert "file:///test_loc_1" not in dc.index.datasets.get_locations(
            ls8_id
        )  # Test of deprecated method
        assert "file:///test_loc_1" not in dc.index.datasets.get_archived_locations(
            ls8_id
        )  # Test of deprecated method
        assert dc.index.datasets.add_location(
            ls8_id, "file:///test_loc_2"
        )  # Test of deprecated method

        assert "file:///test_loc_2" in dc.index.datasets.get_locations(
            ls8_id
        )  # Test of deprecated method
        ds = dc.index.datasets.get(ls8_id)
        assert ds.uri in ds.uris  # Test of deprecated property

        assert dc.index.datasets.archive_location(
            ls8_id, "file:///test_loc_2"
        )  # Test of deprecated method
        assert dc.index.datasets.remove_location(
            ls8_id, "file:///test_loc_2"
        )  # Test of deprecated method
        assert "file:///test_loc_2" not in list(
            dc.index.datasets.get_locations(ls8_id)
        )  # Test of deprecated method
        assert "file:///test_loc_2" not in list(
            dc.index.datasets.get_archived_locations(
                ls8_id
            )  # Test of deprecated method
        )
        assert not dc.index.datasets.archive_location(
            ls8_id, "file:////not_a_valid_loc"
        )  # Test of deprecated method
        assert not dc.index.datasets.remove_location(
            ls8_id, "file:////not_a_valid_loc"
        )  # Test of deprecated method
        assert dc.index.datasets.remove_location(ls8_id, ls8ds.uri)
    ls8ds = dc.index.datasets.get(ls8_id)
    assert ls8ds.uri is None
    assert dc.index.datasets.get_location(ls8_id) is None


def test_mem_ds_updates(mem_eo3_data: tuple) -> None:
    dc, ls8_id, _ = mem_eo3_data
    # Test updates
    raw = dc.index.datasets.get(ls8_id)
    # Update location only
    raw._uris.append("file:///update_test_1")
    with suppress_deprecations():
        updated = dc.index.datasets.update(raw)
        raw = dc.index.datasets.get(ls8_id)
        assert raw._uris == updated.uris
        # Test bad change
        raw._uris.append("file:///update_test_2")
        raw.metadata_doc["properties"]["silly_sausages"] = ["weisswurst", "frankfurter"]
        with pytest.raises(ValueError):
            updated = dc.index.datasets.update(raw)
        assert "file:///update_test_2" in raw._uris
        # Make bad change ok
        from datacube.utils import changes

        updated = dc.index.datasets.update(
            raw, updates_allowed={("properties", "silly_sausages"): changes.allow_any}
        )
        assert "silly_sausages" in updated.metadata_doc["properties"]
        raw = dc.index.datasets.get(ls8_id)
    assert "silly_sausages" in raw.metadata_doc["properties"]
    assert "file:///update_test_1" in raw._uris
    assert "file:///update_test_2" in raw._uris


def test_mem_ds_expand_periods(mem_index_fresh: Datacube) -> None:
    assert isinstance(mem_index_fresh.index, datacube.index.memory.index.Index)
    periods = list(
        mem_index_fresh.index.datasets._expand_period(
            "1 day",
            datetime.datetime(2016, 5, 5),
            datetime.datetime(2016, 5, 8),
        )
    )
    assert periods == [
        Range(
            datetime.datetime(2016, 5, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 6, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 5, 6, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 7, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 5, 7, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 8, tzinfo=datetime.timezone.utc),
        ),
    ]
    periods = list(
        mem_index_fresh.index.datasets._expand_period(
            "2 days",
            datetime.datetime(2016, 5, 5),
            datetime.datetime(2016, 5, 8),
        )
    )
    assert periods == [
        Range(
            datetime.datetime(2016, 5, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 7, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 5, 7, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 9, tzinfo=datetime.timezone.utc),
        ),
    ]
    periods = list(
        mem_index_fresh.index.datasets._expand_period(
            "1 weeks",
            datetime.datetime(2016, 5, 1),
            datetime.datetime(2016, 5, 25),
        )
    )
    assert periods == [
        Range(
            datetime.datetime(2016, 5, 1, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 8, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 5, 8, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 15, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 5, 15, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 22, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 5, 22, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 29, tzinfo=datetime.timezone.utc),
        ),
    ]
    periods = list(
        mem_index_fresh.index.datasets._expand_period(
            "2 months",
            datetime.datetime(2016, 3, 5),
            datetime.datetime(2016, 12, 25),
        )
    )
    assert periods == [
        Range(
            datetime.datetime(2016, 3, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 5, 5, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 5, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 7, 5, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 7, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 9, 5, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 9, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2016, 11, 5, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2016, 11, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2017, 1, 5, tzinfo=datetime.timezone.utc),
        ),
    ]
    periods = list(
        mem_index_fresh.index.datasets._expand_period(
            "2 years",
            datetime.datetime(2016, 3, 5),
            datetime.datetime(2019, 12, 25),
        )
    )
    assert periods == [
        Range(
            datetime.datetime(2016, 3, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2018, 3, 5, tzinfo=datetime.timezone.utc),
        ),
        Range(
            datetime.datetime(2018, 3, 5, tzinfo=datetime.timezone.utc),
            datetime.datetime(2020, 3, 5, tzinfo=datetime.timezone.utc),
        ),
    ]


def test_spatiotemporal_extent(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    ls8 = dc.index.datasets.get(ls8_id)
    wo = dc.index.datasets.get(wo_id)
    with pytest.raises(KeyError):
        dc.index.datasets.temporal_extent(ids=[uuid4()])

    with suppress_deprecations(), pytest.raises(KeyError):
        dc.index.datasets.get_product_time_bounds(
            "orthentik_producked"
        )  # Test of deprecated method

    # Test get_product_time_bounds
    for ds in (ls8, wo):
        with suppress_deprecations():
            tmin, tmax = dc.index.datasets.get_product_time_bounds(
                ds.product.name
            )  # Test of deprecated method
        assert (tmin is None and tmax is None) or tmin < tmax
        tmin2, tmax2 = dc.index.products.temporal_extent(product=ds.product)
        assert tmin2 == tmin and tmax2 == tmax
        ids = [
            doc["id"]
            for prod, doc, uris in dc.index.datasets.get_all_docs_for_product(
                product=ds.product
            )
        ]
        tmin2, tmax2 = dc.index.datasets.temporal_extent(ids=ids)
        assert tmin2 == tmin and tmax2 == tmax

    # Spatial extent
    assert dc.index.products.spatial_extent(ls8.product) is None
    assert dc.index.datasets.spatial_extent([ls8_id, wo_id]) is None


def test_mem_ds_archive_purge(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    # Test archiving, restoring and purging datasets
    # Both datasets are not archived
    all_ids = list(dc.index.datasets.get_all_dataset_ids(False))
    assert ls8_id in all_ids
    assert wo_id in all_ids
    assert list(dc.index.datasets.get_all_dataset_ids(True)) == []
    # Archive both datasets
    dc.index.datasets.archive((wo_id, ls8_id))
    # Both datasets ARE archived
    all_ids = list(dc.index.datasets.get_all_dataset_ids(True))
    assert ls8_id in all_ids
    assert wo_id in all_ids
    assert list(dc.index.datasets.get_all_dataset_ids(False)) == []
    archived_ls_ds = dc.index.datasets.get(ls8_id)
    assert archived_ls_ds.is_archived
    # Purge ls8_ds and restore wo_ds
    dc.index.datasets.purge((ls8_id,))
    dc.index.datasets.restore((wo_id,))
    active_ids = list(dc.index.datasets.get_all_dataset_ids(False))
    archived_ids = list(dc.index.datasets.get_all_dataset_ids(True))
    assert ls8_id not in active_ids
    assert wo_id in active_ids
    assert archived_ids == []
    # And archive wo_ds again
    dc.index.datasets.archive((wo_id,))
    assert list(dc.index.datasets.get_all_dataset_ids(False)) == []


def test_mem_ds_search_and_count(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    # No source_filter; no results
    assert not list(dc.index.datasets.search(platform="deplatformed"))
    lds = list(dc.index.datasets.search(platform="landsat-8"))
    assert len(lds) == 2
    assert dc.index.datasets.count(platform="landsat-8") == 2
    lds = list(dc.index.datasets.search(platform="landsat-8", limit=1))
    assert len(lds) == 1
    with suppress_deprecations():
        # Testing source_filter arg, which is deprecated
        lds = list(dc.index.datasets.search(source_filter={"product_family": "ard"}))
        assert len(lds) == 1
        assert dc.index.datasets.count(source_filter={"product_family": "ard"}) == 1
        lds = list(
            dc.index.datasets.search(
                platform="landsat-8", source_filter={"product_family": "ard"}
            )
        )
        assert len(lds) == 1
        lds = list(
            dc.index.datasets.search(
                product_family="wo", source_filter={"product_family": "ard"}
            )
        )
        assert len(lds) == 1
        lds = list(
            dc.index.datasets.search(
                product_family="ard", source_filter={"product_family": "ard"}
            )
        )
        assert len(lds) == 0
        assert (
            dc.index.datasets.count(
                product_family="ard", source_filter={"product_family": "ard"}
            )
            == 0
        )
    lds = list(dc.index.datasets.search(product="ga_ls_wo_3", platform="landsat-8"))
    assert len(lds) == 1
    with pytest.raises(ValueError):
        lds = list(dc.index.datasets.search(product="weird_whacky_product"))
    with pytest.raises(ValueError):
        lds = list(dc.index.datasets.search(product_family="addams"))

    lds = list(dc.index.datasets.search(archived=None, platform="landsat-8"))
    assert len(lds) == 2
    lds = list(dc.index.datasets.search(archived=True, platform="landsat-8"))
    assert len(lds) == 0

    dc.index.datasets.archive([ls8_id, wo_id])
    lds = list(dc.index.datasets.search(platform="landsat-8"))
    assert len(lds) == 0
    lds = list(dc.index.datasets.search(archived=None, platform="landsat-8"))
    assert len(lds) == 2
    lds = list(dc.index.datasets.search(archived=True, platform="landsat-8"))
    assert len(lds) == 2


def test_mem_ds_search_and_count_by_product(mem_eo3_data: tuple) -> None:
    dc, _, _ = mem_eo3_data
    # No source_filter; no results
    assert not list(dc.index.datasets.search_by_product(platform="deplatformed"))
    lds = list(dc.index.datasets.search_by_product(platform="landsat-8"))
    assert len(lds) == 2
    for product, dss in lds:
        for ds in dss:
            assert ds.product.name == product.name
    lds = list(dc.index.datasets.count_by_product(platform="landsat-8"))
    assert len(lds) == 2
    for _, count in lds:
        assert count == 1


def test_mem_ds_search_returning(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    lds = list(
        dc.index.datasets.search_returning(
            field_names=["platform", "id", "product_family"], platform="landsat-8"
        )
    )
    assert len(lds) == 2
    for res in lds:
        assert res.platform == "landsat-8"
        assert res.id in (str(ls8_id), str(wo_id))
    lds = list(dc.index.datasets.search_returning(platform="landsat-8"))
    assert len(lds) == 2
    for res in lds:
        assert res.platform == "landsat-8"
        assert res.id in (str(ls8_id), str(wo_id))
    lds = list(
        dc.index.datasets.search_returning(
            field_names=["id", "platform"],
            custom_offsets={
                "cloud_cover": ["properties", "eo:cloud_cover"],
                "instrument": ["properties", "eo:instrument"],
            },
            platform="landsat-8",
        )
    )
    assert len(lds) == 2
    for res in lds:
        assert res.platform == "landsat-8"
        assert res.id in (str(ls8_id), str(wo_id))
        assert res.cloud_cover < 59.0 and res.cloud_cover > 58.9
        assert res.instrument.endswith("OLI_TIRS")
    lds = list(
        dc.index.datasets.search_returning(
            custom_offsets={
                "cloud_cover": ["properties", "eo:cloud_cover"],
                "instrument": ["properties", "eo:instrument"],
            },
            platform="landsat-8",
        )
    )
    for res in lds:
        assert res.cloud_cover < 59.0 and res.cloud_cover > 58.9
        assert res.instrument.endswith("OLI_TIRS")
        with pytest.raises(AttributeError):
            assert res.id in (str(ls8_id), str(wo_id))


def test_mem_ds_search_summary(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    lds = list(dc.index.datasets.search_returning(platform="landsat-8"))
    assert len(lds) == 2
    for res in lds:
        assert res.platform == "landsat-8"
        assert res.id in (str(ls8_id), str(wo_id))


def test_mem_ds_search_returning_datasets_light(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    lds = list(
        dc.index.datasets.search_returning_datasets_light(
            field_names=["platform", "id"], platform="landsat-8"
        )
    )
    assert len(lds) == 2
    for res in lds:
        assert res.__class__.__name__ == "DatasetLight"
        assert res.platform == "landsat-8"
        assert res.id in (str(ls8_id), str(wo_id))
    lds = list(
        dc.index.datasets.search_returning_datasets_light(
            archived=None, field_names=["platform", "id"], platform="landsat-8"
        )
    )
    assert len(lds) == 2
    lds = list(
        dc.index.datasets.search_returning_datasets_light(
            archived=True, field_names=["platform", "id"], platform="landsat-8"
        )
    )
    assert len(lds) == 0


def test_mem_ds_search_by_metadata(mem_eo3_data: tuple) -> None:
    dc, ls8_id, wo_id = mem_eo3_data
    lds = list(
        dc.index.datasets.search_by_metadata({"properties": {"product_family": "ard"}})
    )
    assert len(lds) == 0
    lds = list(
        dc.index.datasets.search_by_metadata(
            {"properties": {"odc:product_family": "ard"}}
        )
    )
    assert len(lds) == 1
    lds = list(
        dc.index.datasets.search_by_metadata({"properties": {"platform": "landsat-8"}})
    )
    assert len(lds) == 0
    lds = list(
        dc.index.datasets.search_by_metadata(
            {"properties": {"eo:platform": "landsat-8"}}
        )
    )
    assert len(lds) == 2
    lds = list(
        dc.index.datasets.search_by_metadata(
            {"properties": {"eo:platform": "landsat-8"}}, archived=None
        )
    )
    assert len(lds) == 2
    lds = list(
        dc.index.datasets.search_by_metadata(
            {"properties": {"eo:platform": "landsat-8"}}, archived=True
        )
    )
    assert len(lds) == 0
    dc.index.datasets.archive([ls8_id, wo_id])
    lds = list(
        dc.index.datasets.search_by_metadata(
            {"properties": {"eo:platform": "landsat-8"}}
        )
    )
    assert len(lds) == 0
    lds = list(
        dc.index.datasets.search_by_metadata(
            {"properties": {"eo:platform": "landsat-8"}}, archived=None
        )
    )
    assert len(lds) == 2
    lds = list(
        dc.index.datasets.search_by_metadata(
            {"properties": {"eo:platform": "landsat-8"}}, archived=True
        )
    )
    assert len(lds) == 2


def test_mem_ds_count_product_through_time(mem_eo3_data: tuple) -> None:
    dc, _, _ = mem_eo3_data
    lds = list(
        dc.index.datasets.count_by_product_through_time(
            period="1 day",
            time=[datetime.datetime(2016, 5, 10), datetime.datetime(2016, 5, 15)],
        )
    )
    for _, counts in lds:
        for rng, count in counts:
            if rng.begin == datetime.datetime(
                2016, 5, 12, tzinfo=datetime.timezone.utc
            ):
                assert count == 1
            else:
                assert count == 0

    counts = list(
        dc.index.datasets.count_product_through_time(
            period="1 month",
            product="ga_ls_wo_3",
            time=[datetime.datetime(2016, 4, 1), datetime.datetime(2016, 12, 1)],
        )
    )
    for rng, count in counts:
        if rng.begin == datetime.datetime(2016, 5, 1, tzinfo=datetime.timezone.utc):
            assert count == 1
        else:
            assert count == 0


# Tests adapted from test_dataset_add
def test_memory_dataset_add(dataset_add_configs, mem_index_fresh: Datacube) -> None:
    assert isinstance(mem_index_fresh.index, datacube.index.memory.index.Index)
    idx = mem_index_fresh.index
    # Make sure index is empty
    assert list(idx.products.get_all()) == []
    for _, metadata_doc in read_documents(dataset_add_configs.metadata):
        idx.metadata_types.add(idx.metadata_types.from_doc(metadata_doc))
    for _, product_doc in read_documents(dataset_add_configs.products):
        idx.products.add_document(product_doc)
    ds_ids = set()
    ds_bad_ids = set()
    from datacube.index.hl import Doc2Dataset

    resolver = Doc2Dataset(idx)
    for _, ds_doc in read_documents(dataset_add_configs.datasets):
        ds, err = resolver(ds_doc, "file:///fake_uri")
        assert err is None
        assert ds is not None
        ds_ids.add(ds.id)
        idx.datasets.add(ds)
    for _, ds_doc in read_documents(dataset_add_configs.datasets_bad1):
        ds, err = resolver(ds_doc, "file:///fake_bad_uri")
        if err is not None:
            ds_bad_ids.add(ds_doc["id"])
            continue
        assert ds is not None
        ds_ids.add(ds.id)
        idx.datasets.add(ds)
    for _, ds_doc in read_documents(dataset_add_configs.datasets_eo3):
        ds, err = resolver(ds_doc, "file:///fake_eo3_uri")
        assert err is None
        assert ds is not None
        ds_ids.add(ds.id)
        idx.datasets.add(ds)

    for id_ in ds_ids:
        assert idx.datasets.has(id_)
    for id_ in ds_bad_ids:
        assert not idx.datasets.has(id_)
    loc_matches = idx.datasets.get_datasets_for_location("file:///fake", mode="prefix")
    loc_ids = [loc.id for loc in loc_matches]
    for id_ in ds_ids:
        assert id_ in loc_ids
    ds_ = SimpleDocNav(gen_dataset_test_dag(1, force_tree=True))
    assert ds_.id in ds_ids
    ds_from_idx = idx.datasets.get(ds_.id, include_sources=True)
    assert ds_from_idx is not None
    assert ds_from_idx.sources is not None
    assert ds_from_idx.sources["ab"].id == ds_.sources["ab"].id
    p1 = ds_from_idx.sources["ac"]
    assert p1 is not None
    assert p1.sources is not None
    p2 = ds_.sources["ac"]
    assert p2 is not None
    assert p2.sources is not None
    assert p1.sources["cd"].id == p2.sources["cd"].id


def test_mem_transactions(mem_index_fresh: Datacube) -> None:
    trans = mem_index_fresh.index.transaction()
    assert not trans.active
    trans.begin()
    assert trans.active
    trans.commit()
    assert not trans.active
    trans.begin()
    assert mem_index_fresh.index.thread_transaction() == trans
    with pytest.raises(ValueError):
        trans.begin()
    trans.rollback()
    assert not trans.active
    assert mem_index_fresh.index.thread_transaction() is None


def test_default_clone_bulk_ops(
    mem_index_fresh: Datacube,
    index,
    extended_eo3_metadata_type,
    ls8_eo3_product,
    wo_eo3_product,
    africa_s2_eo3_product,
    ls8_eo3_dataset,
    ls8_eo3_dataset2,
    ls8_eo3_dataset3,
    ls8_eo3_dataset4,
    wo_eo3_dataset,
    africa_eo3_dataset,
) -> None:
    mem_index_fresh.index.clone(index)
    assert mem_index_fresh.index.datasets.has(africa_eo3_dataset.id)
    assert mem_index_fresh.index.datasets.has(wo_eo3_dataset.id)
    assert mem_index_fresh.index.datasets.has(ls8_eo3_dataset.id)
    assert mem_index_fresh.index.datasets.has(ls8_eo3_dataset4.id)


@pytest.mark.parametrize("datacube_env_name", ("datacube", "datacube3"))
def test_default_clone_bulk_ops_multiloc(
    mem_index_fresh: Datacube,
    index,
    extended_eo3_metadata_type,
    ls8_eo3_product,
    wo_eo3_product,
    africa_s2_eo3_product,
    ls8_eo3_dataset,
    ls8_eo3_dataset2,
    ls8_eo3_dataset3,
    ls8_eo3_dataset4,
    wo_eo3_dataset,
    africa_eo3_dataset,
) -> None:
    with suppress_deprecations():
        index.datasets.add_location(ls8_eo3_dataset.id, "file:///a/o/fish")
        mem_index_fresh.index.clone(index)
        assert mem_index_fresh.index.datasets.has(africa_eo3_dataset.id)
        assert mem_index_fresh.index.datasets.has(wo_eo3_dataset.id)
        assert mem_index_fresh.index.datasets.has(ls8_eo3_dataset.id)
        assert mem_index_fresh.index.datasets.has(ls8_eo3_dataset4.id)
        d = mem_index_fresh.index.datasets.get(ls8_eo3_dataset.id)
        assert d is not None
        assert len(d._uris) == 2


@pytest.mark.filterwarnings("ignore::antimeridian.FixWindingWarning")
def test_default_clone_bulk_ops_reverse(mem_eo3_data: tuple, index) -> None:
    mem_idx, ls8id, woid = mem_eo3_data
    index.clone(mem_idx.index)
    assert index.datasets.has(ls8id)
    assert index.datasets.has(woid)
