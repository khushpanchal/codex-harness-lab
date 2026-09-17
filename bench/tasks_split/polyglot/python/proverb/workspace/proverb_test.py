# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/proverb/canonical-data.json
# File last updated on 2023-07-19

import unittest

from proverb import (
    proverb,
)

# PLEASE TAKE NOTE: Expected result lists for these test cases use **implicit line joining.**
# A new line in a result list below **does not** always equal a new list element.
# Check comma placement carefully!


class ProverbTest(unittest.TestCase):
    def test_zero_pieces(self):
        input_data = []
        self.assertEqual(proverb(*input_data, qualifier=None), [])


    def test_two_pieces(self):
        input_data = ["nail", "shoe"]
        self.assertEqual(
            proverb(*input_data, qualifier=None),
            [
                "For want of a nail the shoe was lost.",
                "And all for the want of a nail.",
            ],
        )


    def test_full_proverb(self):
        input_data = ["nail", "shoe", "horse", "rider", "message", "battle", "kingdom"]
        self.assertEqual(
            proverb(*input_data, qualifier=None),
            [
                "For want of a nail the shoe was lost.",
                "For want of a shoe the horse was lost.",
                "For want of a horse the rider was lost.",
                "For want of a rider the message was lost.",
                "For want of a message the battle was lost.",
                "For want of a battle the kingdom was lost.",
                "And all for the want of a nail.",
            ],
        )


    # Track-specific tests

    def test_an_optional_qualifier_can_be_added(self):
        input_data = ["nail"]
        self.assertEqual(
            proverb(*input_data, qualifier="horseshoe"),
            ["And all for the want of a horseshoe nail."],
        )

