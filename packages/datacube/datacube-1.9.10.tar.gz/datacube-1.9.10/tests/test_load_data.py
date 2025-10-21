# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest
from typing_extensions import Never
from xarray import Dataset

from datacube import Datacube
from datacube.api.query import query_group_by
from datacube.testutils import (
    gen_tiff_dataset,
    mk_sample_dataset,
    mk_test_image,
)
from datacube.testutils.io import (
    get_raster_info,
    native_geobox,
    native_load,
    rio_slurp,
    rio_slurp_xarray,
    write_gtiff,
)
from datacube.testutils.iodriver import NetCDF
from datacube.utils import ignore_exceptions_if


def test_load_data(tmpdir) -> None:
    tmpdir = Path(str(tmpdir))

    group_by = query_group_by("time")
    spatial = {
        "resolution": (15, -15),
        "offset": (11230, 1381110),
    }

    nodata = -999
    aa = mk_test_image(96, 64, "int16", nodata=nodata)

    ds, geobox = gen_tiff_dataset(
        [SimpleNamespace(name="aa", values=aa, nodata=nodata)],
        tmpdir,
        prefix="ds1-",
        timestamp="2018-07-19",
        **spatial,
    )
    assert ds.time is not None

    ds2, _ = gen_tiff_dataset(
        [SimpleNamespace(name="aa", values=aa, nodata=nodata)],
        tmpdir,
        prefix="ds2-",
        timestamp="2018-07-19",
        **spatial,
    )
    assert ds.time is not None
    assert ds.time == ds2.time

    sources = Datacube.group_datasets([ds], "time")
    sources2 = Datacube.group_datasets([ds, ds2], group_by)

    mm = ["aa"]
    mm = [ds.product.measurements[k] for k in mm]

    ds_data = Datacube.load_data(sources, geobox, mm)
    assert ds_data.aa.nodata == nodata
    np.testing.assert_array_equal(aa, ds_data.aa.values[0])

    custom_fuser_call_count = 0

    def custom_fuser(dest: np.ndarray[Any, Any], delta) -> None:
        nonlocal custom_fuser_call_count
        custom_fuser_call_count += 1
        dest[:] += delta

    progress_call_data = []

    def progress_cbk(n: int, nt: int) -> None:
        progress_call_data.append((n, nt))

    ds_data = Datacube.load_data(
        sources2, geobox, mm, fuse_func=custom_fuser, progress_cbk=progress_cbk
    )
    assert ds_data.aa.nodata == nodata
    assert custom_fuser_call_count > 0
    np.testing.assert_array_equal(nodata + aa + aa, ds_data.aa.values[0])

    assert progress_call_data == [(1, 2), (2, 2)]

    ds_data = Datacube.load_data(sources, geobox, mm, dask_chunks={"x": 8, "y": 8})
    assert ds_data.aa.nodata == nodata
    np.testing.assert_array_equal(aa, ds_data.aa.values[0])

    ds_data = Datacube.load_data(sources, geobox, mm, dask_chunks={}, driver="rio")
    assert ds_data.aa.attrs == {"nodata": nodata, "units": "1"}


def test_load_data_dask(tmp_path) -> None:
    spatial = {
        "resolution": (15, -15),
        "offset": (11230, 1381110),
    }

    nodata = -999
    aa = mk_test_image(128, 128, "int16", nodata=nodata)

    ds, geobox = gen_tiff_dataset(
        [SimpleNamespace(name="aa", values=aa, nodata=nodata)],
        tmp_path,
        prefix="ds1-",
        timestamp="2018-07-19",
        **spatial,
    )

    sources = Datacube.group_datasets([ds], "time")
    mm = ds.product.measurements

    import dask

    dask.config.set(scheduler="synchronous")

    ds_data = Datacube.load_data(
        sources, geobox, mm, dask_chunks={"x": 50, "y": 67}
    )  # spatial dims not equal!
    ds_data.compute()
    assert ds_data.aa.nodata == nodata
    np.testing.assert_array_equal(aa, ds_data.aa.values[0])

    # Include an empty value area outside the data area, large enough to include completely empty chunks
    geobox = geobox.pad(100, 100)
    ds_data = Datacube.load_data(
        sources, geobox, mm, dask_chunks={"x": 50, "y": 67}
    )  # spatial dims not equal!

    ds_data.compute()
    assert ds_data.aa.nodata == nodata
    np.testing.assert_array_equal(aa, ds_data.aa.values[0, 100:228, 100:228])


