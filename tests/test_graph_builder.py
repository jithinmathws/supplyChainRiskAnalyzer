import pandas as pd
import pytest

from core.graph_builder import SupplyChainGraph


def test_graph_builder_builds_valid_graph(tmp_path):
    nodes_csv = tmp_path / "nodes.csv"
    edges_csv = tmp_path / "edges.csv"

    pd.DataFrame(
        [
            {
                "node_id": "A",
                "name": "Supplier A",
                "type": "supplier",
                "location": "Loc A",
                "capacity": 100,
            },
            {
                "node_id": "B",
                "name": "Hub B",
                "type": "hub",
                "location": "Loc B",
                "capacity": 200,
            },
            {
                "node_id": "D",
                "name": "Customer D",
                "type": "customer",
                "location": "Loc D",
                "capacity": 300,
            },
        ]
    ).to_csv(nodes_csv, index=False)

    pd.DataFrame(
        [
            {
                "source": "A",
                "target": "B",
                "transport_mode": "road",
                "distance": 10,
                "transport_time": 1,
            },
            {
                "source": "B",
                "target": "D",
                "transport_mode": "road",
                "distance": 20,
                "transport_time": 2,
            },
        ]
    ).to_csv(edges_csv, index=False)

    builder = SupplyChainGraph(str(nodes_csv), [str(edges_csv)])
    builder.load_data()
    G = builder.build_graph()

    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 2
    assert "A" in G.nodes
    assert G.nodes["A"]["name"] == "Supplier A"
    assert G.has_edge("A", "B")


def test_graph_builder_fails_when_edge_references_missing_node(tmp_path):
    nodes_csv = tmp_path / "nodes.csv"
    edges_csv = tmp_path / "edges.csv"

    pd.DataFrame(
        [
            {
                "node_id": "A",
                "name": "Supplier A",
                "type": "supplier",
                "location": "Loc A",
                "capacity": 100,
            },
            {
                "node_id": "D",
                "name": "Customer D",
                "type": "customer",
                "location": "Loc D",
                "capacity": 300,
            },
        ]
    ).to_csv(nodes_csv, index=False)

    pd.DataFrame(
        [
            {
                "source": "A",
                "target": "B",
                "transport_mode": "road",
                "distance": 10,
                "transport_time": 1,
            },
        ]
    ).to_csv(edges_csv, index=False)

    builder = SupplyChainGraph(str(nodes_csv), [str(edges_csv)])
    builder.load_data()

    with pytest.raises(ValueError, match="undefined node"):
        builder.build_graph()
