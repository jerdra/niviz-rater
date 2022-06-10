"""
Niviz-Rater Spec representation module
"""

from __future__ import annotations
from typing import (List, NamedTuple, TYPE_CHECKING, Dict, Any, Optional)

from dataclasses import dataclass
from string import Template
from itertools import groupby
import logging

if TYPE_CHECKING:
    from niviz_rater.validation import ValidConfig

logger = logging.getLogger(__name__)


class RowDescription(NamedTuple):
    entities: List[str]
    name: Template


DBSettings = Dict[str, Any]


@dataclass
class SpecConfig:
    globals: ConfigGlobals
    components: List[ConfigComponent]

    def from_validated(cls, config: ValidConfig) -> SpecConfig:
        return cls(globals=ConfigGlobals.from_config(config),
                   components=list(ConfigComponent.yield_from_config(config)))


@dataclass
class ConfigGlobals:
    """
    Global settings for Niviz-Rater specification file
    """

    row_entities: List[str]
    image_extensions: List[str]
    row_description: RowDescription

    def from_config(cls, config: ValidConfig) -> ConfigGlobals:

        row_description = RowDescription(
            entities=config['RowDescription']['entities'],
            name=config['RowDescription']['name'])

        return cls(row_entities=config['RowEntities'],
                   image_extensions=config['ImageExtensions'],
                   row_description=row_description)


@dataclass
class QCEntity:
    """
    Helper class to represent a single QC entity
    """
    images: list
    entities: dict
    tpl_label: str
    tpl_column_name: str

    @property
    def name(self):
        return Template(self.tpl_label).substitute(self.entities)

    @property
    def column_name(self):
        return Template(self.tpl_column_name).substitute(self.entities)


class ConfigComponent:
    """
    Configurable Factory class for building QC components
    from list of images
    """

    def __init__(self, name, entities, label, column, images, annotations):
        self.name = name
        self.entities = entities
        self.label = label
        self.column = column
        self.image_descriptors = images
        self.available_annotations = annotations

    @classmethod
    def yield_from_config(cls, config: ValidConfig) -> ConfigComponent:
        """
        Create ConfigComponent instances from a validated configuration
        for niviz-rater
        """
        for component in config['Components']:
            yield cls(**component)

    def build_qc_entities(self, image_list):
        """
        Build QC Entities given a list of images

        Arguments:
            image_list          List of BIDSFile images
                                to build QC entities from
        """

        qc_entities = []

        for key, group in _group_by_entities(image_list, self.entities):
            group_entities = list(group)
            try:
                matched_images = [
                    find_matches(group_entities, i)
                    for i in self.image_descriptors
                ]
            except IndexError:
                logger.error(f"No entities found for {key}")
                continue

            qc_entities.append(
                QCEntity(images=[m.path for m in matched_images],
                         entities={
                             k: matched_images[0].entities[k]
                             for k in self.entities
                         },
                         tpl_label=self.label,
                         tpl_column_name=self.column))

        return qc_entities


def _is_subdict(big, small):
    return dict(big, **small) == big


def _get_key(bidsfile, entities):
    return tuple([bidsfile.entities[e] for e in entities])


def _group_by_entities(bidsfiles, entities):
    filtered = [b for b in bidsfiles if all(k in b.entities for k in entities)]
    return groupby(sorted(filtered, key=lambda x: _get_key(x, entities)),
                   key=lambda x: _get_key(x, entities))


def find_matches(images, image_descriptor):

    matches = [b for b in images if _is_subdict(b.entities, image_descriptor)]
    if len(matches) > 1:
        logger.error(f"Got {len(matches)} matches to entity,"
                     " expected 1!")
        logger.error(f"Matching specification:\n {image_descriptor}")
        print_matches = "\n".join([m.path for m in matches])
        logger.error(f"{print_matches}")
        raise ValueError

    try:
        return matches[0]
    except IndexError:
        logger.error(f"Found 0 matches for\n {image_descriptor}!")
        raise


def db_settings_from_config(config: ValidConfig,
                            keys: List[str]) -> DBSettings:
    """
    Extract database settings from a valid configuration file
    """

    db_settings = {}
    for k in keys:
        if k in config:
            db_settings[k] = config[k]

    return db_settings
