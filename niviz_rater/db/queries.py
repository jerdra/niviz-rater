from __future__ import annotations

from typing import Optional, Tuple, List
import logging
from peewee import JOIN, ModelSelect
from niviz_rater.db.models import (Entity, Component, TableColumn, TableRow,
                                   Rating, Image, Annotation)

logger = logging.getLogger(__name__)


def get_component(component_name: str, create=False) -> Component:

    if create:
        component = Component.get_or_create(Component.name == component_name)
    else:
        component = Component.get(Component.name == component_name)

    return component


def get_entity_by_row_col(row_name: str, col_name: str) -> Optional[Entity]:
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


def _denormalized_query() -> ModelSelect:
    """
    Return denormalized Entity query with all foreign keys joined
    To attach images use a `prefetch`
    """

    q = (Entity.select(
        Entity, TableRow, TableColumn, Rating,
        Annotation, Component).join_from(Entity, TableRow).join_from(
            Entity,
            TableColumn).join_from(Entity, Rating, JOIN.LEFT_OUTER).join_from(
                Entity, Annotation,
                JOIN.LEFT_OUTER).join_from(Entity, Component).switch(Entity))
    return q


def get_denormalized_entities() -> List[Entity]:
    """
    Return Entities joined against all dimension tables

    Returns:
        entities (List[Entity]): List of all entities with foreign keys
            joined and Images prefetched
    """
    q = _denormalized_query().prefetch(Image)
    return q


def get_denormalized_entity_by_id(entity_id: int) -> Entity:
    """
    Return Entity joined against all dimension tables

    Returns:
        entity (Entity): Entity with foreign keys joined
            and Images prefetched

    Raises:
        ValueError: If more than 1 entity is found to contain a given ID
    """
    q = _denormalized_query().where(Entity.id == entity_id).prefetch(Image)

    if len(q) != 1:
        raise ValueError(f"Expected 1 Entity, received {len(q)}!")
    return q[0]


def get_available_annotations(entity: Entity) -> List[Annotation]:

    annotations = Annotation.select().where(
        Annotation.component == entity.component)
    return annotations
