import yaml
import json
import os
import yamale
from yamale.validators import DefaultValidators, Validator
from bids.config import get_option

SCHEMAFILE = os.path.join(os.path.dirname(__file__), 'data/schema.yaml')


def load_json(file):
    with open(file, 'r') as f:
        result = json.load(f)
    return result


def get_entities():
    configfiles = [
        load_json(file)['entities']
        for file in get_option('config_paths').values()
    ]
    enumstrs = list()
    for configfile in configfiles:
        enumstr = [x['name'] for x in configfile]
        enumstrs.append(enumstr)
    enumstrs = [item for sublist in enumstrs for item in sublist]
    return enumstrs


class Entities(Validator):
    tag = 'Entities'

    def _is_valid(self, value):
        return value in get_entities()


def _validate_config(config):

    validators = DefaultValidators.copy()
    validators[Entities.tag] = Entities

    schema = yamale.make_schema(SCHEMAFILE, validators=validators)
    yamaledata = yamale.make_data(config)

    yamale.validate(schema, yamaledata)

    with open(config, 'r') as f:
        config = yaml.load(f, Loader=yaml.CLoader)

    return config
