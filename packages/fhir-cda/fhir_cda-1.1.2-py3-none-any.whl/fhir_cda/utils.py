import yaml
from collections import OrderedDict
from pathlib import Path


def is_observation_type(variable):
    if isinstance(variable, dict):
        required_keys = {"value_system", "value", "code", "units_system", "units"}

        if required_keys.issubset(variable.keys()):
            if isinstance(variable["value"], (int, float, str)) and \
                    isinstance(variable["value_system"], str) and \
                    isinstance(variable["code"], str) and \
                    isinstance(variable["units_system"], str) and \
                    isinstance(variable["units"], str):
                return True
    return False


def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def check_first_file_extension(folder_path):
    folder = Path(folder_path)
    files = sorted([f for f in folder.iterdir() if f.is_file()])

    if not files:
        return None

    first_file = files[0]
    ext = first_file.suffix.lower()

    if ext == '.dcm':
        return 'dcm'
    elif ext == '.nrrd':
        return 'nrrd'
    else:
        return 'unknown'
