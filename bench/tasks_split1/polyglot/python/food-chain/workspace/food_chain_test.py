# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/food-chain/canonical-data.json
# File last updated on 2023-07-19

import unittest

from food_chain import (
    recite,
)


class FoodChainTest(unittest.TestCase):
    def test_fly(self):
        self.assertEqual(
            recite(1, 1),
            [
                "I know an old lady who swallowed a fly.",
                "I don't know why she swallowed the fly. Perhaps she'll die.",
            ],
        )









