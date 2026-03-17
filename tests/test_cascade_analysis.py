from analysis.cascade_simulator import CascadeSimulator


def test_cascade_reroutes_flow_when_primary_hub_fails(small_supply_chain_graph):
    simulator = CascadeSimulator(
        small_supply_chain_graph,
        reroute_cost_rate=1.0,
        delay_penalty_rate=2.0,
        unmet_demand_loss_rate=5.0,
    )

    result = simulator.run_simulation(
        disrupted_nodes=["B"],
        flows=[{"source": "A", "target": "D", "demand": 10}],
        max_steps=5,
    )

    flow_result = result["flow_impacts"][0]
    metrics = result["metrics"]

    assert flow_result["status"] == "rerouted"
    assert flow_result["rerouted"] is True
    assert flow_result["baseline_path"] == ["A", "B", "D"]
    assert flow_result["final_path"] == ["A", "C", "D"]
    assert flow_result["baseline_cost"] == 2.0
    assert flow_result["final_cost"] == 4.0
    assert flow_result["cost_increase"] == 2.0
    assert flow_result["delivered_demand"] == 10.0
    assert flow_result["unmet_demand"] == 0.0

    assert flow_result["reroute_cost"] == 20.0
    assert flow_result["delay_penalty"] == 40.0
    assert flow_result["unmet_demand_loss"] == 0.0
    assert flow_result["total_economic_impact"] == 60.0

    assert metrics["total_reroute_cost"] == 20.0
    assert metrics["total_delay_penalty"] == 40.0
    assert metrics["total_unmet_demand_loss"] == 0.0
    assert metrics["total_economic_impact"] == 60.0


def test_cascade_disrupts_flow_when_all_routes_fail(small_supply_chain_graph):
    simulator = CascadeSimulator(
        small_supply_chain_graph,
        reroute_cost_rate=1.0,
        delay_penalty_rate=2.0,
        unmet_demand_loss_rate=5.0,
    )

    result = simulator.run_simulation(
        disrupted_nodes=["B", "C"],
        flows=[{"source": "A", "target": "D", "demand": 10}],
        max_steps=5,
    )

    flow_result = result["flow_impacts"][0]
    metrics = result["metrics"]

    assert flow_result["status"] == "disrupted"
    assert flow_result["rerouted"] is False
    assert flow_result["baseline_path"] == ["A", "B", "D"]
    assert flow_result["baseline_cost"] == 2.0
    assert flow_result["final_path"] is None
    assert flow_result["final_cost"] is None
    assert flow_result["delivered_demand"] == 0.0
    assert flow_result["unmet_demand"] == 10.0

    assert flow_result["reroute_cost"] == 0.0
    assert flow_result["delay_penalty"] == 0.0
    assert flow_result["unmet_demand_loss"] == 50.0
    assert flow_result["total_economic_impact"] == 50.0

    assert metrics["total_reroute_cost"] == 0.0
    assert metrics["total_delay_penalty"] == 0.0
    assert metrics["total_unmet_demand_loss"] == 50.0
    assert metrics["total_economic_impact"] == 50.0
