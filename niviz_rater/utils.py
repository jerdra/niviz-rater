import json


def load_json(file):
    with open(file, 'r') as f:
        result = json.load(f)
    return result
