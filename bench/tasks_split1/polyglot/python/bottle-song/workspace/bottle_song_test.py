# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/bottle-song/canonical-data.json
# File last updated on 2023-07-20

import unittest

from bottle_song import (
    recite,
)


class BottleSongTest(unittest.TestCase):
    def test_first_generic_verse(self):
        expected = [
            "Ten green bottles hanging on the wall,",
            "Ten green bottles hanging on the wall,",
            "And if one green bottle should accidentally fall,",
            "There'll be nine green bottles hanging on the wall.",
        ]
        self.assertEqual(recite(start=10), expected)






