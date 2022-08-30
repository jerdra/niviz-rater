from __future__ import annotations

from typing import Optional, Tuple
import logging
from peewee import JOIN
from niviz_rater.db.models import (
        Entity, Component, TableColumn, TableRow
        )


logger = logging.getLogger(__name__)


def get_component(component_name: str, create=False) -> Component:

    if create:
        component = Component.get_or_create(
            Component.name == component_name)
    else:
        component = Component.get(
            Component.name == component_name)

    return component


def get_entity_by_row_col(row_name: str,
                          col_name: str) -> Optional[Entity]:
    """
    Return an Entity by it's unique row/col combination
    """

    result = Entity.select(Entity, TableColumn,
                                  TableRow) \
        .join(TableRow) \
        .switch(Entity) \
        .join(TableColumn) \
        .switch(Entity) \
        .where((TableColumn.name == col_name) &
               (TableRow.name == row_name))

    if len(result) > 1:
        logger.error(f"Expected 1 result but got {len(result)}\n"
                     "Only returning first result")

    return result.first()

def get_summary() -> Tuple[int, int, int]:
    """
    Get number of Entities that have yet to be rated

    Returns:
        summary: (total_entities, number_rated, number_unrated)
    """

    total = Entity.select().count()
    n_unrated = Entity.select().where(Entity.rating.is_null()).count()
    n_rated = total - n_unrated

    return total, n_rated, n_unrated
