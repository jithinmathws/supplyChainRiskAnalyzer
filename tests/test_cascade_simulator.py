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
    simulator = CascadeSimulator(
        _build_graph(),
        reroute_cost_rate=1.0,
        delay_penalty_rate=2.0,
        unmet_demand_loss_rate=5.0,
    )

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=[{"source": "A", "target": "D", "demand": 35}],
        max_steps=5,
    )

    flow = result["flow_impacts"][0]
    metrics = result["metrics"]

    assert result["failed_edges"] == [("A", "B")]
    assert result["failed_nodes"] == []
    assert metrics["disrupted_flows"] == 0
    assert metrics["service_level"] == 1.0

    assert flow["status"] == "rerouted"
    assert flow["final_path"] == ["A", "C", "D"]
    assert flow["baseline_path"] == ["A", "B", "D"]
    assert flow["baseline_cost"] == 2.0
    assert flow["final_cost"] == 4.0
    assert flow["cost_increase"] == 2.0

    assert flow["delivered_demand"] == 35.0
    assert flow["unmet_demand"] == 0.0

    assert flow["reroute_cost"] == 70.0
    assert flow["delay_penalty"] == 140.0
    assert flow["unmet_demand_loss"] == 0.0
    assert flow["total_economic_impact"] == 210.0

    assert metrics["total_reroute_cost"] == 70.0
    assert metrics["total_delay_penalty"] == 140.0
    assert metrics["total_unmet_demand_loss"] == 0.0
    assert metrics["total_economic_impact"] == 210.0


def test_overload_causes_cascade_and_unmet_demand():
    simulator = CascadeSimulator(
        _build_graph(),
        reroute_cost_rate=1.0,
        delay_penalty_rate=2.0,
        unmet_demand_loss_rate=5.0,
    )

    result = simulator.run_simulation(
        disrupted_edges=[("A", "B")],
        flows=[{"source": "A", "target": "D", "demand": 45}],
        max_steps=5,
    )

    flow = result["flow_impacts"][0]
    metrics = result["metrics"]

    assert ("A", "B") in result["failed_edges"]
    assert ("A", "C") in result["failed_edges"]
    assert ("C", "D") in result["failed_edges"]

    assert metrics["disrupted_flows"] == 1
    assert metrics["unmet_demand"] == 45.0
    assert metrics["service_level"] == 0.0

    assert flow["status"] == "disrupted"
    assert flow["final_path"] is None
    assert flow["baseline_path"] == ["A", "B", "D"]
    assert flow["baseline_cost"] == 2.0
    assert flow["delivered_demand"] == 0.0
    assert flow["unmet_demand"] == 45.0

    assert flow["reroute_cost"] == 0.0
    assert flow["delay_penalty"] == 0.0
    assert flow["unmet_demand_loss"] == 225.0
    assert flow["total_economic_impact"] == 225.0

    assert metrics["total_reroute_cost"] == 0.0
    assert metrics["total_delay_penalty"] == 0.0
    assert metrics["total_unmet_demand_loss"] == 225.0
    assert metrics["total_economic_impact"] == 225.0
