# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
import warnings
from copy import deepcopy
from datetime import datetime
from unittest import mock

import numpy
import pytest
import xarray as xr
from odc.geo import CRS
from odc.geo.gridspec import GridSpec
from typing_extensions import override

from datacube.model import Dataset, MetadataType, Product
from datacube.virtual import (
    DEFAULT_RESOLVER,
    Transformation,
    VirtualProductException,
    catalog_from_yaml,
    construct_from_yaml,
)
from datacube.virtual.expr import FormulaEvaluator, evaluate_data, formula_parser
from datacube.virtual.impl import Datacube
from datacube.virtual.transformations import fiscal_year

##########################################
# Set up some common test data and fixtures


def test_formula_parsing() -> None:
    parser = formula_parser()
    evaluator = FormulaEvaluator
    env = {"x": 4, "y": 2, "true": True, "false": False}

    assert evaluate_data("x", env, parser, evaluator) == 4
    assert evaluate_data("-y", env, parser, evaluator) == -2
    assert evaluate_data("x / y", env, parser, evaluator) == 2
    assert evaluate_data("(x + y) * 3", env, parser, evaluator) == 18
    assert not evaluate_data("x == y", env, parser, evaluator)
    assert not evaluate_data("true == false", env, parser, evaluator)
    assert evaluate_data("not (true == false)", env, parser, evaluator)
    assert evaluate_data("x > y", env, parser, evaluator)
    assert not evaluate_data("(x > y) & (x < y)", env, parser, evaluator)


PRODUCT_LIST = ["ls7_pq_albers", "ls8_pq_albers", "ls7_nbar_albers", "ls8_nbar_albers"]


def example_metadata_type() -> MetadataType:
    return MetadataType(
        {
            "name": "eo",
            "dataset": {
                "id": ["id"],
                "label": ["ga_label"],
                "creation_time": ["creation_dt"],
                "measurements": ["image", "bands"],
                "grid_spatial": ["grid_spatial", "projection"],
                "sources": ["lineage", "source_datasets"],
            },
        },
    )


def example_product(name: str):
    if name not in PRODUCT_LIST:
        return None

    blue = {"name": "blue", "dtype": "int16", "nodata": -999, "units": "1"}
    green = {
        "name": "green",
        "dtype": "int16",
        "nodata": -999,
        "units": "1",
        "aliases": ["verde"],
    }
    flags = {
        "cloud_acca": {"bits": 10, "values": {"0": "cloud", "1": "no_cloud"}},
        "contiguous": {"bits": 8, "values": {"0": False, "1": True}},
        "cloud_fmask": {"bits": 11, "values": {"0": "cloud", "1": "no_cloud"}},
        "nir_saturated": {"bits": 3, "values": {"0": True, "1": False}},
        "red_saturated": {"bits": 2, "values": {"0": True, "1": False}},
        "blue_saturated": {"bits": 0, "values": {"0": True, "1": False}},
        "green_saturated": {"bits": 1, "values": {"0": True, "1": False}},
        "swir1_saturated": {"bits": 4, "values": {"0": True, "1": False}},
        "swir2_saturated": {"bits": 7, "values": {"0": True, "1": False}},
        "cloud_shadow_acca": {
            "bits": 12,
            "values": {"0": "cloud_shadow", "1": "no_cloud_shadow"},
        },
        "cloud_shadow_fmask": {
            "bits": 13,
            "values": {"0": "cloud_shadow", "1": "no_cloud_shadow"},
        },
    }

    pixelquality = {
        "name": "pixelquality",
        "dtype": "int16",
        "nodata": 0,
        "units": "1",
        "flags_definition": flags,
    }

    result = Product(
        example_metadata_type(),
        {"name": name, "description": "", "metadata_type": "eo", "metadata": {}},
    )
    result.grid_spec = GridSpec(
        crs=CRS("EPSG:3577"), tile_shape=(4000, 4000), resolution=25
    )
    if "_pq_" in name:
        result.definition = {"name": name, "measurements": [pixelquality]}
    else:
        result.definition = {"name": name, "measurements": [blue, green]}
    return result


