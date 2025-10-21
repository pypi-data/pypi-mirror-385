# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
# TODO: type hints need attention
"""Tools for working with EO3 metadata"""

from collections.abc import Iterable, Mapping
from functools import reduce
from typing import Any, cast
from uuid import UUID

from affine import Affine
from odc.geo import (
    CRS,
    BoundingBox,
    CoordList,
    Geometry,
    SomeCRS,
)
from odc.geo.geom import lonlat_bounds, polygon

EO3_SCHEMA = "https://schemas.opendatacube.org/dataset"


class EO3Grid:
    def __init__(self, grid: dict[str, Any]) -> None:
        shape = grid.get("shape")
        if shape is None:
            raise ValueError("Each grid must have a shape")
        if len(shape) != 2:
            raise ValueError("Grid shape must be two dimensional")
        self.shape = cast(tuple[int, int], tuple(int(x) for x in shape))
        xform = grid.get("transform")
        if xform is None:
            raise ValueError("Each grid must have a transform")
        if len(xform) != 6 and len(xform) != 9:
            raise ValueError("Grid transform must have 6 or 9 elements.")
        for elem in xform:
            if type(elem) not in (int, float):
                raise ValueError("All grid transform elements must be numbers")
        if len(xform) == 9 and list(xform[6:]) != [0, 0, 1]:
            raise ValueError("Grid transform must be a valid Affine matrix")
        self.transform = Affine(*xform[:6])

    def points(self, ring: bool = False) -> CoordList:
        ny, nx = (float(dim) for dim in self.shape)
        pts = [(0.0, 0.0), (nx, 0.0), (nx, ny), (0.0, ny)]
        if ring:
            pts += pts[:1]
        return [self.transform * pt for pt in pts]

    def ref_points(self) -> dict[str, dict[str, float]]:
        nn = ["ul", "ur", "lr", "ll"]
        return {n: {"x": x, "y": y} for n, (x, y) in zip(nn, self.points())}

    def polygon(self, crs: SomeCRS | None = None) -> Geometry:
        return polygon(self.points(ring=True), crs=crs)


def eo3_lonlat_bbox(
    grids: Iterable[EO3Grid],
    crs: CRS,
    valid_data: Geometry | None = None,
    resolution: float | None = None,
) -> BoundingBox:
    """Compute bounding box for all grids in Lon/Lat"""
    if valid_data is not None:
        return lonlat_bounds(valid_data, resolution=resolution)

    all_grids_extent = reduce(
        lambda x, y: x.union(y), (grid.polygon(crs) for grid in grids)
    )
    return lonlat_bounds(all_grids_extent, resolution=resolution)


def eo3_grid_spatial(
    doc: Mapping[str, Any], resolution: float | None = None, grid_name: str = "default"
) -> dict[str, Any]:
    """Using doc[grids|crs|geometry] compute EO3 style grid spatial:

    Note that `geo_ref_points` are set to the 4 corners of the default grid
    only, while lon/lat bounds are computed using all the grids, unless tighter
    valid region is defined via `geometry` key, in which case it is used to
    determine lon/lat bounds instead.
    Uses the default grid.

    inputs:

    ```
    crs: "<:str>"
    geometry: <:GeoJSON object>  # optional
    grids:
       default:
          shape: [ny: int, nx: int]
          transform: [a0, a1, a2, a3, a4, a5, 0, 0, 1]
       <...> # optionally more grids
    ```

    Where transform is a linear mapping matrix from pixel space to projected
    space encoded in row-major order:

       [X]   [a0, a1, a2] [ Pixel]
       [Y] = [a3, a4, a5] [ Line ]
       [1]   [ 0,  0,  1] [  1   ]

    outputs:
    ```
      extent:
        lat: {begin=<>, end=<>}
        lon: {begin=<>, end=<>}

      grid_spatial:
        projection:
          spatial_reference: "<crs>"
          geo_ref_points: {ll: {x:<>, y:<>}, ...}
          valid_data: {...}
    ```
    """
    gridspecs = doc.get("grids", {})
    crs = doc.get("crs")
    if crs is None or not gridspecs:
        raise ValueError("Input must have crs and grids.")
    grids = {name: EO3Grid(grid_spec) for name, grid_spec in gridspecs.items()}
    grid = grids.get(grid_name)
    if not grid:
        raise ValueError(f"Input must have grids.{grid_name}")

    geometry = doc.get("geometry")
    if geometry is not None:
        valid_data: dict[str, Any] = {"valid_data": geometry}
        valid_geom: Geometry | None = polygon(
            valid_data["valid_data"]["coordinates"][0], crs=crs
        )
    else:
        valid_data = {"valid_data": grid.polygon().json}
        valid_geom = None

    oo = {
        "grid_spatial": {
            "projection": {
                "spatial_reference": crs,
                "geo_ref_points": grid.ref_points(),
                **valid_data,
            }
        }
    }

    x1, y1, x2, y2 = eo3_lonlat_bbox(
        grids.values(), crs, valid_data=valid_geom, resolution=resolution
    )
    oo["extent"] = {"lon": {"begin": x1, "end": x2}, "lat": {"begin": y1, "end": y2}}
    return oo


