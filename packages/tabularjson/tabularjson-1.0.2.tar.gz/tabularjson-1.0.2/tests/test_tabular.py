import json
import unittest
from os import path

from tabularjson.tabular import collect_fields, is_tabular


class TabularTestCase(unittest.TestCase):
    def test_suite(self):
        """Run the official stringify test-suite"""
        test_suite_file = (
            path.dirname(path.realpath(__file__)) + "/test-suite/tabular.test.json"
        )

        with open(test_suite_file, "r", encoding="utf-8") as read_file:
            suite = json.load(read_file)

            for group in suite["groups"]:
                for test in group["tests"]:
                    message = (
                        f"{group['function']}({test['input']}) == {test['output']}"
                    )

                    with self.subTest(message=message):
                        match group["function"]:
                            case "isTabular":
                                self.assertEqual(
                                    is_tabular(test["input"]), test["output"]
                                )
                            case "collectFields":
                                self.assertEqual(
                                    collect_fields(test["input"]), test["output"]
                                )
                            case _:
                                raise TypeError(
                                    f'Unknown function "{group["function"]}"'
                                )
