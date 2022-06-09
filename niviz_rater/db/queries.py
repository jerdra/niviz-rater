from __future__ import annotations

from typing import Union, Tuple
import logging
from peewee import IntegrityError
import niviz_rater.db.models as models
import niviz_rater.config.db_defaults as db_defaults

logger = logging.getLogger(__name__)


def get_component(component_name: str, create=False) -> models.Component:

    if create:
        component = models.Component.get_or_create(
            models.Component.name == component_name)
    else:
        component = models.Component.get(
            models.Component.name == component_name)

    return component


def add_annotation_to_component(
        component: Union[str, models.Component],
        annotation: str) -> Tuple[models.Component, models.Annotation]:

    if isinstance(component, str):
        try:
            component = models.Component.get(
                models.Component.name == component)
        except IntegrityError:
            logger.error(f"Component {component} does not exist")
            logger.error("Create component before using")
            raise

    annotation = component.add_annotation(annotation)
    return (component, annotation)
