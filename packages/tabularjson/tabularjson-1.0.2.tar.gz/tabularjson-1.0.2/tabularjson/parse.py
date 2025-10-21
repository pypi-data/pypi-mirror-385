from math import inf
from typing import Any, Callable

from tabularjson.objects import set_in
from tabularjson.types import TableFieldSetter, SetValue, ParseResult, Record


def parse(text: str) -> Any:
    """
    Parse a string containing Tabular-JSON data into JSON.

    Example:

        text = \"\"\"{
                "id": 1,
                "name": "Brandon",
                "friends": ---
                "id", "name"
                    2,    "Joe"
                    3,    "Sarah"
                          ---
            }
        \"\"\"

        data = parse(text)

        print(data)
        # {
        #     'id': 1,
        #     'name': 'Brandon',
        #     'friends': [
        #         {'id': 2, 'name': 'Joe'},
        #         {'id': 3, 'name': 'Sarah'}
        #     ]
        # }

    :param text: A string containing Tabular-JSON data
    :return: Returns the parsed JSON data
    """

    i = 0

    def parse_object() -> ParseResult:
        nonlocal i

        if text_at(i) != "{":
            return False, None

        i += 1
        skip_whitespace()

        obj = {}
        initial = True
        while i < len(text) and text_at(i) != "}":
            if not initial:
                eat_comma()
                skip_whitespace()

                if text_at(i) == "}":
                    # trailing comma
                    break
            else:
                initial = False

            start = i

            key = parse_string_or(raise_object_key_expected)

            skip_whitespace()
            eat_colon()
            parsed, value = parse_value()

            if not parsed:
                raise_object_value_expected()

            if key in obj and not value == obj[key]:
                raise_duplicate_key(key, start + 1)

            obj[key] = value

        if text_at(i) != "}":
            raise_object_key_or_end_expected()
        i += 1

        return True, obj

    def parse_array() -> ParseResult:
        nonlocal i

        if text_at(i) != "[":
            return False, None

        i += 1
        skip_whitespace()

        array: list[Any] = []
        initial = True
        while i < len(text) and text_at(i) != "]":
            if not initial:
                eat_comma()
                skip_whitespace()

                if text_at(i) == "]":
                    # trailing comma
                    break
            else:
                initial = False

            value = parse_value_or(raise_array_item_expected)
            array.append(value)

        if text_at(i) != "]":
            raise_array_item_or_end_expected()
        i += 1

        return True, array

    def parse_root_table() -> ParseResult:
        nonlocal i

        parsed, value = parse_value()

        if parsed and type(value) is str and text_at(i) == ",":
            i = 0

            skip_whitespace()

            fields = parse_table_fields()
            eat_table_row_separator()

            rows: list[Record] = []

            while i < len(text):
                rows.append(parse_table_row(fields))

                if i < len(text):
                    eat_table_row_separator()

            return True, rows

        return parsed, value

    def parse_table() -> ParseResult:
        nonlocal i

        if text_at(i) != "-" or text[i : i + 3] != "---":
            return False, None

        i += 3
        skip_table_whitespace()
        eat_table_row_separator()

        fields = parse_table_fields()
        eat_table_row_separator()

        rows: list[Record] = []
        while i < len(text) and text[i : i + 3] != "---":
            rows.append(parse_table_row(fields))
            eat_table_row_separator()

        if text[i : i + 3] != "---":
            raise_table_row_or_end_expected()
        i += 3

        return True, rows

    def parse_table_fields() -> list[TableFieldSetter]:
        nonlocal i

        fields: list[TableFieldSetter] = []
        initial_field = True

        while i < len(text) and text_at(i) != "\n":
            if not initial_field:
                eat_comma()
                skip_table_whitespace()
            else:
                initial_field = False

            keys: list[str] = [parse_string_or(raise_table_field_expected)]
            skip_table_whitespace()

            while i < len(text) and text_at(i) == ".":
                i += 1
                skip_table_whitespace()

                keys.append(parse_string_or(raise_table_field_expected))
                skip_table_whitespace()

            fields.append({"keys": keys, "set_value": create_set_value(keys)})

        return fields

    def parse_table_row(fields: list[TableFieldSetter]) -> Record:
        row: Record = {}

        for index, field in enumerate(fields):
            parsed, value = parse_element()
            skip_table_whitespace()

            if parsed:
                field["set_value"](row, value)

            if index < len(fields) - 1:
                eat_comma()
                skip_table_whitespace()

        return row

    def parse_value() -> ParseResult:
        skip_whitespace()

        parsed, value = parse_element()

        skip_whitespace()

        return parsed, value

    def parse_value_or(raise_error: Callable[[], None]):
        parsed, value = parse_value()
        if not parsed:
            raise_error()

        return value

    def parse_element() -> ParseResult:
        parsed, elem = parse_object()
        if parsed:
            return parsed, elem

        parsed, elem = parse_array()
        if parsed:
            return parsed, elem

        parsed, elem = parse_table()
        if parsed:
            return parsed, elem

        parsed, elem = parse_string()
        if parsed:
            return parsed, elem

        parsed, elem = parse_number()
        if parsed:
            return parsed, elem

        parsed, elem = parse_keyword("true", True)
        if parsed:
            return parsed, elem

        parsed, elem = parse_keyword("false", False)
        if parsed:
            return parsed, elem

        parsed, elem = parse_keyword("null", None)
        if parsed:
            return parsed, elem

        return False, None

    def parse_keyword(name: str, value: Any) -> ParseResult:
        nonlocal i

        if text[i : i + len(name)] == name:
            i += len(name)
            return True, value

        return False, None

    def skip_whitespace():
        while skip_whitespace_chars() or skip_line_comment() or skip_block_comment():
            # repeat until no more whitespace or comments
            pass

    def skip_table_whitespace():
        while (
            skip_table_whitespace_chars() or skip_line_comment() or skip_block_comment()
        ):
            # repeat until no more whitespace or comments
            pass

    def skip_whitespace_chars():
        nonlocal i

        if is_whitespace(text_at(i)):
            i += 1

            while is_whitespace(text_at(i)):
                i += 1

            return True

        return False

    def skip_table_whitespace_chars():
        nonlocal i

        if is_table_whitespace(text_at(i)):
            i += 1

            while is_table_whitespace(text_at(i)):
                i += 1

            return True

        return False

    def skip_line_comment():
        nonlocal i

        # skip a line comment like "// ..."
        if text_at(i) == "/" and i + 1 < len(text) and text_at(i + 1) == "/":
            i += 2

            while i < len(text) and text_at(i) != "\n":
                i += 1

            return True

        return False

    def skip_block_comment():
        nonlocal i

        # skip a block comment like "/* ... */"
        if text_at(i) == "/" and i + 1 < len(text) and text_at(i + 1) == "*":
            i += 2

            while (i < len(text) and text_at(i) != "*") or (
                i + 1 < len(text) and text[i + 1] != "/"
            ):
                i += 1

            i += 2

            return True

        return False

    def parse_string() -> ParseResult:
        nonlocal i

        if text_at(i) != '"':
            return False, None

        i += 1

        result: str = ""
        has_unicode = False
        while i < len(text) and text_at(i) != '"':
            if text_at(i) == "\\":
                char = text_at(i + 1)
                escape_char = escape_characters.get(char) if char else None
                if escape_char is not None:
                    result += escape_char
                    i += 1
                elif char == "u":
                    if (
                        is_hex(text_at(i + 2))
                        and is_hex(text_at(i + 3))
                        and is_hex(text_at(i + 4))
                        and is_hex(text_at(i + 5))
                    ):
                        result += chr(int(text[i + 2 : i + 6], 16))
                        i += 5
                        has_unicode = True
                    else:
                        raise_invalid_unicode_character(i)
                else:
                    raise_invalid_escape_character(i)
            else:
                c = text_at(i)
                if c is not None and is_valid_string_character(c):
                    result += c
                else:
                    raise_invalid_character(c or "")
            i += 1

        expect_end_of_string()
        i += 1

        return True, (
            result
            if not has_unicode
            else result.encode("utf-16", "surrogatepass").decode("utf-16")
        )

    def parse_string_or(raise_error: Callable[[], None]) -> str:
        parsed, string = parse_string()
        if not parsed:
            raise_error()

        return string

    def parse_number() -> ParseResult:
        nonlocal i

        start = i
        is_int = True

        parsed, special = parse_keyword("inf", inf)
        if parsed:
            return parsed, special

        parsed, special = parse_keyword("-inf", -inf)
        if parsed:
            return parsed, special

        parsed, special = parse_keyword("nan", inf / inf)
        if parsed:
            return parsed, special

        if text_at(i) == "-":
            i += 1
            expect_digit(start)

        if text_at(i) == "0":
            i += 1
        elif is_non_zero_digit(text_at(i)):
            i += 1
            while is_digit(text_at(i)):
                i += 1

        if text_at(i) == ".":
            i += 1
            is_int = False
            expect_digit(start)
            while is_digit(text_at(i)):
                i += 1

        if text_at(i) == "e" or text_at(i) == "E":
            is_int = False
            i += 1
            if text_at(i) == "-" or text_at(i) == "+":
                i += 1

            expect_digit(start)
            while is_digit(text_at(i)):
                i += 1

        if i > start:
            return True, int(text[start:i]) if is_int else float(text[start:i])

        return False, None

    def eat_comma():
        nonlocal i

        if text_at(i) != ",":
            raise SyntaxError(f"Comma ',' expected after value {got_at()}")
        i += 1

    def eat_colon():
        nonlocal i

        if text_at(i) != ":":
            raise SyntaxError(f"Colon ':' expected after property name {got_at()}")
        i += 1

    def eat_table_row_separator():
        # must start with a newline
        if text_at(i) != "\n":
            raise SyntaxError(f"Newline '\n' expected after table row {got_at()}")

        # can optionally be followed by more newlines and whitespace and comments
        skip_whitespace()

    def expect_end_of_input():
        if i < len(text):
            raise SyntaxError(f"Expected end of input {got_at()}")

    def expect_digit(start: int):
        if not is_digit(text_at(i)):
            num_so_far = text[start:i]
            raise SyntaxError(
                f"Invalid number '{num_so_far}', expecting a digit {got_at()}"
            )

    def expect_end_of_string():
        if text_at(i) != '"':
            raise SyntaxError(f"End of string '\"' expected {got_at()}")

    def raise_object_key_expected():
        raise SyntaxError(f"Quoted object key expected {got_at()}")

    def raise_table_field_expected():
        raise SyntaxError(f"Table field expected {got_at()}")

    def raise_duplicate_key(key: str, position: int):
        raise SyntaxError(f"Duplicate key '{key}' encountered at position {position}")

    def raise_object_key_or_end_expected():
        raise SyntaxError(
            f"Quoted object key or end of object '}}' expected {got_at()}"
        )

    def raise_array_item_or_end_expected():
        raise SyntaxError(f"Array item or end of array ']' expected {got_at()}")

    def raise_table_row_or_end_expected():
        raise SyntaxError(f"Table row or end of table '---' expected {got_at()}")

    def raise_array_item_expected():
        raise SyntaxError(f"Array item expected {got_at()}")

    def raise_value_expected():
        raise SyntaxError(f"Value expected {got_at()}")

    def raise_invalid_character(char: str):
        raise SyntaxError(f"Invalid character '{char}' {pos()}")

    def raise_invalid_escape_character(start: int):
        chars = text[start : start + 2]
        raise SyntaxError(f"Invalid escape character '{chars}' {pos()}")

    def raise_object_value_expected():
        raise SyntaxError(f"Object value expected after ':' {pos()}")

    def raise_invalid_unicode_character(start: int):
        chars = text[start : start + 6]
        raise SyntaxError(f"Invalid unicode character '{chars}' {pos()}")

    def pos() -> str:
        """Zero based character position"""
        return f"at position {i}"

    def got() -> str:
        return (
            f"but got '{text_at(i)}'" if i < len(text) else "but reached end of input"
        )

    def got_at() -> str:
        return f"{got()} {pos()}"

    def text_at(index: int) -> str | None:
        return text[index] if index < len(text) else None

    root_parsed, root_value = parse_root_table()
    if not root_parsed:
        raise_value_expected()

    expect_end_of_input()

    return root_value


def is_whitespace(char: str | None) -> bool:
    return char in set(" \n\t\r")


def is_table_whitespace(char: str | None) -> bool:
    return char in set(" \t\r")


def is_hex(char: str | None) -> bool:
    return char in set("0123456789abcdefABCDEF") if char else False


def is_digit(char: str | None) -> bool:
    return char in set("0123456789")


def is_non_zero_digit(char: str | None) -> bool:
    return char in set("123456789")


def is_valid_string_character(char: str) -> bool:
    code = ord(char)
    return 0x20 <= code <= 0x10FFFF


def create_set_value(keys: list[str]) -> SetValue:
    if len(keys) == 1:
        first = keys[0]

        def set_value(record: Record, value: Any) -> None:
            record[first] = value

        return set_value
    else:

        def set_value(record: Record, value: Any) -> None:
            _ = set_in(record, keys, value)

        return set_value


escape_characters = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    # note that \u is handled separately in parseString()
}
