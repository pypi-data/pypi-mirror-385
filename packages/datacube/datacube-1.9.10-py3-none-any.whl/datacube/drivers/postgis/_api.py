# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0

# We often have one-arg-per column, so these checks aren't so useful.
# pylint: disable=too-many-arguments,too-many-public-methods,too-many-lines

# SQLAlchemy queries require "column == None", not "column is None" due to operator overloading:
# pylint: disable=singleton-comparison

"""
Persistence API implementation for postgis.
"""

import datetime
import json
import logging
import uuid
from collections.abc import Generator, Iterable, Mapping, Sequence
from typing import Any
from typing import cast as type_cast

from odc.geo import CRS, Geometry
from sqlalchemy import (
    and_,
    cast,
    column,
    delete,
    func,
    or_,
    select,
    text,
    update,
)
from sqlalchemy.dialects.postgresql import INTERVAL, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import Select
from typing_extensions import override

from datacube.index.abstract import DSID
from datacube.index.fields import OrExpression
from datacube.model import Range
from datacube.model.fields import Expression
from datacube.model.lineage import LineageDirection, LineageRelation
from datacube.utils.uris import split_uri

from ...utils.changes import Offset
from . import _core
from ._fields import (
    DateDocField,
    DateRangeDocField,
    NativeField,
    PgExpression,
    PgField,
    SimpleDocField,
    UnindexableValue,
    parse_fields,
)
from ._schema import (
    Dataset,
    DatasetHome,
    DatasetLineage,
    MetadataType,
    Product,
    search_field_index_map,
    search_field_indexes,
)
from ._spatial import (
    extract_geometry_from_eo3_projection,
    generate_dataset_spatial_values,
    geom_alchemy,
)
from .sql import escape_pg_identifier

_LOG: logging.Logger = logging.getLogger(__name__)


# Make a function because it's broken
def _dataset_select_fields() -> tuple:
    return tuple(f.alchemy_expression for f in _dataset_fields())


def _base_known_fields() -> dict[str, PgField]:
    fields = get_native_fields().copy()
    fields["archived"] = NativeField(
        "archived", "Archived date", Dataset.__table__.c.archived
    )
    return fields


def _dataset_fields() -> tuple:
    native_flds = get_native_fields()
    return (
        native_flds["id"],
        native_flds["indexed_time"],
        native_flds["indexed_by"],
        native_flds["product_id"],
        native_flds["metadata_type_id"],
        native_flds["metadata_doc"],
        NativeField("archived", "Archived date", Dataset.__table__.c.archived),
        native_flds["uri"],
    )


def get_native_fields() -> dict[str, PgField]:
    # Native fields (hard-coded into the schema)
    fields: dict[str, PgField] = {
        "id": NativeField("id", "Dataset UUID", Dataset.__table__.c.id),
        "indexed_time": NativeField(
            "indexed_time", "When dataset was indexed", Dataset.__table__.c.added
        ),
        "indexed_by": NativeField(
            "indexed_by", "User who indexed the dataset", Dataset.__table__.c.added_by
        ),
        "product": NativeField(
            "product",
            "Product name",
            Product.__table__.c.name,
            join_clause=(Product.id == Dataset.product_ref),
        ),
        "product_id": NativeField(
            "product_id", "ID of a dataset type", Dataset.__table__.c.product_ref
        ),
        "metadata_type": NativeField(
            "metadata_type",
            "Metadata type name of dataset",
            MetadataType.__table__.c.name,
            join_clause=(MetadataType.id == Dataset.metadata_type_ref),
        ),
        "metadata_type_id": NativeField(
            "metadata_type_id",
            "ID of a metadata type",
            Dataset.__table__.c.metadata_type_ref,
        ),
        "metadata_doc": NativeField(
            "metadata_doc",
            "Full metadata document",
            Dataset.metadata_doc,  # type: ignore[arg-type]
        ),
        "uri": NativeField(
            "uri",
            "Dataset URI",
            Dataset.__table__.c.uri_body,
            alchemy_expression=Dataset.uri,
        ),
    }
    return fields


def mk_simple_offset_field(
    field_name: str, description: str, offset: Offset
) -> SimpleDocField:
    return SimpleDocField(
        name=field_name,
        description=description,
        alchemy_column=Dataset.metadata_doc,
        indexed=False,
        offset=offset,
    )


def get_dataset_fields(
    metadata_type_definition: Mapping[str, Any],
) -> dict[str, PgField]:
    dataset_section = metadata_type_definition["dataset"]

    fields = get_native_fields()
    # "Fixed fields" (not dynamic: defined in metadata type schema)
    fields.update(
        {
            "creation_time": DateDocField(
                "creation_time",
                "Time when dataset was created (processed)",
                Dataset.metadata_doc,
                False,
                offset=dataset_section.get("creation_dt") or ("creation_dt",),
            ),
            "format": mk_simple_offset_field(
                "format",
                "File format (GeoTiff, NetCDF)",
                dataset_section.get("format") or ("format", "name"),
            ),
            "label": mk_simple_offset_field(
                "label", "Label", dataset_section.get("label") or ("label",)
            ),
        }
    )

    # noinspection PyTypeChecker
    fields.update(parse_fields(dataset_section["search_fields"], Dataset.metadata_doc))
    return fields


def non_native_fields(mdt_metadata: Mapping[str, Any]) -> dict[str, PgField]:
    return {
        name: field
        for name, field in get_dataset_fields(mdt_metadata).items()
        if not isinstance(field, NativeField)
    }


