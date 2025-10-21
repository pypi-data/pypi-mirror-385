# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
py.test configuration fixtures

This module defines any fixtures or other extensions to py.test to be used throughout the
tests in this and sub packages.
"""

import os
from pathlib import Path
from typing import Any

import pystac
import pystac.collection
import pystac.item
import pytest
from affine import Affine
from odc.geo import CRS, wh_
from odc.geo.geobox import GeoBox

from datacube import Datacube
from datacube.index.eo3 import prep_eo3
from datacube.model import (
    Dataset,
    LineageTree,
    Measurement,
    MetadataType,
    Product,
    metadata_from_doc,
)
from datacube.utils.documents import load_from_yaml, read_documents

AWS_ENV_VARS = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_DEFAULT_REGION",
    "AWS_DEFAULT_OUTPUT",
    "AWS_PROFILE",
    "AWS_ROLE_SESSION_NAME",
    "AWS_CA_BUNDLE",
    "AWS_SHARED_CREDENTIALS_FILE",
    "AWS_CONFIG_FILE",
]


@pytest.fixture
def example_gdal_path(data_folder):
    """Return the pathname of a sample geotiff file

    Use this fixture by specifying an argument named 'example_gdal_path' in your
    test method.
    """
    return str(os.path.join(data_folder, "sample_tile_151_-29.tif"))


@pytest.fixture
def no_crs_gdal_path(data_folder):
    """Return the pathname of a GDAL file that doesn't contain a valid CRS."""
    return str(os.path.join(data_folder, "no_crs_ds.tif"))


@pytest.fixture
def data_folder():
    """Return a string path to the location `test/data`"""
    return os.path.join(os.path.split(os.path.realpath(__file__))[0], "data")


@pytest.fixture
def example_netcdf_path(request):
    """Return a string path to `sample_tile.nc` in the test data dir"""
    return str(request.fspath.dirpath("data/sample_tile.nc"))


@pytest.fixture
def non_geo_dataset_file(data_folder):
    return os.path.join(data_folder, "ds_non-geo.yaml")


@pytest.fixture
def non_geo_dataset_doc(non_geo_dataset_file):
    (_, doc), *_ = read_documents(non_geo_dataset_file)
    return doc


@pytest.fixture
def eo_dataset_file(data_folder):
    return os.path.join(data_folder, "ds_eo.yaml")


@pytest.fixture
def eo_dataset_doc(eo_dataset_file):
    (_, doc), *_ = read_documents(eo_dataset_file)
    return doc


@pytest.fixture
def eo3_dataset_file(data_folder):
    return os.path.join(data_folder, "ds_eo3.yaml")


@pytest.fixture
def eo3_dataset_doc(eo3_dataset_file):
    (_, doc), *_ = read_documents(eo3_dataset_file)
    return doc


@pytest.fixture
def eo3_metadata_file(data_folder):
    return os.path.join(data_folder, "eo3.yaml")


@pytest.fixture
def eo3_metadata(eo3_metadata_file):
    (_, doc), *_ = read_documents(eo3_metadata_file)
    return MetadataType(doc)


