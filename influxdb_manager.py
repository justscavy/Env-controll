import json


def read_config(file_path):
        with open(file_path) as f:
            return json.load(f)