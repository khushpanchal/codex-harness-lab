# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/two-bucket/canonical-data.json
# File last updated on 2023-07-21

import unittest

from two_bucket import (
    measure,
)


class TwoBucketTest(unittest.TestCase):
    def test_measure_using_bucket_one_of_size_3_and_bucket_two_of_size_5_start_with_bucket_one(
        self,
    ):
        self.assertEqual(measure(3, 5, 1, "one"), (4, "one", 5))


    def test_measure_using_bucket_one_of_size_7_and_bucket_two_of_size_11_start_with_bucket_one(
        self,
    ):
        self.assertEqual(measure(7, 11, 2, "one"), (14, "one", 11))


    def test_measure_one_step_using_bucket_one_of_size_1_and_bucket_two_of_size_3_start_with_bucket_two(
        self,
    ):
        self.assertEqual(measure(1, 3, 3, "two"), (1, "two", 0))


    def test_not_possible_to_reach_the_goal(self):
        with self.assertRaisesWithMessage(ValueError):
            measure(6, 15, 5, "one")


    def test_goal_larger_than_both_buckets_is_impossible(self):
        with self.assertRaisesWithMessage(ValueError):
            measure(5, 7, 8, "one")

    # Utility functions
    def assertRaisesWithMessage(self, exception):
        return self.assertRaisesRegex(exception, r".+")
