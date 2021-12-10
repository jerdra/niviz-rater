import json


def _load_json(file):
    with open(file, 'r') as f:
        result = json.load(f)
    return result
