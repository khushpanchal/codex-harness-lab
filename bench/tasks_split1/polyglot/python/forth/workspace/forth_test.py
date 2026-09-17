# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/forth/canonical-data.json
# File last updated on 2024-11-04

import unittest

from forth import (
    evaluate,
    StackUnderflowError,
)


class ForthTest(unittest.TestCase):
    def test_parsing_and_numbers_numbers_just_get_pushed_onto_the_stack(self):
        self.assertEqual(evaluate(["1 2 3 4 5"]), [1, 2, 3, 4, 5])





















































