from typing import Any

from tabularjson.types import Path, Record


def get_in(obj: Record, path: Path) -> tuple[Any, bool]:
    """
    Get a nested property from a nested object or array.
    Returns a tuple (value: Any, exists: bool).
    """
    value = obj
    i = 0

    while i < len(path):
        key = path[i]

        if type(value) is dict:
            if type(key) is str and key in value:
                value = value[key]
            else:
                return None, False
        elif type(value) is list:
            index = int(key)

            if index < len(value):
                value = value[index]
            else:
                return None, False
        else:
            return None, False

        i += 1

    return value, True


def set_in(obj: Record, path: Path, value: Any):
    nested = obj
    i_last = len(path) - 1
    i = 0

    while i < i_last:
        part = path[i]

        if part not in nested:
            if type(path[i + 1]) is int:
                nested[part] = []
            else:
                nested[part] = {}

        nested = nested[part]
        i += 1

    key = path[i_last]
    if type(key) is int:
        arr_assign(nested, key, value)
    elif type(key) is str:
        # dict
        nested[key] = value

    return obj


def arr_assign(arr: list[Any], key: int, val: Any):
    # https://stackoverflow.com/questions/20567465/dynamically-growing-a-python-array-when-assigning-to-it
    try:
        arr[key] = val
        return
    except IndexError:
        # Do not extend the array for negative indices
        # That is ridiculously counterintuitive
        assert key >= 0
        arr.extend(((key + 1) - len(arr)) * [None])
        arr[key] = val
        return
