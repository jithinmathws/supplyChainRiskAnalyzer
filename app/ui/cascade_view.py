import streamlit as st
from services.cascade_service import build_cascade_overview, run_cascade_analysis_cached
from services.graph_service import get_available_scenario_flows, get_default_scenario_flows


def normalize_edge_tuple(edge):
    """
    Normalize disrupted edge tuples for cache-safe transport.

    Supports:
    - (u, v)
    - (u, v, key)
    """
    if len(edge) == 3:
        u, v, k = edge
        return (str(u), str(v), k)
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

    available_flows = get_available_scenario_flows(graph, node_options)
    flow_labels = [item["label"] for item in available_flows]

    builder_mode = st.radio(
        "Cascade Flow Input Mode",
        options=["Default Flows", "Custom Flows"],
        horizontal=True,
        key="cascade_builder_mode",
    )

    if builder_mode == "Default Flows":
        selected_flows = get_default_scenario_flows()
        st.info(
            "Default cascade set uses predefined origin-destination flows. "
            "You can switch to Custom Flows for manual selection."
        )
    else:
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
                edge_label_to_tuple[edge_label] = (str(u), str(v), k)
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

    run_cascade = st.button("Run Cascade Simulation", type="secondary")

    cascade_result = None
    step_metrics_df = None
    flow_impact_df = None
    cascade_overview = {}

    if run_cascade:
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
            )

            cascade_overview = build_cascade_overview(cascade_result, step_metrics_df)

    return {
        "selected_flows": selected_flows,
        "disrupted_nodes": disrupted_nodes,
        "disrupted_edges": disrupted_edges,
        "cascade_result": cascade_result,
        "step_metrics_df": step_metrics_df,
        "flow_impact_df": flow_impact_df,
        "cascade_overview": cascade_overview,
    }


def render_cascade_analysis_tab(cascade_result, step_metrics_df, cascade_overview, flow_impact_df):
    st.subheader("Cascade Simulation")
    st.write("Simulate rerouting, overload propagation, and cascading failures across the network.")

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

    collapse_step = cascade_overview.get("collapse_step")
    if collapse_step is not None:
        st.warning(f"Network demand fully collapsed by step {collapse_step}.")
    else:
        st.success("No full demand collapse detected within the simulated steps.")

    st.markdown("### Step Metrics Table")
    st.dataframe(step_metrics_df, use_container_width=True)

    st.markdown("### Demand Progression")
    demand_cols = [c for c in ["routed_demand", "disrupted_demand"] if c in step_metrics_df.columns]
    if demand_cols:
        st.line_chart(step_metrics_df.set_index("step")[demand_cols], use_container_width=True)

    st.markdown("### Failure Progression")
    failure_cols = [
        c
        for c in ["cumulative_failed_edge_count", "cumulative_failed_node_count"]
        if c in step_metrics_df.columns
    ]
    if failure_cols:
        st.line_chart(step_metrics_df.set_index("step")[failure_cols], use_container_width=True)

    st.markdown("### Flow Impact Table")
    if flow_impact_df is not None and not flow_impact_df.empty:
        st.dataframe(flow_impact_df, use_container_width=True)
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
