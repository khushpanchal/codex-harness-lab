# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/transpose/canonical-data.json
# File last updated on 2024-08-26

import unittest

from transpose import (
    transpose,
)


class TransposeTest(unittest.TestCase):
    def test_empty_string(self):
        text = ""
        expected = ""

        self.assertEqual(transpose(text), expected)


    def test_two_characters_in_a_column(self):
        text = "A\n1"
        expected = "A1"

        self.assertEqual(transpose(text), expected)


    def test_single_line(self):
        text = "Single line."
        expected = "S\ni\nn\ng\nl\ne\n \nl\ni\nn\ne\n."

        self.assertEqual(transpose(text), expected)


    def test_second_line_longer_than_first_line(self):
        text = "The first line.\nThe second line."
        expected = "TT\nhh\nee\n  \nfs\nie\nrc\nso\ntn\n d\nl \nil\nni\nen\n.e\n ."

        self.assertEqual(transpose(text), expected)


    def test_square(self):
        text = "HEART\nEMBER\nABUSE\nRESIN\nTREND"
        expected = "HEART\nEMBER\nABUSE\nRESIN\nTREND"

        self.assertEqual(transpose(text), expected)


    def test_triangle(self):
        text = "T\nEE\nAAA\nSSSS\nEEEEE\nRRRRRR"
        expected = "TEASER\n EASER\n  ASER\n   SER\n    ER\n     R"

        self.assertEqual(transpose(text), expected)