def extract_dataset_search_fields(ds_metadata, mdt_metadata: Mapping[str, Any]) -> dict:
    """
    :param ds_metadata: A Dataset metadata document
    :param mdt_metadata: The corresponding metadata-type definition document

    :return: A dictionary mapping search field names to (type_name, value) tuples.
    """
    return extract_dataset_fields(ds_metadata, non_native_fields(mdt_metadata))


def extract_dataset_fields(ds_metadata, fields: Mapping) -> dict:
    """
    :param ds_metadata: A Dataset metadata document
    :param fields: A dictionary of field names to Field objects

    :return: A dictionary mapping search field names to (type_name, value) tuples.
    """
    result = {}
    for field_name, field in fields.items():
        try:
            fld_type = field.type_name
            raw_val = field.extract(ds_metadata)
            sqla_val = field.search_value_to_alchemy(raw_val)
            result[field_name] = (fld_type, sqla_val)
        except UnindexableValue:
            continue
    return result


# Min/Max aggregating time fields for temporal_extent methods
time_min = DateDocField(
    "acquisition_time_min",
    "Min of time when dataset was acquired",
    Dataset.metadata_doc,
    False,  # is it indexed
    offset=[("properties", "dtr:start_datetime"), ("properties", "datetime")],
    selection="least",
)


time_max = DateDocField(
    "acquisition_time_max",
    "Max of time when dataset was acquired",
    Dataset.metadata_doc,
    False,  # is it indexed
    offset=[("properties", "dtr:end_datetime"), ("properties", "datetime")],
    selection="greatest",
)


