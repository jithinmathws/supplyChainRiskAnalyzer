import networkx as nx
import pandas as pd


class BottleneckDetector:
    def __init__(self, G):
        self.G = G

    def _to_weighted_digraph(self):
        """
        Convert MultiDiGraph/DiGraph to DiGraph by keeping the fastest edge
        between each source-target pair.
        """
        reduced = nx.DiGraph()

        for node, attrs in self.G.nodes(data=True):
            reduced.add_node(node, **attrs)

        if self.G.is_multigraph():
            edge_iter = self.G.edges(keys=True, data=True)
            for u, v, _, data in edge_iter:
                weight = data.get("weight", data.get("transport_time", float("inf")))

                if reduced.has_edge(u, v):
                    existing_weight = reduced[u][v]["weight"]
                    if weight < existing_weight:
                        reduced[u][v].clear()
                        reduced[u][v].update(data)
                        reduced[u][v]["weight"] = weight
                else:
                    reduced.add_edge(u, v, **data)
                    reduced[u][v]["weight"] = weight
        else:
            for u, v, data in self.G.edges(data=True):
                weight = data.get("weight", data.get("transport_time", float("inf")))

                if reduced.has_edge(u, v):
                    existing_weight = reduced[u][v]["weight"]
                    if weight < existing_weight:
                        reduced[u][v].clear()
                        reduced[u][v].update(data)
                        reduced[u][v]["weight"] = weight
                else:
                    reduced.add_edge(u, v, **data)
                    reduced[u][v]["weight"] = weight

        return reduced

    def _get_baseline_route(self, source_id, target_id):
        H = self._to_weighted_digraph()
        source_id = str(source_id)
        target_id = str(target_id)

        path = nx.dijkstra_path(H, source_id, target_id, weight="weight")
        total_time = nx.dijkstra_path_length(H, source_id, target_id, weight="weight")

        return path, total_time

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

    def simulate_node_failure(self, disrupted_node, source_id, target_id):
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
            new_path = nx.dijkstra_path(H_removed, source_id, target_id, weight="weight")
            new_time = nx.dijkstra_path_length(H_removed, source_id, target_id, weight="weight")
            new_route_names = [H_removed.nodes[n].get("name", n) for n in new_path]

            increase = new_time - baseline_time
            increase_ratio = increase / baseline_time if baseline_time > 0 else 0.0

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
                "impact_category": self._classify_impact("Rerouted", increase_ratio),
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
        source_id = str(source_id)
        target_id = str(target_id)

        results = []
        for node_id in self.G.nodes():
            node_id = str(node_id)
            if exclude_terminals and node_id in {source_id, target_id}:
                continue
            results.append(self.simulate_node_failure(node_id, source_id, target_id))

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
            ascending=[False, False, False],
        ).drop(columns=["status_priority"])

        return df.reset_index(drop=True)

    def summary_report(self, source_id, target_id, exclude_terminals=False):
        df = self.rank_node_bottlenecks(
            source_id=source_id,
            target_id=target_id,
            exclude_terminals=exclude_terminals,
        )

        disconnected_count = (df["status"] == "Disconnected").sum()
        rerouted_count = (df["status"] == "Rerouted").sum()

        return {
            "total_nodes_evaluated": len(df),
            "disconnected_nodes": int(disconnected_count),
            "rerouted_nodes": int(rerouted_count),
            "most_critical_node": df.iloc[0]["node_name"] if not df.empty else None,
            "most_critical_status": df.iloc[0]["status"] if not df.empty else None,
        }