def example_grid_spatial() -> dict:
    return {
        "projection": {
            "valid_data": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [1500000.0, -4000000.0],
                        [1500000.0, -3900000.0],
                        [1600000.0, -3900000.0],
                        [1600000.0, -4000000.0],
                        [1500000.0, -4000000.0],
                    ]
                ],
            },
            "geo_ref_points": {
                "ll": {"x": 1500000.0, "y": -4000000.0},
                "lr": {"x": 1600000.0, "y": -4000000.0},
                "ul": {"x": 1500000.0, "y": -3900000.0},
                "ur": {"x": 1600000.0, "y": -3900000.0},
            },
            "spatial_reference": "EPSG:3577",
        }
    }


@pytest.fixture
def catalog():
    return catalog_from_yaml("""
        about: this is a test catalog of virtual products
        products:
            cloud_free_ls8_nbar:
                tags: [nbar, landsat-8]
                recipe:
                    &cloud_free_ls8_nbar_recipe
                    transform: apply_mask
                    mask_measurement_name: pixelquality
                    input:
                        &cloud_mask_recipe
                        transform: make_mask
                        flags:
                            blue_saturated: false
                            cloud_acca: no_cloud
                            cloud_fmask: no_cloud
                            cloud_shadow_acca: no_cloud_shadow
                            cloud_shadow_fmask: no_cloud_shadow
                            contiguous: true
                            green_saturated: false
                            nir_saturated: false
                            red_saturated: false
                            swir1_saturated: false
                            swir2_saturated: false
                        mask_measurement_name: pixelquality
                        input:
                            juxtapose:
                              - product: ls8_nbar_albers
                                measurements: ['blue', 'green']
                              - product: ls8_pq_albers

            cloud_free_ls7_nbar:
                tags: [nbar, landsat-7]
                recipe:
                    &cloud_free_ls7_nbar_recipe
                    transform: datacube.virtual.transformations.ApplyMask
                    mask_measurement_name: pixelquality
                    input:
                      <<: *cloud_mask_recipe
                      input:
                        juxtapose:
                          - product: ls7_nbar_albers
                            measurements: ['blue', 'green']
                          - product: ls7_pq_albers

            cloud_free_nbar:
                description: cloud free NBAR from Landsat-7 and Landsat-8
                tags: [nbar, landsat-7, landsat-8]
                recipe:
                    collate:
                        - *cloud_free_ls8_nbar_recipe
                        - *cloud_free_ls7_nbar_recipe

                    index_measurement_name: source_index

            mean_blue:
                recipe:
                    aggregate: xarray_reduction
                    method: mean
                    group_by: month
                    input:
                        transform: expressions
                        output:
                          blue:
                            formula: blue
                            dtype: float32
                        input:
                            collate:
                              - product: ls7_nbar_albers
                                measurements: [blue]
                              - product: ls8_nbar_albers
                                measurements: [blue]

            reproject_utm:
                recipe:
                    reproject:
                        output_crs: EPSG:32755
                        resolution: [30, -30]
                    input:
                        collate:
                          - product: ls7_nbar_albers
                            measurements: [blue]
                          - product: ls8_nbar_albers
                            measurements: [blue]
    """)


@pytest.fixture
def cloud_free_nbar(catalog):
    return catalog["cloud_free_nbar"]


def load_data(*args, **kwargs):
    sources, geobox, measurements = args

    # this returns nodata bands which are good enough for this test
    return Datacube.create_storage(sources.coords, geobox, measurements)


def group_datasets(*args, **kwargs):
    return Datacube.group_datasets(*args, **kwargs)


