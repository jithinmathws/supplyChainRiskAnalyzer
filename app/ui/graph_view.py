import streamlit as st
import streamlit.components.v1 as components

from core.network_visualizer import NetworkVisualizer
from services.graph_service import enrich_graph_for_visualization


def extract_bottleneck_nodes(node_result_df, top_n=5):
    if node_result_df is None or node_result_df.empty:
        return []

    top_df = node_result_df.head(top_n)

    if "node_id" in top_df.columns:
        return [str(x) for x in top_df["node_id"].tolist()]

    if "node_name" in top_df.columns:
        return [str(x) for x in top_df["node_name"].tolist()]

    return []


def extract_failed_nodes_from_node_summary(node_scenario_summary_df, top_n=5):
    if node_scenario_summary_df is None or node_scenario_summary_df.empty:
        return []

    candidate_col = None
    sort_cols = []

    if "node_id" in node_scenario_summary_df.columns:
        candidate_col = "node_id"
    elif "node_name" in node_scenario_summary_df.columns:
        candidate_col = "node_name"

    if candidate_col is None:
        return []

    if "catastrophic_count" in node_scenario_summary_df.columns:
        sort_cols.append("catastrophic_count")
    if "avg_impact_score" in node_scenario_summary_df.columns:
        sort_cols.append("avg_impact_score")

    if sort_cols:
        summary_sorted = node_scenario_summary_df.sort_values(by=sort_cols, ascending=False)
    else:
        summary_sorted = node_scenario_summary_df.copy()

    return [str(x) for x in summary_sorted[candidate_col].head(top_n).tolist()]


def extract_failed_edges_from_edge_summary(edge_scenario_summary_df, top_n=5):
    if edge_scenario_summary_df is None or edge_scenario_summary_df.empty:
        return []

    if "edge_id" not in edge_scenario_summary_df.columns:
        return []

    sort_cols = []
    if "catastrophic_count" in edge_scenario_summary_df.columns:
        sort_cols.append("catastrophic_count")
    if "avg_impact_score" in edge_scenario_summary_df.columns:
        sort_cols.append("avg_impact_score")

    if sort_cols:
        summary_sorted = edge_scenario_summary_df.sort_values(by=sort_cols, ascending=False)
    else:
        summary_sorted = edge_scenario_summary_df.copy()

    failed_edges = []
    for edge_id in summary_sorted["edge_id"].head(top_n).tolist():
        edge_id_str = str(edge_id)

        if "->" in edge_id_str:
            parts = edge_id_str.split("->")
            if len(parts) == 2:
                failed_edges.append((parts[0].strip(), parts[1].strip()))
        elif "-" in edge_id_str:
            parts = edge_id_str.split("-")
            if len(parts) >= 2:
                failed_edges.append((parts[0].strip(), parts[1].strip()))

    return failed_edges


def render_graph_tab(graph, node_result_df, controls):
    st.header("📡 Network Visualization")
    st.write("Interactive network graph with bottleneck and scenario overlays.")

    scenario_node_summary_df = st.session_state.get("scenario_node_summary_df")
    scenario_edge_summary_df = st.session_state.get("scenario_edge_summary_df")

    bottleneck_nodes = extract_bottleneck_nodes(node_result_df, top_n=5)

    failed_nodes = []
    failed_edges = []

    if controls["network_overlay_mode"] == "Scenario View":
        if scenario_node_summary_df is None or scenario_node_summary_df.empty:
            st.warning("⚠️ No scenario overlay data available.")
        else:
            failed_nodes = extract_failed_nodes_from_node_summary(
                scenario_node_summary_df,
                top_n=5,
            )
            failed_edges = extract_failed_edges_from_edge_summary(
                scenario_edge_summary_df,
                top_n=5,
            )

    graph_viz = enrich_graph_for_visualization(
        graph,
        node_result_df=node_result_df,
        edge_result_df=st.session_state.get("edge_result_df"),
    )

    route_node_ids = st.session_state.get("baseline_route_ids", [])
    highlighted_edges = [
        (str(route_node_ids[i]), str(route_node_ids[i + 1]))
        for i in range(len(route_node_ids) - 1)
    ]

    st.markdown("### Visualization Settings Summary")
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    info_col1.info(f"Layout: {controls['layout_mode']}")
    info_col2.info(f"Node Size: {controls['node_size_by'] or 'fixed'}")
    info_col3.info(f"Node Color: {controls['node_color_by']}")
    info_col4.info(f"Edge Width: {controls['edge_width_by'] or 'fixed'}")

    visualizer = NetworkVisualizer(height="760px", width="100%")

    try:
        html_path = visualizer.generate_html(
            graph_viz,
            node_size_by=controls["node_size_by"],
            node_color_by=controls["node_color_by"],
            edge_width_by=controls["edge_width_by"],
            show_node_labels=controls["show_node_labels"],
            show_edge_labels=controls["show_edge_labels"],
            failed_nodes=failed_nodes,
            failed_edges=failed_edges,
            highlighted_nodes=route_node_ids,
            highlighted_edges=highlighted_edges,
            bottleneck_nodes=bottleneck_nodes,
            layout=controls["layout_mode"],
        )

        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        components.html(html_content, height=780, scrolling=True)

    except Exception as exc:
        st.error(f"Failed to render network visualization: {exc}")

    st.markdown("### Overlay Details")
    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.write("**Highlighted Baseline Route Nodes**")
        if route_node_ids:
            route_names = [graph.nodes[n].get("name", n) for n in route_node_ids]
            st.success(" → ".join(route_names))
        else:
            st.info("No baseline route highlight available.")

        st.write("**Top Bottleneck Nodes**")
        if bottleneck_nodes:
            st.write(", ".join(map(str, bottleneck_nodes)))
        else:
            st.info("No bottleneck nodes available.")

    with detail_col2:
        st.write("**Scenario Overlay Nodes**")
        if failed_nodes:
            st.write(", ".join(map(str, failed_nodes)))
        else:
            st.info("No scenario node overlay active.")

        st.write("**Scenario Overlay Edges**")
        if failed_edges:
            st.write(", ".join([f"{u} → {v}" for u, v in failed_edges]))
        else:
            st.info("No scenario edge overlay active.")
