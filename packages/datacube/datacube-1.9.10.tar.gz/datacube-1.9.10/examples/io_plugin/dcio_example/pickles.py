# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""Example reader plugin"""

import pickle
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

from datacube.utils.uris import normalise_path

PROTOCOL = "file"
FORMAT = "pickle"


def uri_split(uri):
    loc = uri.find("://")
    if loc < 0:
        return uri, PROTOCOL
    return uri[loc + 3 :], uri[:loc]


class PickleDataSource:
    class BandDataSource:
        def __init__(self, da):
            self._da = da
            self.nodata = da.nodata

        @property
        def crs(self):
            return self._da.crs

        @property
        def transform(self):
            return self._da.affine

        @property
        def dtype(self):
            return self._da.dtype

        @property
        def shape(self):
            return self._da.shape

        def read(self, window=None, out_shape=None):
            if window is None:
                data = self._da.values
            else:
                rows, cols = [slice(*w) for w in window]
                data = self._da.values[rows, cols]

            if out_shape is None or out_shape == data.shape:
                return data

            raise NotImplementedError(
                "Native reading not supported for this data source"
            )

    def __init__(self, band):
        self._band = band
        uri = band.uri
        self._filename, protocol = uri_split(uri)

        if protocol not in [PROTOCOL, "pickle"]:
            raise ValueError("Expected file:// or pickle:// url")

    @contextmanager
    def open(self):
        with open(self._filename, "rb") as f:
            ds = pickle.load(f)

        yield PickleDataSource.BandDataSource(ds[self._band.name].isel(time=0))


class PickleReaderDriver:
    def __init__(self) -> None:
        self.name = "PickleReader"
        self.protocols = [PROTOCOL, "pickle"]
        self.formats = [FORMAT]

    def supports(self, protocol, fmt) -> bool:
        return protocol in self.protocols and fmt in self.formats

    def new_datasource(self, band) -> PickleDataSource:
        return PickleDataSource(band)


def rdr_driver_init() -> PickleReaderDriver:
    return PickleReaderDriver()


class PickleWriterDriver:
    def __init__(self) -> None:
        pass

    @property
    def aliases(self) -> list[str]:
        return ["pickles"]

    @property
    def format(self) -> str:
        return FORMAT

    @property
    def uri_scheme(self) -> str:
        return PROTOCOL

    def mk_uri(self, file_path: Path | str) -> str:
        """
        Constructs a URI from the file_path.

        A typical implementation should return f'{scheme}://{file_path}'

        Example:
            file_path = '/path/to/my_file.pickled'

            mk_uri(file_path) should return 'file:///path/to/my_file.pickled'

        :param file_path: The file path of the file to be converted into a URI.
        :return: file_path as a URI that the Driver understands.
        """
        return normalise_path(file_path).as_uri()

    def write_dataset_to_storage(
        self, dataset, file_uri, global_attributes=None, variable_params=None, **kwargs
    ) -> dict:
        filepath = Path(urlsplit(file_uri).path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("wb") as f:
            pickle.dump(dataset, f)
        return {}


def writer_driver_init():
    return PickleWriterDriver()
