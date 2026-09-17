import unittest

from dot_dsl import Graph, Node, Edge, NODE, EDGE, ATTR


class DotDslTest(unittest.TestCase):
    def test_empty_graph(self):
        g = Graph()

        self.assertEqual(g.nodes, [])
        self.assertEqual(g.edges, [])
        self.assertEqual(g.attrs, {})


    def test_graph_with_one_node_with_keywords(self):
        g = Graph([
            (NODE, "a", {"color": "green"})
        ])

        self.assertEqual(g.nodes, [Node("a", {"color": "green"})])
        self.assertEqual(g.edges, [])
        self.assertEqual(g.attrs, {})


    def test_graph_with_one_attribute(self):
        g = Graph([
            (ATTR, "foo", "1")
        ])

        self.assertEqual(g.nodes, [])
        self.assertEqual(g.edges, [])
        self.assertEqual(g.attrs, {"foo": "1"})


    def test_malformed_graph(self):
        with self.assertRaises(TypeError) as err:
            Graph(1)
        self.assertEqual(type(err.exception), TypeError)
        self.assertEqual(err.exception.args[0], "Graph data malformed")

        with self.assertRaises(TypeError) as err:
            Graph("problematic")
        self.assertEqual(type(err.exception), TypeError)
        self.assertEqual(err.exception.args[0], "Graph data malformed")



    def test_malformed_attr(self):
        with self.assertRaises(ValueError) as err:
            Graph([(ATTR, 1, 2, 3)])
        self.assertEqual(type(err.exception), ValueError)
        self.assertEqual(err.exception.args[0], "Attribute is malformed")




    def test_malformed_EDGE(self):
        with self.assertRaises(ValueError) as err:
            Graph([(EDGE, 1, 2)])
        self.assertEqual(type(err.exception), ValueError)
        self.assertEqual(err.exception.args[0], "Edge is malformed")

