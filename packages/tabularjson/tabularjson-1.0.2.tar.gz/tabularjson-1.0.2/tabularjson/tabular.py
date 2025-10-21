from typing import Any

from tabularjson.types import Path, Record, Symbol

leaf = Symbol("leaf")


def is_tabular(value: Any) -> bool:
    return (
        type(value) is list
        and len(value) > 0
        and all(type(item) is dict for item in value)
    )


def collect_fields(array: list[Any]) -> list[Path]:
    merged = {}

    for item in array:
        if type(item) is dict:
            _merge_object(item, merged)
        else:
            _merge_value(item, merged)

    paths = []
    _collect_paths(merged, [], paths)

    return paths


def _merge_object(obj: Record, merged: Record):
    for key, value in obj.items():
        if key not in merged:
            merged[key] = {}

        value_merged = merged[key]

        if type(value) is dict:
            _merge_object(value, value_merged)
        else:
            _merge_value(value, value_merged)


def _merge_value(value: Any, merged: Record):
    if leaf not in merged:
        merged[leaf] = False if value is None else True


def _collect_paths(merged: Record, parent_path: Path, paths: list[Path]):
    if merged.get(leaf) is True or (merged.get(leaf) is False and is_empty(merged)):
        paths.append(parent_path)
    elif type(merged) is list:
        for index, item in enumerate(merged):
            _collect_paths(item, parent_path + [index], paths)
    elif type(merged) is dict:
        for key, value in merged.items():
            if key != leaf:
                _collect_paths(value, parent_path + [key], paths)


def is_empty(obj: Record) -> bool:
    return len(list(filter(lambda key: key != leaf, obj.keys()))) == 0
