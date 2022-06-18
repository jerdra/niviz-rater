from __future__ import annotations
from typing import Any, Dict, Callable, TYPE_CHECKING

from bottle import route, run, static_file, debug, default_app

import os
import argparse
import logging
import inspect
from pathlib import Path

from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from functools import partial

from niviz_rater.api import apiRoutes
import niviz_rater.db.utils as dbutils
import niviz_rater.db.exceptions as exceptions
from niviz_rater.utils import get_bids_layout, update_bids_configuration
from niviz_rater.spec import SpecConfig, db_settings_from_config

from niviz_rater.validation import validate_config

from niviz_rater.db.models import database_proxy

if TYPE_CHECKING:
    from bids import BIDSLayout

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

app = default_app()

FILE = Path(__file__).parent
DEFAULT_BIDS_CONFIGURATION = FILE / "data/bids.json"
CONFIGURABLE_DB_SETTINGS = ['Ratings']


def is_subcommand(func: Callable):

    def _wrapped(args):
        try:
            extracted = {
                e: getattr(args, e)
                for e in inspect.getfullargspec(func).args
            }
        except AttributeError:
            raise
        else:
            return func(**extracted)

    return _wrapped


@route('/')
def index():
    return static_file("index.html", root=FILE / "client/public/")


@route('/<path:path>')
def home(path):
    return static_file(path, root=FILE / "client/public")


# Route to store user path
@route('/user_path')
def user_path():
    logging.info("User path selected")
    return str(app.config['niviz_rater.base_path'])


def launch_fileserver(base_directory, port=5002, hostname='localhost'):
    """
    Launch background TCP server at `base_directory`
    """
    path = os.path.abspath(base_directory)
    handler = partial(SimpleHTTPRequestHandler, directory=path)
    httpd = HTTPServer((hostname, port), handler)

    address = f"http://{httpd.server_name}:{httpd.server_port}"

    def serve(httpd):
        with httpd:
            logger.info(f"Creating server at {port}")
            httpd.serve_forever()

    thread = Thread(target=serve, args=(httpd, ))
    thread.setDaemon(True)
    thread.start()

    return httpd, address


@is_subcommand
def initialize_db(db_settings: Dict[str, Any], config: SpecConfig,
                  bids_layout: BIDSLayout) -> None:

    db = dbutils.fetch_db_from_config(app.config)

    logging.info("Creating Database tables...")
    try:
        dbutils.initialize_tables(db, db_settings)
    except exceptions.IsInitialized:
        logger.error(f"DB { app.config['niviz_rater.db.file'] }"
                     " is already initialized!")
        logger.error(
            "Use `update_db` subcommand to add new qc images or annotations"
            " to DB or use `runserver` to launch the QC web interface!")
        return

    logging.info("Building Index of QC images")
    for component_entity in config.entities_by_component(bids_layout):

        logger.info(f"Adding {component_entity.component_name} to DB\n")
        logger.info(
            f"Attempting to add {len(component_entity.entities)} records")

        dbutils.component_entities_to_db(db, component_entity)


@is_subcommand
def update_db(db_file, config: SpecConfig, bids_layout: BIDSLayout,
              update_existing: bool, no_reset_on_update: bool):

    if not Path(db_file).exists():
        logger.error(f"Did not find existing db_file: {db_file}")
        logger.error("Use `initialize_db` prior to running `update_db`")
        return

    db = dbutils.fetch_db_from_config(app.config)

    if not dbutils.is_initialized(db):
        logger.error("Database is not yet initialized, it may be corrupted")
        logger.error(
            f"Remove DB {Path(db_file).absolute()} then use `initialize_db`!")
        return

    logging.info("Updating database with new entities...")
    for component_entity in config.entities_by_component(bids_layout):
        logger.info(f"Working on {component_entity.component_name}\n")
        logger.info(
            f"Attempting to add {len(component_entity.entities)} records")

        dbutils.component_entities_to_db(
            db,
            component_entity,
            update_existing=update_existing,
            reset_on_update=not no_reset_on_update)


@is_subcommand
def runserver(base_directory: str, fileserver_port: int, port: int):
    _, address = launch_fileserver(base_directory, port=fileserver_port)
    app.config['niviz_rater.fileserver'] = address

    app.merge(apiRoutes)
    debug(True)
    run(host='localhost', port=port)


def main():
    parser = argparse.ArgumentParser(
        description="QC Application to perform"
        " quality control on Niviz-generated or BIDS organized QC images")
    parser.add_argument("--base-directory",
                        "-i",
                        type=Path,
                        required=True,
                        help="Base directory of BIDS-organized QC directory")
    parser.add_argument("--qc-specification-file",
                        "-c",
                        type=Path,
                        required=True,
                        help="Path to QC rating specification file to use"
                        " when rating images")
    parser.add_argument("--bids-settings",
                        type=Path,
                        default=DEFAULT_BIDS_CONFIGURATION,
                        help="Path to pyBIDS configuration json")

    parser.add_argument("--db-file",
                        type=Path,
                        required=False,
                        default="niviz.db",
                        help="Path to store SQLite DB containing state")

    subparsers = parser.add_subparsers(help='sub-command help')

    create_db_parser = subparsers.add_parser('initialize_db',
                                             help='Initialize database')
    create_db_parser.set_defaults(func=initialize_db)

    update_db_parser = subparsers.add_parser('update_db',
                                             help='Update database')
    update_db_parser.add_argument("--update-existing",
                                  help=("Update existing Entity if it "
                                        "already exists in the database"),
                                  default=False,
                                  action="store_true")
    update_db_parser.add_argument("--no-reset-on-update",
                                  help=("Do not reset the rating/annotation "
                                        "of the Entity if it is updated\n"
                                        "This flag can only be used "
                                        "concurrently with --update-existing"),
                                  default=False,
                                  action="store_true")
    update_db_parser.set_defaults(func=update_db)

    runserver_parser = subparsers.add_parser('runserver',
                                             help='Run bottle web interface')
    runserver_parser.add_argument("--port",
                                  type=int,
                                  help="Port to use to open server",
                                  default=5000)
    runserver_parser.add_argument(
        "--fileserver-port",
        type=int,
        help="Port to use for serving local image files",
        default=5001)
    runserver_parser.set_defaults(func=runserver)

    args = parser.parse_args()
    bids_configs = update_bids_configuration(args.bids_settings)

    # Config parsing
    qc_spec = validate_config(args.qc_specification_file, bids_configs)
    db_settings = db_settings_from_config(qc_spec, CONFIGURABLE_DB_SETTINGS)
    config = SpecConfig.from_validated(qc_spec)

    bids_layout = get_bids_layout(args.base_directory)

    # Setup application configuration and DB
    app.config['niviz_rater.base_path'] = args.base_directory
    app.config['niviz_rater.db.file'] = args.db_file

    database_proxy.initialize(dbutils.fetch_db_from_config(app.config))
    app.config['niviz_rater.db.instance'] = database_proxy

    args.config = config
    args.bids_layout = bids_layout
    args.db_settings = db_settings
    args.func(args)


if __name__ == '__main__':
    main()
