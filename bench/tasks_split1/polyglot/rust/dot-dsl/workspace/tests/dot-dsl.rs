use std::collections::HashMap;

use dot_dsl::graph::graph_items::edge::Edge;
use dot_dsl::graph::graph_items::node::Node;
use dot_dsl::graph::Graph;

#[test]
fn empty_graph() {
    let graph = Graph::new();

    assert!(graph.nodes.is_empty());

    assert!(graph.edges.is_empty());

    assert!(graph.attrs.is_empty());
}

