import pandas as pd
import networkx as nx
from analysis.cascade_simulator import CascadeSimulator

G = nx.DiGraph()
G.add_edge("A", "B", capacity=50, weight=1)
G.add_edge("B", "D", capacity=50, weight=1)
G.add_edge("A", "C", capacity=40, weight=2)
G.add_edge("C", "D", capacity=40, weight=2)

flows = [
    {"source": "A", "target": "D", "demand": 45},
]

sim = CascadeSimulator(G)

result = sim.run_simulation(
    disrupted_edges=[("A", "B")],
    flows=flows,
    max_steps=5,
)

step_rows = sim.get_step_metrics_table(result)
df = pd.DataFrame(step_rows)

def verify_flow_impacts(result):
    flow_impacts = result.get("flow_impacts", [])
    metrics = result.get("metrics", {})

    delivered_sum = 0.0
    unmet_sum = 0.0

    for i, row in enumerate(flow_impacts):
        demand = float(row["demand"])
        delivered = float(row["delivered_demand"])
        unmet = float(row["unmet_demand"])
        status = row["status"]
        baseline_path = row["baseline_path"]
        final_path = row["final_path"]
        rerouted = row["rerouted"]

        assert abs((delivered + unmet) - demand) < 1e-9, f"Row {i}: demand mismatch"

        if status == "disrupted":
            assert final_path is None, f"Row {i}: disrupted flow should have no final path"
            assert delivered == 0.0, f"Row {i}: disrupted flow should deliver 0"
            assert unmet == demand, f"Row {i}: disrupted flow unmet demand incorrect"

        elif status == "delivered":
            assert final_path == baseline_path, f"Row {i}: delivered flow path mismatch"
            assert rerouted is False, f"Row {i}: delivered flow should not be rerouted"
            assert delivered == demand, f"Row {i}: delivered demand incorrect"
            assert unmet == 0.0, f"Row {i}: unmet demand should be 0"

        elif status == "rerouted":
            assert final_path != baseline_path, f"Row {i}: rerouted flow should change path"
            assert rerouted is True, f"Row {i}: rerouted flag incorrect"
            assert delivered == demand, f"Row {i}: rerouted flow should still deliver all demand"
            assert unmet == 0.0, f"Row {i}: rerouted flow unmet demand should be 0"

        else:
            raise AssertionError(f"Row {i}: unknown status {status}")

        delivered_sum += delivered
        unmet_sum += unmet

    assert abs(delivered_sum - float(metrics.get("delivered_demand", 0.0))) < 1e-9, "Delivered demand total mismatch"
    assert abs(unmet_sum - float(metrics.get("unmet_demand", 0.0))) < 1e-9, "Unmet demand total mismatch"

    print("Flow impact verification passed.")

verify_flow_impacts(result)
print(df)