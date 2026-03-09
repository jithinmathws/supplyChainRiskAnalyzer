import networkx as nx
import pandas as pd


class FragilityAnalyzer:
    def __init__(self, G):
        self.G = G

    def _to_weighted_digraph(self):
        """
        Convert MultiDiGraph to DiGraph by keeping only the fastest edge
        between each source-target pair.
        """
        reduced = nx.DiGraph()

        for node, attrs in self.G.nodes(data=True):
            reduced.add_node(node, **attrs)

        for u, v, key, data in self.G.edges(keys=True, data=True):
            weight = data.get("transport_time", float("inf"))

            if reduced.has_edge(u, v):
                existing_weight = reduced[u][v]["transport_time"]
                if weight < existing_weight:
                    reduced[u][v].update(data)
            else:
                reduced.add_edge(u, v, **data)

        return reduced

    def calculate_centrality(self):
        H = self._to_weighted_digraph()

        degree = nx.degree_centrality(H)
        in_degree = nx.in_degree_centrality(H)
        out_degree = nx.out_degree_centrality(H)
        betweenness = nx.betweenness_centrality(H, weight="transport_time")
        closeness = nx.closeness_centrality(H, distance="transport_time")

        metrics = []
        for node_id in H.nodes():
            metrics.append({
                "node_id": node_id,
                "name": H.nodes[node_id].get("name", "Unknown"),
                "type": H.nodes[node_id].get("type", "Unknown"),
                "degree_centrality": degree[node_id],
                "in_degree_centrality": in_degree[node_id],
                "out_degree_centrality": out_degree[node_id],
                "bottleneck_score": betweenness[node_id],
                "closeness_centrality": closeness[node_id],
            })

        return pd.DataFrame(metrics).sort_values(by="bottleneck_score", ascending=False)

    def get_route_analysis(self, source_id, target_id):
        source_id = str(source_id)
        target_id = str(target_id)

        H = self._to_weighted_digraph()

        try:
            path = nx.dijkstra_path(H, source_id, target_id, weight="transport_time")
            total_time = nx.dijkstra_path_length(H, source_id, target_id, weight="transport_time")

            path_names = [H.nodes[n].get("name", n) for n in path]

            return {
                "path_node_ids": path,
                "path_node_names": path_names,
                "route": " -> ".join(path_names),
                "total_lead_time_days": total_time,
                "stops": len(path) - 1
            }

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def simulate_disruption(self, disrupted_node, source_id, target_id):
        disrupted_node = str(disrupted_node)
        source_id = str(source_id)
        target_id = str(target_id)

        H = self._to_weighted_digraph()

        if disrupted_node not in H:
            return {
                "status": "Error",
                "impact": f"Node {disrupted_node} not found in graph.",
                "new_route": None,
                "new_lead_time": None
            }

        disrupted_name = H.nodes[disrupted_node].get("name", disrupted_node)

        H_removed = H.copy()
        H_removed.remove_node(disrupted_node)

        try:
            new_path = nx.dijkstra_path(H_removed, source_id, target_id, weight="transport_time")
            new_time = nx.dijkstra_path_length(H_removed, source_id, target_id, weight="transport_time")
            new_path_names = [H_removed.nodes[n].get("name", n) for n in new_path]

            return {
                "status": "Rerouted",
                "impact": f"Disruption at {disrupted_name} handled.",
                "new_route": " -> ".join(new_path_names),
                "new_lead_time": new_time
            }

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                "status": "Disconnected",
                "impact": f"Disruption at {disrupted_name} breaks the supply route.",
                "new_route": None,
                "new_lead_time": None
            }


if __name__ == "__main__":
    from graph_builder import SupplyChainGraph

    builder = SupplyChainGraph(
        "data/nodes.csv",
        ["data/edges.csv", "data/alternate_edges.csv"]
    )
    builder.load_data()
    G = builder.build_graph()
    builder.print_edges()

    analyzer = FragilityAnalyzer(G)

    print("\n--- Fragility & Bottleneck Report ---")
    print(analyzer.calculate_centrality())

    print("\n--- Normal Route Analysis ---")
    route = analyzer.get_route_analysis("3", "5")
    if route:
        print(f"Optimal Path: {route['route']}")
        print(f"Estimated Time: {route['total_lead_time_days']} days")
    else:
        print("No valid route found.")

    print("\n--- DISRUPTION SIMULATION: SHANGHAI PORT CLOSED ---")
    result = analyzer.simulate_disruption("1", "3", "5")
    print(f"Status: {result['status']}")
    print(f"Impact: {result['impact']}")
    if result["new_route"]:
        print(f"New Route: {result['new_route']}")
        print(f"New Lead Time: {result['new_lead_time']} days")