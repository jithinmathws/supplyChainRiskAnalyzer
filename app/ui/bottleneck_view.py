import streamlit as st

from visualization.fragility_plots import FragilityVisualizer


def render_executive_summary(baseline_time, baseline_route_names, node_result_df, edge_result_df):
    st.markdown("---")
    st.subheader("Executive Summary")

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns([1, 2, 1, 1])

    with summary_col1:
        st.metric("Baseline Lead Time", f"{baseline_time} days")

    with summary_col2:
        st.write("**Baseline Route**")
        st.info(" → ".join(baseline_route_names))

    with summary_col3:
        if node_result_df is not None and not node_result_df.empty:
            st.metric("Most Critical Node", node_result_df.iloc[0]["node_name"])
        else:
            st.metric("Most Critical Node", "N/A")

    with summary_col4:
        if edge_result_df is not None and not edge_result_df.empty:
            st.metric("Most Critical Edge", edge_result_df.iloc[0]["edge_id"])
        else:
            st.metric("Most Critical Edge", "N/A")


def render_node_analysis_tab(node_result_df):
    st.subheader("Node Bottleneck Ranking")

    node_display_cols = [
        "node_name",
        "status",
        "impact_score",
        "impact_category",
        "lead_time_increase",
    ]
    available_node_cols = [c for c in node_display_cols if c in node_result_df.columns]

    st.dataframe(node_result_df[available_node_cols], use_container_width=True)

    node_visualizer = FragilityVisualizer(
        node_result_df,
        label_column="node_name",
        entity_name="Supply Chain Node",
    )

    col_plot1, col_plot2 = st.columns(2)

    with col_plot1:
        st.plotly_chart(
            node_visualizer.plot_impact_score(title="Node Vulnerability (Impact Score)"),
            use_container_width=True,
        )

    with col_plot2:
        try:
            st.plotly_chart(
                node_visualizer.plot_lead_time_increase(
                    title="Node Delay Impact",
                    include_zero_delay=False,
                ),
                use_container_width=True,
            )
        except ValueError:
            st.info("No rerouted node delays to display.")


def render_edge_analysis_tab(edge_result_df):
    st.subheader("Edge Bottleneck Ranking")

    edge_display_cols = [
        "edge_id",
        "status",
        "impact_score",
        "impact_category",
        "lead_time_increase",
    ]
    available_edge_cols = [c for c in edge_display_cols if c in edge_result_df.columns]

    st.dataframe(edge_result_df[available_edge_cols], use_container_width=True)

    edge_visualizer = FragilityVisualizer(
        edge_result_df,
        label_column="edge_id",
        entity_name="Transport Link",
    )

    col_plot3, col_plot4 = st.columns(2)

    with col_plot3:
        st.plotly_chart(
            edge_visualizer.plot_impact_score(title="Link Vulnerability (Impact Score)"),
            use_container_width=True,
        )

    with col_plot4:
        try:
            st.plotly_chart(
                edge_visualizer.plot_lead_time_increase(
                    title="Link Delay Impact",
                    include_zero_delay=False,
                ),
                use_container_width=True,
            )
        except ValueError:
            st.info("No rerouted edge delays to display.")
