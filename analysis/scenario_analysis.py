import pandas as pd

from analysis.bottleneck_detection import BottleneckDetector
from analysis.edge_bottleneck_detection import EdgeBottleneckDetector


class ScenarioAnalyzer:
    def __init__(self, G):
        self.G = G
        self.node_detector = BottleneckDetector(G)
        self.edge_detector = EdgeBottleneckDetector(G)

    def run_node_scenarios(self, flows, exclude_terminals=True):
        """
        Run node bottleneck analysis for multiple source-target flows.
        flows: list of tuples like [("3", "5"), ("3", "2")]
        """
        all_results = []

        for source_id, target_id in flows:
            result_df = self.node_detector.rank_node_bottlenecks(
                source_id=source_id, target_id=target_id, exclude_terminals=exclude_terminals
            ).copy()

            result_df["scenario_source"] = str(source_id)
            result_df["scenario_target"] = str(target_id)
            result_df["scenario"] = f"{source_id}->{target_id}"

            all_results.append(result_df)

        if not all_results:
            return pd.DataFrame()

        return pd.concat(all_results, ignore_index=True)

    def run_edge_scenarios(self, flows, only_active_route_edges=False):
        """
        Run edge bottleneck analysis for multiple source-target flows.
        """
        all_results = []

        for source_id, target_id in flows:
            result_df = self.edge_detector.rank_edge_bottlenecks(
                source_id=source_id, target_id=target_id, only_active_route_edges=only_active_route_edges
            ).copy()

            result_df["scenario_source"] = str(source_id)
            result_df["scenario_target"] = str(target_id)
            result_df["scenario"] = f"{source_id}->{target_id}"

            all_results.append(result_df)

        if not all_results:
            return pd.DataFrame()

        return pd.concat(all_results, ignore_index=True)

    def summarize_node_scenarios(self, node_results_df):
        """
        Aggregate node results across scenarios.
        """
        if node_results_df.empty:
            return pd.DataFrame()

        summary = node_results_df.groupby(["node_id", "node_name", "node_type"], as_index=False).agg(
            scenarios_evaluated=("scenario", "count"),
            catastrophic_count=("status", lambda s: (s == "Disconnected").sum()),
            rerouted_count=("status", lambda s: (s == "Rerouted").sum()),
            avg_impact_score=("impact_score", "mean"),
            max_impact_score=("impact_score", "max"),
            avg_lead_time_increase=("lead_time_increase", "mean"),
            max_lead_time_increase=("lead_time_increase", "max"),
        )

        summary = summary.sort_values(
            by=["catastrophic_count", "max_impact_score", "avg_impact_score"], ascending=[False, False, False]
        ).reset_index(drop=True)

        return summary

    def summarize_edge_scenarios(self, edge_results_df):
        """
        Aggregate edge results across scenarios.
        """
        if edge_results_df.empty:
            return pd.DataFrame()

        summary = edge_results_df.groupby(["edge_id", "source_node", "target_node", "edge_key"], as_index=False).agg(
            scenarios_evaluated=("scenario", "count"),
            catastrophic_count=("status", lambda s: (s == "Disconnected").sum()),
            rerouted_count=("status", lambda s: (s == "Rerouted").sum()),
            avg_impact_score=("impact_score", "mean"),
            max_impact_score=("impact_score", "max"),
            avg_lead_time_increase=("lead_time_increase", "mean"),
            max_lead_time_increase=("lead_time_increase", "max"),
        )

        summary = summary.sort_values(
            by=["catastrophic_count", "max_impact_score", "avg_impact_score"], ascending=[False, False, False]
        ).reset_index(drop=True)

        return summary

    def scenario_overview(self, node_results_df, edge_results_df):
        """
        Return a compact overview for reporting.
        """
        overview = {
            "node_scenarios_evaluated": 0,
            "edge_scenarios_evaluated": 0,
            "most_critical_node": None,
            "most_critical_edge": None,
        }

        if not node_results_df.empty:
            node_summary = self.summarize_node_scenarios(node_results_df)
            overview["node_scenarios_evaluated"] = node_results_df["scenario"].nunique()
            if not node_summary.empty:
                overview["most_critical_node"] = node_summary.iloc[0]["node_name"]

        if not edge_results_df.empty:
            edge_summary = self.summarize_edge_scenarios(edge_results_df)
            overview["edge_scenarios_evaluated"] = edge_results_df["scenario"].nunique()
            if not edge_summary.empty:
                overview["most_critical_edge"] = edge_summary.iloc[0]["edge_id"]

        return overview


if __name__ == "__main__":
    from core.graph_builder import SupplyChainGraph

    builder = SupplyChainGraph("data/nodes.csv", ["data/edges.csv", "data/alternate_edges.csv"])
    builder.load_data()
    G = builder.build_graph()

    flows = [
        ("3", "5"),
        ("3", "2"),
        ("4", "5"),
    ]

    analyzer = ScenarioAnalyzer(G)

    print("\n=== RUNNING NODE SCENARIOS ===")
    node_results = analyzer.run_node_scenarios(flows, exclude_terminals=True)
    print(node_results.to_string(index=False))

    print("\n=== NODE SCENARIO SUMMARY ===")
    node_summary = analyzer.summarize_node_scenarios(node_results)
    print(node_summary.to_string(index=False))

    print("\n=== RUNNING EDGE SCENARIOS ===")
    edge_results = analyzer.run_edge_scenarios(flows, only_active_route_edges=False)
    print(edge_results.to_string(index=False))

    print("\n=== EDGE SCENARIO SUMMARY ===")
    edge_summary = analyzer.summarize_edge_scenarios(edge_results)
    print(edge_summary.to_string(index=False))

    print("\n=== SCENARIO OVERVIEW ===")
    print(analyzer.scenario_overview(node_results, edge_results))
