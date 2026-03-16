import networkx as nx

from analysis.cascade_simulator import CascadeSimulator


def _build_graph():
    graph = nx.DiGraph()
    graph.add_edge("A", "B", capacity=50, weight=1)
    graph.add_edge("B", "D", capacity=50, weight=1)
    graph.add_edge("A", "C", capacity=40, weight=2)
    graph.add_edge("C", "D", capacity=40, weight=2)
    return graph


def test_disrupted_edge_reroutes_flow_without_failures():
    simulator = CascadeSimulator(_build_graph())

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=[{"source": "A", "target": "D", "demand": 35}],
        max_steps=5,
    )

    flow = result["flow_impacts"][0]

    assert result["failed_edges"] == [("A", "B")]
    assert result["failed_nodes"] == []
    assert result["metrics"]["disrupted_flows"] == 0
    assert result["metrics"]["service_level"] == 1.0
    assert flow["status"] == "rerouted"
    assert flow["final_path"] == ["A", "C", "D"]


def test_overload_causes_cascade_and_unmet_demand():
    simulator = CascadeSimulator(_build_graph())

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=[{"source": "A", "target": "D", "demand": 45}],
        max_steps=5,
    )

    flow = result["flow_impacts"][0]

    assert ("A", "B") in result["failed_edges"]
    assert ("A", "C") in result["failed_edges"]
    assert ("C", "D") in result["failed_edges"]
    assert result["metrics"]["disrupted_flows"] == 1
    assert result["metrics"]["unmet_demand"] == 45.0
    assert result["metrics"]["service_level"] == 0.0
    assert flow["status"] == "disrupted"
    assert flow["final_path"] is None
