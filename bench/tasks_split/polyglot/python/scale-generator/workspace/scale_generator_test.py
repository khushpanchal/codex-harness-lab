# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/scale-generator/canonical-data.json
# File last updated on 2023-07-19

import unittest

from scale_generator import (
    Scale,
)


class ScaleGeneratorTest(unittest.TestCase):

    # Test chromatic scales
    def test_chromatic_scale_with_sharps(self):
        expected = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.assertEqual(Scale("C").chromatic(), expected)


    # Test scales with specified intervals
    def test_simple_major_scale(self):
        expected = ["C", "D", "E", "F", "G", "A", "B", "C"]
        self.assertEqual(Scale("C").interval("MMmMMMm"), expected)


    def test_major_scale_with_flats(self):
        expected = ["F", "G", "A", "Bb", "C", "D", "E", "F"]
        self.assertEqual(Scale("F").interval("MMmMMMm"), expected)


    def test_minor_scale_with_flats(self):
        expected = ["Bb", "C", "Db", "Eb", "F", "Gb", "Ab", "Bb"]
        self.assertEqual(Scale("bb").interval("MmMMmMM"), expected)


    def test_mixolydian_mode(self):
        expected = ["Eb", "F", "G", "Ab", "Bb", "C", "Db", "Eb"]
        self.assertEqual(Scale("Eb").interval("MMmMMmM"), expected)


    def test_phrygian_mode(self):
        expected = ["E", "F", "G", "A", "B", "C", "D", "E"]
        self.assertEqual(Scale("e").interval("mMMMmMM"), expected)


    def test_harmonic_minor(self):
        expected = ["D", "E", "F", "G", "A", "Bb", "Db", "D"]
        self.assertEqual(Scale("d").interval("MmMMmAm"), expected)


    def test_hexatonic(self):
        expected = ["Db", "Eb", "F", "G", "A", "B", "Db"]
        self.assertEqual(Scale("Db").interval("MMMMMM"), expected)


    def test_enigmatic(self):
        expected = ["G", "G#", "B", "C#", "D#", "F", "F#", "G"]
        self.assertEqual(Scale("G").interval("mAMMMmm"), expected)
