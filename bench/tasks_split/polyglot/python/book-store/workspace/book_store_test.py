# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/book-store/canonical-data.json
# File last updated on 2023-07-20

import unittest

from book_store import (
    total,
)


class BookStoreTest(unittest.TestCase):
    def test_only_a_single_book(self):
        basket = [1]
        self.assertEqual(total(basket), 800)


    def test_empty_basket(self):
        basket = []
        self.assertEqual(total(basket), 0)


    def test_three_different_books(self):
        basket = [1, 2, 3]
        self.assertEqual(total(basket), 2160)


    def test_five_different_books(self):
        basket = [1, 2, 3, 4, 5]
        self.assertEqual(total(basket), 3000)


    def test_two_groups_of_four_is_cheaper_than_groups_of_five_and_three(self):
        basket = [1, 1, 2, 3, 4, 4, 5, 5]
        self.assertEqual(total(basket), 5120)


    def test_two_each_of_first_four_books_and_one_copy_each_of_rest(self):
        basket = [1, 1, 2, 2, 3, 3, 4, 4, 5]
        self.assertEqual(total(basket), 5560)


    def test_three_copies_of_first_book_and_two_each_of_remaining(self):
        basket = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 1]
        self.assertEqual(total(basket), 6800)


    def test_four_groups_of_four_are_cheaper_than_two_groups_each_of_five_and_three(
        self,
    ):
        basket = [1, 1, 2, 2, 3, 3, 4, 5, 1, 1, 2, 2, 3, 3, 4, 5]
        self.assertEqual(total(basket), 10240)


    def test_one_group_of_one_and_four_is_cheaper_than_one_group_of_two_and_three(self):
        basket = [1, 1, 2, 3, 4]
        self.assertEqual(total(basket), 3360)


    # Additional tests for this track

    def test_two_groups_of_four_and_a_group_of_five(self):
        basket = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5]
        self.assertEqual(total(basket), 8120)

