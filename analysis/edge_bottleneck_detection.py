import networkx as nx
import pandas as pd


class EdgeBottleneckDetector:
    def __init__(self, G):
        self.G = G

    def _to_weighted_digraph(self):
        """
        Convert MultiDiGraph to DiGraph by keeping the fastest edge
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
                    reduced[u][v].clear()
                    reduced[u][v].update(data)
                    reduced[u][v]["edge_key"] = key
                    reduced[u][v]["source"] = u
                    reduced[u][v]["target"] = v
            else:
                reduced.add_edge(u, v, **data)
                reduced[u][v]["edge_key"] = key
                reduced[u][v]["source"] = u
                reduced[u][v]["target"] = v

        return reduced

    def _get_baseline_route(self, source_id, target_id):
        H = self._to_weighted_digraph()
        source_id = str(source_id)
        target_id = str(target_id)

        path = nx.dijkstra_path(H, source_id, target_id, weight="transport_time")
        total_time = nx.dijkstra_path_length(H, source_id, target_id, weight="transport_time")

        return H, path, total_time

    def _classify_impact(self, status, increase_ratio):
        if status == "Disconnected":
            return "Catastrophic"
        if increase_ratio is None:
            return "Unknown"
        if increase_ratio >= 1.0:
            return "Severe Delay"
        if increase_ratio > 0:
            return "Moderate Delay"
        return "Low Impact"

    def simulate_edge_failure(self, edge_source, edge_target, edge_key, source_id, target_id):
        edge_source = str(edge_source)
        edge_target = str(edge_target)
        edge_key = str(edge_key)
        source_id = str(source_id)
        target_id = str(target_id)

        try:
            H, baseline_path, baseline_time = self._get_baseline_route(source_id, target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                "edge_id": f"{edge_source}->{edge_target} [{edge_key}]",
                "source_node": edge_source,
                "target_node": edge_target,
                "transport_mode": edge_key,
                "status": "No Baseline Route",
                "baseline_time": None,
                "new_time": None,
                "lead_time_increase": None,
                "increase_ratio": None,
                "impact_score": None,
                "impact_category": "Unknown",
                "new_route": None,
            }

        if not H.has_edge(edge_source, edge_target):
            return {
                "edge_id": f"{edge_source}->{edge_target} [{edge_key}]",
                "source_node": edge_source,
                "target_node": edge_target,
                "transport_mode": edge_key,
                "status": "Error",
                "baseline_time": baseline_time,
                "new_time": None,
                "lead_time_increase": None,
                "increase_ratio": None,
                "impact_score": None,
                "impact_category": "Unknown",
                "new_route": None,
            }

        H_removed = H.copy()
        H_removed.remove_edge(edge_source, edge_target)

        try:
            new_path = nx.dijkstra_path(H_removed, source_id, target_id, weight="transport_time")
            new_time = nx.dijkstra_path_length(H_removed, source_id, target_id, weight="transport_time")
            new_route_names = [H_removed.nodes[n].get("name", n) for n in new_path]

            increase = new_time - baseline_time
            increase_ratio = increase / baseline_time if baseline_time > 0 else 0.0
            impact_category = self._classify_impact("Rerouted", increase_ratio)

            return {
                "edge_id": f"{edge_source}->{edge_target} [{edge_key}]",
                "source_node": edge_source,
                "target_node": edge_target,
                "transport_mode": edge_key,
                "status": "Rerouted",
                "baseline_time": baseline_time,
                "new_time": new_time,
                "lead_time_increase": increase,
                "increase_ratio": round(increase_ratio, 4),
                "impact_score": round(increase_ratio, 4),
                "impact_category": impact_category,
                "new_route": " -> ".join(new_route_names),
            }

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                "edge_id": f"{edge_source}->{edge_target} [{edge_key}]",
                "source_node": edge_source,
                "target_node": edge_target,
                "transport_mode": edge_key,
                "status": "Disconnected",
                "baseline_time": baseline_time,
                "new_time": None,
                "lead_time_increase": None,
                "increase_ratio": None,
                "impact_score": 10.0,
                "impact_category": "Catastrophic",
                "new_route": None,
            }

    def rank_edge_bottlenecks(self, source_id, target_id, only_active_route_edges=False):
        """
        Simulate failure for each reduced edge in the fastest-path graph.
        If only_active_route_edges=True, only test edges currently used by the baseline route.
        """
        H, baseline_path, baseline_time = self._get_baseline_route(source_id, target_id)

        active_edges = set()
        for i in range(len(baseline_path) - 1):
            active_edges.add((baseline_path[i], baseline_path[i + 1]))

        results = []

        for u, v, data in H.edges(data=True):
            if only_active_route_edges and (u, v) not in active_edges:
                continue

            edge_key = data.get("edge_key", data.get("transport_mode", "Unknown"))

            result = self.simulate_edge_failure(
                edge_source=u,
                edge_target=v,
                edge_key=edge_key,
                source_id=source_id,
                target_id=target_id
            )
            results.append(result)

        df = pd.DataFrame(results)

        status_priority = {
            "Disconnected": 3,
            "Rerouted": 2,
            "Error": 1,
            "No Baseline Route": 0,
        }
        df["status_priority"] = df["status"].map(status_priority).fillna(0)

        df = df.sort_values(
            by=["status_priority", "impact_score", "lead_time_increase"],
            ascending=[False, False, False]
        ).drop(columns=["status_priority"])

        return df.reset_index(drop=True)

    def summary_report(self, source_id, target_id, only_active_route_edges=False):
        df = self.rank_edge_bottlenecks(
            source_id=source_id,
            target_id=target_id,
            only_active_route_edges=only_active_route_edges
        )

        disconnected_count = (df["status"] == "Disconnected").sum()
        rerouted_count = (df["status"] == "Rerouted").sum()

        if not df.empty:
            top_edge = df.iloc[0]["edge_id"]
            top_status = df.iloc[0]["status"]
        else:
            top_edge = None
            top_status = None

        return {
            "total_edges_evaluated": len(df),
            "disconnected_edges": int(disconnected_count),
            "rerouted_edges": int(rerouted_count),
            "most_critical_edge": top_edge,
            "most_critical_status": top_status,
        }


if __name__ == "__main__":
    from core.graph_builder import SupplyChainGraph

    builder = SupplyChainGraph(
        "data/nodes.csv",
        ["data/edges.csv", "data/alternate_edges.csv"]
    )
    builder.load_data()
    G = builder.build_graph()

    detector = EdgeBottleneckDetector(G)

    print("\n--- Edge Bottleneck Ranking ---")
    result_df = detector.rank_edge_bottlenecks("3", "5", only_active_route_edges=False)
    print(result_df.to_string(index=False))

    print("\n--- Edge Summary Report ---")
    print(detector.summary_report("3", "5", only_active_route_edges=False))