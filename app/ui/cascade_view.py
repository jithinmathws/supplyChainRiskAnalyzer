import services.graph_service as gs
import streamlit as st
from services.cascade_service import (
    build_cascade_insight,
    build_cascade_overview,
    run_cascade_analysis_cached,
)


def normalize_edge_tuple(edge):
    if len(edge) == 3:
        u, v, k = edge
        return (str(u), str(v), str(k))
    if len(edge) == 2:
        u, v = edge
        return (str(u), str(v))
    raise ValueError(f"Invalid disrupted edge format: {edge}")


def format_edge_tuple(edge):
    """
    Render edge tuple for display.

    Supports:
    - (u, v)
    - (u, v, key)
    """
    if len(edge) == 3:
        u, v, k = edge
        return f"{u} → {v} [{k}]"
    if len(edge) == 2:
        u, v = edge
        return f"{u} → {v}"
    return str(edge)


def render_cascade_builder(graph, graph_signature, node_options):
    st.markdown("---")
    st.subheader("Cascade Simulation Builder")

    available_flows = gs.get_available_scenario_flows(graph, node_options)
    flow_labels = [item["label"] for item in available_flows]

    builder_mode = st.radio(
        "Cascade Flow Input Mode",
        options=["Default Flows", "Custom Flows", "Upload Flows CSV"],
        horizontal=True,
        key="cascade_builder_mode",
    )

    selected_flows = []
    uploaded_flow_dicts = None

    if builder_mode == "Default Flows":
        selected_flows = gs.get_default_scenario_flows(graph, node_options)

        if selected_flows:
            st.info(
                "Default cascade set uses reachable origin-destination flows from the current graph. "
                "You can switch to Custom Flows or Upload Flows CSV."
            )
        else:
            st.warning("No valid default flows were found for the current graph. " "Please switch to Custom Flows or Upload Flows CSV.")

    elif builder_mode == "Custom Flows":
        selected_flow_labels = st.multiselect(
            "Select one or more cascade flows",
            options=flow_labels,
            default=flow_labels[:2] if len(flow_labels) >= 2 else flow_labels,
            key="cascade_flow_selection",
        )

        selected_flows = [item["flow"] for item in available_flows if item["label"] in selected_flow_labels]

        if selected_flow_labels:
            st.write("Selected cascade flows:")
            for label in selected_flow_labels:
                st.write(f"- {label}")
        else:
            st.warning("Please select at least one cascade flow.")

    else:
        flows_file = st.file_uploader(
            "Upload flows.csv",
            type="csv",
            key=f"cascade_flows_upload_{graph_signature}",
        )

        with st.expander("Required flows.csv columns"):
            st.markdown(
                """
- `source`
- `target`
- `demand`
                """
            )

        if flows_file is not None:
            try:
                preview_df = gs.preview_uploaded_flows(flows_file)
                st.write("Preview: flows.csv")
                st.dataframe(preview_df, use_container_width=True)

                uploaded_flow_dicts = gs.load_uploaded_flows(flows_file)

                st.success(f"Loaded {len(uploaded_flow_dicts)} flows from CSV.")

            except Exception as exc:
                st.error(f"Invalid flows.csv: {exc}")
                uploaded_flow_dicts = None
        else:
            st.info("Upload a flows.csv file to use CSV-driven cascade demand.")

    st.markdown("### Initial Disruption Settings")

    disruption_col1, disruption_col2 = st.columns(2)

    with disruption_col1:
        disrupted_node_labels = st.multiselect(
            "Disrupted Nodes",
            options=list(node_options.keys()),
            default=[],
            key="cascade_disrupted_nodes",
        )
        disrupted_nodes = [str(node_options[label]) for label in disrupted_node_labels]

    with disruption_col2:
        edge_options = []
        edge_label_to_tuple = {}

        if graph.is_multigraph():
            for u, v, k, data in graph.edges(keys=True, data=True):
                edge_id = data.get("edge_id", str(k))
                edge_label = f"{u} → {v} ({edge_id})"
                edge_options.append(edge_label)
                edge_label_to_tuple[edge_label] = (str(u), str(v), str(k))
        else:
            for u, v, data in graph.edges(data=True):
                edge_id = data.get("edge_id", f"{u}->{v}")
                edge_label = f"{u} → {v} ({edge_id})"
                edge_options.append(edge_label)
                edge_label_to_tuple[edge_label] = (str(u), str(v))

        disrupted_edge_labels = st.multiselect(
            "Disrupted Edges",
            options=edge_options,
            default=[],
            key="cascade_disrupted_edges",
        )
        disrupted_edges = [edge_label_to_tuple[label] for label in disrupted_edge_labels]

    st.markdown("### Simulation Parameters")

    param_col1, param_col2, param_col3 = st.columns(3)

    with param_col1:
        demand_per_flow = st.number_input(
            "Demand per Flow",
            min_value=1.0,
            value=45.0,
            step=5.0,
            key="cascade_demand_per_flow",
            disabled=(builder_mode == "Upload Flows CSV"),
        )

    with param_col2:
        max_steps = st.number_input(
            "Max Steps",
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            key="cascade_max_steps",
        )

    with param_col3:
        default_capacity = st.number_input(
            "Default Capacity",
            min_value=1.0,
            value=100.0,
            step=10.0,
            key="cascade_default_capacity",
        )

    st.markdown("### Economic Impact Parameters")

    econ_col1, econ_col2, econ_col3 = st.columns(3)

    with econ_col1:
        reroute_cost_rate = st.number_input(
            "Reroute Cost Rate",
            min_value=0.0,
            value=1.0,
            step=0.5,
            key="cascade_reroute_cost_rate",
            help="Cost multiplier applied to added route cost for delivered demand.",
        )

    with econ_col2:
        delay_penalty_rate = st.number_input(
            "Delay Penalty Rate",
            min_value=0.0,
            value=2.0,
            step=0.5,
            key="cascade_delay_penalty_rate",
            help="Penalty multiplier applied to added route cost for delivered demand.",
        )

    with econ_col3:
        unmet_demand_loss_rate = st.number_input(
            "Unmet Demand Loss Rate",
            min_value=0.0,
            value=5.0,
            step=0.5,
            key="cascade_unmet_demand_loss_rate",
            help="Loss applied per unit of unmet demand.",
        )

    run_cascade = st.button("Run Cascade Simulation", type="secondary")

    cascade_result = None
    step_metrics_df = None
    flow_impact_df = None
    cascade_overview = {}
    cascade_insight = ""

    if run_cascade:
        if builder_mode == "Upload Flows CSV":
            if not uploaded_flow_dicts:
                st.warning("Please upload a valid flows.csv before running cascade simulation.")
            else:
                disrupted_nodes_tuple = tuple(str(n) for n in disrupted_nodes)
                disrupted_edges_tuple = tuple(normalize_edge_tuple(edge) for edge in disrupted_edges)
                uploaded_flows_tuple = tuple((f["source"], f["target"], float(f["demand"])) for f in uploaded_flow_dicts)

                cascade_result, step_metrics_df, flow_impact_df = run_cascade_analysis_cached(
                    graph_signature=graph_signature,
                    selected_flows_tuple=uploaded_flows_tuple,
                    disrupted_nodes_tuple=disrupted_nodes_tuple,
                    disrupted_edges_tuple=disrupted_edges_tuple,
                    max_steps=int(max_steps),
                    default_capacity=float(default_capacity),
                    default_weight=1.0,
                    demand_per_flow=None,
                    _graph=graph,
                    flows_from_csv=True,
                    reroute_cost_rate=float(reroute_cost_rate),
                    delay_penalty_rate=float(delay_penalty_rate),
                    unmet_demand_loss_rate=float(unmet_demand_loss_rate),
                )

                cascade_overview = build_cascade_overview(cascade_result, step_metrics_df)
                cascade_insight = build_cascade_insight(
                    cascade_result,
                    flow_impact_df,
                    step_metrics_df,
                )

        else:
            if not selected_flows:
                st.warning("Please select at least one flow before running cascade simulation.")
            else:
                selected_flows_tuple = tuple((str(o), str(d)) for o, d in selected_flows)
                disrupted_nodes_tuple = tuple(str(n) for n in disrupted_nodes)
                disrupted_edges_tuple = tuple(normalize_edge_tuple(edge) for edge in disrupted_edges)

                cascade_result, step_metrics_df, flow_impact_df = run_cascade_analysis_cached(
                    graph_signature=graph_signature,
                    selected_flows_tuple=selected_flows_tuple,
                    disrupted_nodes_tuple=disrupted_nodes_tuple,
                    disrupted_edges_tuple=disrupted_edges_tuple,
                    max_steps=int(max_steps),
                    default_capacity=float(default_capacity),
                    default_weight=1.0,
                    demand_per_flow=float(demand_per_flow),
                    _graph=graph,
                    flows_from_csv=False,
                    reroute_cost_rate=float(reroute_cost_rate),
                    delay_penalty_rate=float(delay_penalty_rate),
                    unmet_demand_loss_rate=float(unmet_demand_loss_rate),
                )

                cascade_overview = build_cascade_overview(cascade_result, step_metrics_df)
                cascade_insight = build_cascade_insight(
                    cascade_result,
                    flow_impact_df,
                    step_metrics_df,
                )

    return {
        "selected_flows": selected_flows,
        "uploaded_flow_dicts": uploaded_flow_dicts,
        "disrupted_nodes": disrupted_nodes,
        "disrupted_edges": disrupted_edges,
        "cascade_result": cascade_result,
        "step_metrics_df": step_metrics_df,
        "flow_impact_df": flow_impact_df,
        "cascade_overview": cascade_overview,
        "cascade_insight": cascade_insight,
    }


