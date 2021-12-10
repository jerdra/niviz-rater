import json
import logging
import os
from typing import List

from bids.layout import BIDSLayout, add_config_paths

DEFAULT_BIDS_FILE = os.path.join(os.path.dirname(__file__), 'data/bids.json')


def load_json(file):
    with open(file, 'r') as f:
        result = json.load(f)
    return result


def update_bids_configuration(bids_config: str = os.path.join(os.path.dirname(__file__), 'data/bids.json')) -> None:
    """
    Update configuration path for bids with
    """
    logging.debug(f'Replacing bids configuration with user={bids_config}')
    add_config_paths(user=bids_config)


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