def test_load_data_with_url_mangling(tmpdir) -> None:
    actual_tmpdir = Path(str(tmpdir))
    recorded_tmpdir = Path(str(tmpdir / "not" / "actual" / "location"))

    def url_mangler(raw: str) -> str:
        actual_uri_root = actual_tmpdir.absolute().as_uri()
        recorded_uri_root = recorded_tmpdir.absolute().as_uri()
        return raw.replace(recorded_uri_root, actual_uri_root)

    group_by = query_group_by("time")
    spatial = {
        "resolution": (15, -15),
        "offset": (11230, 1381110),
    }

    nodata = -999
    aa = mk_test_image(96, 64, "int16", nodata=nodata)

    ds, geobox = gen_tiff_dataset(
        [SimpleNamespace(name="aa", values=aa, nodata=nodata)],
        tmpdir,
        prefix="ds1-",
        timestamp="2018-07-19",
        base_folder_of_record=recorded_tmpdir,
        **spatial,
    )
    assert ds.time is not None

    ds2, _ = gen_tiff_dataset(
        [SimpleNamespace(name="aa", values=aa, nodata=nodata)],
        tmpdir,
        prefix="ds2-",
        timestamp="2018-07-19",
        base_folder_of_record=recorded_tmpdir,
        **spatial,
    )
    assert ds.time is not None
    assert ds.time == ds2.time

    sources = Datacube.group_datasets([ds], "time")
    sources2 = Datacube.group_datasets([ds, ds2], group_by)

    mm = ["aa"]
    mm = [ds.product.measurements[k] for k in mm]

    ds_data = Datacube.load_data(sources, geobox, mm, patch_url=url_mangler)
    assert ds_data.aa.nodata == nodata
    np.testing.assert_array_equal(aa, ds_data.aa.values[0])

    ds_data = Datacube.load_data(
        sources, geobox, mm, dask_chunks={"x": 8, "y": 8}, patch_url=url_mangler
    )
    assert ds_data.aa.nodata == nodata
    np.testing.assert_array_equal(aa, ds_data.aa.values[0])

    custom_fuser_call_count = 0

    def custom_fuser(dest: np.ndarray[Any, Any], delta) -> None:
        nonlocal custom_fuser_call_count
        custom_fuser_call_count += 1
        dest[:] += delta

    progress_call_data = []

    def progress_cbk(n: int, nt: int) -> None:
        progress_call_data.append((n, nt))

    ds_data = Datacube.load_data(
        sources2,
        geobox,
        mm,
        fuse_func=custom_fuser,
        progress_cbk=progress_cbk,
        patch_url=url_mangler,
    )
    assert ds_data.aa.nodata == nodata
    assert custom_fuser_call_count > 0
    np.testing.assert_array_equal(nodata + aa + aa, ds_data.aa.values[0])

    assert progress_call_data == [(1, 2), (2, 2)]


def test_load_data_cbk(tmpdir) -> None:
    from datacube.api import TerminateCurrentLoad

    tmpdir = Path(str(tmpdir))

    spatial = {
        "resolution": (15, -15),
        "offset": (11230, 1381110),
    }

    nodata = -999
    aa = mk_test_image(96, 64, "int16", nodata=nodata)

    bands = [
        SimpleNamespace(name=name, values=aa, nodata=nodata) for name in ["aa", "bb"]
    ]

    ds, geobox = gen_tiff_dataset(
        bands, tmpdir, prefix="ds1-", timestamp="2018-07-19", **spatial
    )
    assert ds.time is not None

    ds2, _ = gen_tiff_dataset(
        bands, tmpdir, prefix="ds2-", timestamp="2018-07-19", **spatial
    )
    assert ds.time is not None
    assert ds.time == ds2.time

    sources = Datacube.group_datasets([ds, ds2], "time")
    progress_call_data = []

    def progress_cbk(n: int, nt: int) -> None:
        progress_call_data.append((n, nt))

    ds_data = Datacube.load_data(
        sources, geobox, ds.product.measurements, progress_cbk=progress_cbk
    )

    assert progress_call_data == [(1, 4), (2, 4), (3, 4), (4, 4)]
    np.testing.assert_array_equal(aa, ds_data.aa.values[0])
    np.testing.assert_array_equal(aa, ds_data.bb.values[0])

    def progress_cbk_fail_early(n: int, nt: int) -> Never:
        progress_call_data.append((n, nt))
        raise TerminateCurrentLoad()

    def progress_cbk_fail_early2(n: int, nt: int) -> None:
        progress_call_data.append((n, nt))
        if n > 1:
            raise KeyboardInterrupt()

    progress_call_data = []
    ds_data = Datacube.load_data(
        sources, geobox, ds.product.measurements, progress_cbk=progress_cbk_fail_early
    )

    assert progress_call_data == [(1, 4)]
    assert ds_data.dc_partial_load is True
    np.testing.assert_array_equal(aa, ds_data.aa.values[0])
    np.testing.assert_array_equal(nodata, ds_data.bb.values[0])

    progress_call_data = []
    ds_data = Datacube.load_data(
        sources, geobox, ds.product.measurements, progress_cbk=progress_cbk_fail_early2
    )

    assert ds_data.dc_partial_load is True
    assert progress_call_data == [(1, 4), (2, 4)]


