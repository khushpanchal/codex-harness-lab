# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/affine-cipher/canonical-data.json
# File last updated on 2023-07-20

import unittest

from affine_cipher import (
    decode,
    encode,
)


class AffineCipherTest(unittest.TestCase):
    def test_encode_yes(self):
        self.assertEqual(encode("yes", 5, 7), "xbt")


    def test_encode_omg(self):
        self.assertEqual(encode("OMG", 21, 3), "lvz")


    def test_encode_mindblowingly(self):
        self.assertEqual(encode("mindblowingly", 11, 15), "rzcwa gnxzc dgt")


    def test_encode_deep_thought(self):
        self.assertEqual(encode("Truth is fiction.", 5, 17), "iynia fdqfb ifje")


    def test_encode_with_a_not_coprime_to_m(self):
        with self.assertRaises(ValueError) as err:
            encode("This is a test.", 6, 17)
        self.assertEqual(type(err.exception), ValueError)
        self.assertEqual(err.exception.args[0], "a and m must be coprime.")


    def test_decode_a_sentence(self):
        self.assertEqual(
            decode("qdwju nqcro muwhn odqun oppmd aunwd o", 19, 16),
            "anobstacleisoftenasteppingstone",
        )


    def test_decode_all_the_letters(self):
        self.assertEqual(
            decode("swxtj npvyk lruol iejdc blaxk swxmh qzglf", 17, 33),
            "thequickbrownfoxjumpsoverthelazydog",
        )


    def test_decode_with_too_many_spaces(self):
        self.assertEqual(
            decode("vszzm    cly   yd cg    qdp", 15, 16), "jollygreengiant"
        )

