from bottle import route, run, static_file, debug, default_app

import os
import argparse
import logging
from pathlib import Path

from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from functools import partial

from niviz_rater.index import build_index
from niviz_rater.api import apiRoutes

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


def main():
    parser = argparse.ArgumentParser(
        description="QC Application to perform"
        " quality control on Niviz-generated or BIDS organized QC images")

    parser.add_argument("base_directory",
                        type=Path,
                        help="Base directory of BIDS-organized QC directory")
    parser.add_argument("qc_settings",
                        type=Path,
                        help="Path to QC rating specification to use"
                        " when rating images")
    parser.add_argument("--bids-settings",
                        type=Path,
                        help="Path to pyBIDS configuration json")
    parser.add_argument("--port",
                        type=int,
                        help="Port to use to open server",
                        default=5000)
    parser.add_argument("--fileserver-port",
                        type=int,
                        help="Port to use for serving local image files",
                        default=5001)
    parser.add_argument("--use-existing-index",
                        type=Path,
                        help="Use an existing database file")

    args = parser.parse_args()
    app.config['niviz_rater.base_path'] = args.base_directory

    logging.info("Building Index of QC images")
    if not args.use_existing_index:
        build_index(args.base_directory, args.qc_settings, args.bids_settings)

    _, address = launch_fileserver(args.base_directory,
                                   port=args.fileserver_port)
    app.config['niviz_rater.fileserver'] = address

    app.merge(apiRoutes)
    debug(True)
    run(host='localhost', port=args.port)


if __name__ == '__main__':
    main()
