# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Tables for indexing the datasets which were ingested into the AGDC.
"""

import logging

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects import postgresql as postgres
from sqlalchemy.sql import func

from . import _core, sql

_LOG: logging.Logger = logging.getLogger(__name__)

METADATA_TYPE = Table(
    "metadata_type",
    _core.METADATA,
    Column("id", SmallInteger, primary_key=True, autoincrement=True),
    Column("name", String, unique=True, nullable=False),
    Column("definition", postgres.JSONB, nullable=False),
    # When it was added and by whom.
    Column("added", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("added_by", sql.PGNAME, server_default=func.current_user(), nullable=False),
    # Note that the `updated` column is not present in pre-1.8.3 datacubes
    Column("updated", DateTime(timezone=True), default=None, nullable=True),
    # Name must be alphanumeric + underscores.
    CheckConstraint(r"name ~* '^\w+$'", name="alphanumeric_name"),
)

PRODUCT = Table(
    "dataset_type",
    _core.METADATA,
    Column("id", SmallInteger, primary_key=True, autoincrement=True),
    # A name/label for this type (eg. 'ls7_nbar'). Specified by users.
    Column("name", String, unique=True, nullable=False),
    # All datasets of this type should contain these fields.
    # (newly-ingested datasets may be matched against these fields to determine the dataset type)
    Column("metadata", postgres.JSONB, nullable=False),
    # The metadata format expected (eg. what fields to search by)
    Column("metadata_type_ref", None, ForeignKey(METADATA_TYPE.c.id), nullable=False),
    Column("definition", postgres.JSONB, nullable=False),
    # When it was added and by whom.
    Column("added", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("added_by", sql.PGNAME, server_default=func.current_user(), nullable=False),
    # Note that the `updated` column is not present in pre-1.8.3 datacubes
    Column("updated", DateTime(timezone=True), default=None, nullable=True),
    # Name must be alphanumeric + underscores.
    CheckConstraint(r"name ~* '^\w+$'", name="alphanumeric_name"),
)

DATASET = Table(
    "dataset",
    _core.METADATA,
    Column("id", postgres.UUID(as_uuid=True), primary_key=True),
    Column("metadata_type_ref", None, ForeignKey(METADATA_TYPE.c.id), nullable=False),
    Column(
        "dataset_type_ref", None, ForeignKey(PRODUCT.c.id), index=True, nullable=False
    ),
    Column("metadata", postgres.JSONB, nullable=False),
    # Date it was archived. Null for active datasets.
    Column("archived", DateTime(timezone=True), default=None, nullable=True),
    # When it was added and by whom.
    Column("added", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("added_by", sql.PGNAME, server_default=func.current_user(), nullable=False),
    # Note that the `updated` column is not present in pre-1.8.3 datacubes
    Column("updated", DateTime(timezone=True), default=None, nullable=True),
)


Index("ix_ds_isactive", DATASET.c.archived == None)
Index("ix_ds_prod_isactive", DATASET.c.dataset_type_ref, DATASET.c.archived == None)
Index("ix_ds_mdt_isactive", DATASET.c.metadata_type_ref, DATASET.c.archived == None)


DATASET_LOCATION = Table(
    "dataset_location",
    _core.METADATA,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("dataset_ref", None, ForeignKey(DATASET.c.id), index=True, nullable=False),
    # The base URI to find the dataset.
    #
    # All paths in the dataset metadata can be computed relative to this.
    # (it is often the path of the source metadata file)
    #
    # eg 'file:///g/data/datasets/LS8_NBAR/agdc-metadata.yaml' or 'ftp://eo.something.com/dataset'
    # 'file' is a scheme, '///g/data/datasets/LS8_NBAR/agdc-metadata.yaml' is a body.
    Column("uri_scheme", String, nullable=False),
    Column("uri_body", String, nullable=False),
    # When it was added and by whom.
    Column("added", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("added_by", sql.PGNAME, server_default=func.current_user(), nullable=False),
    # Date it was archived. Null for active locations.
    Column("archived", DateTime(timezone=True), default=None, nullable=True),
    UniqueConstraint("uri_scheme", "uri_body", "dataset_ref"),
)

# Link datasets to their source datasets.
DATASET_SOURCE = Table(
    "dataset_source",
    _core.METADATA,
    Column("dataset_ref", None, ForeignKey(DATASET.c.id), nullable=False),
    # An identifier for this source dataset.
    #    -> Usually it's the dataset type ('ortho', 'nbar'...), as there's typically only one source
    #       of each type.
    Column("classifier", String, nullable=False),
    Column("source_dataset_ref", None, ForeignKey(DATASET.c.id), nullable=False),
    PrimaryKeyConstraint("dataset_ref", "classifier"),
    UniqueConstraint("source_dataset_ref", "dataset_ref"),
    # This table is immutable and uses a migrations based `added` column to keep track of new
    # dataset locations being added. The added column defaults to `now()`
)
