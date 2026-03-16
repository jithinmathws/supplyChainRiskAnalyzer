import networkx as nx

from analysis.cascade_simulator import CascadeSimulator


def build_test_graph():
    graph = nx.DiGraph()

    # Main route
    graph.add_edge("A", "B", capacity=50, weight=1)
    graph.add_edge("B", "D", capacity=50, weight=1)

    # Alternate route
    graph.add_edge("A", "C", capacity=40, weight=2)
    graph.add_edge("C", "D", capacity=40, weight=2)

    return graph


def test_cascade_simulation_overload_failure():
    graph = build_test_graph()

    flows = [
        {"source": "A", "target": "D", "demand": 45},
    ]

    simulator = CascadeSimulator(graph)

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=flows,
        max_steps=5,
    )

    assert "timeline" in result
    assert "metrics" in result
    assert "flow_impacts" in result

    # After disrupting A->B, flow reroutes via A->C->D and overloads both edges
    failed_edges = set(result["failed_edges"])
    assert ("A", "B") in failed_edges
    assert ("A", "C") in failed_edges
    assert ("C", "D") in failed_edges

    metrics = result["metrics"]
    assert metrics["total_flows"] == 1
    assert metrics["disrupted_flows"] == 1
    assert metrics["delivered_demand"] == 0.0
    assert metrics["unmet_demand"] == 45.0
    assert metrics["service_level"] == 0.0


def test_flow_impact_tracking_for_disrupted_flow():
    graph = build_test_graph()

    flows = [
        {"source": "A", "target": "D", "demand": 45},
    ]

    simulator = CascadeSimulator(graph)

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=flows,
        max_steps=5,
    )

    flow_impacts = result["flow_impacts"]
    assert len(flow_impacts) == 1

    row = flow_impacts[0]
    assert row["source"] == "A"
    assert row["target"] == "D"
    assert row["status"] == "disrupted"
    assert row["baseline_path"] == ["A", "B", "D"]
    assert row["final_path"] is None
    assert row["delivered_demand"] == 0.0
    assert row["unmet_demand"] == 45.0


def test_step_metrics_table_is_consistent():
    graph = build_test_graph()

    flows = [
        {"source": "A", "target": "D", "demand": 45},
    ]

    simulator = CascadeSimulator(graph)

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=flows,
        max_steps=5,
    )

    rows = simulator.get_step_metrics_table(result)

    assert len(rows) >= 1
    assert "step" in rows[0]
    assert "routed_flow_count" in rows[0]
    assert "disrupted_flow_count" in rows[0]
    assert "routed_demand" in rows[0]
    assert "disrupted_demand" in rows[0]


def build_reroute_success_graph():
    graph = nx.DiGraph()

    graph.add_edge("A", "B", capacity=100, weight=1)
    graph.add_edge("B", "D", capacity=100, weight=1)

    graph.add_edge("A", "C", capacity=100, weight=2)
    graph.add_edge("C", "D", capacity=100, weight=2)

    return graph


def test_flow_impact_tracking_for_rerouted_flow():
    graph = build_reroute_success_graph()

    flows = [
        {"source": "A", "target": "D", "demand": 45},
    ]

    simulator = CascadeSimulator(graph)

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=flows,
        max_steps=5,
    )

    row = result["flow_impacts"][0]

    assert row["status"] == "rerouted"
    assert row["rerouted"] is True
    assert row["baseline_path"] == ["A", "B", "D"]
    assert row["final_path"] == ["A", "C", "D"]
    assert row["delivered_demand"] == 45.0
    assert row["unmet_demand"] == 0.0
    assert row["cost_increase"] == 2.0
    assert row["hop_increase"] == 0
