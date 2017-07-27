try:
    import json
except ImportError:
    import simplejson as json


def loadJsonConfig(fileName):
    with open(fileName, 'r') as json_file:
        data = json.load(json_file)
        return data
