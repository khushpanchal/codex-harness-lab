# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/pov/canonical-data.json
# File last updated on 2023-07-19

import unittest

from pov import (
    Tree,
)


class PovTest(unittest.TestCase):
    def test_results_in_the_same_tree_if_the_input_tree_is_a_singleton(self):
        tree = Tree("x")
        expected = Tree("x")
        self.assertTreeEquals(tree.from_pov("x"), expected)


    def test_can_reroot_a_tree_with_a_parent_and_many_siblings(self):
        tree = Tree("parent", [Tree("a"), Tree("x"), Tree("b"), Tree("c")])
        expected = Tree("x", [Tree("parent", [Tree("a"), Tree("b"), Tree("c")])])
        self.assertTreeEquals(tree.from_pov("x"), expected)


    def test_moves_children_of_the_new_root_to_same_level_as_former_parent(self):
        tree = Tree("parent", [Tree("x", [Tree("kid-0"), Tree("kid-1")])])
        expected = Tree("x", [Tree("kid-0"), Tree("kid-1"), Tree("parent")])
        self.assertTreeEquals(tree.from_pov("x"), expected)


    def test_errors_if_target_does_not_exist_in_a_singleton_tree(self):
        tree = Tree("x")
        with self.assertRaises(ValueError) as err:
            tree.from_pov("nonexistent")
        self.assertEqual(type(err.exception), ValueError)
        self.assertEqual(err.exception.args[0], "Tree could not be reoriented")


    def test_can_find_path_to_parent(self):
        tree = Tree("parent", [Tree("x"), Tree("sibling")])
        expected = ["x", "parent"]
        self.assertEqual(tree.path_to("x", "parent"), expected)


    def test_can_find_path_to_cousin(self):
        tree = Tree(
            "grandparent",
            [
                Tree(
                    "parent",
                    [
                        Tree("x", [Tree("kid-0"), Tree("kid-1")]),
                        Tree("sibling-0"),
                        Tree("sibling-1"),
                    ],
                ),
                Tree("uncle", [Tree("cousin-0"), Tree("cousin-1")]),
            ],
        )
        expected = ["x", "parent", "grandparent", "uncle", "cousin-1"]
        self.assertEqual(tree.path_to("x", "cousin-1"), expected)


    def test_can_find_path_from_nodes_other_than_x(self):
        tree = Tree("parent", [Tree("a"), Tree("x"), Tree("b"), Tree("c")])
        expected = ["a", "parent", "c"]
        self.assertEqual(tree.path_to("a", "c"), expected)


    def test_errors_if_source_does_not_exist(self):
        tree = Tree(
            "parent",
            [
                Tree("x", [Tree("kid-0"), Tree("kid-1")]),
                Tree("sibling-0"),
                Tree("sibling-1"),
            ],
        )
        with self.assertRaises(ValueError) as err:
            tree.path_to("nonexistent", "x")
        self.assertEqual(type(err.exception), ValueError)

        self.assertEqual(err.exception.args[0], "Tree could not be reoriented")

    # Custom Utility Functions
    def assertTreeEquals(self, result, expected):
        self.assertEqual(result, expected, "{} != {}".format(result, expected))
