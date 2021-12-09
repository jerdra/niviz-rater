'''
Module for handling and enforcing configuration rules for
packaging and rules for associating QC images with an entity
'''

import yaml
import os
from itertools import groupby
import logging
from string import Template
from dataclasses import dataclass
from collections import namedtuple
import yamale

from bids.layout import BIDSLayout, add_config_paths

from niviz_rater import db
from niviz_rater.models import Entity, Rating, Image, Component, TableRow, TableColumn

logger = logging.getLogger(__name__)

DEFAULT_BIDS = os.path.join(os.path.dirname(__file__), 'data/bids.json')

SCHEMAFILE = os.path.join(os.path.dirname(__file__), 'data/schema.yaml')

AxisNameTpl = namedtuple('AxisNameTpl', ('tpl', 'entities'))


def _validate_config(config):

    # load schema as yamale schema object
    schema = yamale.make_schema(SCHEMAFILE)

    yamaledata = yamale.make_data(config)

    # validate config against schema; returns ValueError if invalid
    yamale.validate(schema, yamaledata)

    with open(config, 'r') as f:
        config = yaml.load(f, Loader=yaml.CLoader)

    return config


@dataclass
class QCEntity:
    '''
    Helper class to represent a single QC entity
    '''
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
    '''
    Configurable Factory class for building QC components
    from list of images
    '''
    def __init__(self, entities, name, column, images, ratings):
        self.entities = entities
        self.name = name
        self.column = column
        self.image_descriptors = images
        self.available_ratings = ratings

    def _group_by_entities(self, bidsfiles):
        '''
        Sort list of bidsfiles by requested entities
        '''

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
        if len(matches) != 1:
            logger.error(f"Got {len(matches)} matches to entity,"
                         " expected 1!")
            logger.error(f"Matching specification:\n {image_descriptor}")
            print_matches = "\n".join([m.path for m in matches])
            if len(matches) > 1:
                logger.error(f"Found:\n {print_matches}")
            raise ValueError
        return matches[0]

    def build_qc_entities(self, image_list):
        '''
        Build QC Entities given a list of images

        Arguments:
            image_list          List of BIDSFile images
                                to build QC entities from
        '''

        qc_entities = []

        for key, group in self._group_by_entities(image_list):
            group_entities = list(group)
            matched_images = [
                self.find_matches(group_entities, i)
                for i in self.image_descriptors
            ]

            qc_entities.append(
                QCEntity(images=[m.path for m in matched_images],
                         entities={
                             k: matched_images[0].entities[k]
                             for k in self.entities
                         },
                         tpl_name=self.name,
                         tpl_column_name=self.column))

        return qc_entities


def get_qc_bidsfiles(qc_dataset, qc_config, bids_config):
    '''
    Get BIDSFiles associated with qc_dataset
    '''

    add_config_paths(user=bids_config)
    layout = BIDSLayout(qc_dataset,
                        validate=False,
                        index_metadata=False,
                        config=["user"])
    bidsfiles = layout.get(extension=qc_config['ImageExtensions'])
    return bidsfiles


def build_index(qc_dataset, qc_config, bids_config=None):
    '''
    Build database
    '''

    if bids_config is None:
        bids_config = DEFAULT_BIDS
        print(DEFAULT_BIDS)

    config = _validate_config(qc_config)
    bidsfiles = get_qc_bidsfiles(qc_dataset, config, bids_config)
    row_tpl = AxisNameTpl(Template(config['RowDescription']['name']),
                          config['RowDescription']['entities'])

    for c in config['Components']:
        component = ConfigComponent(**c)
        make_database(component.build_qc_entities(bidsfiles),
                      component.available_ratings, row_tpl)


def make_rowname(rowtpl, entities):
    keys = {k: v for k, v in entities.items() if k in rowtpl.entities}
    return rowtpl.tpl.substitute(keys)


def make_database(entities, available_ratings, row_tpl):
    '''
    Create database
    '''
    # First create necessary tables
    db.create_tables([Component, Rating, Entity, Image, TableRow, TableColumn])

    # Step 0: We'll create our component and ratings
    with db.atomic():
        component = Component.create()
        [
            Rating.create(name=r, component=component.id)
            for r in available_ratings
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
                                   columnname=e.column_name)
            [image_inserts.append((i, entity.id)) for i in e.images]

    with db.atomic():
        Image.insert_many(image_inserts, fields=[Image.path,
                                                 Image.entity]).execute()


def _is_subdict(big, small):
    return dict(big, **small) == big


def _get_key(bidsfile, entities):
    return tuple([bidsfile.entities[e] for e in entities])
