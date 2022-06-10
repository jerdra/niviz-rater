from __future__ import annotations

import json
import logging
from typing import List, Iterable, TYPE_CHECKING

import bids.config
from bids.layout import BIDSLayout, add_config_paths

if TYPE_CHECKING:
    from niviz_rater.spec import ConfigGlobals


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


def get_qc_bidsfiles(qc_dataset: str, config: ConfigGlobals) -> List[str]:
    """
    Get BIDSFiles associated with qc_dataset
    """
    layout = BIDSLayout(qc_dataset,
                        validate=False,
                        index_metadata=False,
                        config=["user"])
    bidsfiles = layout.get(extension=config.image_extensions)
    return bidsfiles
