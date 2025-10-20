"""Reference data helpers."""

import json
import pkgutil
from mgz.util import Version


REF_PACKAGE = 'aocref'


def get_dataset(version, mod):
    """Fetch dataset reference data."""
    if version is Version.DE:
        if isinstance(mod, list) and 11 in mod:
            dataset_id = 101
        else:
            dataset_id = 100
    elif version is Version.HD:
        dataset_id = 300
    elif mod:
        dataset_id = mod[0]
    else:
        dataset_id = 0
    return dataset_id, json.loads(pkgutil.get_data(REF_PACKAGE, f'data/datasets/{dataset_id}.json'))


def get_consts():
    """Fetch constants."""
    return json.loads(pkgutil.get_data(REF_PACKAGE, f'data/constants.json'))
