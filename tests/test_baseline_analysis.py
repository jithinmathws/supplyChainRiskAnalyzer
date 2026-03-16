import networkx as nx
import pytest

from app.services.analysis_service import run_baseline_analysis
from app.services.graph_service import get_node_options, load_graph


def test_run_baseline_analysis_returns_expected_keys():
    graph = load_graph()
    node_options = get_node_options(graph)

    node_ids = list(node_options.values())
    assert len(node_ids) >= 2

    origin_id = node_ids[0]
    destination_id = node_ids[1]

    if origin_id == destination_id and len(node_ids) > 2:
        destination_id = node_ids[2]

    result = run_baseline_analysis(graph, origin_id, destination_id)

    assert isinstance(result, dict)
    assert "baseline_route_ids" in result
    assert "baseline_route_names" in result
    assert "baseline_time" in result
    assert "node_result_df" in result
    assert "edge_result_df" in result


def test_run_baseline_analysis_raises_for_no_path():
    """
    This is a more valuable test than same-origin testing.

    We construct a disconnected graph and verify
    the service raises for no available route.
    """
    graph = nx.DiGraph()
    graph.add_node("A", name="A")
    graph.add_node("B", name="B")

    with pytest.raises(ValueError):
        run_baseline_analysis(graph, "A", "B")
