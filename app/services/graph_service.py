import networkx as nx
import streamlit as st

from core.graph_builder import SupplyChainGraph


@st.cache_resource
def load_graph():
    builder = SupplyChainGraph(
        "data/nodes.csv",
        ["data/edges.csv", "data/alternate_edges.csv"],
    )
    builder.load_data()
    return builder.build_graph()


def get_graph_signature(graph):
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    edge_signature = tuple(
        sorted((str(u), str(v), str(data.get("transport_time", ""))) for u, v, data in graph.edges(data=True))
    )
    return node_count, edge_count, edge_signature


def get_node_options(graph):
    options = {}
    for node_id, attrs in graph.nodes(data=True):
        label = f"{node_id} - {attrs.get('name', node_id)}"
        options[label] = str(node_id)
    return options


def get_baseline_route(graph, source_id, target_id):
    """
    Returns baseline shortest path route ids, names, and lead time.
    Uses the fastest available edge between each source-target pair.
    """
    route_graph = nx.DiGraph()

    for u, v, data in graph.edges(data=True):
        weight = data.get("transport_time", float("inf"))

        if route_graph.has_edge(u, v):
            if weight < route_graph[u][v]["transport_time"]:
                route_graph[u][v]["transport_time"] = weight
        else:
            route_graph.add_edge(u, v, transport_time=weight)

    route_ids = nx.dijkstra_path(route_graph, source_id, target_id, weight="transport_time")
    total_time = nx.dijkstra_path_length(route_graph, source_id, target_id, weight="transport_time")
    route_names = [graph.nodes[n].get("name", n) for n in route_ids]

    return route_ids, route_names, total_time


def get_default_scenario_flows():
    return [
        ("3", "5"),
        ("3", "2"),
        ("4", "5"),
    ]


def get_available_scenario_flows(graph, node_options):
    """Returns all reachable origin-destination pairs from current nodes."""
    flows = []
    items = list(node_options.items())

    for origin_label, origin_id in items:
        for destination_label, destination_id in items:
            origin_id = str(origin_id)
            destination_id = str(destination_id)

            if origin_id == destination_id:
                continue

            if nx.has_path(graph, origin_id, destination_id):
                flows.append(
                    {
                        "label": f"{origin_label} → {destination_label}",
                        "flow": (origin_id, destination_id),
                    }
                )

    return flows


def enrich_graph_for_visualization(graph, node_result_df=None, edge_result_df=None):
    """Add visualization-friendly attributes to a graph copy."""
    graph_viz = graph.copy()

    betweenness = nx.betweenness_centrality(graph_viz)
    degree_dict = dict(graph_viz.degree())

    for node in graph_viz.nodes():
        graph_viz.nodes[node]["betweenness"] = float(betweenness.get(node, 0.0))
        graph_viz.nodes[node]["degree"] = float(degree_dict.get(node, 0))
        graph_viz.nodes[node]["fragility_score"] = 0.0
        graph_viz.nodes[node]["bottleneck_score"] = 0.0

        if "label" not in graph_viz.nodes[node]:
            graph_viz.nodes[node]["label"] = str(graph_viz.nodes[node].get("name", node))

    if node_result_df is not None and not node_result_df.empty:
        node_name_to_score = {}
        if {"node_name", "impact_score"}.issubset(node_result_df.columns):
            node_name_to_score = dict(
                zip(node_result_df["node_name"], node_result_df["impact_score"])
            )

        node_id_to_score = {}
        if {"node_id", "impact_score"}.issubset(node_result_df.columns):
            node_id_to_score = {
                str(node_id): score
                for node_id, score in zip(
                    node_result_df["node_id"], node_result_df["impact_score"]
                )
            }

        for node, attrs in graph_viz.nodes(data=True):
            node_id_str = str(node)
            node_name = attrs.get("name", node_id_str)

            score = 0.0
            if node_id_str in node_id_to_score:
                score = node_id_to_score[node_id_str]
            elif node_name in node_name_to_score:
                score = node_name_to_score[node_name]

            graph_viz.nodes[node]["fragility_score"] = float(score)
            graph_viz.nodes[node]["bottleneck_score"] = float(score)

    edge_lookup = {}
    if edge_result_df is not None and not edge_result_df.empty:
        if {"edge_id", "impact_score"}.issubset(edge_result_df.columns):
            for _, row in edge_result_df.iterrows():
                edge_lookup[str(row["edge_id"])] = float(row["impact_score"])

    for u, v, attrs in graph_viz.edges(data=True):
        attrs["weight"] = float(
            attrs.get(
                "weight",
                attrs.get("transport_time", attrs.get("flow", 1.0)),
            )
        )
        attrs["flow"] = float(attrs.get("flow", attrs.get("capacity", 1.0)))
        attrs["criticality"] = 0.0

        edge_id = attrs.get("edge_id")
        if edge_id is None:
            edge_id = f"{u}->{v}"
            attrs["edge_id"] = edge_id

        if str(edge_id) in edge_lookup:
            attrs["criticality"] = edge_lookup[str(edge_id)]

        if "label" not in attrs:
            attrs["label"] = str(edge_id)

    return graph_viz
