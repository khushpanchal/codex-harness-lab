# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/beer-song/canonical-data.json
# File last updated on 2023-07-20

import unittest

from beer_song import (
    recite,
)


class BeerSongTest(unittest.TestCase):
    def test_first_generic_verse(self):
        expected = [
            "99 bottles of beer on the wall, 99 bottles of beer.",
            "Take one down and pass it around, 98 bottles of beer on the wall.",
        ]
        self.assertEqual(recite(start=99), expected)







