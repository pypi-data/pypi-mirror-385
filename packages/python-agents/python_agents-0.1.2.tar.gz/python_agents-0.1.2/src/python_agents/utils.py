import json


def pretty_print(data: dict):
    print(json.dumps(data, sort_keys=True, indent=4))
