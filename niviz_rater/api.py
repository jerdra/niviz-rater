"""
API for accessing and updating stored QC Index
"""

import os
from bottle import route, Bottle, request, response

from niviz_rater.db.utils import fetch_db_from_config
import niviz_rater.db.queries as queries
from niviz_rater.config import db_defaults
import logging

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
    if annotation is None:
        return {'id': None, 'name': db_defaults.DEFAULT_ANNOTATION}
    else:
        return {'id': annotation.id, 'name': annotation.name}


def _rating(rating):
    if rating is None:
        return {'id': None, 'name': db_defaults.DEFAULT_RATING}
    else:
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

    total, n_rated, n_unrated = queries.get_summary()
    logger.info(f"Number of unrated scans is: {n_unrated}")

    return {
        "numberOfUnrated": n_unrated,
        "numberOfRated": n_rated,
        "numberOfRows": 0,
        "numberOfEntities": total
    }


@route('/api/ratings')
def ratings():
    """
    Return list of available ratings
    """
    valid_rating = [_rating(r) for r in queries.get_avilable_ratings()]
    return {"validRatings": valid_rating}


@route('/api/spreadsheet')
def spreadsheet():
    """
    Query database for information required to construct
    interactive table, yields for each TableRow it's
    set of entities
    """
    entities = queries.get_denormalized_entities()

    # Need to remove base path
    payload = {
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
        } for e in entities]
    }
    return payload


@route('/api/entity/<entity_id:int>')
def get_entity_info(entity_id):
    try:
        entity = queries.get_denormalized_entity_by_id(entity_id)
    except ValueError as e:
        logger.error(f"Issue with obtaining Entity with id {entity_id}")
        logger.error(f"Error msg: {e}")
        response.status_code = 400
        return

    payload = {
        "name":
        entity.name,
        "annotation":
        _annotation(entity.annotation),
        "comment":
        entity.comment,
        "rating":
        _rating(entity.rating),
        "imagePaths":
        [_fileserver(i.path, request.app.config) for i in entity.images],
        "id":
        entity.id,
        "rowName":
        entity.rowname.name,
        "columnName":
        entity.columnname.name
    }
    return payload


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

    entity = queries.get_denormalized_entity_by_id(entity_id)
    available_annotations = [
        _annotation(a) for a in queries.get_available_annotations(entity)
    ]

    response = {
        "entityId":
        entity.id,
        "entityName":
        entity.name,
        "entityAnnotation":
        _annotation(entity.annotation),
        "entityComment":
        entity.comment,
        "entityAvailableAnnotations":
        available_annotations,
        "entityImages":
        [_fileserver(i.path, request.app.config) for i in entity.images],
        "entityRating":
        _rating(entity.rating)
    }
    return response


@route('/api/entity', method='POST')
def update_entity():
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
    entity = queries.get_denormalized_entity_by_id(data['id'])
    logger.info(data)

    # Update entity with available keys
    db = fetch_db_from_config(request.app.config)

    # TODO: Pull this out into a query function
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

    rows = queries.get_denormalized_rows()
    columns = queries.get_columns()

    rows = [_make_row(r, columns) for r in rows]
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
