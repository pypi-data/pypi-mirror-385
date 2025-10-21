# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
from collections.abc import Iterable
from time import monotonic

from typing_extensions import override

from datacube.index.abstract import BatchStatus, NoLineageResource
from datacube.index.postgres._transaction import IndexResourceAddIn
from datacube.model import LineageRelation


class LineageResource(NoLineageResource, IndexResourceAddIn):
    def __init__(self, db, index) -> None:
        self._db = db
        super().__init__(index)

    @override
    def get_all_lineage(self, batch_size: int = 1000) -> Iterable[LineageRelation]:
        with self._db_connection(transaction=True) as connection:
            for row in connection.get_all_lineage(batch_size=batch_size):
                yield LineageRelation(
                    derived_id=row.dataset_ref,
                    classifier=row.classifier,
                    source_id=row.source_dataset_ref,
                )

    @override
    def _add_batch(self, batch_rels: Iterable[LineageRelation]) -> BatchStatus:
        b_started = monotonic()
        with self._db_connection(transaction=True) as connection:
            b_added, b_skipped = connection.insert_lineage_bulk(
                [
                    (str(rel.derived_id), rel.classifier, str(rel.source_id))
                    for rel in batch_rels
                ]
            )
        return BatchStatus(b_added, b_skipped, monotonic() - b_started)
