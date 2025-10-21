# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Module
"""

import datetime
import warnings
from collections import namedtuple
from datetime import timezone
from typing import Any

import pytest
import yaml
from antimeridian import FixWindingWarning

import datacube.scripts.cli_app
import datacube.scripts.search_tool
from datacube import Datacube
from datacube.cfg import ODCEnvironment
from datacube.cfg.opt import _DEFAULT_DB_USER
from datacube.index import Index
from datacube.model import Dataset, Range
from datacube.testutils import suppress_deprecations
from datacube.utils.dates import tz_as_utc

from .search_utils import _cli_csv_search, _csv_search_raw, _load_product_query


def test_search_by_metadata(index: Index, ls8_eo3_product, wo_eo3_product) -> None:
    lds = list(
        index.products.search_by_metadata({"properties": {"product_family": "ard"}})
    )
    assert len(lds) == 0
    lds = list(
        index.products.search_by_metadata({"properties": {"odc:product_family": "ard"}})
    )
    assert len(lds) == 1
    lds = list(
        index.products.search_by_metadata({"properties": {"platform": "landsat-8"}})
    )
    assert len(lds) == 0
    lds = list(
        index.products.search_by_metadata({"properties": {"eo:platform": "landsat-8"}})
    )
    assert len(lds) == 1


def test_find_most_recent_change(
    index: Index, ls8_eo3_dataset, ls8_eo3_dataset2, ls8_eo3_dataset3
) -> None:
    product = ls8_eo3_dataset.product
    dt = index.products.most_recent_change(product)
    assert dt == ls8_eo3_dataset3.indexed_time
    index.datasets.archive([ls8_eo3_dataset.id, ls8_eo3_dataset2.id])
    dt = index.products.most_recent_change(product.name)
    d = index.datasets.get(ls8_eo3_dataset2.id)
    assert d is not None
    assert dt == d.archived_time


def test_search_dataset_equals_eo3(index: Index, ls8_eo3_dataset: Dataset) -> None:
    datasets = list(index.datasets.search(platform="landsat-8"))
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    datasets = list(index.datasets.search(platform="landsat-8", instrument="OLI_TIRS"))
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    # Wrong product family
    with pytest.raises(ValueError):
        next(
            index.datasets.search(
                platform="landsat-8",
                product_family="splunge",
            )
        )


def test_search_dataset_range_eo3(
    index: Index,
    ls8_eo3_dataset: Dataset,
    ls8_eo3_dataset2: Dataset,
    ls8_eo3_dataset3: Dataset,
    ls8_eo3_dataset4: Dataset,
) -> None:
    # Less Than
    datasets = list(
        index.datasets.search(
            product=ls8_eo3_dataset.product.name, cloud_cover=Range(0.0, 50.0)
        )
    )
    assert len(datasets) == 2
    ids = [ds.id for ds in datasets]
    assert ls8_eo3_dataset3.id in ids
    assert ls8_eo3_dataset4.id in ids

    # Greater than
    datasets = list(
        index.datasets.search(
            product=ls8_eo3_dataset.product.name, cloud_cover=Range(50.0, 100.0)
        )
    )
    assert len(datasets) == 2
    ids = [ds.id for ds in datasets]
    assert ls8_eo3_dataset.id in ids
    assert ls8_eo3_dataset2.id in ids

    # Full Range comparison
    datasets = list(
        index.datasets.search(
            product=ls8_eo3_dataset.product.name, cloud_cover=Range(20.0, 55.0)
        )
    )
    assert len(datasets) == 2
    ids = [ds.id for ds in datasets]
    assert ls8_eo3_dataset2.id in ids
    assert ls8_eo3_dataset3.id in ids


def test_search_dataset_by_metadata_eo3(index: Index, ls8_eo3_dataset: Dataset) -> None:
    datasets = index.datasets.search_by_metadata(
        {"properties": {"eo:platform": "landsat-8", "eo:instrument": "OLI_TIRS"}}
    )
    datasets = list(datasets)
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    datasets = index.datasets.search_by_metadata(
        {"properties": {"eo:platform": "landsat-5", "eo:instrument": "TM"}}
    )
    datasets = list(datasets)
    assert len(datasets) == 0
    datasets = index.datasets.search_by_metadata(
        {"properties": {"eo:platform": "landsat-8", "eo:instrument": "OLI_TIRS"}},
        archived=None,
    )
    datasets = list(datasets)
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id
    datasets = index.datasets.search_by_metadata(
        {"properties": {"eo:platform": "landsat-8", "eo:instrument": "OLI_TIRS"}},
        archived=True,
    )
    datasets = list(datasets)
    assert len(datasets) == 0

    index.datasets.archive([ls8_eo3_dataset.id])

    datasets = index.datasets.search_by_metadata(
        {"properties": {"eo:platform": "landsat-8", "eo:instrument": "OLI_TIRS"}},
        archived=None,
    )
    datasets = list(datasets)
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id
    datasets = index.datasets.search_by_metadata(
        {"properties": {"eo:platform": "landsat-8", "eo:instrument": "OLI_TIRS"}},
        archived=True,
    )
    datasets = list(datasets)
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id


def test_search_day_eo3(index: Index, ls8_eo3_dataset: Dataset) -> None:
    # Matches day
    datasets = list(index.datasets.search(time=datetime.date(2016, 5, 12)))
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    # Different day: no match
    datasets = list(index.datasets.search(time=datetime.date(2016, 5, 13)))
    assert len(datasets) == 0


def test_search_dataset_ranges_eo3(index: Index, ls8_eo3_dataset: Dataset) -> None:
    # In the lat bounds.
    datasets = list(
        index.datasets.search(
            lat=Range(-37.5, -36.5),
            time=Range(
                datetime.datetime(2016, 5, 12, 23, 0, 0),
                datetime.datetime(2016, 5, 12, 23, 59, 59),
            ),
        )
    )
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    # Out of the lat bounds.
    datasets = list(
        index.datasets.search(
            lat=Range(28, 32),
            time=Range(
                datetime.datetime(2016, 5, 12, 23, 0, 0),
                datetime.datetime(2016, 5, 12, 23, 59, 59),
            ),
        )
    )
    assert len(datasets) == 0

    # Out of the time bounds
    datasets = list(
        index.datasets.search(
            lat=Range(-37.5, -36.5),
            time=Range(
                datetime.datetime(2014, 7, 26, 21, 48, 0),
                datetime.datetime(2014, 7, 26, 21, 50, 0),
            ),
        )
    )
    assert len(datasets) == 0

    # A dataset that overlaps but is not fully contained by the search bounds.
    # Should we distinguish between 'contains' and 'overlaps'?
    datasets = list(index.datasets.search(lat=Range(-40, -37.1)))
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    # Single point search
    datasets = list(
        index.datasets.search(
            lat=-37.0,
            time=Range(
                datetime.datetime(2016, 5, 12, 23, 0, 0),
                datetime.datetime(2016, 5, 12, 23, 59, 59),
            ),
        )
    )
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    datasets = list(
        index.datasets.search(
            lat=30.0,
            time=Range(
                datetime.datetime(2016, 5, 12, 23, 0, 0),
                datetime.datetime(2016, 5, 12, 23, 59, 59),
            ),
        )
    )
    assert len(datasets) == 0

    # Single timestamp search
    datasets = list(
        index.datasets.search(
            lat=Range(-37.5, -36.5),
            time=datetime.datetime(2016, 5, 12, 23, 50, 40),
        )
    )
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    datasets = list(
        index.datasets.search(
            lat=Range(-37.5, -36.5), time=datetime.datetime(2016, 5, 12, 23, 0, 0)
        )
    )
    assert len(datasets) == 0


def test_zero_width_range_search(index: Index, ls8_eo3_dataset4: Dataset) -> None:
    # Test time search against zero-width time metadata
    datasets = list(
        index.datasets.search(
            time=Range(
                begin=datetime.datetime(
                    2013, 7, 21, 0, 57, 26, 432563, tzinfo=datetime.timezone.utc
                ),
                end=datetime.datetime(
                    2013, 7, 21, 0, 57, 26, 432563, tzinfo=datetime.timezone.utc
                ),
            )
        )
    )
    assert len(datasets) == 1

    datasets = list(
        index.datasets.search(
            time=Range(
                begin=datetime.datetime(
                    2013, 7, 21, 0, 57, 26, 432563, tzinfo=datetime.timezone.utc
                ),
                end=datetime.datetime(
                    2013, 7, 21, 0, 57, 27, 432563, tzinfo=datetime.timezone.utc
                ),
            )
        )
    )
    assert len(datasets) == 1

    datasets = list(
        index.datasets.search(
            time=Range(
                begin=datetime.datetime(
                    2013, 7, 21, 0, 57, 25, 432563, tzinfo=datetime.timezone.utc
                ),
                end=datetime.datetime(
                    2013, 7, 21, 0, 57, 26, 432563, tzinfo=datetime.timezone.utc
                ),
            )
        )
    )
    assert len(datasets) == 1


def test_search_globally_eo3(index: Index, ls8_eo3_dataset: Dataset) -> None:
    # No expressions means get all.
    results = list(index.datasets.search())
    assert len(results) == 1

    # Dataset sources aren't loaded by default
    assert results[0].sources is None


def test_search_by_product_eo3(
    index: Index,
    base_eo3_product_doc: dict,
    ls8_eo3_dataset: Dataset,
    wo_eo3_dataset: Dataset,
) -> None:
    # Query all the test data, the counts should match expected
    results = _load_product_query(index.datasets.search_by_product())
    assert len(results) == 2
    dataset_count = sum(len(ds) for ds in results.values())
    assert dataset_count == 2

    # Query one product
    products = _load_product_query(
        index.datasets.search_by_product(platform="landsat-8", product_family="wo")
    )
    assert len(products) == 1
    [dataset] = products[base_eo3_product_doc["name"]]
    assert dataset.id == wo_eo3_dataset.id
    assert dataset.is_eo3
    with suppress_deprecations():
        assert dataset.type == dataset.product  # DEPRECATED MEMBER


def test_search_limit_eo3(
    index: Index, ls8_eo3_dataset, ls8_eo3_dataset2, wo_eo3_dataset
) -> None:
    prod = ls8_eo3_dataset.product.name
    datasets = list(index.datasets.search(product=prod))
    assert len(datasets) == 2
    datasets = list(index.datasets.search(limit=1, product=prod))
    ids = [ds.id for ds in datasets]
    assert len(ids) == 1
    assert len(datasets) == 1
    datasets = list(index.datasets.search(limit=0, product=prod))
    assert len(datasets) == 0
    datasets = list(index.datasets.search(limit=5, product=prod))
    assert len(datasets) == 2

    datasets = list(index.datasets.search_returning(("id",), product=prod))
    assert len(datasets) == 2
    datasets = list(index.datasets.search_returning(("id",), limit=1, product=prod))
    assert len(datasets) == 1
    datasets = list(index.datasets.search_returning(("id",), limit=0, product=prod))
    assert len(datasets) == 0
    datasets = list(index.datasets.search_returning(("id",), limit=5, product=prod))
    assert len(datasets) == 2

    # Limit is per product not overall.  (But why?!?)
    datasets = list(index.datasets.search())
    assert len(datasets) == 3
    datasets = list(index.datasets.search(limit=1))
    assert len(datasets) == 2
    datasets = list(index.datasets.search(limit=0))
    assert len(datasets) == 0
    datasets = list(index.datasets.search(limit=5))
    assert len(datasets) == 3

    datasets = list(index.datasets.search_returning(("id",)))
    assert len(datasets) == 3
    datasets = list(index.datasets.search_returning(("id",), limit=1))
    assert len(datasets) == 2
    datasets = list(index.datasets.search_returning(("id",), limit=0))
    assert len(datasets) == 0
    datasets = list(index.datasets.search_returning(("id",), limit=5))
    assert len(datasets) == 3


def test_search_archived_eo3(
    index: Index, ls8_eo3_dataset, ls8_eo3_dataset2, wo_eo3_dataset
) -> None:
    prod = ls8_eo3_dataset.product.name
    datasets = list(index.datasets.search(archived=False, product=prod))
    assert len(datasets) == 2
    datasets = list(index.datasets.search(archived=None, product=prod))
    assert len(datasets) == 2
    datasets = list(index.datasets.search(archived=True, product=prod))
    assert len(datasets) == 0

    index.datasets.archive([ls8_eo3_dataset.id])

    datasets = list(index.datasets.search(archived=False, product=prod))
    assert len(datasets) == 1
    datasets = list(index.datasets.search(archived=None, product=prod))
    assert len(datasets) == 2
    datasets = list(index.datasets.search(archived=True, product=prod))
    assert len(datasets) == 1

    index.datasets.archive([ls8_eo3_dataset2.id])

    datasets = list(index.datasets.search(archived=False, product=prod))
    assert len(datasets) == 0
    datasets = list(index.datasets.search(archived=None, product=prod))
    assert len(datasets) == 2
    datasets = list(index.datasets.search(archived=True, product=prod))
    assert len(datasets) == 2


def test_search_order_by_eo3(
    index: Index, ls8_eo3_dataset, ls8_eo3_dataset2, ls8_eo3_dataset3
) -> None:
    # provided as a string
    datasets = list(index.datasets.search(order_by=["id"]))
    assert len(datasets) == 3
    assert str(datasets[0].id) < str(datasets[1].id)
    assert str(datasets[1].id) < str(datasets[2].id)

    # provided as a Field
    prod = ls8_eo3_dataset.product
    fields = prod.metadata_type.dataset_fields
    index.datasets.archive([ls8_eo3_dataset3.id])
    datasets = list(index.datasets.search(order_by=[fields["id"]]))
    assert len(datasets) == 2
    assert str(datasets[0].id) < str(datasets[1].id)

    # ensure limit doesn't interfere with ordering
    datasets = list(index.datasets.search(order_by=["id"], limit=1))
    assert datasets[0] == ls8_eo3_dataset2

    datasets = list(
        index.datasets.search(order_by=[fields["id"].alchemy_expression.desc()])
    )
    assert len(datasets) == 2
    assert str(datasets[0].id) > str(datasets[1].id)


def test_search_or_expressions_eo3(
    index: Index,
    ls8_eo3_dataset: Dataset,
    ls8_eo3_dataset2: Dataset,
    wo_eo3_dataset: Dataset,
) -> None:
    # Three EO3 datasets:
    # - two landsat8 ard
    # - one wo

    all_datasets = list(index.datasets.search())
    assert len(all_datasets) == 3
    all_ids = {dataset.id for dataset in all_datasets}

    # OR all instruments: should return all datasets
    datasets = list(
        index.datasets.search(instrument=["WOOLI_TIRS", "OLI_TIRS", "OLI_TIRS2"])
    )
    assert len(datasets) == 3
    ids = {dataset.id for dataset in datasets}
    assert ids == all_ids

    # OR expression with only one clause.
    datasets = list(index.datasets.search(instrument=["OLI_TIRS"]))
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    # OR both products: return all
    datasets = list(
        index.datasets.search(
            product=[ls8_eo3_dataset.product.name, wo_eo3_dataset.product.name]
        )
    )
    assert len(datasets) == 3
    ids = {dataset.id for dataset in datasets}
    assert ids == all_ids

    # eo OR eo3: return all
    datasets = list(
        index.datasets.search(
            metadata_type=[
                # LS5 + children
                ls8_eo3_dataset.metadata_type.name,
                # Nothing
                # LS8 dataset
                wo_eo3_dataset.metadata_type.name,
            ]
        )
    )
    assert len(datasets) == 3
    ids = {dataset.id for dataset in datasets}
    assert ids == all_ids

    # Redundant ORs should have no effect.
    datasets = list(
        index.datasets.search(
            product=[
                wo_eo3_dataset.product.name,
                wo_eo3_dataset.product.name,
                wo_eo3_dataset.product.name,
            ]
        )
    )
    assert len(datasets) == 1
    assert datasets[0].id == wo_eo3_dataset.id


def test_search_returning_eo3(
    index: Index,
    cfg_env: ODCEnvironment,
    ls8_eo3_dataset: Dataset,
    ls8_eo3_dataset2: Dataset,
    wo_eo3_dataset: Dataset,
) -> None:
    assert index.datasets.count() == 3, "Expected three test datasets"

    # Expect one product with our one dataset.
    results = list(
        index.datasets.search_returning(
            ("id", "region_code", "dataset_maturity"),
            platform="landsat-8",
            instrument="OLI_TIRS",
        )
    )
    assert len(results) == 1
    id_, region_code, maturity = results[0]
    assert id_ == ls8_eo3_dataset.id
    assert region_code == "090086"
    assert maturity == "final"

    count_by_date = index.datasets.count(
        product="ga_ls8c_ard_3",
        time=Range(
            begin=datetime.datetime(2016, 5, 12, 18, tzinfo=datetime.timezone.utc),
            end=datetime.datetime(2016, 5, 13, 2, tzinfo=datetime.timezone.utc),
        ),
    )
    assert count_by_date == 1
    results = list(
        index.datasets.search_returning(
            ("id", "metadata_doc"), platform="landsat-8", instrument="OLI_TIRS"
        )
    )
    assert len(results) == 1
    id_, document = results[0]
    assert id_ == ls8_eo3_dataset.id
    assert document == ls8_eo3_dataset.metadata_doc

    my_username = cfg_env.db_username
    if not my_username:
        my_username = _DEFAULT_DB_USER

    # Mixture of document and native fields
    results = list(
        index.datasets.search_returning(
            ("id", "creation_time", "format", "label"),
            platform="landsat-8",
            instrument="OLI_TIRS",
            indexed_by=my_username,
        )
    )
    assert len(results) == 1

    id_, creation_time, format_, label = results[0]

    assert id_ == ls8_eo3_dataset.id
    assert format_ == "GeoTIFF"

    # It's always UTC in the document
    expected_time = creation_time.astimezone(timezone.utc).replace(tzinfo=None)
    assert expected_time.isoformat() == ls8_eo3_dataset.metadata.creation_dt
    assert label == ls8_eo3_dataset.metadata.label

    # All Fields
    results = list(index.datasets.search_returning(platform="landsat-8"))
    assert len(results) == 3

    assert ls8_eo3_dataset.id in (result.id for result in results)  # type: ignore[attr-defined]


def test_search_returning_rows_eo3(
    index: Index,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
    ls8_eo3_dataset,
    ls8_eo3_dataset2,
) -> None:
    dataset = ls8_eo3_dataset
    uri = eo3_ls8_dataset_doc[1]
    uri2 = eo3_ls8_dataset2_doc[1]
    results = list(
        index.datasets.search_returning(
            ("id", "uri"),
            platform="landsat-8",
            instrument="OLI_TIRS",
        )
    )
    assert len(results) == 1
    assert results == [(dataset.id, uri)]

    results = list(
        index.datasets.search_returning(
            ("id", "uri"),
            custom_offsets={
                "cloud_shadow": ("properties", "fmask:cloud_shadow"),
                "sun_azimuth": ("properties", "eo:sun_azimuth"),
            },
            platform="landsat-8",
            instrument="OLI_TIRS",
        )
    )
    assert len(results) == 1
    assert results[0].id == dataset.id  # type: ignore[attr-defined]
    assert 1.31 < results[0].cloud_shadow < 1.32  # type: ignore[attr-defined]
    assert 34.58 < results[0].sun_azimuth < 34.59  # type: ignore[attr-defined]

    results = list(
        index.datasets.search_returning(
            [],
            custom_offsets={
                "cloud_shadow": ("properties", "fmask:cloud_shadow"),
                "sun_azimuth": ("properties", "eo:sun_azimuth"),
            },
            platform="landsat-8",
            instrument="OLI_TIRS",
        )
    )
    assert len(results) == 1
    assert 1.31 < results[0].cloud_shadow < 1.32  # type: ignore[attr-defined]

    # A second dataset already has a location:
    results = set(
        index.datasets.search_returning(
            ("id", "uri"),
            platform="landsat-8",
            dataset_maturity="final",
        )
    )
    assert len(results) == 2
    assert results == {
        (dataset.id, uri),
        (ls8_eo3_dataset2.id, uri2),
    }


@pytest.mark.parametrize("datacube_env_name", ("postgis", "postgis3"))
def test_search_returning_uri(
    index: Index, eo3_ls8_dataset_doc, ls8_eo3_dataset
) -> None:
    dataset = ls8_eo3_dataset
    uri = eo3_ls8_dataset_doc[1]

    with suppress_deprecations():
        # If returning a field like uri, there will be one result per dataset.
        index.datasets.remove_location(dataset.id, uri)  # deprecated method
    results = list(
        index.datasets.search_returning(
            ("id", "uri"),
            platform="landsat-8",
            instrument="OLI_TIRS",
        )
    )
    assert len(results) == 1


@pytest.mark.parametrize("datacube_env_name", ("datacube", "datacube3"))
def test_search_returning_uris_legacy(
    index: Index,
    eo3_ls8_dataset_doc,
    eo3_ls8_dataset2_doc,
    ls8_eo3_dataset,
    ls8_eo3_dataset2,
) -> None:
    dataset = ls8_eo3_dataset
    uri = eo3_ls8_dataset_doc[1]
    uri3 = eo3_ls8_dataset2_doc[1]

    # If returning a field like uri, there will be one result per location.
    with suppress_deprecations():
        # No locations
        index.datasets.archive_location(dataset.id, uri)
        index.datasets.remove_location(dataset.id, uri)
        results = list(
            index.datasets.search_returning(
                ("id", "uri"),
                platform="landsat-8",
                instrument="OLI_TIRS",
            )
        )
        assert len(results) == 0

        # Add a second location and we should get two results
        index.datasets.add_location(dataset.id, uri)
        uri2 = "file:///tmp/test2"
        index.datasets.add_location(dataset.id, uri2)
        results = set(
            index.datasets.search_returning(
                ("id", "uri"),
                platform="landsat-8",
                instrument="OLI_TIRS",
            )
        )
    assert len(results) == 2
    assert results == {(dataset.id, uri), (dataset.id, uri2)}

    # A second dataset already has a location:
    results = set(
        index.datasets.search_returning(
            ("id", "uri"),
            platform="landsat-8",
            dataset_maturity="final",
        )
    )
    assert len(results) == 3
    assert results == {
        (dataset.id, uri),
        (dataset.id, uri2),
        (ls8_eo3_dataset2.id, uri3),
    }


def test_searches_only_type_eo3(
    index: Index, wo_eo3_dataset: Dataset, ls8_eo3_dataset: Dataset
) -> None:
    assert ls8_eo3_dataset.metadata_type.name != wo_eo3_dataset.metadata_type.name

    # One result in the product
    datasets = list(
        index.datasets.search(product=wo_eo3_dataset.product.name, platform="landsat-8")
    )
    assert len(datasets) == 1
    assert datasets[0].id == wo_eo3_dataset.id

    # One result in the metadata type
    datasets = list(index.datasets.search(metadata_type="eo3", platform="landsat-8"))
    assert len(datasets) == 1
    assert datasets[0].id == wo_eo3_dataset.id

    # No results when searching for a different dataset type.
    with pytest.raises(ValueError):
        next(index.datasets.search(product="spam_and_eggs", platform="landsat-8"))

    # Two result when no types specified.
    datasets = list(index.datasets.search(platform="landsat-8"))
    assert len(datasets) == 2
    assert {ds.id for ds in datasets} == {ls8_eo3_dataset.id, wo_eo3_dataset.id}

    # No results for different metadata type.
    with pytest.raises(ValueError):
        next(
            index.datasets.search(
                metadata_type="spam_type",
                platform="landsat-8",
            )
        )


def test_search_special_fields_eo3(
    index: Index, ls8_eo3_dataset: Dataset, wo_eo3_dataset: Dataset
) -> None:
    # 'product' is a special case
    datasets = list(index.datasets.search(product=ls8_eo3_dataset.product.name))
    assert len(datasets) == 1
    assert datasets[0].id == ls8_eo3_dataset.id

    # Unknown field: no results
    with pytest.raises(ValueError):
        next(
            index.datasets.search(
                platform="landsat-8",
                flavour="vanilla",
            )
        )


def test_search_by_uri_eo3(
    index: Index, ls8_eo3_dataset, ls8_eo3_dataset2, eo3_ls8_dataset_doc
) -> None:
    datasets = list(
        index.datasets.search(
            product=ls8_eo3_dataset.product.name, uri=eo3_ls8_dataset_doc[1]
        )
    )
    assert len(datasets) == 1
    datasets = list(
        index.datasets.search(product=ls8_eo3_dataset.product.name, uri="file:///x/yz")
    )
    assert len(datasets) == 0


def test_search_conflicting_types(index: Index, ls8_eo3_dataset) -> None:
    # Should return no results.
    with pytest.raises(ValueError):
        next(
            index.datasets.search(
                product=ls8_eo3_dataset.product.name,
                # The ls8 type is not of type storage_unit.
                metadata_type="storage_unit",
            )
        )


def test_fetch_all_of_md_type(index: Index, ls8_eo3_dataset: Dataset) -> None:
    # Get every dataset of the md type.
    assert ls8_eo3_dataset.metadata_type is not None  # to shut up mypy
    results = list(
        index.datasets.search(metadata_type=ls8_eo3_dataset.metadata_type.name)
    )
    assert len(results) == 1
    assert results[0].id == ls8_eo3_dataset.id
    # Get every dataset of the type.
    results = list(index.datasets.search(product=ls8_eo3_dataset.product.name))
    assert len(results) == 1
    assert results[0].id == ls8_eo3_dataset.id

    # No results for another.
    with pytest.raises(ValueError):
        next(index.datasets.search(metadata_type="spam_and_eggs"))


def test_count_searches(index: Index, ls8_eo3_dataset: Dataset) -> None:
    # One result in the telemetry type
    datasets = index.datasets.count(
        product=ls8_eo3_dataset.product.name,
        platform="landsat-8",
        instrument="OLI_TIRS",
    )
    assert datasets == 1

    # One result in the metadata type
    datasets = index.datasets.count(
        metadata_type=ls8_eo3_dataset.metadata_type.name,
        platform="landsat-8",
        instrument="OLI_TIRS",
    )
    assert datasets == 1

    # No results when searching for a different dataset type.
    datasets = index.datasets.count(
        product="spam_and_eggs", platform="landsat-8", instrument="OLI_TIRS"
    )
    assert datasets == 0

    # One result when no types specified.
    datasets = index.datasets.count(
        platform="landsat-8",
        instrument="OLI_TIRS",
    )
    assert datasets == 1

    # No results for different metadata type.
    datasets = index.datasets.count(
        metadata_type="spam_and_eggs", platform="landsat-8", instrument="OLI_TIRS"
    )
    assert datasets == 0


def test_count_by_product_searches_eo3(
    index: Index,
    ls8_eo3_dataset: Dataset,
    ls8_eo3_dataset2: Dataset,
    wo_eo3_dataset: Dataset,
) -> None:
    # Two result in the ls8 type
    products = tuple(
        index.datasets.count_by_product(
            product=ls8_eo3_dataset.product.name, platform="landsat-8"
        )
    )
    assert products == ((ls8_eo3_dataset.product, 2),)

    # Two results in the metadata type
    products = tuple(
        index.datasets.count_by_product(
            metadata_type=ls8_eo3_dataset.metadata_type.name,
            platform="landsat-8",
        )
    )
    assert products == ((ls8_eo3_dataset.product, 2),)

    # No results when searching for a different dataset type.
    products = tuple(
        index.datasets.count_by_product(product="spam_and_eggs", platform="landsat-8")
    )
    assert products == ()

    # Three results over 2 products when no types specified.
    products = set(
        index.datasets.count_by_product(
            platform="landsat-8",
        )
    )
    assert products == {(ls8_eo3_dataset.product, 2), (wo_eo3_dataset.product, 1)}

    # No results for different metadata type.
    products = tuple(
        index.datasets.count_by_product(
            metadata_type="spam_and_eggs",
        )
    )
    assert products == ()

    index.datasets.archive([ls8_eo3_dataset.id])
    products = tuple(
        index.datasets.count_by_product(
            product=ls8_eo3_dataset.product.name, platform="landsat-8"
        )
    )
    assert products == ((ls8_eo3_dataset.product, 1),)
    products = tuple(
        index.datasets.count_by_product(
            archived=True, product=ls8_eo3_dataset.product.name, platform="landsat-8"
        )
    )
    assert products == ((ls8_eo3_dataset.product, 1),)
    products = tuple(
        index.datasets.count_by_product(
            archived=None, product=ls8_eo3_dataset.product.name, platform="landsat-8"
        )
    )
    assert products == ((ls8_eo3_dataset.product, 2),)


def test_count_time_groups(index: Index, ls8_eo3_dataset: Dataset) -> None:
    timeline = list(
        index.datasets.count_product_through_time(
            "1 day",
            product=ls8_eo3_dataset.product.name,
            time=Range(
                datetime.datetime(2016, 5, 11, tzinfo=timezone.utc),
                datetime.datetime(2016, 5, 13, tzinfo=timezone.utc),
            ),
        )
    )

    assert len(timeline) == 2
    assert timeline == [
        (
            Range(
                datetime.datetime(2016, 5, 11, tzinfo=timezone.utc),
                datetime.datetime(2016, 5, 12, tzinfo=timezone.utc),
            ),
            0,
        ),
        (
            Range(
                datetime.datetime(2016, 5, 12, tzinfo=timezone.utc),
                datetime.datetime(2016, 5, 13, tzinfo=timezone.utc),
            ),
            1,
        ),
    ]


def test_count_time_groups_cli(clirunner: Any, ls8_eo3_dataset: Dataset) -> None:
    result = clirunner(
        ["product-counts", "1 day", "time in [2016-05-11, 2016-05-13]"],
        cli_method=datacube.scripts.search_tool.cli,
        verbose_flag="",
    )
    expected_out = (
        f"{ls8_eo3_dataset.product.name}\n    2016-05-11: 0\n    2016-05-12: 1\n"
    )
    assert result.stdout.endswith(expected_out)

    # updated version of the test
    result = clirunner(
        [
            "dataset",
            "count",
            "--period",
            "1 day",
            "--query",
            "time in [2016-05-11, 2016-05-13]",
        ],
        cli_method=datacube.scripts.cli_app.cli,
        verbose_flag="",
    )
    assert result.output.endswith(
        f"product: {ls8_eo3_dataset.product.name}\ntime: '2016-05-12'\ncount: 1\n"
    )


def test_search_cli_basic(clirunner: Any, ls8_eo3_dataset: Dataset) -> None:
    """
    Search datasets using the cli.
    """
    result = clirunner(
        [
            # No search arguments: return all datasets.
            "datasets"
        ],
        cli_method=datacube.scripts.search_tool.cli,
    )
    assert str(ls8_eo3_dataset.id) in result.output
    assert str(ls8_eo3_dataset.metadata_type.name) in result.output
    assert result.exit_code == 0, f"Output: {result.output}"

    result = clirunner(
        ["dataset", "search"],
        cli_method=datacube.scripts.cli_app.cli,
    )
    assert str(ls8_eo3_dataset.id) in result.output
    assert str(ls8_eo3_dataset.product.name) in result.output
    assert result.exit_code == 0, f"Output: {result.output}"


def test_cli_info_eo3(
    index: Index,
    clirunner: Any,
    ls8_eo3_dataset: Dataset,
    ls8_eo3_dataset2: Dataset,
    eo3_ls8_dataset_doc,
) -> None:
    """
    Search datasets using the cli.
    """
    opts = ["dataset", "info", str(ls8_eo3_dataset.id)]
    with suppress_deprecations():
        result = clirunner(opts, verbose_flag="")

    output = result.output
    output_lines = list(output.splitlines())

    # Should be a valid yaml
    yaml_docs = list(yaml.safe_load_all(output))
    assert len(yaml_docs) == 1

    # We output properties in order for readability:
    output_lines = set(output_lines)
    expected_lines = [
        "id: " + str(ls8_eo3_dataset.id),
        "product: ga_ls8c_ard_3",
        "status: active",
        "location: " + str(ls8_eo3_dataset.uri),
        "fields:",
        "    creation_time: 2019-10-07 20:19:19.218290",
        "    format: GeoTIFF",
        "    instrument: OLI_TIRS",
        "    label: ga_ls8c_ard_3-0-0_090086_2016-05-12_final",
        "    landsat_product_id: LC08_L1TP_090086_20160512_20180203_01_T1",
        "    landsat_scene_id: LC80900862016133LGN02",
        "    lat: {begin: -38.53221689818913, end: -36.41618895501644}",
        "    lon: {begin: 147.65992717003462, end: 150.3003802932316}",
        "    platform: landsat-8",
        "    product_family: ard",
        "    region_code: 090086",
        "    time: {begin: '2016-05-12T23:50:23.054165+00:00', end: '2016-05-12T23:50:52.031499+00:00'}",
    ]
    for line in expected_lines:
        assert line in output_lines

    # Check indexed time separately, as we don't care what timezone it's displayed in.
    indexed_time = yaml_docs[0]["indexed"]
    assert isinstance(indexed_time, datetime.datetime)
    t = ls8_eo3_dataset.indexed_time
    assert t is not None
    assert tz_as_utc(indexed_time) == tz_as_utc(t)

    # Request two, they should have separate yaml documents
    opts.append(str(ls8_eo3_dataset2.id))

    result = clirunner(opts)
    yaml_docs = list(yaml.safe_load_all(result.stdout))
    assert len(yaml_docs) == 2, "Two datasets should produce two sets of info"
    assert yaml_docs[0]["id"] == str(ls8_eo3_dataset.id)
    assert yaml_docs[1]["id"] == str(ls8_eo3_dataset2.id)


def test_find_duplicates_eo3(
    index,
    ls8_eo3_dataset,
    ls8_eo3_dataset2,
    ls8_eo3_dataset3,
    ls8_eo3_dataset4,
    wo_eo3_dataset,
) -> None:
    # Our four ls8 datasets and one wo.
    all_datasets = list(index.datasets.search())
    assert len(all_datasets) == 5

    # First two ls8 datasets have the same path/row, last two have a different row.
    search_result = namedtuple("search_result", ["region_code", "dataset_maturity"])
    expected_ls8_path_row_duplicates = [
        (search_result("090086", "final"), {ls8_eo3_dataset.id, ls8_eo3_dataset2.id}),
        (search_result("101077", "final"), {ls8_eo3_dataset3.id, ls8_eo3_dataset4.id}),
    ]

    # Specifying groups as fields:
    f = ls8_eo3_dataset.metadata_type.dataset_fields.get
    field_res = sorted(
        index.datasets.search_product_duplicates(
            ls8_eo3_dataset.product, f("region_code"), f("dataset_maturity")
        )
    )
    assert field_res == expected_ls8_path_row_duplicates
    # Field names as strings
    product_res = sorted(
        index.datasets.search_product_duplicates(
            ls8_eo3_dataset.product, "region_code", "dataset_maturity"
        )
    )
    assert product_res == expected_ls8_path_row_duplicates

    # No WO duplicates: there's only one
    sat_res = sorted(
        index.datasets.search_product_duplicates(
            wo_eo3_dataset.product, "region_code", "dataset_maturity"
        )
    )
    assert sat_res == []


def test_find_duplicates_with_time(
    index: Index, nrt_dataset, final_dataset, ls8_eo3_dataset
) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FixWindingWarning)
        index.datasets.add(nrt_dataset, with_lineage=False)
        index.datasets.add(final_dataset, with_lineage=False)
    d = index.datasets.get(nrt_dataset.id)
    assert d is not None
    assert not d.is_archived
    d = index.datasets.get(final_dataset.id)
    assert d is not None
    assert not d.is_archived

    all_datasets = list(index.datasets.search())
    assert len(all_datasets) == 3

    search_result = namedtuple("search_result", ["region_code", "time"])

    # Postgis driver returns tuple of datetime, postgres with psycopg3 returns
    # tuple of strings, postgres with psycopg2 returns a string.
    time = (
        (
            datetime.datetime(
                2023, 4, 30, 23, 50, 33, 884549, tzinfo=datetime.timezone.utc
            ),
            datetime.datetime(
                2023, 4, 30, 23, 50, 34, 884549, tzinfo=datetime.timezone.utc
            ),
        )
        if index._db.driver_name == "postgis"  # type: ignore[attr-defined]
        else ("2023-04-30 23:50:33.884549", "2023-04-30 23:50:34.884549")
        if str(index._db._engine.url).startswith("postgresql+psycopg:")  # type: ignore[attr-defined]
        else '("2023-04-30 23:50:33.884549","2023-04-30 23:50:34.884549")'
    )
    res = sorted(
        index.datasets.search_product_duplicates(
            nrt_dataset.product, "region_code", "time"
        )
    )

    assert res == [(search_result("090086", time), {nrt_dataset.id, final_dataset.id})]


def test_csv_search_via_cli_eo3(
    clirunner: Any, ls8_eo3_dataset: Dataset, ls8_eo3_dataset2: Dataset
) -> None:
    """
    Search datasets via the cli with csv output
    """

    def matches_both(*args) -> None:
        rows = _cli_csv_search(("datasets", *args), clirunner)
        assert len(rows) == 2
        assert {rows[0]["id"], rows[1]["id"]} == {
            str(ls8_eo3_dataset.id),
            str(ls8_eo3_dataset2.id),
        }

    def matches_1(*args) -> None:
        rows = _cli_csv_search(("datasets", *args), clirunner)
        assert len(rows) == 1
        assert rows[0]["id"] == str(ls8_eo3_dataset.id)

    def matches_none(*args) -> None:
        rows = _cli_csv_search(("datasets", *args), clirunner)
        assert len(rows) == 0

    def no_such_product(*args) -> None:
        with pytest.raises(ValueError):
            _cli_csv_search(("datasets", *args), clirunner)

    matches_both("lat in [-40, -10]")
    matches_both("product=" + ls8_eo3_dataset.product.name)

    # Don't return on a mismatch
    matches_none("lat in [150, 160]")

    # Match only a single dataset using multiple fields
    matches_1("platform=landsat-8", "time in [2016-05-11, 2016-05-13]")

    # One matching field, one non-matching
    no_such_product("time in [2016-05-11, 2014-05-13]", "platform=landsat-5")

    # Test date shorthand
    matches_both("time in [2016-05, 2016-05]")
    matches_none("time in [2014-06, 2014-06]")

    matches_both("time in 2016-05")
    matches_none("time in 2014-08")
    matches_both("time in 2016")
    matches_none("time in 2015")

    matches_both("time in [2016, 2016]")
    matches_both("time in [2015, 2017]")
    matches_none("time in [2015, 2015]")
    matches_none("time in [2013, 2013]")

    matches_both("time in [2016-4, 2016-8]")
    matches_none("time in [2016-1, 2016-3]")
    matches_both("time in [2005, 2017]")


_EXT_AND_BASE_EO3_OUTPUT_HEADER = [
    "id",
    "crs_raw",
    "dataset_maturity",
    "eo_gsd",
    "eo_sun_azimuth",
    "eo_sun_elevation",
    "cloud_cover",
    "fmask_clear",
    "fmask_cloud_shadow",
    "fmask_snow",
    "fmask_water",
    "format",
    "gqa",
    "gqa_abs_iterative_mean_x",
    "gqa_abs_iterative_mean_xy",
    "gqa_abs_iterative_mean_y",
    "gqa_abs_x,gqa_abs_xy",
    "gqa_abs_y",
    "gqa_cep90",
    "gqa_iterative_mean_x",
    "gqa_iterative_mean_xy",
    "gqa_iterative_mean_y",
    "gqa_iterative_stddev_x",
    "gqa_iterative_stddev_xy",
    "gqa_iterative_stddev_y",
    "gqa_mean_x",
    "gqa_mean_xy",
    "gqa_mean_y,gqa_stddev_x",
    "gqa_stddev_xy",
    "gqa_stddev_y",
    "creation_time",
    "indexed_by",
    "indexed_time",
    "instrument",
    "label",
    "landsat_product_id",
    "landsat_scene_id",
    "lat",
    "lon",
    "metadata_doc",
    "metadata_type",
    "metadata_type_id",
    "platform",
    "product",
    "product_family",
    "region_code",
    "time",
    "uri",
]


def test_csv_structure_eo3(clirunner, ls8_eo3_dataset, ls8_eo3_dataset2) -> None:
    output = _csv_search_raw(["datasets", " lat in [-40, -10]"], clirunner)
    lines = [line.strip() for line in output.split("\n") if line]
    # A header and two dataset rows
    assert len(lines) == 3
    header_line = lines[0]
    for header in _EXT_AND_BASE_EO3_OUTPUT_HEADER:
        assert header in header_line


def test_query_dataset_multi_product_eo3(
    index: Index, ls8_eo3_dataset, wo_eo3_dataset
) -> None:
    # We have one ls5 level1 and its child nbar
    dc = Datacube(index)

    # Can we query a single product name?
    datasets = dc.find_datasets(product="ga_ls8c_ard_3")
    assert len(datasets) == 1

    # Can we query multiple products?
    datasets = dc.find_datasets(product=["ga_ls8c_ard_3", "ga_ls_wo_3"])
    assert len(datasets) == 2

    # Can we query multiple products in a tuple
    datasets = dc.find_datasets(product=("ga_ls8c_ard_3", "ga_ls_wo_3"))
    assert len(datasets) == 2


def test_search_boolean_eo3(index: Index, s1_eo3_dataset) -> None:
    res = list(
        index.datasets.search(
            product=s1_eo3_dataset.product.name, speckle_filter_applied=False
        )
    )
    assert len(res) == 1
    res = list(
        index.datasets.search(
            product=s1_eo3_dataset.product.name, speckle_filter_applied=True
        )
    )
    assert len(res) == 0
