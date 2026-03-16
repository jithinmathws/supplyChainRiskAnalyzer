import networkx as nx

from app.services.graph_service import get_graph_signature, get_node_options, load_graph


def test_load_graph_returns_directed_graph():
    graph = load_graph()

    assert graph is not None
    assert isinstance(graph, (nx.DiGraph, nx.MultiDiGraph))
    assert graph.is_directed()
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0


def test_node_options_are_non_empty():
    graph = load_graph()
    node_options = get_node_options(graph)

    assert isinstance(node_options, dict)
    assert len(node_options) > 0

    first_label, first_node_id = next(iter(node_options.items()))
    assert isinstance(first_label, str)
    assert first_label != ""
    assert first_node_id is not None


def test_graph_signature_is_stable_for_same_graph():
    graph = load_graph()

    sig1 = get_graph_signature(graph)
    sig2 = get_graph_signature(graph)

    assert sig1 == sig2
