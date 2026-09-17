# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/poker/canonical-data.json
# File last updated on 2023-12-27

import unittest

from poker import (
    best_hands,
)


class PokerTest(unittest.TestCase):
    def test_single_hand_always_wins(self):
        self.assertEqual(best_hands(["4S 5S 7H 8D JC"]), ["4S 5S 7H 8D JC"])


    def test_a_tie_has_multiple_winners(self):
        self.assertEqual(
            best_hands(
                [
                    "4D 5S 6S 8D 3C",
                    "2S 4C 7S 9H 10H",
                    "3S 4S 5D 6H JH",
                    "3H 4H 5C 6C JD",
                ]
            ),
            ["3S 4S 5D 6H JH", "3H 4H 5C 6C JD"],
        )


    def test_winning_high_card_hand_also_has_the_lowest_card(self):
        self.assertEqual(
            best_hands(["2S 5H 6S 8D 7H", "3S 4D 6D 8C 7S"]), ["2S 5H 6S 8D 7H"]
        )


    def test_highest_pair_wins(self):
        self.assertEqual(
            best_hands(["4S 2H 6S 2D JH", "2S 4H 6C 4D JD"]), ["2S 4H 6C 4D JD"]
        )


    def test_two_pairs_beats_one_pair(self):
        self.assertEqual(
            best_hands(["2S 8H 6S 8D JH", "4S 5H 4C 8C 5C"]), ["4S 5H 4C 8C 5C"]
        )


    def test_both_hands_have_two_pairs_with_the_same_highest_ranked_pair_tie_goes_to_low_pair(
        self,
    ):
        self.assertEqual(
            best_hands(["2S QS 2C QD JH", "JD QH JS 8D QC"]), ["JD QH JS 8D QC"]
        )


    def test_both_hands_have_two_pairs_that_add_to_the_same_value_win_goes_to_highest_pair(
        self,
    ):
        self.assertEqual(
            best_hands(["6S 6H 3S 3H AS", "7H 7S 2H 2S AC"]), ["7H 7S 2H 2S AC"]
        )


    def test_three_of_a_kind_beats_two_pair(self):
        self.assertEqual(
            best_hands(["2S 8H 2H 8D JH", "4S 5H 4C 8S 4H"]), ["4S 5H 4C 8S 4H"]
        )


    def test_with_multiple_decks_two_players_can_have_same_three_of_a_kind_ties_go_to_highest_remaining_cards(
        self,
    ):
        self.assertEqual(
            best_hands(["5S AH AS 7C AD", "4S AH AS 8C AD"]), ["4S AH AS 8C AD"]
        )


    def test_aces_can_end_a_straight_10_j_q_k_a(self):
        self.assertEqual(
            best_hands(["4S 5H 4C 8D 4H", "10D JH QS KD AC"]), ["10D JH QS KD AC"]
        )


    def test_aces_cannot_be_in_the_middle_of_a_straight_q_k_a_2_3(self):
        self.assertEqual(
            best_hands(["2C 3D 7H 5H 2S", "QS KH AC 2D 3S"]), ["2C 3D 7H 5H 2S"]
        )


    def test_even_though_an_ace_is_usually_high_a_5_high_straight_is_the_lowest_scoring_straight(
        self,
    ):
        self.assertEqual(
            best_hands(["2H 3C 4D 5D 6H", "4S AH 3S 2D 5H"]), ["2H 3C 4D 5D 6H"]
        )


    def test_both_hands_have_a_flush_tie_goes_to_high_card_down_to_the_last_one_if_necessary(
        self,
    ):
        self.assertEqual(
            best_hands(["2H 7H 8H 9H 6H", "3S 5S 6S 7S 8S"]), ["2H 7H 8H 9H 6H"]
        )


    def test_both_hands_have_a_full_house_tie_goes_to_highest_ranked_triplet(self):
        self.assertEqual(
            best_hands(["4H 4S 4D 9S 9D", "5H 5S 5D 8S 8D"]), ["5H 5S 5D 8S 8D"]
        )


    def test_four_of_a_kind_beats_a_full_house(self):
        self.assertEqual(
            best_hands(["4S 5H 4D 5D 4H", "3S 3H 2S 3D 3C"]), ["3S 3H 2S 3D 3C"]
        )


    def test_with_multiple_decks_both_hands_with_identical_four_of_a_kind_tie_determined_by_kicker(
        self,
    ):
        self.assertEqual(
            best_hands(["3S 3H 2S 3D 3C", "3S 3H 4S 3D 3C"]), ["3S 3H 4S 3D 3C"]
        )


    def test_aces_can_end_a_straight_flush_10_j_q_k_a(self):
        self.assertEqual(
            best_hands(["KC AH AS AD AC", "10C JC QC KC AC"]), ["10C JC QC KC AC"]
        )


    def test_aces_cannot_be_in_the_middle_of_a_straight_flush_q_k_a_2_3(self):
        self.assertEqual(
            best_hands(["2C AC QC 10C KC", "QH KH AH 2H 3H"]), ["2C AC QC 10C KC"]
        )


    def test_even_though_an_ace_is_usually_high_a_5_high_straight_flush_is_the_lowest_scoring_straight_flush(
        self,
    ):
        self.assertEqual(
            best_hands(["2H 3H 4H 5H 6H", "4D AD 3D 2D 5D"]), ["2H 3H 4H 5H 6H"]
        )
