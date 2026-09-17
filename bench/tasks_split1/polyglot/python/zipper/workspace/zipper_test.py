# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/zipper/canonical-data.json
# File last updated on 2023-07-19

import unittest

from zipper import (
    Zipper,
)


class ZipperTest(unittest.TestCase):
    def test_data_is_retained(self):
        initial = {
            "value": 1,
            "left": {
                "value": 2,
                "left": None,
                "right": {"value": 3, "left": None, "right": None},
            },
            "right": {"value": 4, "left": None, "right": None},
        }

        expected = {
            "value": 1,
            "left": {
                "value": 2,
                "left": None,
                "right": {"value": 3, "left": None, "right": None},
            },
            "right": {"value": 4, "left": None, "right": None},
        }

        zipper = Zipper.from_tree(initial)
        result = zipper.to_tree()
        self.assertEqual(result, expected)













