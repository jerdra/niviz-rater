from typing import Iterable, Any, Dict

from bottle import route, run, static_file, debug, default_app

import os
import argparse
import logging
from pathlib import Path

from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from functools import partial

from niviz_rater.db import get_or_create_db, build_index
from niviz_rater.api import apiRoutes
from niviz_rater.validation import validate_config
from niviz_rater.utils import get_qc_bidsfiles, update_bids_configuration

logger = logging.getLogger(__file__)

app = default_app()


@route('/')
def index():
    return static_file("index.html", root="./client/public/")


@route('/<path:path>')
def home(path):
    return static_file(path, root="./client/public")


# Route to store user path
@route('/user_path')
def user_path():
    logging.info("User path selected")
    return str(app.config['niviz_rater.base_path'])


def launch_fileserver(base_directory, port=5002, hostname='localhost'):
    '''
    Launch background TCP server at `base_directory`
    '''
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


def initialize_db(qc_spec: Dict[str, Any], bids_files: Iterable[str]) -> None:
    db = get_or_create_db()
    logging.info("Building Index of QC images")
    build_index(db, bids_files, qc_spec)


def update_db(db_name, base_directory, qc_settings, bids_settings):
    raise NotImplementedError()


def runserver(base_directory, fileserver_port, port):
    _, address = launch_fileserver(base_directory,
                                   port=fileserver_port)
    app.config['niviz_rater.fileserver'] = address

    app.merge(apiRoutes)
    debug(True)
    run(host='localhost', port=port)


def main():
    parser = argparse.ArgumentParser(
        description="QC Application to perform"
        " quality control on Niviz-generated or BIDS organized QC images")
    parser.add_argument("--base-directory",
                        type=Path,
                        required=True,
                        help="Base directory of BIDS-organized QC directory")
    parser.add_argument("--qc-specification-file",
                        type=Path,
                        required=True,
                        help="Path to QC rating specification file to use"
                        " when rating images")
    parser.add_argument("--bids-settings",
                        type=Path,
                        help="Path to pyBIDS configuration json")
    subparsers = parser.add_subparsers(help='sub-command help')
    create_db_parser = subparsers.add_parser('initialize_db', help='Initialize database')
    update_db_parser = subparsers.add_parser('update_db', help='Update database')
    runserver_parser = subparsers.add_parser('runserver', help='Run bottle web interface')

    create_db_parser.set_defaults(func=initialize_db)
    update_db_parser.set_defaults(func=update_db)
    runserver_parser.set_defaults(func=runserver)

    runserver_parser.add_argument("--port",
                        type=int,
                        help="Port to use to open server",
                        default=5000)
    runserver_parser.add_argument("--fileserver-port",
                        type=int,
                        help="Port to use for serving local image files",
                        default=5001)
    parser.add_argument("--use-existing-index",
                        type=Path,
                        help="Use an existing database file")

    args = parser.parse_args()
    app.config['niviz_rater.base_path'] = args.base_directory

    qc_spec = validate_config(args.qc_specification_file)
    update_bids_configuration(args.bids_settings)
    bids_files = get_qc_bidsfiles(args.base_directory, qc_spec)
    args.qc_spec = qc_spec
    args.bids_files = bids_files
    args.func(args)


if __name__ == '__main__':
    main()