@pytest.fixture
def dc():
    result = mock.MagicMock()
    result.index.products.get_field_names.return_value = {"id", "product", "time"}

    ids = [
        "87a68652-b76a-450f-b44f-e5192243218e",
        "af9deddf-daf3-4e93-8f36-21437b52817c",
        "0c5d304f-7cd8-425e-8b0f-0f72b4fc4e6e",
        "9dcfc6f6-aa36-47ef-9501-177fa39e7e7d",
        "dda8b22e-27f5-40a5-99d4-b94810f545d0",
    ]

    def example_dataset(product, id_, center_time) -> Dataset:
        result = Dataset(
            example_product(product),
            {"id": id_, "grid_spatial": example_grid_spatial()},
            uri="file://test.zzz",
        )
        result.center_time = center_time
        return result

    def find_datasets(*args, **kwargs) -> list:
        product = kwargs["product"]
        if product == "ls8_nbar_albers":
            return [
                example_dataset(product, ids[0], datetime(2014, 2, 7, 23, 57, 26)),
                example_dataset(product, ids[1], datetime(2014, 1, 1, 23, 57, 26)),
            ]
        if product == "ls8_pq_albers":
            return [example_dataset(product, ids[2], datetime(2014, 2, 7, 23, 57, 26))]
        if product == "ls7_nbar_albers":
            return [example_dataset(product, ids[3], datetime(2014, 1, 22, 23, 57, 36))]
        if product == "ls7_pq_albers":
            return [example_dataset(product, ids[4], datetime(2014, 1, 22, 23, 57, 36))]
        return []

    result.index.products.get_all = lambda: [example_product(x) for x in PRODUCT_LIST]
    result.index.products.get_by_name = example_product
    result.find_datasets = find_datasets
    return result


@pytest.fixture
def query() -> dict[str, tuple[str | float, str | float]]:
    return {
        "time": ("2014-01-01", "2014-03-01"),
        "lat": (-35.2, -35.21),
        "lon": (149.0, 149.01),
    }


##################################
# Virtual Product Tests Start Here


def test_name_resolution(cloud_free_nbar) -> None:
    for prod in cloud_free_nbar["collate"]:
        assert callable(prod["transform"])


def test_str(cloud_free_nbar) -> None:
    assert str(cloud_free_nbar)


def test_output_measurements(cloud_free_nbar, dc) -> None:
    measurements = cloud_free_nbar.output_measurements(
        {product.name: product for product in dc.index.products.get_all()}
    )
    assert "blue" in measurements
    assert "green" in measurements
    assert "source_index" in measurements
    assert "pixelquality" not in measurements


def test_group_datasets(cloud_free_nbar, dc, query) -> None:
    bag = cloud_free_nbar.query(dc, **query)
    box = cloud_free_nbar.group(bag, **query)

    [time] = box.box.shape
    assert time == 2


def test_explode(dc, query) -> None:
    collate = construct_from_yaml("""
        collate:
            - product: ls8_nbar_albers
            - product: ls7_nbar_albers
    """)

    bag = collate.query(dc, **query)

    # three datasets in two products
    assert len(list(bag.contained_datasets())) == 3

    bags = list(bag.explode())

    # each element should contain one dataset
    assert len(bags) == 3

    for bag in bags:
        assert len(list(bag.contained_datasets())) == 1

        # the smaller bags should have the same structure
        assert "collate" in bag.bag

        # there were two products (only one of them should have the single dataset)
        assert len(bag.bag["collate"]) == 2


def test_load_data(cloud_free_nbar, dc, query) -> None:
    with mock.patch("datacube.virtual.impl.Datacube") as mock_datacube:
        mock_datacube.load_data = load_data
        mock_datacube.group_datasets = group_datasets
        data = cloud_free_nbar.load(dc, **query)

    assert "blue" in data
    assert "green" in data
    assert "source_index" in data
    assert "pixelquality" not in data

    assert numpy.array_equal(numpy.unique(data.blue.values), numpy.array([-999]))
    assert numpy.array_equal(numpy.unique(data.green.values), numpy.array([-999]))
    assert numpy.array_equal(
        numpy.unique(data.source_index.values), numpy.array([0, 1])
    )


