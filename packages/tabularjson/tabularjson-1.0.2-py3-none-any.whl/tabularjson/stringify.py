import json
from math import isnan, inf
from symtable import Function
from typing import Any

from tabularjson.objects import get_in
from tabularjson.tabular import collect_fields, is_tabular
from tabularjson.types import (
    StringifyOptions,
    Path,
    TableFieldGetter,
    Record,
    GetValue,
)


def stringify(data: Any, options: StringifyOptions | None = None) -> str:
    """
    Stringify data into a string containing Tabular-JSON.

    Example:

        data = {
            'id': 1,
            'name': 'Brandon',
            'friends': [
                {'id': 2, 'name': 'Joe'},
                {'id': 3, 'name': 'Sarah'}
            ]
        }

        text = stringify(data, {"indentation": 4, "trailingCommas": False})

        print(text)
        # {
        #     "id": 1,
        #     "name": "Brandon",
        #     "friends": ---
        #         "id", "name"
        #         2,    "Joe"
        #         3,    "Sarah"
        #     ---
        # }


    :param data: JSON data
    :param options: A dict with indentation and trailingCommas
    :return: Returns a string containing Tabular-JSON.
    """

    global_indentation = resolve_indentation(
        options.get("indentation") if options else None
    )
    trailing_commas = (options.get("trailingCommas") if options else False) or False

    def stringify_value(value: Any, indent: str, indentation: str | None) -> str:
        # number
        if type(value) is int or type(value) is float:
            if isnan(value):
                return "nan"

            if value == inf:
                return "inf"

            if value == -inf:
                return "-inf"

            return stringify_primitive_value(value)

        # boolean, null, string
        if type(value) is bool or value is None or type(value) is str:
            return stringify_primitive_value(value)

        # table
        if is_tabular(value):
            return stringify_table(value, indent, indentation)

        # array
        if type(value) is list:
            return stringify_array(value, indent, indentation)

        # object
        if type(value) is dict:
            return stringify_object(value, indent, indentation)

        raise TypeError("Unknown type of data: " + str(type(value)))

    def stringify_array(array: list[Any], indent: str, indentation: str | None):
        if len(array) == 0:
            return "[]"

        child_indent = (indent + indentation) if indentation else indent
        text = "[\n" if indentation else "["

        for index, item in enumerate(array):
            if indentation:
                text += child_indent

            if type(item) is not Function:
                text += stringify_value(item, child_indent, indentation)

            if index < len(array) - 1:
                text += ",\n" if indentation else ","
            elif trailing_commas:
                text += ","

        text += "\n" + indent + "]" if indentation else "]"

        return text

    def stringify_table(array: list[Any], indent: str, indentation: str | None):
        is_root = array == data
        child_indent = (indent + indentation) if (indentation and indent) else indent
        col_separator = ", " if indentation else ","

        fields = get_fields(array)

        text = "" if is_root else "---\n"

        def stringify_cell(item: Any, field: TableFieldGetter):
            value, exists = field["get_value"](item)
            return stringify_value(value, child_indent, None) if exists else ""

        header = list(map(lambda field: field["name"], fields))
        rows = list(
            map(
                lambda item: list(
                    map(
                        lambda field: stringify_cell(item, field),
                        fields,
                    )
                ),
                array,
            )
        )

        if indentation:
            widths = calculate_column_widths(header, rows)

            text += child_indent + format_row(header, widths)
            for row in rows:
                text += child_indent + format_row(row, widths)
        else:
            text += child_indent + col_separator.join(header) + "\n"
            for row in rows:
                text += child_indent + col_separator.join(row) + "\n"

        text += "" if is_root else indent + "---"

        return text

    def format_row(row: list[str], widths: list[int]):
        cells = map(
            lambda entry: (entry[1] + ",").ljust(widths[entry[0]])
            if entry[0] < len(widths) - 1
            else entry[1] + "\n",
            enumerate(row),
        )

        return "".join(cells)

    def stringify_object(obj: Record, indent: str, indentation: str | None):
        entries = obj.items()

        if len(entries) == 0:
            return "{}"

        child_indent = indent + indentation if indentation else indent
        text = "{\n" if indentation else "{"

        for index, (key, value) in enumerate(entries):
            key_str = stringify_primitive_value(key)

            text += child_indent + key_str + ": " if indentation else key_str + ":"
            text += stringify_value(value, child_indent, indentation)

            if index < len(entries) - 1:
                text += ",\n" if indentation else ","
            elif trailing_commas:
                text += ","

        text += "\n" + indent + "}" if indentation else "}"

        return text

    return stringify_value(data, "", global_indentation)


def get_fields(records: list[Any]) -> list[TableFieldGetter]:
    nested_paths = collect_fields(records)

    return list(
        map(
            lambda path: {
                "name": stringify_field(path),
                "get_value": create_get_value(path),
            },
            nested_paths,
        )
    )


def create_get_value(path: Path) -> GetValue:
    if len(path) == 1:
        key = path[0]
        return lambda item: (item[key], True) if key in item else (None, False)

    return lambda item: get_in(item, path)


def stringify_primitive_value(value: str | int | float | bool | None) -> str:
    return json.dumps(value, ensure_ascii=False)


def stringify_field(path: Path):
    return ".".join(map(lambda key: stringify_primitive_value(key), path))


def resolve_indentation(indentation: int | str | None) -> str | None:
    if type(indentation) is int:
        return " " * indentation

    if type(indentation) is str and indentation != "":
        return indentation

    return None


def calculate_column_widths(header: list[str], rows: list[list[str]]) -> list[int]:
    widths = list(map(len, header))

    for row in rows:
        for i, field in enumerate(row):
            widths[i] = max(widths[i], len(field))

    # Note: we add 1 space to account for the comma,
    # and another to ensure there is at least 1 space between the columns
    return list(map(lambda width: width + 2, widths))
