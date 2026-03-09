import networkx as nx
import pandas as pd


class BottleneckDetector:
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
                    reduced[u][v].update(data)
            else:
                reduced.add_edge(u, v, **data)

        return reduced

    def _get_baseline_route(self, source_id, target_id):
        """
        Get the normal shortest route before any disruption.
        """
        H = self._to_weighted_digraph()
        source_id = str(source_id)
        target_id = str(target_id)

        path = nx.dijkstra_path(H, source_id, target_id, weight="transport_time")
        total_time = nx.dijkstra_path_length(H, source_id, target_id, weight="transport_time")

        return path, total_time

    def _classify_impact(self, status, increase_ratio):
        """
        Convert disruption outcome into a human-readable impact category.
        """
        if status == "Disconnected":
            return "Catastrophic"
        if increase_ratio is None:
            return "Unknown"
        if increase_ratio >= 1.0:
            return "Severe Delay"
        if increase_ratio > 0:
            return "Moderate Delay"
        return "Low Impact"

    def simulate_node_failure(self, disrupted_node, source_id, target_id):
        """
        Simulate failure of one node and evaluate rerouting impact.
        """
        disrupted_node = str(disrupted_node)
        source_id = str(source_id)
        target_id = str(target_id)

        H = self._to_weighted_digraph()

        if disrupted_node not in H:
            return {
                "node_id": disrupted_node,
                "node_name": "Unknown",
                "node_type": "Unknown",
                "status": "Error",
                "baseline_time": None,
                "new_time": None,
                "lead_time_increase": None,
                "increase_ratio": None,
                "impact_score": None,
                "impact_category": "Unknown",
                "new_route": None,
            }

        node_name = H.nodes[disrupted_node].get("name", disrupted_node)
        node_type = H.nodes[disrupted_node].get("type", "Unknown")

        try:
            baseline_path, baseline_time = self._get_baseline_route(source_id, target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                "node_id": disrupted_node,
                "node_name": node_name,
                "node_type": node_type,
                "status": "No Baseline Route",
                "baseline_time": None,
                "new_time": None,
                "lead_time_increase": None,
                "increase_ratio": None,
                "impact_score": None,
                "impact_category": "Unknown",
                "new_route": None,
            }

        if disrupted_node == source_id or disrupted_node == target_id:
            return {
                "node_id": disrupted_node,
                "node_name": node_name,
                "node_type": node_type,
                "status": "Disconnected",
                "baseline_time": baseline_time,
                "new_time": None,
                "lead_time_increase": None,
                "increase_ratio": None,
                "impact_score": 10.0,
                "impact_category": "Catastrophic",
                "new_route": None,
            }

        H_removed = H.copy()
        H_removed.remove_node(disrupted_node)

        try:
            new_path = nx.dijkstra_path(H_removed, source_id, target_id, weight="transport_time")
            new_time = nx.dijkstra_path_length(H_removed, source_id, target_id, weight="transport_time")
            new_route_names = [H_removed.nodes[n].get("name", n) for n in new_path]

            increase = new_time - baseline_time
            increase_ratio = increase / baseline_time if baseline_time > 0 else 0.0
            impact_category = self._classify_impact("Rerouted", increase_ratio)

            return {
                "node_id": disrupted_node,
                "node_name": node_name,
                "node_type": node_type,
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
                "node_id": disrupted_node,
                "node_name": node_name,
                "node_type": node_type,
                "status": "Disconnected",
                "baseline_time": baseline_time,
                "new_time": None,
                "lead_time_increase": None,
                "increase_ratio": None,
                "impact_score": 10.0,
                "impact_category": "Catastrophic",
                "new_route": None,
            }

    def rank_node_bottlenecks(self, source_id, target_id, exclude_terminals=False):
        """
        Simulate disruption for every node and rank by impact.
        """
        source_id = str(source_id)
        target_id = str(target_id)

        results = []

        for node_id in self.G.nodes():
            node_id = str(node_id)

            if exclude_terminals and node_id in {source_id, target_id}:
                continue

            result = self.simulate_node_failure(node_id, source_id, target_id)
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

    def summary_report(self, source_id, target_id, exclude_terminals=False):
        """
        Return a compact summary dictionary for reporting.
        """
        df = self.rank_node_bottlenecks(
            source_id=source_id,
            target_id=target_id,
            exclude_terminals=exclude_terminals
        )

        disconnected_count = (df["status"] == "Disconnected").sum()
        rerouted_count = (df["status"] == "Rerouted").sum()

        if not df.empty:
            top_node = df.iloc[0]["node_name"]
            top_status = df.iloc[0]["status"]
        else:
            top_node = None
            top_status = None

        return {
            "total_nodes_evaluated": len(df),
            "disconnected_nodes": int(disconnected_count),
            "rerouted_nodes": int(rerouted_count),
            "most_critical_node": top_node,
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

    detector = BottleneckDetector(G)

    print("\n--- Node Bottleneck Ranking (excluding source/destination) ---")
    result_df = detector.rank_node_bottlenecks("3", "5", exclude_terminals=True)
    print(result_df.to_string(index=False))

    print("\n--- Summary Report ---")
    print(detector.summary_report("3", "5", exclude_terminals=True))