@pytest.fixture
def eo3_dataset_s2(eo3_metadata):
    ds_doc = {
        "$schema": "https://schemas.opendatacube.org/dataset",
        "id": "8b0e2770-5d4e-5238-8995-4aa91691ab85",
        "product": {"name": "s2b_msil2a"},
        "label": "S2B_MSIL2A_20200101T070219_N0213_R120_T39LVG_20200101T091825",
        "crs": "epsg:32739",
        "grids": {
            "g20m": {
                "shape": [5490, 5490],
                "transform": [20, 0, 399960, 0, -20, 8700040, 0, 0, 1],
            },
            "g60m": {
                "shape": [1830, 1830],
                "transform": [60, 0, 399960, 0, -60, 8700040, 0, 0, 1],
            },
            "default": {
                "shape": [10980, 10980],
                "transform": [10, 0, 399960, 0, -10, 8700040, 0, 0, 1],
            },
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [509759.0000000001, 8590241.0],
                    [399960.99999999977, 8590241.0],
                    [399960.99999999977, 8700039.0],
                    [509758.99999999965, 8700039.0],
                    [509759.0000000001, 8590241.0],
                ]
            ],
        },
        "properties": {
            "eo:gsd": 10,
            "datetime": "2020-01-01T07:02:54.188Z",
            "eo:platform": "sentinel-2b",
            "eo:instrument": "msi",
            "eo:cloud_cover": 0,
            "odc:file_format": "GeoTIFF",
            "odc:region_code": "39LVG",
            "odc:processing_datetime": "2020-01-01T07:02:54.188Z",
        },
        "measurements": {
            "red": {"path": "B04.tif"},
            "scl": {"grid": "g20m", "path": "SCL.tif"},
            "blue": {"path": "B02.tif"},
            "green": {"path": "B03.tif"},
            "nir_1": {"path": "B08.tif"},
            "nir_2": {"grid": "g20m", "path": "B8A.tif"},
            "swir_1": {"grid": "g20m", "path": "B11.tif"},
            "swir_2": {"grid": "g20m", "path": "B12.tif"},
            "red_edge_1": {"grid": "g20m", "path": "B05.tif"},
            "red_edge_2": {"grid": "g20m", "path": "B06.tif"},
            "red_edge_3": {"grid": "g20m", "path": "B07.tif"},
            "water_vapour": {"grid": "g60m", "path": "B09.tif"},
            "coastal_aerosol": {"grid": "g60m", "path": "B01.tif"},
        },
        "lineage": {},
    }
    product_doc = {
        "name": "s2b_msil2a",
        "description": "Sentinel-2B Level 2 COGs",
        "metadata_type": "eo3",
        "metadata": {"product": {"name": "s2b_msil2a"}},
        "measurements": [
            {
                "name": "coastal_aerosol",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_01", "B01"],
            },
            {
                "name": "blue",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_02", "B02"],
            },
            {
                "name": "green",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_03", "B03"],
            },
            {
                "name": "red",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_04", "B04"],
            },
            {
                "name": "red_edge_1",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_05", "B05"],
            },
            {
                "name": "red_edge_2",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_06", "B06"],
            },
            {
                "name": "red_edge_3",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_07", "B07"],
            },
            {
                "name": "nir_1",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_08", "B08"],
            },
            {
                "name": "nir_2",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_8a", "B8A"],
            },
            {
                "name": "water_vapour",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_09", "B09"],
            },
            {
                "name": "swir_1",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_11", "B11"],
            },
            {
                "name": "swir_2",
                "dtype": "uint16",
                "units": "1",
                "nodata": 0,
                "aliases": ["band_12", "B12"],
            },
            {
                "name": "scl",
                "dtype": "uint8",
                "units": "1",
                "nodata": 0,
                "aliases": ["mask", "qa"],
                "flags_definition": {
                    "sca": {
                        "description": "Sen2Cor Scene Classification",
                        "bits": [0, 1, 2, 3, 4, 5, 6, 7],
                        "values": {
                            "0": "nodata",
                            "1": "defective",
                            "2": "dark",
                            "3": "shadow",
                            "4": "vegetation",
                            "5": "bare",
                            "6": "water",
                            "7": "unclassified",
                            "8": "cloud medium probability",
                            "9": "cloud high probability",
                            "10": "thin cirrus",
                            "11": "snow or ice",
                        },
                    }
                },
            },
        ],
    }

    return Dataset(Product(eo3_metadata, product_doc), prep_eo3(ds_doc))


netcdf_num = 1


@pytest.fixture
def tmpnetcdf_filename(tmpdir):
    """Return a generated filename for a non-existent netcdf file"""
    global netcdf_num
    filename = str(tmpdir.join(f"testfile_np_{netcdf_num}.nc"))
    netcdf_num += 1
    return filename