def test_misspelled_product(dc, query) -> None:
    ls8_nbar = construct_from_yaml("product: ls8_nbar")

    with pytest.raises(VirtualProductException):
        ls8_nbar.query(dc, **query)


#####################################
# Virtual Product Transform Tests
#####################################


def test_vp_handles_product_aliases(dc, query) -> None:
    verde = construct_from_yaml("""
        product: ls8_nbar_albers
        measurements: [verde]
    """)

    measurements = verde.output_measurements(
        {product.name: product for product in dc.index.products.get_all()}
    )
    assert "verde" in measurements
    assert "green" not in measurements

    with mock.patch("datacube.virtual.impl.Datacube") as mock_datacube:
        mock_datacube.load_data = load_data
        mock_datacube.group_datasets = group_datasets
        data = verde.load(dc, **query)

    assert "verde" in data
    assert "green" not in data


def test_expressions_transform(dc, query) -> None:
    bluegreen = construct_from_yaml("""
        transform: expressions
        output:
            bluegreen:
                formula: blue + green
                nodata: -999
            blue: blue
        input:
            product: ls8_nbar_albers
            measurements: [blue, green]
    """)

    measurements = bluegreen.output_measurements(
        {product.name: product for product in dc.index.products.get_all()}
    )
    assert "bluegreen" in measurements

    with mock.patch("datacube.virtual.impl.Datacube") as mock_datacube:
        mock_datacube.load_data = load_data
        mock_datacube.group_datasets = group_datasets
        data = bluegreen.load(dc, **query)

    assert "bluegreen" in data
    assert numpy.all((data.bluegreen == -999).values)
    assert "blue" in data
    assert numpy.all((data.blue == -999).values)
    assert "green" not in data

    bluegreen = construct_from_yaml("""
        transform: expressions
        output:
            bluegreen:
                formula: blue + green
                dtype: float32
            blue: blue
        input:
            product: ls8_nbar_albers
            measurements: [blue, green]
    """)

    measurements = bluegreen.output_measurements(
        {product.name: product for product in dc.index.products.get_all()}
    )
    assert "bluegreen" in measurements
    assert measurements["bluegreen"].dtype == numpy.dtype("float32")
    assert numpy.isnan(measurements["bluegreen"].nodata)

    with mock.patch("datacube.virtual.impl.Datacube") as mock_datacube:
        mock_datacube.load_data = load_data
        mock_datacube.group_datasets = group_datasets
        data = bluegreen.load(dc, **query)

    assert "bluegreen" in data
    assert numpy.all(numpy.isnan(data.bluegreen.values))
    assert "blue" in data
    assert numpy.all((data.blue == -999).values)
    assert "green" not in data


