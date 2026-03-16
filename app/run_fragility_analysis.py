from analysis.bottleneck_detection import BottleneckDetector
from analysis.edge_bottleneck_detection import EdgeBottleneckDetector
from core.graph_builder import SupplyChainGraph
from visualization.fragility_plots import FragilityVisualizer


def main():
    source_id = "3"
    target_id = "5"

    builder = SupplyChainGraph("data/nodes.csv", ["data/edges.csv", "data/alternate_edges.csv"])
    builder.load_data()
    G = builder.build_graph()

    # -------------------------------
    # NODE BOTTLENECK ANALYSIS
    # -------------------------------
    node_detector = BottleneckDetector(G)

    node_result_df = node_detector.rank_node_bottlenecks(
        source_id=source_id, target_id=target_id, exclude_terminals=True
    )

    node_summary = node_detector.summary_report(
        source_id=source_id, target_id=target_id, exclude_terminals=True
    )

    print("\n=== NODE BOTTLENECK RANKING ===")
    print(node_result_df.to_string(index=False))

    print("\n=== NODE SUMMARY REPORT ===")
    print(node_summary)

    node_visualizer = FragilityVisualizer(
        node_result_df, label_column="node_name", entity_name="Supply Chain Node"
    )

    node_impact_fig = node_visualizer.plot_impact_score(
        title="Supply Chain Node Vulnerability (Impact Score)"
    )
    node_impact_fig.show()

    node_delay_fig = node_visualizer.plot_lead_time_increase(
        title="Supply Chain Node Delay Impact", include_zero_delay=False
    )
    node_delay_fig.show()

    # -------------------------------
    # EDGE BOTTLENECK ANALYSIS
    # -------------------------------
    edge_detector = EdgeBottleneckDetector(G)

    edge_result_df = edge_detector.rank_edge_bottlenecks(
        source_id=source_id, target_id=target_id, only_active_route_edges=False
    )

    edge_summary = edge_detector.summary_report(
        source_id=source_id, target_id=target_id, only_active_route_edges=False
    )

    print("\n=== EDGE BOTTLENECK RANKING ===")
    print(edge_result_df.to_string(index=False))

    print("\n=== EDGE SUMMARY REPORT ===")
    print(edge_summary)

    edge_visualizer = FragilityVisualizer(
        edge_result_df, label_column="edge_id", entity_name="Transport Link"
    )

    edge_impact_fig = edge_visualizer.plot_impact_score(title="Transport Link Vulnerability (Impact Score)")
    edge_impact_fig.show()

    edge_delay_fig = edge_visualizer.plot_lead_time_increase(
        title="Transport Link Delay Impact", include_zero_delay=False
    )
    edge_delay_fig.show()


if __name__ == "__main__":
    main()
