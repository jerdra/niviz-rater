"""
Module for handling and enforcing configuration rules for
packaging and rules for associating QC images with an entity
"""

from itertools import groupby
import logging
from string import Template
from dataclasses import dataclass
from collections import namedtuple
from typing import Iterable, Dict, Any

from peewee import SqliteDatabase

from niviz_rater.models import (Entity, Rating, Annotation, Image, Component,
                                TableRow, TableColumn)

logger = logging.getLogger(__name__)

AxisNameTpl = namedtuple('AxisNameTpl', ('tpl', 'entities'))


@dataclass
class QCEntity:
    """
    Helper class to represent a single QC entity
    """
    images: list
    entities: dict
    tpl_name: str
    tpl_column_name: str

    @property
    def name(self):
        return Template(self.tpl_name).substitute(self.entities)

    @property
    def column_name(self):
        return Template(self.tpl_column_name).substitute(self.entities)


class ConfigComponent:
    """
    Configurable Factory class for building QC components
    from list of images
    """
    def __init__(self, entities, name, column, images, annotations):
        self.entities = entities
        self.name = name
        self.column = column
        self.image_descriptors = images
        self.available_annotations = annotations

    def _group_by_entities(self, bidsfiles):
        """
        Sort list of bidsfiles by requested entities
        """

        filtered = [
            b for b in bidsfiles if all(k in b.entities for k in self.entities)
        ]
        return groupby(sorted(filtered,
                              key=lambda x: _get_key(x, self.entities)),
                       key=lambda x: _get_key(x, self.entities))

    def find_matches(self, images, image_descriptor):

        matches = [
            b for b in images if _is_subdict(b.entities, image_descriptor)
        ]
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

    def build_qc_entities(self, image_list):
        """
        Build QC Entities given a list of images

        Arguments:
            image_list          List of BIDSFile images
                                to build QC entities from
        """

        qc_entities = []

        for key, group in self._group_by_entities(image_list):
            group_entities = list(group)
            try:
                matched_images = [
                    self.find_matches(group_entities, i)
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
                         tpl_name=self.name,
                         tpl_column_name=self.column))

        return qc_entities


def build_index(db: SqliteDatabase, bids_files: Iterable[str],
                qc_spec: Dict[str, Any]) -> None:
    """
    Initialize database with objects
    """
    row_tpl = AxisNameTpl(Template(qc_spec['RowDescription']['name']),
                          qc_spec['RowDescription']['entities'])

    default_rating = initialize_db_ratings(db)
    for c in qc_spec['Components']:
        component = ConfigComponent(**c)
        make_database(db, component.build_qc_entities(bids_files),
                      component.available_annotations, row_tpl, default_rating)


def make_rowname(rowtpl, entities):
    keys = {k: v for k, v in entities.items() if k in rowtpl.entities}
    return rowtpl.tpl.substitute(keys)


def initialize_db_ratings(db):
    """
    Set-up Ratings table in database
    """

    Rating.create_table()
    with db.atomic():
        default_rating = Rating.create(name="None")
        [Rating.create(name=r) for r in ["Pass", "Fail", "Uncertain"]]

    return default_rating


def make_database(db, entities, available_annotations, row_tpl,
                  default_rating):
    """
    Add tables and data to database
    """
    # First create necessary tables
    db.create_tables(
        [Component, Annotation, Entity, Image, TableRow, TableColumn])

    # Step 0: We'll create our component and annotations
    with db.atomic():
        component = Component.create()
        default_annotation = Annotation.create(name="No Rating",
                                               component=component.id)
        [
            Annotation.create(name=r, component=component.id)
            for r in available_annotations
        ]

    # Step 1: Get set of row names to use and save in dictionary
    unique_rows = set([make_rowname(row_tpl, e.entities) for e in entities])
    unique_cols = set([e.column_name for e in entities])
    insert_cols = [{'name': c} for c in unique_cols]
    with db.atomic():
        for r in unique_rows:
            TableRow.get_or_create(name=r)
        TableColumn.insert_many(insert_cols).execute()

    # Step 3: Create entities
    image_inserts = []
    with db.atomic():
        for e in entities:
            entity = Entity.create(name=e.name,
                                   component=component.id,
                                   rowname=make_rowname(row_tpl, e.entities),
                                   columnname=e.column_name,
                                   annotation=default_annotation.id,
                                   rating=default_rating.id)
            [image_inserts.append((i, entity.id)) for i in e.images]

    with db.atomic():
        Image.insert_many(image_inserts, fields=[Image.path,
                                                 Image.entity]).execute()


def _is_subdict(big, small):
    return dict(big, **small) == big


def _get_key(bidsfile, entities):
    return tuple([bidsfile.entities[e] for e in entities])
