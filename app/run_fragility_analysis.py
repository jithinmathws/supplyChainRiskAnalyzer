from core.graph_builder import SupplyChainGraph
from analysis.bottleneck_detection import BottleneckDetector
from visualization.fragility_plots import FragilityVisualizer


def main():
    source_id = "3"
    target_id = "5"

    builder = SupplyChainGraph(
        "data/nodes.csv",
        ["data/edges.csv", "data/alternate_edges.csv"]
    )
    builder.load_data()
    G = builder.build_graph()

    detector = BottleneckDetector(G)

    result_df = detector.rank_node_bottlenecks(
        source_id=source_id,
        target_id=target_id,
        exclude_terminals=True
    )

    summary = detector.summary_report(
        source_id=source_id,
        target_id=target_id,
        exclude_terminals=True
    )

    print("\n--- Node Bottleneck Ranking ---")
    print(result_df.to_string(index=False))

    print("\n--- Summary Report ---")
    print(summary)

    visualizer = FragilityVisualizer(result_df)

    fig1 = visualizer.plot_impact_score()
    fig1.show()

    fig2 = visualizer.plot_lead_time_increase(include_zero_delay=True)
    fig2.show()


if __name__ == "__main__":
    main()