# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from datacube import Datacube
from datacube.cfg import ODCEnvironment
from datacube.testutils import suppress_deprecations

test_uuid = UUID("4ec8fe97-e8b9-11e4-87ff-1040f381a756")


def empty(iterable) -> bool:
    for _ in iterable:
        return False
    return True


def test_init_null(null_config: ODCEnvironment) -> None:
    from datacube.drivers.indexes import index_cache

    idxs = index_cache()
    assert "default" in idxs._drivers
    assert "null" in idxs._drivers
    with Datacube(env=null_config, validate_connection=True) as dc:
        assert dc.index.url == "null"
        assert dc.index.environment.index_driver == "null"


def test_null_user_resource(null_config: ODCEnvironment) -> None:
    with Datacube(env=null_config, validate_connection=True) as dc:
        assert empty(dc.index.users.list_users())
        with pytest.raises(NotImplementedError):
            dc.index.users.create_user("user1", "password2", "role1")
        with pytest.raises(NotImplementedError):
            dc.index.users.delete_user("user1", "user2")
        with pytest.raises(NotImplementedError):
            dc.index.users.grant_role("role1", "user1", "user2")


def test_null_metadata_types_resource(null_config: ODCEnvironment) -> None:
    with Datacube(env=null_config, validate_connection=True) as dc:
        assert dc.index.metadata_types.get_all() == []
        with pytest.raises(NotImplementedError):
            dc.index.metadata_types.from_doc({})
        with pytest.raises(NotImplementedError):
            dc.index.metadata_types.add(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.metadata_types.can_update(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.metadata_types.update(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.metadata_types.update_document({})
        with pytest.raises(KeyError):
            dc.index.metadata_types.get_unsafe(1)
        with pytest.raises(KeyError):
            dc.index.metadata_types.get_by_name_unsafe("eo")
        with pytest.raises(NotImplementedError):
            dc.index.metadata_types.check_field_indexes()


def test_null_product_resource(null_config: ODCEnvironment) -> None:
    with Datacube(env=null_config, validate_connection=True) as dc:
        assert dc.index.products.get_all() == []
        assert dc.index.products.search_robust(foo="bar", baz=12) == []
        assert empty(dc.index.products.get_with_fields(["foo", "bar"]))
        assert empty(dc.index.products.get_field_names())
        with pytest.raises(KeyError):
            dc.index.products.spatial_extent("a_prod")
        with pytest.raises(KeyError):
            dc.index.products.temporal_extent("a_prod")
        with pytest.raises(KeyError):
            dc.index.products.get_unsafe(1)
        with pytest.raises(KeyError):
            dc.index.products.get_by_name_unsafe("product1")
        with pytest.raises(NotImplementedError):
            dc.index.products.add(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.products.can_update(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.products.update(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.products.delete(MagicMock())


def test_null_dataset_resource(null_config: ODCEnvironment) -> None:
    with Datacube(env=null_config, validate_connection=True) as dc:
        assert dc.index.datasets.get(test_uuid) is None
        assert dc.index.datasets.bulk_get([test_uuid, "foo"]) == []
        assert dc.index.datasets.get_derived(test_uuid) == []
        assert not dc.index.datasets.has(test_uuid)
        assert dc.index.datasets.bulk_has([test_uuid, "foo"]) == [False, False]
        with pytest.raises(NotImplementedError):
            dc.index.datasets.add(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.datasets.can_update(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.datasets.update(MagicMock())
        with pytest.raises(NotImplementedError):
            dc.index.datasets.archive([test_uuid, "foo"])
        with pytest.raises(NotImplementedError):
            dc.index.datasets.restore([test_uuid, "foo"])
        with pytest.raises(NotImplementedError):
            dc.index.datasets.purge([test_uuid, "foo"])

        assert empty(dc.index.datasets.get_all_dataset_ids(True))
        assert dc.index.datasets.get_location(test_uuid) is None
        assert dc.index.datasets.get_datasets_for_location("http://a.uri/test") == []

        with suppress_deprecations():
            assert empty(
                dc.index.datasets.get_field_names()
            )  # DEPRECATED WRAPPER METHOD
            assert (
                dc.index.datasets.get_locations(test_uuid) == []
            )  # Test deprecated method
            assert (
                dc.index.datasets.get_archived_locations(test_uuid) == []
            )  # Test deprecated method
            assert (
                dc.index.datasets.get_archived_location_times(test_uuid) == []
            )  # Test deprecated method

            with pytest.raises(NotImplementedError):
                dc.index.datasets.add_location(
                    test_uuid, "http://a.uri/test"
                )  # Test deprecated method
            with pytest.raises(NotImplementedError):
                dc.index.datasets.remove_location(
                    test_uuid, "http://a.uri/test"
                )  # Test deprecated method
            with pytest.raises(NotImplementedError):
                dc.index.datasets.archive_location(
                    test_uuid, "http://a.uri/test"
                )  # Test deprecated method
            with pytest.raises(NotImplementedError):
                dc.index.datasets.restore_location(
                    test_uuid, "http://a.uri/test"
                )  # Test deprecated method
        with pytest.raises(KeyError):
            dc.index.datasets.temporal_extent(ids=[test_uuid])
        assert dc.index.datasets.spatial_extent(ids=[test_uuid]) is None
        with suppress_deprecations(), pytest.raises(KeyError):
            dc.index.datasets.get_product_time_bounds(
                "product1"
            )  # Test deprecated method

        assert dc.index.datasets.search_product_duplicates(MagicMock()) == []
        assert dc.index.datasets.search_by_metadata({}) == []
        assert dc.index.datasets.search(foo="bar", baz=12) == []
        assert dc.index.datasets.search_by_product(foo="bar", baz=12) == []
        assert (
            list(dc.index.datasets.search_returning(["foo", "bar"], foo="bar", baz=12))
            == []
        )
        assert dc.index.datasets.count(foo="bar", baz=12) == 0
        assert dc.index.datasets.count_by_product(foo="bar", baz=12) == []
        assert (
            dc.index.datasets.count_by_product_through_time(
                "1 month", foo="bar", baz=12
            )
            == []
        )
        assert (
            dc.index.datasets.count_product_through_time("1 month", foo="bar", baz=12)
            == []
        )
        with suppress_deprecations():
            # Coverage test of deprecated method
            assert dc.index.datasets.search_summaries(foo="bar", baz=12) == []
            # Coverage test of deprecated base class method
            assert dc.index.datasets.search_eager(foo="bar", baz=12) == []
        assert (
            dc.index.datasets.search_returning_datasets_light(
                ("foo", "baz"), foo="bar", baz=12
            )
            == []
        )


def test_null_transactions(null_config: ODCEnvironment) -> None:
    with Datacube(env=null_config, validate_connection=True) as dc:
        trans = dc.index.transaction()
        assert not trans.active
        trans.begin()
        assert trans.active
        trans.commit()
        assert not trans.active
        trans.begin()
        assert dc.index.thread_transaction() == trans
        with pytest.raises(ValueError):
            trans.begin()
        trans.rollback()
        assert not trans.active
        assert dc.index.thread_transaction() is None
