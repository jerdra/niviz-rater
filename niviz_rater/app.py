from typing import Iterable, Any, Dict, Callable

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
from niviz_rater.db.utils import fetch_db_from_config, initialize_tables
import niviz_rater.db.exceptions as exceptions
from niviz_rater.index import build_index
from niviz_rater.utils import (get_qc_bidsfiles, update_bids_configuration)
from niviz_rater.spec import SpecConfig, db_settings_from_config

from niviz_rater.validation import validate_config

from niviz_rater.db.models import database_proxy

logger = logging.getLogger(__file__)

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
                  bids_files: Iterable[str]) -> None:

    db = fetch_db_from_config(app.config)

    logging.info("Creating Database tables...")
    try:
        initialize_tables(db, db_settings)
    except exceptions.IsInitialized:
        logger.error(f"DB { app.config['niviz_rater.db.file'] }"
                     " is already initialized!")
        logger.error(
            "Use `update_db` subcommand to add new qc images or annotations"
            " to DB or use runserver to launch the QC web interface!")
        return

    logging.info("Building Index of QC images")
    # build_index(db, bids_files, qc_spec)


@is_subcommand
def update_db(db_name, base_directory, qc_settings, bids_settings):
    raise NotImplementedError()


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
    update_db_parser = subparsers.add_parser('update_db',
                                             help='Update database')
    runserver_parser = subparsers.add_parser('runserver',
                                             help='Run bottle web interface')

    create_db_parser.set_defaults(func=initialize_db)
    update_db_parser.set_defaults(func=update_db)
    runserver_parser.set_defaults(func=runserver)

    runserver_parser.add_argument("--port",
                                  type=int,
                                  help="Port to use to open server",
                                  default=5000)
    runserver_parser.add_argument(
        "--fileserver-port",
        type=int,
        help="Port to use for serving local image files",
        default=5001)

    args = parser.parse_args()
    bids_configs = update_bids_configuration(args.bids_settings)

    # Config parsing
    qc_spec = validate_config(args.qc_specification_file, bids_configs)
    db_settings = db_settings_from_config(qc_spec, CONFIGURABLE_DB_SETTINGS)
    config = SpecConfig.from_validated(qc_spec)

    bids_files = get_qc_bidsfiles(args.base_directory, config.globals)

    # Setup application configuration and DB
    app.config['niviz_rater.base_path'] = args.base_directory
    app.config['niviz_rater.db.file'] = args.db_file

    database_proxy.initialize(fetch_db_from_config(app.config))
    app.config['niviz_rater.db.instance'] = database_proxy

    args.config = config
    args.bids_files = bids_files
    args.db_settings = db_settings

    args.func(args)


if __name__ == '__main__':
    main()
