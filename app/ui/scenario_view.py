import streamlit as st
from services.graph_service import get_available_scenario_flows, get_default_scenario_flows
from services.scenario_service import run_scenario_analysis_cached

from visualization.scenario_plots import ScenarioVisualizer


def render_scenario_builder(graph, graph_signature, node_options):
    st.markdown("---")
    st.subheader("Scenario Builder")

    available_flows = get_available_scenario_flows(graph, node_options)
    flow_labels = [item["label"] for item in available_flows]

    builder_mode = st.radio(
        "Scenario Input Mode",
        options=["Default Flows", "Custom Flows"],
        horizontal=True,
        key="scenario_builder_mode",
    )

    if builder_mode == "Default Flows":
        selected_flows = get_default_scenario_flows(graph, node_options)

        if selected_flows:
            st.info("Default scenario set uses reachable origin-destination flows from the current graph.")
        else:
            st.warning("No valid default flows were found for the current graph. " "Please switch to Custom Flows.")
    else:
        selected_flow_labels = st.multiselect(
            "Select one or more scenario flows",
            options=flow_labels,
            default=flow_labels[:3] if len(flow_labels) >= 3 else flow_labels,
            key="scenario_flow_selection",
        )

        selected_flows = [item["flow"] for item in available_flows if item["label"] in selected_flow_labels]

        if selected_flow_labels:
            st.write("Selected flows:")
            for label in selected_flow_labels:
                st.write(f"- {label}")
        else:
            st.warning("Please select at least one scenario flow.")

    node_scenario_results_df = None
    edge_scenario_results_df = None
    node_scenario_summary_df = None
    edge_scenario_summary_df = None
    scenario_overview = {}

    if selected_flows:
        selected_flows_tuple = tuple((str(o), str(d)) for o, d in selected_flows)
        (
            node_scenario_results_df,
            edge_scenario_results_df,
            node_scenario_summary_df,
            edge_scenario_summary_df,
            scenario_overview,
        ) = run_scenario_analysis_cached(graph_signature, selected_flows_tuple, graph)

    return {
        "selected_flows": selected_flows,
        "node_scenario_results_df": node_scenario_results_df,
        "edge_scenario_results_df": edge_scenario_results_df,
        "node_scenario_summary_df": node_scenario_summary_df,
        "edge_scenario_summary_df": edge_scenario_summary_df,
        "scenario_overview": scenario_overview,
    }


def render_scenario_analysis_tab(
    selected_flows,
    node_scenario_summary_df,
    edge_scenario_summary_df,
    scenario_overview,
):
    st.subheader("Scenario Analysis")
    st.write("Compare recurring fragility patterns across multiple source-destination flows.")

    if selected_flows and node_scenario_summary_df is not None and edge_scenario_summary_df is not None:
        st.markdown("### Scenario Summary Metrics")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        scenarios_eval = scenario_overview.get("node_scenarios_evaluated", 0)
        crit_node = scenario_overview.get("most_critical_node", "N/A")
        crit_edge = scenario_overview.get("most_critical_edge", "N/A")

        avg_impact = 0.0
        if not node_scenario_summary_df.empty and "avg_impact_score" in node_scenario_summary_df.columns:
            avg_impact = round(node_scenario_summary_df["avg_impact_score"].mean(), 2)

        metric_col1.metric("Scenarios Evaluated", scenarios_eval)
        metric_col2.metric("Most Critical Node", crit_node or "N/A")
        metric_col3.metric("Most Critical Edge", crit_edge or "N/A")
        metric_col4.metric("Avg Impact Score", avg_impact)

        scenario_mode = st.radio(
            "View Scenario Summaries",
            options=["Both", "Node Summary", "Edge Summary"],
            horizontal=True,
            key="scenario_summary_mode",
        )

        if scenario_mode in ["Both", "Node Summary"]:
            st.markdown("#### Node Scenario Summary")
            st.dataframe(node_scenario_summary_df, use_container_width=True)

        if scenario_mode in ["Both", "Edge Summary"]:
            st.markdown("#### Edge Scenario Summary")
            st.dataframe(edge_scenario_summary_df, use_container_width=True)

        st.markdown("### Scenario Charts")

        node_scenario_visualizer = ScenarioVisualizer(
            node_scenario_summary_df,
            label_column="node_name",
            entity_name="Supply Chain Node",
        )
        edge_scenario_visualizer = ScenarioVisualizer(
            edge_scenario_summary_df,
            label_column="edge_id",
            entity_name="Transport Link",
        )

        if scenario_mode in ["Both", "Node Summary"]:
            st.markdown("#### Node Scenario Charts")
            node_chart_col1, node_chart_col2 = st.columns(2)

            with node_chart_col1:
                st.plotly_chart(
                    node_scenario_visualizer.plot_catastrophic_count(title="Node Catastrophic Failure Count"),
                    use_container_width=True,
                )

            with node_chart_col2:
                st.plotly_chart(
                    node_scenario_visualizer.plot_average_impact(title="Node Average Impact Score"),
                    use_container_width=True,
                )

        if scenario_mode in ["Both", "Edge Summary"]:
            st.markdown("#### Edge Scenario Charts")
            edge_chart_col1, edge_chart_col2 = st.columns(2)

            with edge_chart_col1:
                st.plotly_chart(
                    edge_scenario_visualizer.plot_catastrophic_count(title="Edge Catastrophic Failure Count"),
                    use_container_width=True,
                )

            with edge_chart_col2:
                st.plotly_chart(
                    edge_scenario_visualizer.plot_average_impact(title="Edge Average Impact Score"),
                    use_container_width=True,
                )
    else:
        st.info("Select at least one scenario flow to run scenario analysis.")