class PostgisDbAPI:
    def __init__(self, parentdb, connection) -> None:
        self._db = parentdb
        self._connection = connection
        self._sqla_txn = None

    @property
    def in_transaction(self):
        return self._connection.in_transaction()

    def begin(self) -> None:
        self._connection.execution_options(isolation_level="REPEATABLE READ")
        self._sqla_txn = self._connection.begin()

    def _end_transaction(self) -> None:
        self._sqla_txn = None
        self._connection.execution_options(isolation_level="AUTOCOMMIT")

    def commit(self) -> None:
        self._sqla_txn.commit()  # type: ignore[attr-defined]
        self._end_transaction()

    def rollback(self) -> None:
        self._sqla_txn.rollback()  # type: ignore[attr-defined]
        self._end_transaction()

    def execute(self, command):
        return self._connection.execute(command)

    def insert_dataset(self, metadata_doc, dataset_id, product_id) -> bool:
        """
        Insert dataset if not already indexed.
        :return: whether it was inserted
        """
        metadata_subquery = (
            select(Product.metadata_type_ref)
            .where(Product.id == product_id)
            .scalar_subquery()
        )
        ret = self._connection.execute(
            insert(Dataset)
            .values(
                id=dataset_id,
                product_ref=product_id,
                metadata_doc=metadata_doc,
                metadata_type_ref=metadata_subquery,
            )
            .on_conflict_do_nothing(index_elements=["id"])
        )
        return ret.rowcount > 0

    def insert_dataset_bulk(self, values: Sequence[dict[str, Any]]) -> tuple[int, int]:
        requested = len(values)
        res = self._connection.execute(insert(Dataset).values(values))
        return res.rowcount, requested - res.rowcount

    def update_dataset(self, metadata_doc, dataset_id, product_id) -> bool:
        """
        Update dataset
        """
        res = self._connection.execute(
            update(Dataset)
            .returning(Dataset.id)
            .where(Dataset.id == dataset_id)
            .where(Dataset.product_ref == product_id)
            .values(metadata_doc=metadata_doc)
        )
        return res.rowcount > 0

    def insert_dataset_location(self, dataset_id: DSID, uri: str) -> bool:
        """
        Add a location to a dataset if it is not already recorded.

        Returns True if success, False if this location already existed
        """
        scheme, body = split_uri(uri)

        r = self._connection.execute(
            update(Dataset)
            .returning(Dataset.uri)
            .where(Dataset.id == dataset_id)
            .values(uri_scheme=scheme, uri_body=body)
        )

        return r.rowcount > 0

    def insert_dataset_search(self, search_table, dataset_id: DSID, key, value) -> bool:
        """
        Add/update a search field index entry for a dataset

        Returns True on success
        """
        if isinstance(value, Range):
            value = list(value)
        r = self._connection.execute(
            insert(search_table)
            .values(
                dataset_ref=dataset_id,
                search_key=key,
                search_val=value,
            )
            .on_conflict_do_update(
                index_elements=[search_table.dataset_ref, search_table.search_key],
                set_={"search_val": value},
            )
        )
        return r.rowcount > 0

    def insert_dataset_search_bulk(self, search_type: str, values) -> int:
        search_table = search_field_index_map[search_type]
        r = self._connection.execute(insert(search_table).values(values))
        return r.rowcount

    def insert_dataset_spatial(
        self, dataset_id: DSID, crs: CRS, extent: Geometry
    ) -> bool:
        """
        Add/update a spatial index entry for a dataset

        Returns True on success
        """
        values = generate_dataset_spatial_values(dataset_id, crs, extent)
        if values is None:
            return False
        SpatialIndex = self._db.spatial_index(crs)  # noqa: N806
        r = self._connection.execute(
            insert(SpatialIndex)
            .values(**values)
            .on_conflict_do_update(
                index_elements=[SpatialIndex.dataset_ref],
                set_={"extent": values["extent"]},
            )
        )
        return r.rowcount > 0

    def insert_dataset_spatial_bulk(self, crs, values) -> int:
        SpatialIndex = self._db.spatial_index(crs)  # noqa: N806
        r = self._connection.execute(insert(SpatialIndex).values(values))
        return r.rowcount

    def spatial_extent(self, ids, crs: CRS) -> Geometry | None:
        SpatialIndex = self._db.spatial_index(crs)  # noqa: N806
        if SpatialIndex is None:
            # Requested a CRS that has no spatial index, so use 4326 (which always has a spatial index)
            # and reproject to requested CRS.
            rv = self.spatial_extent(ids, CRS("epsg:4326"))
            assert rv is not None
            return rv.to_crs(crs)
        query = (
            select(func.ST_AsGeoJSON(func.ST_Union(SpatialIndex.extent)))
            .select_from(SpatialIndex)
            .where(SpatialIndex.dataset_ref.in_(ids))
        )
        result = self._connection.execute(query)
        for r in result:
            extent_json = r[0]
            if extent_json is None:
                return None
            return Geometry(json.loads(extent_json), crs=crs)
        return None

    def contains_dataset(self, dataset_id) -> bool:
        return bool(
            self._connection.execute(
                select(Dataset.id).where(Dataset.id == dataset_id)
            ).fetchone()
        )

    def datasets_intersection(self, dataset_ids) -> list:
        """Compute set intersection: db_dataset_ids & dataset_ids"""
        return [
            ds.id
            for ds in self._connection.execute(
                select(Dataset.id).where(Dataset.id.in_(dataset_ids))
            ).fetchall()
        ]

    def get_datasets_for_location(
        self, uri: str, mode: str | None = None
    ) -> Sequence[Dataset]:
        scheme, body = split_uri(uri)

        if mode is None:
            mode = "exact" if body.count("#") > 0 else "prefix"

        if mode == "exact":
            body_query = Dataset.uri_body == body
        elif mode == "prefix":
            body_query = Dataset.uri_body.startswith(body)
        else:
            raise ValueError(f"Unsupported query mode {mode}")

        return self._connection.execute(
            select(*_dataset_select_fields()).where(
                and_(Dataset.uri_scheme == scheme, body_query)
            )
        ).fetchall()

    def all_dataset_ids(self, archived: bool | None = False) -> Sequence:
        query = select(Dataset.id)
        if archived:
            query = query.where(Dataset.archived.is_not(None))
        elif archived is not None:
            query = query.where(Dataset.archived.is_(None))
        return self._connection.execute(query).fetchall()

    def archive_dataset(self, dataset_id) -> bool:
        r = self._connection.execute(
            update(Dataset)
            .where(Dataset.id == dataset_id)
            .where(Dataset.archived == None)
            .values(archived=func.now())
        )
        return r.rowcount > 0

    def restore_dataset(self, dataset_id) -> bool:
        r = self._connection.execute(
            update(Dataset).where(Dataset.id == dataset_id).values(archived=None)
        )
        return r.rowcount > 0

    def delete_dataset(self, dataset_id) -> bool:
        for table in search_field_indexes.values():
            self._connection.execute(
                delete(table).where(table.dataset_ref == dataset_id)
            )
        for crs in self._db.spatially_indexed_crses():
            SpatialIndex = self._db.spatial_index(crs)  # noqa: N806
            self._connection.execute(
                delete(SpatialIndex).where(SpatialIndex.dataset_ref == dataset_id)
            )
        r = self._connection.execute(delete(Dataset).where(Dataset.id == dataset_id))
        return r.rowcount > 0

    def get_dataset(self, dataset_id):
        return self._connection.execute(
            select(*_dataset_select_fields()).where(Dataset.id == dataset_id)
        ).first()

    def get_datasets(self, dataset_ids) -> Sequence:
        return self._connection.execute(
            select(*_dataset_select_fields()).where(Dataset.id.in_(dataset_ids))
        ).fetchall()

    def get_derived_datasets(self, dataset_id):
        raise NotImplementedError()

    def get_dataset_sources(self, dataset_id):
        raise NotImplementedError()

    def search_datasets_by_metadata(
        self, metadata: dict, archived: bool | None
    ) -> dict:
        """
        Find any datasets that have the given metadata.
        """
        # Find any storage types whose 'dataset_metadata' document is a subset of the metadata.
        where = Dataset.metadata_doc.contains(metadata)
        if archived:
            where = and_(where, Dataset.archived.is_not(None))
        elif archived is not None:
            where = and_(where, Dataset.archived.is_(None))
        query = select(*_dataset_select_fields()).where(where)
        return self._connection.execute(query).fetchall()

    def search_products_by_metadata(self, metadata: dict) -> Sequence:
        """
        Find any datasets that have the given metadata.
        """
        # Find any storage types whose 'dataset_metadata' document is a subset of the metadata.
        return self._connection.execute(
            select(Product).where(Product.metadata_doc.contains(metadata))
        ).fetchall()

    @staticmethod
    def _alchemify_expressions(expressions) -> list:
        def raw_expr(expression):
            if isinstance(expression, OrExpression):
                return or_(raw_expr(expr) for expr in expression.exprs)
            return expression.alchemy_expression

        return [raw_expr(expression) for expression in expressions]

    def geospatial_query(self, geom) -> tuple:
        if not geom.crs:
            raise ValueError("Search geometry must have a CRS")
        SpatialIndex = self._db.spatial_index(geom.crs)  # noqa: N806
        if SpatialIndex is None:
            _LOG.info("No spatial index for crs %s - converting to 4326", geom.crs)
            default_crs = CRS("EPSG:4326")
            geom = geom.to_crs(default_crs)
            SpatialIndex = self._db.spatial_index(default_crs)  # noqa: N806
        geom_sql = geom_alchemy(geom)
        _LOG.info("query geometry = %s (%s)", geom.json, geom.crs)
        spatialquery = func.ST_Intersects(SpatialIndex.extent, geom_sql)
        return SpatialIndex, spatialquery

    def search_datasets_query(
        self,
        expressions: Iterable[Expression],
        source_exprs: Iterable[Expression] | None = None,
        select_fields: Iterable[PgField] | None = None,
        with_source_ids: bool = False,
        limit: int | None = None,
        geom: Geometry | None = None,
        archived: bool | None = False,
        order_by: Iterable | None = None,
    ) -> Select:
        # TODO: lineage handling and source search
        assert source_exprs is None
        assert not with_source_ids

        if not select_fields:
            select_fields = _dataset_fields()

        known_fields = _base_known_fields() | {f.name: f for f in select_fields}

        def _ob_exprs(o):
            if isinstance(o, str):
                if known_fields.get(o.lower()) is not None:
                    return known_fields[o.lower()].alchemy_expression
                raise ValueError(f"Cannot order by unknown field {o}")
            if isinstance(o, PgField):
                return o.alchemy_expression
            # assume func, clause, or other expression, and leave as-is
            return o

        order_by = [] if order_by is None else [_ob_exprs(o) for o in order_by]

        select_columns = tuple(
            f.alchemy_expression.label(f.name)  # type: ignore[union-attr]
            for f in select_fields
        )
        if geom:
            SpatialIndex, spatialquery = self.geospatial_query(geom)  # noqa: N806
        else:
            spatialquery = None
            SpatialIndex = None  # noqa: N806

        raw_expressions = PostgisDbAPI._alchemify_expressions(expressions)
        join_tables = PostgisDbAPI._join_tables(expressions, select_fields)
        if archived:
            # True: Return archived datasets ONLY
            where_expr = and_(Dataset.archived.is_not(None), *raw_expressions)
        elif archived is not None:
            # False: Return active datasets ONLY
            where_expr = and_(Dataset.archived.is_(None), *raw_expressions)
        else:
            # None: Return BOTH active and archived datasets
            where_expr = and_(*raw_expressions)
        query = select(*select_columns).select_from(Dataset)
        for joins in join_tables:
            query = query.join(*joins)
        if spatialquery is not None:
            where_expr = and_(where_expr, spatialquery)
            query = query.join(SpatialIndex)
        return query.where(where_expr).order_by(*order_by).limit(limit)

    def search_datasets(
        self,
        expressions: Iterable[Expression],
        source_exprs: Iterable[Expression] | None = None,
        select_fields: Iterable[PgField] | None = None,
        with_source_ids: bool = False,
        limit: int | None = None,
        geom: Geometry | None = None,
        archived: bool | None = False,
        order_by=None,
    ) -> Generator:
        """
        :return: An iterable of tuples of decoded values
        """
        assert source_exprs is None
        assert not with_source_ids
        if select_fields is None:
            select_fields = _dataset_fields()
        select_query = self.search_datasets_query(
            expressions,
            select_fields=select_fields,
            limit=limit,
            geom=geom,
            archived=archived,
            order_by=order_by,
        )
        _LOG.debug("search_datasets SQL: %s", str(select_query))

        def decode_row(raw: Iterable[Any]) -> dict[str, Any]:
            return {f.name: f.normalise_value(r) for r, f in zip(raw, select_fields)}

        for row in self._connection.execute(select_query):
            yield decode_row(row)

    def bulk_simple_dataset_search(self, products=None, batch_size: int = 0):
        """
        Perform bulk database reads (e.g. for index cloning)

        Note that this operates with product ids to prevent an unnecessary join to the Product table.

        :param products: Optional iterable of product IDs.  Only fetch nominated products.
        :param batch_size: Number of streamed rows to fetch from database at once.
                           Defaults to zero, which means no streaming.
                           Note streaming is only supported inside a transaction.
        :return: Iterable of tuples of:
                 * Product ID
                 * Dataset metadata document
                 * array of uris
        """
        if batch_size > 0 and not self.in_transaction:
            raise ValueError("Postgresql bulk reads must occur within a transaction.")
        query = (
            select(Dataset.product_ref, Dataset.metadata_doc, Dataset.uri)
            .select_from(Dataset)
            .where(Dataset.archived.is_(None))
        )
        if products:
            query = query.where(Dataset.product_ref.in_(products))

        if batch_size > 0:
            conn = self._connection.execution_options(
                stream_results=True, yield_per=batch_size
            )
        else:
            conn = self._connection
        return conn.execute(query)

    def get_all_lineage(self, batch_size: int):
        """
        Stream all lineage data in bulk (e.g. for index cloning)

        :param batch_size: The number of lineage records to return at once.
        :return: Streamable SQLAlchemy result object.
        """
        if batch_size > 0 and not self.in_transaction:
            raise ValueError("Postgresql bulk reads must occur within a transaction.")
        query = select(
            DatasetLineage.derived_dataset_ref,
            DatasetLineage.classifier,
            DatasetLineage.source_dataset_ref,
        )
        return self._connection.execution_options(
            stream_results=True, yield_per=batch_size
        ).execute(query)

    def insert_lineage_bulk(self, values) -> tuple[int, int]:
        """
        Insert bulk lineage records (e.g. for index cloning)

        :param values: An array of values dicts for bulk insert
        :return: Tuple[count of rows loaded, count of rows skipped]
        """
        requested = len(values)
        # Simple bulk insert with on_conflict_do_nothing.
        # No need to check referential integrity as this is an external lineage index driver.
        res = self._connection.execute(
            insert(DatasetLineage).on_conflict_do_nothing(), values
        )
        return res.rowcount, requested - res.rowcount

    def get_duplicates(
        self, match_fields: Sequence[PgField], expressions: Sequence[PgExpression]
    ) -> Generator[dict[str, Any]]:
        # TODO
        if "time" in [f.name for f in match_fields]:
            yield from self.get_duplicates_with_time(match_fields, expressions)

        group_expressions = tuple(f.alchemy_expression for f in match_fields)
        join_tables = PostgisDbAPI._join_tables(expressions, match_fields)

        query = select(
            func.array_agg(Dataset.id).label("ids"), *group_expressions
        ).select_from(Dataset)
        for joins in join_tables:
            query = query.join(*joins)

        query = (
            query.where(
                and_(
                    Dataset.archived.is_(None),
                    *(PostgisDbAPI._alchemify_expressions(expressions)),
                )
            )
            .group_by(*group_expressions)
            .having(func.count(Dataset.id) > 1)
        )
        for row in self._connection.execute(query):
            drow = {"ids": row.ids}
            for f in match_fields:
                drow[f.name] = getattr(row, f.name)
            yield drow

    def get_duplicates_with_time(
        self, match_fields: Sequence[PgField], expressions: Sequence[PgExpression]
    ) -> Generator[dict[str, Any]]:
        fields = []
        for fld in match_fields:
            if fld.name == "time":
                time_field = type_cast(DateRangeDocField, fld)
            else:
                fields.append(fld.alchemy_expression)

        join_tables = PostgisDbAPI._join_tables(expressions, match_fields)

        cols = [Dataset.id, time_field.expression_with_leniency.label("time"), *fields]
        query = select(*cols).select_from(Dataset)
        for joins in join_tables:
            query = query.join(*joins)

        query = query.where(
            and_(
                Dataset.archived.is_(None),
                *(PostgisDbAPI._alchemify_expressions(expressions)),
            )
        )

        t1 = query.alias("t1")
        t2 = query.alias("t2")

        t1fields = [getattr(t1.c, f.name) for f in fields]  # type: ignore[union-attr]
        time_overlap = (
            select(
                t1.c.id,
                t1.c.time.intersection(t2.c.time).label("time_intersect"),
                *t1fields,
            )
            .select_from(
                t1.join(t2, and_(t1.c.time.overlaps(t2.c.time), t1.c.id != t2.c.id))
            )
            .cte("time_overlap")
        )

        tovlap_fields = [getattr(time_overlap.c, f.name) for f in fields]  # type: ignore[union-attr]
        query = (
            select(
                func.array_agg(func.distinct(time_overlap.c.id)).label("ids"),
                *tovlap_fields,
                text("time_intersect as time"),
            )
            .select_from(time_overlap)
            .group_by(*tovlap_fields, text("time_intersect"))
            .having(func.count(time_overlap.c.id) > 1)
        )

        for row in self._connection.execute(query):
            # TODO: Use decode_rows above - would require creating a field class for the ids array.
            drow: dict[str, Any] = {
                "ids": row.ids,
            }
            for f in fields:
                drow[f.key] = getattr(row, f.key)  # type: ignore[union-attr]
            drow["time"] = time_field.normalise_value((row.time.lower, row.time.upper))
            yield drow

    def count_datasets(
        self,
        expressions: Iterable[Expression],
        archived: bool | None = False,
        geom: Geometry | None = None,
    ) -> int:
        raw_expressions = self._alchemify_expressions(expressions)
        if archived:
            where_expressions = and_(Dataset.archived.is_not(None), *raw_expressions)
        elif archived is not None:
            where_expressions = and_(Dataset.archived.is_(None), *raw_expressions)
        else:
            where_expressions = and_(*raw_expressions)

        query = select(func.count(Dataset.id))

        if geom:
            SpatialIndex, spatialquery = self.geospatial_query(geom)  # noqa: N806
            where_expressions = and_(where_expressions, spatialquery)
            query = query.join(SpatialIndex)

        for join in self._join_tables(expressions=expressions):
            query = query.join(*join)

        select_query = query.where(where_expressions)
        return self._connection.scalar(select_query)

    def count_datasets_through_time(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        period,
        time_field,
        expressions: Iterable[Expression],
    ) -> Generator[tuple[tuple[datetime.datetime, datetime.datetime], int]]:
        results = self._connection.execute(
            self.count_datasets_through_time_query(
                start, end, period, time_field, expressions
            )
        )

        for time_period, dataset_count in results:
            # if not time_period.upper_inf:
            yield Range(time_period.lower, time_period.upper), dataset_count

    def count_datasets_through_time_query(
        self, start, end, period, time_field, expressions
    ) -> Select:
        raw_expressions = self._alchemify_expressions(expressions)

        start_times = select(
            func.generate_series(start, end, cast(period, INTERVAL)).label(
                "start_time"
            ),
        ).alias("start_times")

        time_range_select = (
            select(
                func.tstzrange(
                    start_times.c.start_time, func.lead(start_times.c.start_time).over()
                ).label("time_period"),
            )
        ).alias("all_time_ranges")

        # Exclude the trailing (end time to infinite) row. Is there a simpler way?
        time_ranges = (
            select(
                time_range_select,
            ).where(~func.upper_inf(time_range_select.c.time_period))
        ).alias("time_ranges")

        count_query = select(func.count("*"))
        join_tables = self._join_tables(expressions)
        for joins in join_tables:
            count_query = count_query.join(*joins)
        count_query = count_query.where(
            and_(
                time_field.alchemy_expression.overlaps(time_ranges.c.time_period),
                Dataset.archived == None,
                *raw_expressions,
            )
        )

        return select(time_ranges.c.time_period, count_query.label("dataset_count"))

    def update_search_index(
        self, product_names: Sequence[str] = [], dsids: Sequence[DSID] = []
    ) -> int:
        """
        Update search indexes
        :param product_names: Product names to update
        :param dsids: Dataset IDs to update

        if neither product_names nor dataset ids are supplied, update nothing (N.B. NOT all datasets)

        if both are supplied, both the named products and identified datasets are updated.

        :return:  Number of datasets whose search indexes have been updated.
        """
        if not product_names and not dsids:
            return 0

        ds_query = (
            select(
                Dataset.id,
                Dataset.metadata_doc,
                MetadataType.definition,
            )
            .select_from(Dataset)
            .join(MetadataType)
        )
        if product_names:
            ds_query = ds_query.join(Product)
        if product_names and dsids:
            ds_query = ds_query.where(
                or_(Product.name.in_(product_names), Dataset.id.in_(dsids))
            )
        elif product_names:
            ds_query = ds_query.where(Product.name.in_(product_names))
        elif dsids:
            ds_query = ds_query.where(Dataset.id.in_(dsids))
        rowcount = 0
        for result in self._connection.execute(ds_query):
            dsid, ds_metadata, mdt_def = result
            search_field_vals = extract_dataset_search_fields(ds_metadata, mdt_def)
            for field_name, field_info in search_field_vals.items():
                fld_type, fld_val = field_info
                search_idx = search_field_index_map[fld_type]
                self.insert_dataset_search(search_idx, dsid, field_name, fld_val)
            rowcount += 1
        return rowcount

    def update_spindex(
        self,
        crs_seq: Sequence[CRS] = [],
        product_names: Sequence[str] = [],
        dsids: Sequence[DSID] = [],
    ) -> int:
        """
        Update a spatial index
        :param crs_seq: CRSs for Spatial Indexes to update. Default=all indexes
        :param product_names: Product names to update
        :param dsids: Dataset IDs to update

        if neither product_names nor dataset ids are supplied, update for all datasets.

        if both are supplied, both the named products and identified datasets are updated.

        :return:  Number of spatial index entries updated or verified as unindexed.
        """
        verified = 0
        crses = list(crs_seq) if crs_seq else self._db.spatially_indexed_crses()

        # Update implementation.
        # Design will change, but this method should be fairly low level to be as efficient as possible
        query = select(
            Dataset.id, Dataset.metadata_doc["grid_spatial"]["projection"]
        ).select_from(Dataset)
        if product_names:
            query = query.join(Product)
        if product_names and dsids:
            query = query.where(
                or_(Product.name.in_(product_names), Dataset.id.in_(dsids))
            )
        elif product_names:
            query = query.where(Product.name.in_(product_names))
        elif dsids:
            query = query.where(Dataset.id.in_(dsids))
        for result in self._connection.execute(query):
            dsid = result[0]
            geom = extract_geometry_from_eo3_projection(result[1])
            if not geom:
                verified += 1
                continue
            for crs in crses:
                self.insert_dataset_spatial(dsid, crs, geom)
                verified += 1

        return verified

    @staticmethod
    def _join_tables(expressions=None, fields=None) -> list:
        join_args: set = set()
        if expressions:
            join_args.update(
                expression.field.dataset_join_args for expression in expressions
            )
        if fields:
            join_args.update(field.dataset_join_args for field in fields)
        join_args.discard((Dataset.__table__,))
        # Sort simple joins before qualified joins
        return sorted(join_args, key=len)

    def get_product(self, id_):
        return self._connection.execute(
            select(Product).where(Product.id == id_)
        ).first()

    def get_metadata_type(self, id_: int):
        return self._connection.execute(
            select(MetadataType).where(MetadataType.id == id_)
        ).first()

    def get_product_by_name(self, name: str):
        return self._connection.execute(
            select(Product).where(Product.name == name)
        ).first()

    def get_metadata_type_by_name(self, name: str):
        return self._connection.execute(
            select(MetadataType).where(MetadataType.name == name)
        ).first()

    def insert_product(self, name: str, metadata, metadata_type_id, definition):
        res = self._connection.execute(
            insert(Product).values(
                name=name,
                metadata_doc=metadata,
                metadata_type_ref=metadata_type_id,
                definition=definition,
            )
        )

        return res.inserted_primary_key[0]

    def insert_product_bulk(self, values) -> tuple[int, int]:
        requested = len(values)
        res = self._connection.execute(insert(Product), values)
        return res.rowcount, requested - res.rowcount

    def update_product(
        self,
        name: str,
        metadata,
        metadata_type_id,
        definition,
        update_metadata_type: bool = False,
    ):
        res = self._connection.execute(
            update(Product)
            .returning(Product.id)
            .where(Product.name == name)
            .values(
                metadata_doc=metadata,
                metadata_type_ref=metadata_type_id,
                definition=definition,
            )
        )
        prod_id = res.first()[0]

        if update_metadata_type:
            if not self._connection.in_transaction():
                raise RuntimeError("Must update metadata types in transaction")

            self._connection.execute(
                update(Dataset)
                .where(Dataset.product_ref == prod_id)
                .values(metadata_type_ref=metadata_type_id)
            )

        return prod_id

    def delete_product(self, name: str):
        res = self._connection.execute(
            delete(Product).returning(Product.id).where(Product.name == name)
        )

        return res.first()[0]

    def insert_metadata_type(self, name: str, definition):
        res = self._connection.execute(
            insert(MetadataType).values(name=name, definition=definition)
        )
        return res.inserted_primary_key[0]

    def insert_metadata_bulk(self, values) -> tuple[int, int]:
        requested = len(values)
        res = self._connection.execute(
            insert(MetadataType)
            .on_conflict_do_nothing(index_elements=["id"])
            .values(values)
        )
        return res.rowcount, requested - res.rowcount

    def update_metadata_type(self, name: str, definition):
        res = self._connection.execute(
            update(MetadataType)
            .returning(MetadataType.id)
            .where(MetadataType.name == name)
            .values(name=name, definition=definition)
        )
        return res.first()[0]

    @staticmethod
    def _get_active_field_names(fields, metadata_doc) -> Generator:
        for field in fields.values():
            if field.can_extract:
                try:
                    value = field.extract(metadata_doc)
                    if value is not None:
                        yield field.name
                except (AttributeError, KeyError, ValueError):
                    continue

    def get_all_products(self) -> Sequence:
        return self._connection.execute(
            select(Product).order_by(Product.name.asc())
        ).fetchall()

    def get_all_product_docs(self):
        return self._connection.execute(select(Product.definition))

    def _get_products_for_metadata_type(self, id_) -> Sequence:
        return self._connection.execute(
            select(Product)
            .where(Product.metadata_type_ref == id_)
            .order_by(Product.name.asc())
        ).fetchall()

    def get_all_metadata_types(self) -> Sequence:
        return self._connection.execute(
            select(MetadataType).order_by(MetadataType.name.asc())
        ).fetchall()

    def get_all_metadata_type_defs(self) -> Generator:
        for r in self._connection.execute(
            select(MetadataType.definition).order_by(MetadataType.name.asc())
        ):
            yield r[0]

    def get_location(self, dataset_id):
        return self._connection.execute(
            select(Dataset.uri).where(Dataset.id == dataset_id)
        ).first()

    def remove_location(self, dataset_id, uri: str) -> bool:
        """
        Remove a dataset's location

        :returns bool: Was the location deleted?
        """
        scheme, body = split_uri(uri)
        res = self._connection.execute(
            update(Dataset)
            .where(
                and_(
                    Dataset.id == dataset_id,
                    Dataset.uri_scheme == scheme,
                    Dataset.uri_body == body,
                )
            )
            .values(uri_scheme=None, uri_body=None)
        )
        return res.rowcount > 0

    @override
    def __repr__(self) -> str:
        return f"PostgresDb<connection={self._connection!r}>"

    def list_users(self) -> Generator:
        result = self._connection.execute(
            text("""
            select
                group_role.rolname as role_name,
                user_role.rolname as user_name,
                pg_catalog.shobj_description(user_role.oid, 'pg_authid') as description
            from pg_roles group_role
            inner join pg_auth_members am on am.roleid = group_role.oid
            inner join pg_roles user_role on am.member = user_role.oid
            where (group_role.rolname like 'odc_%%') and not (user_role.rolname like 'odc_%%')
            order by group_role.oid asc, user_role.oid asc;
        """)
        )
        for row in result:
            yield _core.from_pg_role(row.role_name), row.user_name, row.description

    def create_user(
        self, username: str, password: str, role, description: str | None = None
    ) -> None:
        pg_role = _core.to_pg_role(role)
        username = escape_pg_identifier(self._connection, username)
        sql = text(f"create user {username} password :password in role {pg_role}")
        self._connection.execute(sql, {"password": password})
        if description:
            sql = text(f"comment on role {username} is :description")
            self._connection.execute(sql, {"description": description})

    def drop_users(self, users: Iterable[str]) -> None:
        for username in users:
            sql = text(f"drop role {escape_pg_identifier(self._connection, username)}")
            self._connection.execute(sql)

    def grant_role(self, role: str, users: Iterable[str]) -> None:
        """
        Grant a role to a user.
        """
        pg_role = _core.to_pg_role(role)

        for user in users:
            if not _core.has_role(self._connection, user):
                raise ValueError(f"Unknown user {user!r}")

        _core.grant_role(self._connection, pg_role, users)

    def insert_home(
        self, home: str, ids: Iterable[uuid.UUID], allow_updates: bool
    ) -> int:
        """
        Set home for multiple IDs (but one home value)

        :param home: The home value to set
        :param ids: The IDs to set it for
        :param allow_updates: If False only inserts are allowed
        :return: number of database records updated or added.
        """
        values = [{"dataset_ref": id_, "home": home} for id_ in ids]
        qry = insert(DatasetHome)
        if allow_updates:
            qry = qry.on_conflict_do_update(
                index_elements=["dataset_ref"],
                set_={"home": home},
                where=(DatasetHome.home != home),
            )
        try:
            res = self._connection.execute(qry, values)
            return res.rowcount
        except IntegrityError:
            return 0

    def delete_home(self, ids) -> int:
        """
        Delete the home value for the specified IDs

        :param ids: The IDs to delete home for
        :return: The number of home records deleted from the database.
        """
        res = self._connection.execute(
            delete(DatasetHome).where(DatasetHome.dataset_ref.in_(ids))
        )
        return res.rowcount

    def select_homes(self, ids) -> dict[uuid.UUID, str]:
        """
        Find homes for IDs.

        :param ids: Iterable of IDs
        :return: Mapping of ID to home string for IDs found in database.
        """
        results = self._connection.execute(
            select(DatasetHome).where(DatasetHome.dataset_ref.in_(ids))
        )
        return {row.dataset_ref: row.home for row in results}

    def get_all_relations(
        self, dsids: Iterable[uuid.UUID]
    ) -> Generator[LineageRelation]:
        """
        Fetch all lineage relations in the database involving a set on dataset IDs.

        :param dsids: Iterable of dataset IDs
        :return: Iterable of LineageRelation objects.
        """
        results = self._connection.execute(
            select(DatasetLineage).where(
                or_(
                    DatasetLineage.derived_dataset_ref.in_(dsids),
                    DatasetLineage.source_dataset_ref.in_(dsids),
                )
            )
        )
        for rel in results:
            yield LineageRelation(
                classifier=rel.classifier,
                source_id=rel.source_dataset_ref,
                derived_id=rel.derived_dataset_ref,
            )

    def write_relations(
        self, relations: Iterable[LineageRelation], allow_updates: bool
    ) -> int:
        """
        Write a set of LineageRelation objects to the database.

        :param relations: An Iterable of LineageRelation objects
        :param allow_updates: if False, only allow adding new relations, not updating old ones.
        :return: Count of database rows affected
        """
        affected = 0
        if allow_updates:
            by_classifier: dict[str, Any] = {}
            for rel in relations:
                db_repr = {
                    "derived_dataset_ref": rel.derived_id,
                    "source_dataset_ref": rel.source_id,
                    "classifier": rel.classifier,
                }
                if rel.classifier in by_classifier:
                    by_classifier[rel.classifier].append(db_repr)
                else:
                    by_classifier[rel.classifier] = [db_repr]
                for classifier, values in by_classifier.items():
                    qry = insert(DatasetLineage).on_conflict_do_update(
                        index_elements=["derived_dataset_ref", "source_dataset_ref"],
                        set_={"classifier": classifier},
                        where=(DatasetLineage.classifier != classifier),
                    )
                    res = self._connection.execute(qry, values)
                    affected += res.rowcount
        else:
            for rel in relations:
                values = [
                    {
                        "derived_dataset_ref": rel.derived_id,
                        "source_dataset_ref": rel.source_id,
                        "classifier": rel.classifier,
                    }
                ]
                qry = insert(DatasetLineage)
                try:
                    res = self._connection.execute(qry, values)
                    affected += res.rowcount
                except IntegrityError:
                    return 0
        return affected

    def load_lineage_relations(
        self,
        roots: Iterable[uuid.UUID],
        direction: LineageDirection,
        depth: int,
        ids_so_far: set[uuid.UUID] | None = None,
    ) -> Iterable[LineageRelation]:
        """
        Read from the database all indexed LineageRelation objects required to build all LineageTrees with
        the given roots, direction and depth.

        :param roots: Iterable of root dataset ids
        :param direction: tree direction
        :param depth: Maximum tree depth - zero indicates unlimited depth.
        :param ids_so_far: Used for maintaining state through recursion - expected to be None on initial call
        :return: Iterable of LineageRelation objects read from database
        """
        # Naive manually-recursive initial implementation.
        # TODO: Reimplement using WITH RECURSIVE query
        if ids_so_far is None:
            ids_so_far = set(roots)
        qry = select(DatasetLineage)
        if direction == LineageDirection.SOURCES:
            qry = qry.where(DatasetLineage.derived_dataset_ref.in_(roots))
        else:
            qry = qry.where(DatasetLineage.source_dataset_ref.in_(roots))
        relations = []
        next_lvl_ids = set()
        results = self._connection.execute(qry)
        for row in results:
            rel = LineageRelation(
                classifier=row.classifier,
                source_id=row.source_dataset_ref,
                derived_id=row.derived_dataset_ref,
            )
            relations.append(rel)
            next_id = (
                rel.source_id
                if direction == LineageDirection.SOURCES
                else rel.derived_id
            )
            if next_id not in ids_so_far:
                next_lvl_ids.add(next_id)
                ids_so_far.add(next_id)
        next_depth = depth - 1
        recurse = True
        if depth == 0:
            next_depth = 0
        elif depth == 1:
            recurse = False
        if recurse and next_lvl_ids:
            relations.extend(
                self.load_lineage_relations(
                    next_lvl_ids, direction, next_depth, ids_so_far
                )
            )
        return relations

    def remove_lineage_relations(
        self, ids: Iterable[DSID], direction: LineageDirection
    ) -> int:
        """
        Remove lineage relations from the provided ids in the specified direction.

        Note no depth parameter - depth is effectively always 1.

        :param ids: Iterable of IDs to remove lineage information for.
        :param direction: Remove the source or derived lineage relation records
        :return: Return number of relation records deleted.
        """
        qry = delete(DatasetLineage)
        if direction == LineageDirection.SOURCES:
            qry = qry.where(DatasetLineage.derived_dataset_ref.in_(ids))
        else:
            qry = qry.where(DatasetLineage.source_dataset_ref.in_(ids))
        results = self._connection.execute(qry)
        return results.rowcount

    def temporal_extent_by_prod(
        self, product_id: int
    ) -> tuple[datetime.datetime, datetime.datetime]:
        query = self.temporal_extent_full().where(Dataset.product_ref == product_id)
        res = self._connection.execute(query)
        for tmin, tmax in res:
            return time_min.normalise_value(tmin), time_max.normalise_value(tmax)
        raise RuntimeError("Product has no datasets and therefore no temporal extent")

    def temporal_extent_by_ids(
        self, ids: Iterable[DSID]
    ) -> tuple[datetime.datetime, datetime.datetime]:
        query = self.temporal_extent_full().where(Dataset.id.in_(ids))
        res = self._connection.execute(query)
        for tmin, tmax in res:
            return time_min.normalise_value(tmin), time_max.normalise_value(tmax)
        raise ValueError("no dataset ids provided")

    def temporal_extent_full(self) -> Select:
        # Hardcode eo3 standard time locations - do not use this approach in a legacy index driver.

        return select(
            func.min(time_min.alchemy_expression), func.max(time_max.alchemy_expression)
        )

    def find_most_recent_change(self, product_id: int):
        """
        Find the database-local time of the last dataset that changed for this product.
        """
        return self._connection.execute(
            select(
                func.max(
                    func.greatest(
                        Dataset.added,
                        column("updated"),
                    )
                )
            ).where(Dataset.product_ref == product_id)
        ).scalar()