def add_eo3_parts(
    doc: Mapping[str, Any], resolution: float | None = None
) -> dict[str, Any]:
    """Add spatial keys the DB requires to eo3 metadata"""
    # Clone and update to ensure idempotency
    out = dict(**doc)
    out.update(eo3_grid_spatial(doc, resolution=resolution))
    return out


def is_doc_eo3(doc: Mapping[str, Any]) -> bool:
    """Is this document eo3?

    :param doc: Parsed ODC Dataset metadata document

    :returns:
        False if this document is a legacy dataset
        True if this document is eo3

    :raises ValueError: For an unsupported document
    """
    schema = doc.get("$schema")
    # All legacy documents had no schema at all.
    if schema is None:
        return False

    if schema == EO3_SCHEMA:
        return True

    # Otherwise it has an unknown schema.
    #
    # Reject it for now.
    # We don't want future documents (like Stac items, or "eo4") to be quietly
    # accepted as legacy eo.
    raise ValueError(f"Unsupported dataset schema: {schema!r}")


def is_doc_geo(doc: Mapping[str, Any], check_eo3: bool = True) -> bool:
    """Is this document geospatial?

    :param doc: Parsed ODC Dataset metadata document
    :param check_eo3: Set to false to skip the EO3 check and assume doc isn't EO3.

    :returns:
        True if this document specifies geospatial dimensions
        False if this document does not specify geospatial dimensions (e.g. telemetry only)

    :raises ValueError: For an unsupported document
    """
    # EO3 is geospatial
    if check_eo3 and is_doc_eo3(doc):
        return True
    # Does this cover EO legacy datasets ok? at all??
    return "extent" in doc or "grid_spatial" in doc


def prep_eo3(
    doc: dict[str, Any],
    auto_skip: bool = False,
    resolution: float | None = None,
    remap_lineage: bool = True,
) -> dict[str, Any]:
    """Modify spatial and lineage sections of eo3 metadata

    Should be idempotent:  prep_eo3(doc, **kwargs) == prep_eo3(prep_eo3(doc, **kwargs), **kwargs)

    :param doc: input document
    :param auto_skip: If true check if dataset is EO3 and if not
                      silently return input dataset without modifications
    :param remap_lineage: If True (default) disambiguate lineage classifiers so that
                          source_id and classifier form a unique index (for indexes that DON'T
                          support external_lineage).
                          If False, leave lineage in the same format.
    """
    if doc is None:
        return None

    if auto_skip and not is_doc_eo3(doc):
        return doc

    def stringify(u: str | UUID | None) -> str | None:
        return u if isinstance(u, str) else str(u) if u else None

    doc["id"] = stringify(doc.get("id"))

    doc = add_eo3_parts(doc, resolution=resolution)
    if remap_lineage:
        lineage = doc.pop("lineage", {})
        if isinstance(lineage, dict) and "source_datasets" in lineage:
            # Is already in pseudo-embedded rewritten form - keep as is.
            doc["lineage"] = lineage
        else:

            def lineage_remap(name: str, uuids) -> dict[str, Any]:
                """Turn name, [uuid] -> {name: {id: uuid}}"""
                if len(uuids) == 0:
                    return {}
                if isinstance(uuids, dict) or isinstance(uuids[0], dict):
                    raise ValueError(
                        "Embedded lineage not supported for eo3 metadata types"
                    )
                if len(uuids) == 1:
                    if isinstance(uuids[0], dict):
                        return {name: uuids}
                    return {name: {"id": stringify(uuids[0])}}

                out: dict[str, Any] = {}
                for idx, uuid in enumerate(uuids, start=1):
                    if isinstance(uuids, dict):
                        out[name] = uuid
                    else:
                        out[name + str(idx)] = {"id": stringify(uuid)}
                return out

            sources = {}
            for name, uuids in lineage.items():
                sources.update(lineage_remap(name, uuids))

            doc["lineage"] = {"source_datasets": sources}
    return doc
