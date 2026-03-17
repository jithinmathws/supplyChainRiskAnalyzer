import networkx as nx
import pandas as pd
import pytest

from app.services.analysis_service import run_baseline_analysis
from app.services.graph_service import get_node_options, load_graph


def test_run_baseline_analysis_returns_expected_keys():
    graph = load_graph()
    node_options = get_node_options(graph)

    node_ids = list(node_options.values())
    assert len(node_ids) >= 2

    reachable_pair = None
    for origin_id in node_ids:
        for destination_id in node_ids:
            if origin_id == destination_id:
                continue
            if nx.has_path(graph, str(origin_id), str(destination_id)):
                reachable_pair = (str(origin_id), str(destination_id))
                break
        if reachable_pair is not None:
            break

    assert reachable_pair is not None, "No reachable origin-destination pair found in graph."

    origin_id, destination_id = reachable_pair
    result = run_baseline_analysis(graph, origin_id, destination_id)

    assert isinstance(result, dict)
    assert "baseline_route_ids" in result
    assert "baseline_route_names" in result
    assert "baseline_time" in result
    assert "node_result_df" in result
    assert "edge_result_df" in result


def test_run_baseline_analysis_raises_for_no_path():
    graph = nx.MultiDiGraph()
    graph.add_node("A", name="A", type="supplier", location="Loc A", capacity=100)
    graph.add_node("B", name="B", type="customer", location="Loc B", capacity=100)

    with pytest.raises(ValueError, match="No valid baseline route exists"):
        run_baseline_analysis(graph, "A", "B")


def test_baseline_route_uses_expected_path(small_supply_chain_graph):
    result = run_baseline_analysis(small_supply_chain_graph, "A", "D")

    assert result["baseline_route_ids"] == ["A", "B", "D"]
    assert result["baseline_route_names"] == ["Supplier A", "Hub B", "Customer D"]
    assert result["baseline_time"] == 2
    assert isinstance(result["node_result_df"], pd.DataFrame)
    assert isinstance(result["edge_result_df"], pd.DataFrame)