def test_hdf5_lock_release_on_failure() -> None:
    from datacube.storage import BandInfo
    from datacube.storage._rio import HDF5_LOCK, RasterDatasetDataSource

    band = {"name": "xx", "layer": "xx", "dtype": "uint8", "units": "K", "nodata": 33}

    ds = mk_sample_dataset(
        [band],
        uri="file:///tmp/this_probably_doesnot_exist_37237827513/xx.nc",
        format=NetCDF,
    )
    src = RasterDatasetDataSource(BandInfo(ds, "xx"))

    with pytest.raises(OSError):  # noqa: SIM117
        with src.open():
            raise Exception("Did not expect to get here")

    assert not HDF5_LOCK._is_owned()  # type: ignore[attr-defined]


def test_rio_slurp(tmpdir) -> None:
    w, h, dtype, nodata, ndw = 96, 64, "int16", -999, 7

    pp = Path(str(tmpdir))

    aa = mk_test_image(w, h, dtype, nodata, nodata_width=ndw)

    assert aa.shape == (h, w)
    assert aa.dtype.name == dtype
    assert aa[10, 30] == (30 << 8) | 10
    assert aa[10, 11] == nodata

    aa0 = aa.copy()
    mm0 = write_gtiff(pp / "rio-slurp-aa.tif", aa, nodata=-999, overwrite=True)
    mm00 = write_gtiff(
        pp / "rio-slurp-aa-missing-nodata.tif", aa, nodata=None, overwrite=True
    )

    aa, mm = rio_slurp(mm0.path)
    np.testing.assert_array_equal(aa, aa0)
    assert mm.geobox == mm0.geobox
    assert aa.shape == mm.geobox.shape
    xx = rio_slurp_xarray(mm0.path)
    assert mm.geobox == xx.odc.geobox
    np.testing.assert_array_equal(xx.values, aa0)

    aa, mm = rio_slurp(mm0.path, aa0.shape)
    np.testing.assert_array_equal(aa, aa0)
    assert aa.shape == mm.geobox.shape
    assert mm.geobox is mm.src_geobox
    xx = rio_slurp_xarray(mm0.path, aa0.shape)
    assert mm.geobox == xx.odc.geobox
    np.testing.assert_array_equal(xx.values, aa0)

    aa, mm = rio_slurp(mm0.path, (3, 7))
    assert aa.shape == (3, 7)
    assert aa.shape == mm.geobox.shape
    assert mm.geobox != mm.src_geobox
    assert mm.src_geobox == mm0.geobox
    assert mm.geobox.extent == mm0.geobox.extent

    aa, mm = rio_slurp(mm0.path, aa0.shape)
    np.testing.assert_array_equal(aa, aa0)
    assert aa.shape == mm.geobox.shape

    aa, mm = rio_slurp(mm0.path, mm0.geobox, resampling="nearest")
    np.testing.assert_array_equal(aa, aa0)
    xx = rio_slurp_xarray(mm0.path, mm0.geobox)
    assert mm.geobox == xx.odc.geobox
    np.testing.assert_array_equal(xx.values, aa0)

    aa, mm = rio_slurp(mm0.path, geobox=mm0.geobox, dtype="float32")
    assert aa.dtype == "float32"
    np.testing.assert_array_equal(aa, aa0.astype("float32"))
    xx = rio_slurp_xarray(mm0.path, geobox=mm0.geobox)
    assert mm.geobox == xx.odc.geobox
    assert mm.nodata == xx.nodata
    np.testing.assert_array_equal(xx.values, aa0)

    aa, mm = rio_slurp(mm0.path, mm0.geobox, dst_nodata=-33)
    np.testing.assert_array_equal(aa == -33, aa0 == -999)

    aa, mm = rio_slurp(mm00.path, mm00.geobox, dst_nodata=None)
    np.testing.assert_array_equal(aa, aa0)