@pytest.fixture
def odc_style_xr_dataset(request):
    """An xarray.Dataset with ODC style coordinates and CRS

    Contains an EPSG:4326, single variable 'B10' of 100x100 int16 pixels."""
    affine = Affine.scale(0.1, 0.1) * Affine.translation(20, 30)
    geobox = GeoBox(wh_(100, 100), affine, CRS(GEO_PROJ))

    return Datacube.create_storage(
        request.param,
        geobox,
        [Measurement(name="B10", dtype="int16", nodata=0, units="1")],
    )


@pytest.fixture(scope="session")
def workdir(tmpdir_factory):
    return tmpdir_factory.mktemp("workdir")


@pytest.fixture
def without_aws_env(monkeypatch) -> None:
    for e in AWS_ENV_VARS:
        monkeypatch.delenv(e, raising=False)


GEO_PROJ = (
    'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
    'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],'
    'AUTHORITY["EPSG","4326"]]'
)


@pytest.fixture(scope="module")
def dask_client():
    from distributed import Client

    client = Client(processes=False, threads_per_worker=1, dashboard_address=None)
    yield client
    client.close()
    del client


# Test fixtures brought in from odc-stac

TEST_DATA_FOLDER: Path = Path(__file__).parent.joinpath("data")
PARTIAL_PROJ_STAC: str = "only_crs_proj.json"
SENTINEL_STAC_COLLECTION: str = "sentinel-2-l2a.collection.json"
SENTINEL_STAC_MS: str = "S2B_MSIL2A_20190629T212529_R043_T06VVN_20201006T080531.json"
SENTINEL_STAC_MS_RASTER_EXT: str = (
    "S2B_MSIL2A_20190629T212529_R043_T06VVN_20201006T080531_raster_ext.json"
)
USGS_LANDSAT_STAC_v1: str = "LC08_L2SP_028030_20200114_20200824_02_T1_SR.json"
S2_L2A_STAC: str = "s2_l2a.stac-item.json"
S2_L2A_PRODUCT: str = "s2_l2a.odc-product.yaml"
ODC_DATASET_FILE: str = "ga_ls8c_ard_3-1-0_088080_2020-05-25_final.odc-metadata.yaml"
ODC_METADATA_FILE: str = "eo3_landsat_ard.odc-type.yaml"
ODC_PRODUCT_FILE: str = "ard_ls8.odc-product.yaml"
S1_NRB_STAC: str = "ga_s1a_nrb_0-1-0_T002-003270-IW2_20180306T203033Z_stac-item.json"
S1_NRB_PRODUCT: str = "ga_s1_nrb_iw_hh_0.odc-product.yaml"
S1_NRB_METADATA_FILE: str = "eo3_s1_nrb.odc-type.yaml"


@pytest.fixture
def partial_proj_stac() -> pystac.Item:
    return pystac.item.Item.from_file(str(TEST_DATA_FOLDER.joinpath(PARTIAL_PROJ_STAC)))


@pytest.fixture
def no_bands_stac(partial_proj_stac) -> pystac.Item:
    partial_proj_stac.assets.clear()
    return partial_proj_stac


@pytest.fixture
def usgs_landsat_stac_v1():
    return pystac.item.Item.from_file(
        str(TEST_DATA_FOLDER.joinpath(USGS_LANDSAT_STAC_v1))
    )


@pytest.fixture
def sentinel_stac_ms() -> pystac.Item:
    return pystac.item.Item.from_file(str(TEST_DATA_FOLDER.joinpath(SENTINEL_STAC_MS)))


@pytest.fixture
def sentinel_stac_ms_with_raster_ext() -> pystac.Item:
    return pystac.item.Item.from_file(
        str(TEST_DATA_FOLDER.joinpath(SENTINEL_STAC_MS_RASTER_EXT))
    )


