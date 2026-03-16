from analysis.cascade_simulator import CascadeSimulator


def test_cascade_reroutes_flow_when_primary_hub_fails(small_supply_chain_graph):
    simulator = CascadeSimulator(small_supply_chain_graph)

    result = simulator.run_simulation(
        disrupted_nodes=["B"],
        flows=[{"source": "A", "target": "D", "demand": 10}],
        max_steps=5,
    )

    flow_result = result["flow_impacts"][0]

    assert flow_result["status"] == "rerouted"
    assert flow_result["rerouted"] is True
    assert flow_result["baseline_path"] == ["A", "B", "D"]
    assert flow_result["final_path"] == ["A", "C", "D"]
    assert flow_result["baseline_cost"] == 2.0
    assert flow_result["final_cost"] == 4.0
    assert flow_result["cost_increase"] == 2.0


def test_cascade_disrupts_flow_when_all_routes_fail(small_supply_chain_graph):
    simulator = CascadeSimulator(small_supply_chain_graph)

    result = simulator.run_simulation(
        disrupted_nodes=["B", "C"],
        flows=[{"source": "A", "target": "D", "demand": 10}],
        max_steps=5,
    )

    flow_result = result["flow_impacts"][0]

    assert flow_result["status"] == "disrupted"
    assert flow_result["rerouted"] is False
    assert flow_result["baseline_path"] == ["A", "B", "D"]
    assert flow_result["final_path"] is None
    assert flow_result["final_cost"] is None
    assert flow_result["delivered_demand"] == 0.0
    assert flow_result["unmet_demand"] == 10.0
