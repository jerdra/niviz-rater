import yaml
import json
import os
import yamale
from yamale.validators import DefaultValidators, Validator

SCHEMAFILE = os.path.join(os.path.dirname(__file__), 'data/schema.yaml')


def _load_json(file):
    with open(file, 'r') as f:
        result = json.load(f)
    return result


def _get_valid_entities(config_files):
    valid_configs = [_load_json(file)['entities'] for file in config_files]
    enumstrs = []
    for configfile in valid_configs:
        enumstrs.extend([entity['name'] for entity in configfile])
    return enumstrs


class Entities(Validator):
    '''
    Class to enable validation of BIDS entities
    from pyBIDS JSON configuration files
    '''

    __slots__ = "valid_configs"

    tag = 'Entities'

    def __init__(self, valid_configs):
        self.valid_configs = valid_configs
        super(Entities, self).__init__()

    def _is_valid(self, value):
        return value in _get_valid_entities(self.valid_configs)


def validate_config(config, bids_configs, schema_file=SCHEMAFILE):
    '''
    Validate a YAML-based configuration file against a
    schema file containing BIDS entity constraints

    Args:
        config (str): Path to YAML configuration file to be validated
        bids_configs (:obj: `list` of :obj: `str): List of paths to pyBIDS
            configuration files to include in validation
        schema_file (str): Path to YAML schema to validate against. Defaults
            to niviz_rater/data/schema.yaml

    Returns:
        config (dict): Parsed configuration file

    Raises:
        YamaleError: If validation fails due to invalid `config` file
    '''

    validators = DefaultValidators.copy()
    validators[Entities.tag] = Entities(valid_configs=bids_configs)

    schema = yamale.make_schema(schema_file, validators=validators)
    yamaledata = yamale.make_data(config)
    yamale.validate(schema, yamaledata)

    with open(config, 'r') as f:
        config = yaml.load(f, Loader=yaml.CLoader)

    return config