@pytest.fixture
def sentinel_stac_collection() -> pystac.Collection:
    return pystac.collection.Collection.from_file(
        str(TEST_DATA_FOLDER.joinpath(SENTINEL_STAC_COLLECTION))
    )


@pytest.fixture
def s2_l2a_stac() -> pystac.Item:
    return pystac.item.Item.from_file(str(TEST_DATA_FOLDER.joinpath(S2_L2A_STAC)))


@pytest.fixture
def s2_l2a_product(eo3_metadata) -> Product:
    filepath = TEST_DATA_FOLDER.joinpath(S2_L2A_PRODUCT)
    (_, doc), *_ = read_documents(filepath)
    return Product(eo3_metadata, doc)


@pytest.fixture
def eo3_metadata_type() -> MetadataType:
    filepath = TEST_DATA_FOLDER.joinpath(ODC_METADATA_FILE)
    (_, doc), *_ = read_documents(filepath)
    return metadata_from_doc(doc)


@pytest.fixture
def eo3_product(eo3_metadata_type: MetadataType) -> Product:
    filepath = TEST_DATA_FOLDER.joinpath(ODC_PRODUCT_FILE)
    (_, doc), *_ = read_documents(filepath)
    return Product(eo3_metadata_type, doc)


@pytest.fixture
def odc_dataset_doc() -> dict[str, Any]:
    filepath = TEST_DATA_FOLDER.joinpath(ODC_DATASET_FILE)
    with open(str(filepath)) as f:
        return next(iter(load_from_yaml(f, parse_dates=True)))


@pytest.fixture
def eo3_dataset(eo3_product, odc_dataset_doc) -> Dataset:
    return Dataset(eo3_product, prep_eo3(odc_dataset_doc), uri=ODC_DATASET_FILE)


@pytest.fixture
def ds_legacy_sources(eo3_product, odc_dataset_doc) -> Dataset:
    sample_source_def = {
        "$schema": "https://schemas.opendatacube.org/dataset",
        "id": "b5f234fe-bba8-5483-9bc0-250360d429cf",
        "product": {"name": eo3_product.name},
        "crs": "epsg:3857",
        "properties": {
            "datetime": "2020-04-20 00:26:43Z",
            "odc:processing_datetime": "2020-05-16 10:56:18Z",
        },
        "grids": {
            "default": {
                "shape": [100, 200],
                "transform": [10, 0, 100000, 0, -10, 200000, 0, 0, 1],
            }
        },
    }
    source_ds = Dataset(eo3_product, sample_source_def)
    return Dataset(
        eo3_product,
        prep_eo3(odc_dataset_doc),
        sources={"level1": source_ds},
        uri=ODC_DATASET_FILE,
    )


@pytest.fixture
def ds_ext_lineage(eo3_product, odc_dataset_doc) -> Dataset:
    ds = Dataset(
        eo3_product,
        prep_eo3(odc_dataset_doc, remap_lineage=False),
        uri=ODC_DATASET_FILE,
    )
    ds.source_tree = LineageTree.from_eo3_doc(ds.metadata_doc, home="src_home")
    return ds


@pytest.fixture
def s1_nrb_metadata_type() -> MetadataType:
    filepath = TEST_DATA_FOLDER.joinpath(S1_NRB_METADATA_FILE)
    (_, doc), *_ = read_documents(filepath)
    return metadata_from_doc(doc)


@pytest.fixture
def s1_nrb_stac() -> pystac.Item:
    return pystac.item.Item.from_file(str(TEST_DATA_FOLDER.joinpath(S1_NRB_STAC)))


@pytest.fixture
def s1_nrb_product(s1_nrb_metadata_type) -> Product:
    filepath = TEST_DATA_FOLDER.joinpath(S1_NRB_PRODUCT)
    (_, doc), *_ = read_documents(filepath)
    return Product(s1_nrb_metadata_type, doc)
