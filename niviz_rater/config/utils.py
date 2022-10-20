from __future__ import annotations

from typing import List
import configparser
import importlib.resources as pkg_resources

import niviz_rater.data


def remove_quotes(text: str) -> str:
    return text.replace("'", "").replace('"', "")


def remove_empty(texts: List[str]) -> List[str]:
    return [t for t in texts if t]


def parse_db_defaults():

    _db_defaults_parser = configparser.ConfigParser()
    with pkg_resources.path(niviz_rater.data, "db_defaults.cfg") as p:
        _db_defaults_parser.read(p)

    return _db_defaults_parser
