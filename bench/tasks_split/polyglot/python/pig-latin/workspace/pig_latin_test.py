# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/pig-latin/canonical-data.json
# File last updated on 2023-07-19

import unittest

from pig_latin import (
    translate,
)


class PigLatinTest(unittest.TestCase):
    def test_word_beginning_with_a(self):
        self.assertEqual(translate("apple"), "appleay")


    def test_word_beginning_with_i(self):
        self.assertEqual(translate("igloo"), "iglooay")


    def test_word_beginning_with_u(self):
        self.assertEqual(translate("under"), "underay")


    def test_word_beginning_with_p(self):
        self.assertEqual(translate("pig"), "igpay")


    def test_word_beginning_with_x(self):
        self.assertEqual(translate("xenon"), "enonxay")


    def test_word_beginning_with_ch(self):
        self.assertEqual(translate("chair"), "airchay")


    def test_word_beginning_with_qu_and_a_preceding_consonant(self):
        self.assertEqual(translate("square"), "aresquay")


    def test_word_beginning_with_thr(self):
        self.assertEqual(translate("thrush"), "ushthray")


    def test_word_beginning_with_yt(self):
        self.assertEqual(translate("yttria"), "yttriaay")


    def test_y_is_treated_like_a_consonant_at_the_beginning_of_a_word(self):
        self.assertEqual(translate("yellow"), "ellowyay")


    def test_y_as_second_letter_in_two_letter_word(self):
        self.assertEqual(translate("my"), "ymay")

