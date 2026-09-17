import unittest

from tree_building import Record, BuildTree


class TreeBuildingTest(unittest.TestCase):
    """
        Record(record_id, parent_id): records given to be processed
        Node(node_id): Node in tree
        BuildTree(records): records as argument and returns tree
        BuildTree should raise ValueError if given records are invalid
    """

    def test_empty_list_input(self):
        records = []
        root = BuildTree(records)
        self.assertIsNone(root)













    def assert_node_is_branch(self, node, node_id, children_count):
        self.assertEqual(node.node_id, node_id)
        self.assertNotEqual(len(node.children), 0)
        self.assertEqual(len(node.children), children_count)

    def assert_node_is_leaf(self, node, node_id):
        self.assertEqual(node.node_id, node_id)
        self.assertEqual(len(node.children), 0)
