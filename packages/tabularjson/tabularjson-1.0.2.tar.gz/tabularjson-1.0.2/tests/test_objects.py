import unittest

from tabularjson.objects import get_in, set_in


class ObjectsTestCase(unittest.TestCase):
    def test_get_in(self):
        self.assertEqual(get_in({"name": "Joe"}, ["name"]), ("Joe", True))
        self.assertEqual(get_in({"name": "Joe"}, ["foo"]), (None, False))
        self.assertEqual(
            get_in({"nested": {"name": "Joe"}}, ["nested", "name"]), ("Joe", True)
        )
        self.assertEqual(
            get_in({"nested": {"array": ["a", "b"]}}, ["nested", "array", "1"]),
            ("b", True),
        )
        self.assertEqual(
            get_in({"nested": {"array": ["a", "b"]}}, ["nested", "array", "99"]),
            (None, False),
        )
        self.assertEqual(
            get_in({"nested": {"array": ["a", "b"]}}, ["nested", "foo", "bar"]),
            (None, False),
        )
        self.assertEqual(
            get_in({"nested": None}, ["nested", "foo", "bar"]), (None, False)
        )
        self.assertEqual(get_in({}, ["nested", "foo", "bar"]), (None, False))
        self.assertEqual(
            get_in({"nested": 123}, ["nested", "foo", "bar"]), (None, False)
        )
        self.assertEqual(
            get_in({"nested": True}, ["nested", "foo", "bar"]), (None, False)
        )

    def test_set_in(self):
        self.assertEqual(set_in({}, ["name"], "Joe"), {"name": "Joe"})
        self.assertEqual(
            set_in({}, ["address", "city"], "Rotterdam"),
            {"address": {"city": "Rotterdam"}},
        )

    def test_set_in_array(self):
        self.assertEqual(set_in({}, ["values", 0], 42), {"values": [42]})