def test_aggregate(dc, query, catalog) -> None:
    aggr = catalog["mean_blue"]

    measurements = aggr.output_measurements(
        {product.name: product for product in dc.index.products.get_all()}
    )
    assert "blue" in measurements

    with (
        mock.patch("datacube.virtual.impl.Datacube") as mock_datacube,
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("ignore")
        mock_datacube.load_data = load_data
        mock_datacube.group_datasets = group_datasets
        data = aggr.load(dc, **query)

    assert data.time.shape == (2,)


def test_register(dc, query) -> None:
    class BlueGreen(Transformation):
        @override
        def compute(self, data):
            return (
                (data.blue + data.green)
                .to_dataset(name="bluegreen")
                .assign_attrs(data.blue.attrs)
            )

        @override
        def measurements(self, input_measurements):
            bluegreen = deepcopy(input_measurements["blue"])
            bluegreen.name = "bluegreen"
            return {"bluegreen": bluegreen}

    resolver = deepcopy(DEFAULT_RESOLVER)
    resolver.register("transform", "bluegreen", BlueGreen)

    bluegreen = construct_from_yaml(
        """
        transform: bluegreen
        input:
            product: ls8_nbar_albers
            measurements: [blue, green]
    """,
        name_resolver=resolver,
    )

    measurements = bluegreen.output_measurements(
        {product.name: product for product in dc.index.products.get_all()}
    )
    assert "bluegreen" in measurements

    with mock.patch("datacube.virtual.impl.Datacube") as mock_datacube:
        mock_datacube.load_data = load_data
        mock_datacube.group_datasets = group_datasets
        data = bluegreen.load(dc, **query)

    assert "bluegreen" in data


def test_reproject(dc, query, catalog) -> None:
    reproject_utm = catalog["reproject_utm"]

    with mock.patch("datacube.virtual.impl.Datacube") as mock_datacube:
        mock_datacube.load_data = load_data
        mock_datacube.group_datasets = group_datasets
        data = reproject_utm.load(dc, **query)

    assert data.crs == CRS("EPSG:32755")
    assert data.geobox.crs == CRS("EPSG:32755")
    assert data.coords["x"].attrs["resolution"] == -30
    assert data.coords["y"].attrs["resolution"] == 30


def test_fiscal_year() -> None:
    """
    Test fiscal year function
    """
    times = [
        "2015-07-02T11:59:59.999999000",
        "2015-07-02T11:59:59.999999000",
        "2016-07-01T23:59:59.999999000",
        "2016-07-01T23:59:59.999999",
    ]

    times = [numpy.datetime64(x) for x in times]
    coords = {"time": times}
    attribs = {"units": "seconds since 1970-01-01 00:00:00"}
    dimension = ("time",)
    da = xr.DataArray(times, name="time", attrs=attribs, coords=coords, dims=dimension)

    fy = fiscal_year(da)

    expected = ["2016-01-01", "2016-01-01", "2017-01-01", "2017-01-01"]
    expected = [numpy.datetime64(x) for x in expected]

    assert (expected == fy.data).all()
    assert (expected == fy.time).all()


def test_fiscal_year_multi_time_dimensions() -> None:
    """
    Test the fiscal year is applied to every
    input time dimension
    """
    times_mock_1 = [
        "2015-06-30T11:59:59.999999000",
        "2015-12-31T11:59:59.999999000",
        "2016-01-01T23:59:59.999999000",
        "2016-07-01T23:59:59.999999",
    ]

    times_mock_2 = [
        "2019-06-30T11:59:59.999999000",
        "2019-12-31T11:59:59.999999000",
        "2020-01-01T23:59:59.999999000",
        "2020-05-31T23:59:59.999999",
    ]

    times_mock_1 = [numpy.datetime64(x) for x in times_mock_1]
    times_mock_2 = [numpy.datetime64(x) for x in times_mock_2]
    data = numpy.array([times_mock_1, times_mock_2])
    attribs = {"units": "seconds since 1970-01-01 00:00:00"}
    da = xr.DataArray(
        data,
        name="time",
        attrs=attribs,
        coords={"x": [1, 2], "time": times_mock_1},
        dims=("x", "time"),
    )
    fy = fiscal_year(da)

    expected_times_mock_1 = ["2015-01-01", "2016-01-01", "2016-01-01", "2017-01-01"]
    expected_times_mock_2 = ["2019-01-01", "2020-01-01", "2020-01-01", "2020-01-01"]
    expected_times_mock_1 = [numpy.datetime64(x) for x in expected_times_mock_1]
    expected_times_mock_2 = [numpy.datetime64(x) for x in expected_times_mock_2]
    expected_data = numpy.array([expected_times_mock_1, expected_times_mock_2])

    assert (expected_data == fy.data).all()
    assert (expected_times_mock_1 == fy.time).all()
