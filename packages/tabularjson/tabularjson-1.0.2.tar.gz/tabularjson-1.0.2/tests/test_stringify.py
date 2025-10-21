import json
import math
import unittest
from os import path

from tabularjson import stringify, StringifyOptions


class StringifyTestCase(unittest.TestCase):
    def test_suite(self):
        """Run the official stringify test-suite"""
        test_suite_file = (
            path.dirname(path.realpath(__file__)) + "/test-suite/stringify.test.json"
        )

        with open(test_suite_file, "r", encoding="utf-8") as read_file:
            suite = json.load(read_file)

            for group in suite["groups"]:
                options = (
                    to_stringify_options(group["options"])
                    if "options" in group
                    else None
                )

                for test in group["tests"]:
                    if "input_enum" in test:
                        message = f"[{group['category']}] {group['description']} (input_enum: {test['input_enum']})"
                        with self.subTest(message=message):
                            match test["input_enum"]:
                                case "negative_zero":
                                    self.assertEqual(
                                        stringify(-0, options), test["output"]
                                    )
                                case "positive_infinity":
                                    self.assertEqual(
                                        stringify(math.inf, options),
                                        test["output"],
                                    )
                                case "negative_infinity":
                                    self.assertEqual(
                                        stringify(-math.inf, options),
                                        test["output"],
                                    )
                                case "not_a_number":
                                    nan = math.inf - math.inf
                                    self.assertEqual(
                                        stringify(nan, options), test["output"]
                                    )
                                case _:
                                    raise SyntaxError(
                                        'Unknown input_enum value "'
                                        + test["input_enum"]
                                        + '"'
                                    )
                    else:
                        message = f"[{group['category']}] {group['description']} (input: {test['input']})"
                        with self.subTest(message=message):
                            self.assertEqual(
                                stringify(test["input"], options), test["output"]
                            )


if __name__ == "__main__":
    unittest.main()


def to_stringify_options(javascript_options) -> StringifyOptions:
    return {
        "indentation": javascript_options.get("indentation", None),
        "trailingCommas": javascript_options.get("trailingCommas", None),
    }
