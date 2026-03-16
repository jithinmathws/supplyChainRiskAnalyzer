import networkx as nx
import pytest


@pytest.fixture
def small_supply_chain_graph():
    """
    Deterministic graph used across baseline and cascade tests.

    Layout:
        A -> B -> D
        A -> C -> D

    Preferred path A->D is A-B-D (cost 2).
    Alternate path is A-C-D (cost 4).
    """
    G = nx.MultiDiGraph()

    G.add_node("A", name="Supplier A", type="supplier", location="Loc A", capacity=100)
    G.add_node("B", name="Hub B", type="hub", location="Loc B", capacity=100)
    G.add_node("C", name="Hub C", type="hub", location="Loc C", capacity=100)
    G.add_node("D", name="Customer D", type="customer", location="Loc D", capacity=100)

    G.add_edge("A", "B", key="road", weight=1, capacity=100)
    G.add_edge("B", "D", key="road", weight=1, capacity=100)

    G.add_edge("A", "C", key="rail", weight=2, capacity=100)
    G.add_edge("C", "D", key="rail", weight=2, capacity=100)

    return G
