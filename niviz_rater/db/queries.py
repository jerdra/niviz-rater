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

    try:
        return models.Entity.get((models.Entity.rowname == row_name)
                                 & (models.Entity.columnname == col_name))
    except models.Entity.DoesNotExist:
        return None