def render_cascade_analysis_tab(
    cascade_result,
    step_metrics_df,
    cascade_overview,
    flow_impact_df,
    cascade_insight,
):
    st.subheader("Cascade Simulation")
    st.write("Simulate rerouting, overload propagation, cascading failures, and economic impact across the network.")

    if cascade_result is None or step_metrics_df is None:
        st.info("Configure a disruption scenario and run cascade simulation to view results.")
        return

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = st.columns(6)

    metric_col1.metric("Total Flows", cascade_overview.get("total_flows", 0))
    metric_col2.metric("Disrupted Flows", cascade_overview.get("disrupted_flows", 0))
    metric_col3.metric("Service Level", f"{cascade_overview.get('service_level', 0.0):.1%}")
    metric_col4.metric("Unmet Demand", f"{cascade_overview.get('unmet_demand', 0.0):.1f}")
    metric_col5.metric("Failed Nodes", cascade_overview.get("failed_node_count", 0))
    metric_col6.metric("Failed Edges", cascade_overview.get("failed_edge_count", 0))

    econ_metric_col1, econ_metric_col2, econ_metric_col3, econ_metric_col4 = st.columns(4)
    econ_metric_col1.metric("Reroute Cost", f"{cascade_overview.get('total_reroute_cost', 0.0):.2f}")
    econ_metric_col2.metric("Delay Penalty", f"{cascade_overview.get('total_delay_penalty', 0.0):.2f}")
    econ_metric_col3.metric("Unmet Demand Loss", f"{cascade_overview.get('total_unmet_demand_loss', 0.0):.2f}")
    econ_metric_col4.metric("Total Economic Impact", f"{cascade_overview.get('total_economic_impact', 0.0):.2f}")

    if cascade_insight:
        st.markdown("### Insight")
        st.info(cascade_insight)

    collapse_step = cascade_overview.get("collapse_step")
    if collapse_step is not None:
        st.warning(f"Network demand fully collapsed by step {collapse_step}.")
    else:
        st.success("No full demand collapse detected within the simulated steps.")

    st.markdown("### Step Metrics Table")
    st.dataframe(step_metrics_df, use_container_width=True)

    if step_metrics_df is not None and not step_metrics_df.empty:
        st.download_button(
            label="📥 Download Step Metrics (CSV)",
            data=step_metrics_df.to_csv(index=False),
            file_name="cascade_step_metrics.csv",
            mime="text/csv",
        )

    st.markdown("### Demand Progression")
    demand_cols = [c for c in ["routed_demand", "disrupted_demand"] if c in step_metrics_df.columns]
    if demand_cols:
        st.line_chart(step_metrics_df.set_index("step")[demand_cols], use_container_width=True)

    st.markdown("### Failure Progression")
    failure_cols = [c for c in ["cumulative_failed_edge_count", "cumulative_failed_node_count"] if c in step_metrics_df.columns]
    if failure_cols:
        st.line_chart(step_metrics_df.set_index("step")[failure_cols], use_container_width=True)

    st.markdown("### Flow Impact Table")
    if flow_impact_df is not None and not flow_impact_df.empty:
        st.dataframe(flow_impact_df, use_container_width=True)

        st.download_button(
            label="📥 Download Flow Impact Results (CSV)",
            data=flow_impact_df.to_csv(index=False),
            file_name="cascade_flow_impacts.csv",
            mime="text/csv",
        )
    else:
        st.info("No flow impact data available.")

    st.markdown("### Final Failed Components")
    final_col1, final_col2 = st.columns(2)

    with final_col1:
        st.write("**Failed Nodes**")
        failed_nodes = cascade_result.get("failed_nodes", [])
        if failed_nodes:
            st.write(", ".join(map(str, failed_nodes)))
        else:
            st.info("No nodes failed.")

    with final_col2:
        st.write("**Failed Edges**")
        failed_edges = cascade_result.get("failed_edges", [])
        if failed_edges:
            st.write(", ".join(format_edge_tuple(edge) for edge in failed_edges))
        else:
            st.info("No edges failed.")
