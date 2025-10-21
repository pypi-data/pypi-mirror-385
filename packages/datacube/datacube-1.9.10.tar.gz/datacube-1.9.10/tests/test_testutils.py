# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
import pytest
from odc.geo import xy_

from datacube.testutils import mk_sample_dataset, mk_sample_xr_dataset
from datacube.testutils.io import native_geobox
from datacube.testutils.threads import FakeThreadPoolExecutor


def test_fakethreadpool() -> None:
    def tfunc(a: int, b: int = 0, please_fail: bool = False) -> int:
        if please_fail:
            raise ValueError("as you wish")
        if a == 13:
            raise ValueError("13")
        return a + b

    pool = FakeThreadPoolExecutor()

    assert pool.submit(tfunc, 1).result() == 1
    assert pool.submit(tfunc, 1, 2).result() == 3

    fut = pool.submit(tfunc, 1, please_fail=True)
    assert fut.done()
    assert fut.exception() is not None

    with pytest.raises(ValueError):
        fut.result()

    ff = list(pool.map(tfunc, range(14)))
    assert len(ff) == 14
    assert [f.result() for f in ff[:13]] == list(range(13))
    assert ff[13].exception() is not None

    aa = list(range(10))
    bb = aa[::-1]
    ff = list(pool.map(tfunc, aa, bb))
    assert len(ff) == 10
    assert [f.result() for f in ff[:13]] == [a + b for a, b in zip(aa, bb)]

    pool.shutdown()


def test_mk_sample_xr() -> None:
    xx = mk_sample_xr_dataset()
    assert "band" in xx.data_vars
    assert list(xx.coords) == ["time", "y", "x", "spatial_ref"]
    assert xx.band.dims == ("time", "y", "x")
    assert xx.odc.geobox is not None

    assert mk_sample_xr_dataset(name="xx", shape=(3, 7)).xx.shape == (1, 3, 7)
    assert mk_sample_xr_dataset(name="xx", time=None, shape=(3, 7)).xx.shape == (3, 7)
    assert mk_sample_xr_dataset(name="xx", time=None).xx.dims == ("y", "x")

    assert mk_sample_xr_dataset(resolution=(1, 100)).odc.geobox.resolution == xy_(
        100, 1
    )
    assert mk_sample_xr_dataset(
        resolution=(1, 100), xy=(3, 55)
    ).odc.geobox.transform * (0, 0) == (3, 55)


def test_native_geobox_ingested() -> None:
    from datacube.testutils.geom import AlbersGS
    from datacube.testutils.io import native_geobox

    gbox = AlbersGS.tile_geobox((15, -40))
    ds = mk_sample_dataset(
        [{"name": "a"}], geobox=gbox, product_opts={"with_grid_spec": True}
    )

    assert native_geobox(ds) == gbox

    # check that dataset covering several tiles is detected as invalid
    ds = mk_sample_dataset(
        [{"name": "a"}],
        geobox=gbox.buffered(10, 10),
        product_opts={"with_grid_spec": True},
    )

    with pytest.raises(ValueError):
        native_geobox(ds)


def test_native_geobox_eo3(eo3_dataset_s2) -> None:
    ds = eo3_dataset_s2
    assert ds.crs is not None
    assert "blue" in ds.measurements

    gb1 = native_geobox(ds, basis="blue")

    assert gb1.width == 10980
    assert gb1.height == 10980
    assert gb1.crs == ds.crs

    gb1_ = native_geobox(ds, ("blue", "red", "green"))
    assert gb1_ == gb1

    gb2 = native_geobox(ds, ["swir_1", "swir_2"])
    assert gb2 != gb1
    assert gb2.width == 5490
    assert gb2.height == 5490
    assert gb2.crs == ds.crs

    with pytest.raises(ValueError):
        native_geobox(ds)

    with pytest.raises(ValueError):
        native_geobox(ds, ["no_such_band"])

    ds.metadata_doc["measurements"]["red_edge_1"]["grid"] = "no-such-grid"

    with pytest.raises(ValueError):
        native_geobox(ds, ["red_edge_1"])
