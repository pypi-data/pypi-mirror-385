import json
import math
import re
import unittest
from os import path

from tabularjson import parse


class ParseTestCase(unittest.TestCase):
    def test_suite(self):
        """Run the official parse test-suite"""

        test_suite_file = (
            path.dirname(path.realpath(__file__)) + "/test-suite/parse.test.json"
        )

        with open(test_suite_file, "r", encoding="utf-8") as read_file:
            suite = json.load(read_file)

            for group in suite["groups"]:
                for test in group["tests"]:
                    message = f"[{group['category']}] {group['description']} (input: {test['input']})"

                    if "output" in test:
                        with self.subTest(message=message):
                            self.assertEqual(parse(test["input"]), test["output"])
                    elif "output_enum" in test:
                        with self.subTest(message=message):
                            match test["output_enum"]:
                                case "negative_zero":
                                    self.assertEqual(parse(test["input"]), -0)
                                case "positive_infinity":
                                    self.assertEqual(parse(test["input"]), float("inf"))
                                case "negative_infinity":
                                    self.assertEqual(
                                        parse(test["input"]), float("-inf")
                                    )
                                case "not_a_number":
                                    self.assertTrue(math.isnan(parse(test["input"])))
                                case _:
                                    raise SyntaxError(
                                        'Unknown output_num value "'
                                        + test["output_enum"]
                                        + '"'
                                    )
                    else:
                        with self.subTest(message=message):
                            self.assertRaisesRegex(
                                SyntaxError,
                                re.escape(test["throws"]),
                                lambda: print("output: ", parse(test["input"])),
                            )


if __name__ == "__main__":
    unittest.main()
