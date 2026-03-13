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

print(df)