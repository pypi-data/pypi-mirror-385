from typing import TypedDict, NotRequired, Any, Callable


class StringifyOptions(TypedDict):
    indentation: NotRequired[str | int | None]
    trailingCommas: NotRequired[bool]


class Symbol(object):
    def __init__(self, name):
        self.name = name


type Path = list[str | int]

type Record = dict[str, Any | Record]

type SetValue = Callable[[Record, Any], None]
type GetValue = Callable[[Record], tuple[Any, bool]]


class TableFieldSetter(TypedDict):
    keys: list[str]
    set_value: SetValue


class TableFieldGetter(TypedDict):
    name: str
    get_value: GetValue


# Parse result is a tuple (parsed, value)
type ParseResult = tuple[bool, Any]
