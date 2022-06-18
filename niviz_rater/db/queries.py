from __future__ import annotations

from typing import Optional
import logging
import niviz_rater.db.models as models


logger = logging.getLogger(__name__)


def get_component(component_name: str, create=False) -> models.Component:

    if create:
        component = models.Component.get_or_create(
            models.Component.name == component_name)
    else:
        component = models.Component.get(
            models.Component.name == component_name)

    return component


def get_entity_by_row_col(row_name: str,
                          col_name: str) -> Optional[models.Entity]:
    """
    Return an Entity by it's unique row/col combination
    """

    result = models.Entity.select(models.Entity, models.TableColumn,
                                  models.TableRow) \
        .join(models.TableRow) \
        .switch(models.Entity) \
        .join(models.TableColumn) \
        .switch(models.Entity) \
        .where((models.TableColumn.name == col_name) &
               (models.TableRow.name == row_name))

    if len(result) > 1:
        logger.error(f"Expected 1 result but got {len(result)}\n"
                     "Only returning first result")

    return result.first()