def test_rio_slurp_with_geobox(tmpdir) -> None:
    w, h, dtype, nodata, ndw = 96, 64, "int16", -999, 7

    pp = Path(str(tmpdir))
    aa = mk_test_image(w, h, dtype, nodata, nodata_width=ndw)
    assert aa.dtype.name == dtype
    assert aa[10, 30] == (30 << 8) | 10
    assert aa[10, 11] == nodata

    aa = np.stack([aa, aa[::-1, ::-1]])
    assert aa.shape == (2, h, w)
    aa0 = aa.copy()

    mm = write_gtiff(pp / "rio-slurp-aa.tif", aa, nodata=-999, overwrite=True)
    assert mm.count == 2

    aa, mm = rio_slurp(mm.path, mm.geobox)
    assert aa.shape == aa0.shape
    np.testing.assert_array_equal(aa, aa0)


def test_missing_file_handling() -> None:
    with pytest.raises(IOError):
        rio_slurp("no-such-file.tiff")

    # by default should catch any exception
    with ignore_exceptions_if(True):
        rio_slurp("no-such-file.tiff")

    # this is equivalent to previous default behaviour, note that missing http
    # resources are not OSError
    with ignore_exceptions_if(True, (OSError,)):
        rio_slurp("no-such-file.tiff")

    # check that only requested exceptions are caught
    with pytest.raises(IOError):  # noqa: SIM117
        with ignore_exceptions_if(True, (ValueError, ArithmeticError)):
            rio_slurp("no-such-file.tiff")


def test_native_load(tmpdir) -> None:
    tmpdir = Path(str(tmpdir))
    spatial = {
        "resolution": (15, -15),
        "offset": (11230, 1381110),
    }
    nodata = -999
    aa = mk_test_image(96, 64, "int16", nodata=nodata)
    cc = mk_test_image(32, 16, "int16", nodata=nodata)

    bands = [
        SimpleNamespace(name=name, values=aa, nodata=nodata) for name in ["aa", "bb"]
    ]
    bands.append(SimpleNamespace(name="cc", values=cc, nodata=nodata))

    ds, geobox = gen_tiff_dataset(
        bands[:2], tmpdir, prefix="ds1-", timestamp="2018-07-19", **spatial
    )

    assert set(get_raster_info(ds)) == set(ds.measurements)

    xx = native_load([ds], ["aa", "bb"], Datacube.group_datasets, "time")
    assert isinstance(xx, Dataset)
    assert xx.odc.geobox == geobox
    np.testing.assert_array_equal(aa, xx.isel(time=0).aa.values)
    np.testing.assert_array_equal(aa, xx.isel(time=0).bb.values)

    ds, geobox_cc = gen_tiff_dataset(
        bands, tmpdir, prefix="ds2-", timestamp="2018-07-19", **spatial
    )

    # cc is different size from aa,bb
    # cc is reprojected
    xx = native_load([ds], ["aa", "bb", "cc"], Datacube.group_datasets, "time")
    assert isinstance(xx, Dataset)
    assert xx.odc.geobox == geobox
    assert xx.odc.geobox != geobox_cc
    np.testing.assert_array_equal(aa, xx.isel(time=0).aa.values)
    np.testing.assert_array_equal(aa, xx.isel(time=0).bb.values)

    assert native_geobox(ds, basis="aa") == geobox
    xx = native_load(
        [ds], ["aa", "bb", "cc"], Datacube.group_datasets, "time", basis="aa"
    )
    assert isinstance(xx, Dataset)
    assert xx.odc.geobox == geobox
    np.testing.assert_array_equal(aa, xx.isel(time=0).aa.values)
    np.testing.assert_array_equal(aa, xx.isel(time=0).bb.values)

    # cc is compatible with self
    xx = native_load([ds], ["cc"], Datacube.group_datasets, "time")
    assert isinstance(xx, Dataset)
    assert xx.odc.geobox == geobox_cc
    np.testing.assert_array_equal(cc, xx.isel(time=0).cc.values)
