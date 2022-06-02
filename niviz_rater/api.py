"""
API for accessing and updating stored QC Index
"""

import os
from bottle import route, Bottle, request, response

from niviz_rater.db.utils import fetch_db_from_config
from niviz_rater.models import (Entity, Image, TableRow, TableColumn,
                                Annotation, Rating)
import logging
from peewee import JOIN, prefetch

apiRoutes = Bottle()
logger = logging.getLogger(__file__)


def _fileserver(path, app_config):
    """
    Transform local directory path to fileserver path
    """

    base = app_config['niviz_rater.base_path']
    address = app_config['niviz_rater.fileserver']

    img = os.path.relpath(path, base)
    addr = f"{address}/{img}"
    return addr


def _annotation(annotation):
    return {'id': annotation.id, 'name': annotation.name}


def _rating(rating):
    return {'id': rating.id, 'name': rating.name}


@route('/api/overview')
def summary():
    """
    Pull summary information from index, yield:
        - rows of entity index
        - qc items per row entity of index
        - remaining un-rated images
        - total number of annotations required
    """
    n_unrated = (Entity.select().join(Rating).where(
        Rating.name == "None").count())
    logger.info(f"Number of unrated scans is: {n_unrated}")

    n_rows = TableRow.select().count()
    n_cols = TableColumn.select().count()
    n_entities = Entity.select().count()
    return {
        "numberOfUnrated": n_unrated,
        "numberOfRows": n_rows,
        "numberOfColumns": n_cols,
        "numberOfEntities": n_entities
    }


@route('/api/ratings')
def ratings():
    """
    Return list of available ratings
    """
    valid_rating = [_rating(r) for r in Rating.select()]
    return {"validRatings": valid_rating}


@route('/api/spreadsheet')
def spreadsheet():
    """
    Query database for information required to construct
    interactive table, yields for each TableRow it's
    set of entities
    """

    q = (Entity.select(Entity).join(TableRow).switch(Entity).join(TableColumn).
         switch(Entity).join(Rating).switch(Entity).prefetch(Image))

    # Need to remove base path
    r = {
        "entities": [{
            "rowName":
            e.rowname.name,
            "columnName":
            e.columnname.name,
            "imagePaths":
            [_fileserver(i.path, request.app.config) for i in e.images],
            "comment":
            e.comment,
            "rating":
            _rating(e.rating),
            "id":
            e.id,
            "name":
            e.name,
            "annotation":
            _annotation(e.annotation)
        } for e in q]
    }
    return r


@route('/api/entity/<entity_id:int>')
def get_entity_info(entity_id):
    try:
        e = (Entity.select(Entity).join(TableRow).switch(Entity).join(
            TableColumn).switch(Entity).join(Rating).switch(Entity).where(
                Entity.id == entity_id).prefetch(Image))[0]
    except IndexError:
        logger.error("Cannot find entity with specified ID!")
        response.status_code = 400
        return

    r = {
        "name": e.name,
        "annotation": _annotation(e.annotation),
        "comment": e.comment,
        "rating": _rating(e.rating),
        "imagePaths":
        [_fileserver(i.path, request.app.config) for i in e.images],
        "id": e.id,
        "rowName": e.rowname.name,
        "columnName": e.columnname.name
    }
    return r


@route('/api/entity/<entity_id:int>/view')
def get_entity_view(entity_id):
    """
    Retrieve full information for entity
    Yields:
        entity name
        array of entity image paths
        available annotations
        current annotation for a given entity
    """

    entity = Entity.select().where(Entity.id == entity_id).first()
    images = Image.select(Image,
                          Entity).join(Entity).where(Image.entity == entity)

    q_annotation = Annotation.select().where(
        Annotation.component_id == entity.component_id)
    available_annotations = [_annotation(r) for r in q_annotation]

    response = {
        "entityId": entity.id,
        "entityName": entity.name,
        "entityAnnotation": _annotation(entity.annotation),
        "entityComment": entity.comment,
        "entityAvailableAnnotations": available_annotations,
        "entityImages":
        [_fileserver(i.path, request.app.config) for i in images],
        "entityRating": _rating(entity.rating)
    }
    return response


@route('/api/entity', method='POST')
def update_annotation():
    """
    Post body should contain information about:
        -   annotation_id
        -   comment
        -   qc_rating
    """
    expected_keys = {'annotation', 'comment', 'rating'}
    data = request.json
    if data is None:
        logger.info("No changes requested...")
        return
    logger.info("Received message from application!")
    update_keys = expected_keys.intersection(data.keys())
    logger.info("Updating keys")
    logger.info(update_keys)

    # Select entity
    entity = Entity.select().where(Entity.id == data['id']).first()
    logger.info(data)

    # Update entity with available keys
    db = fetch_db_from_config(request.app.config)
    with db.atomic():
        for k in update_keys:
            setattr(entity, k, data[k])
        try:
            entity.save()
        except:
            response.status_code = 400
    return


@route("/api/export")
def export_csv():
    """
    Export participants.tsv CSV file
    """

    entities = (Entity.select(Entity, TableColumn, Annotation, Rating).join(
        Annotation, JOIN.LEFT_OUTER).switch(Entity).join(TableColumn).switch(
            Entity).join(Rating).order_by(TableColumn.name))
    columns = TableColumn.select().order_by(TableColumn.name)
    rows = TableRow.select()
    rows_pf = prefetch(rows, entities)

    rows = [_make_row(r, columns) for r in rows_pf]
    header = [
        f"{c.name}\t{c.name}_passfail\t{c.name}_comment" for c in columns
    ]
    header = "\t".join(["subjects"] + header)
    csv = "\n".join([header] + rows)
    return csv


def _make_row(row, columns):
    """
    Given a set of Entities for a given row, create
    column entries
    """
    p = 0
    entities = row.entities
    entries = [row.name]
    empty = ("", "", "")
    for c in columns:
        try:
            e = entities[p]
            if e.columnname == c:
                entries.extend(e.entry)
                p += 1
            else:
                entries.extend(empty)
        except IndexError:
            entries.extend(empty)

    return "\t".join(entries)
