import json
import logging
import os
import configparser
import importlib.resources as pkg_resources
from typing import List, Iterable, Any, Dict

import bids.config
from bids.layout import BIDSLayout, add_config_paths


def load_json(file):
    with open(file, 'r') as f:
        result = json.load(f)
    return result


def update_bids_configuration(bids_config: str) -> Iterable[str]:
    """
    Update configuration path for bids and return file paths
    for new configuration files
    """

    logging.debug(f'Replacing bids configuration with user={bids_config}')
    add_config_paths(user=bids_config)
    return bids.config.get_option('config_paths').values()


def get_qc_bidsfiles(qc_dataset: str, qc_spec: dict) -> List[str]:
    """
    Get BIDSFiles associated with qc_dataset
    """
    layout = BIDSLayout(qc_dataset,
                        validate=False,
                        index_metadata=False,
                        config=["user"])
    bidsfiles = layout.get(extension=qc_spec['ImageExtensions'])
    return bidsfiles


def get_db_settings(settings: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Get DB ratings defaults
    """

    import niviz_rater.data

    config_parser = configparser.ConfigParser()
    with pkg_resources.path(niviz_rater.data, "db_defaults.cfg") as p:
        config_parser.read(p)

    db_settings = {
        "DefaultAnnotation":
        _remove_quotes(config_parser.get("qc-settings", "default_annotation")),
        "DefaultRating":
        _remove_quotes(config_parser.get("qc-settings", "default_rating")),
        "Ratings":
        _remove_quotes(config_parser.get("qc-settings", "ratings")).split("\n")
    }

    db_settings.update(settings)
    return db_settings


def _remove_quotes(text: str) -> str:
    return text.replace("'", "").replace('"', "")
