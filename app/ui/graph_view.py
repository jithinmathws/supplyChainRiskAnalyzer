import streamlit as st
import streamlit.components.v1 as components
from services.graph_service import enrich_graph_for_visualization

from core.network_visualizer import NetworkVisualizer


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


def normalize_edges_for_visualization(edges):
    """
    Convert edge tuples into 2-tuple form for visualization.

    Supports:
    - (u, v)
    - (u, v, key) -> (u, v)

    Returns
    -------
    list[tuple[str, str]]
    """
    normalized = []
    seen = set()

    for edge in edges:
        if len(edge) == 3:
            u, v, _ = edge
            edge_2 = (str(u), str(v))
        elif len(edge) == 2:
            u, v = edge
            edge_2 = (str(u), str(v))
        else:
            continue

        if edge_2 not in seen:
            seen.add(edge_2)
            normalized.append(edge_2)

    return normalized


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


def extract_rerouted_edges_from_flow_impact(flow_impact_df):
    """
    Extract final path edges for rerouted flows from cascade flow impact table.
    """
    if flow_impact_df is None or flow_impact_df.empty:
        return []

    if "status" not in flow_impact_df.columns or "final_path" not in flow_impact_df.columns:
        return []

    rerouted_df = flow_impact_df[flow_impact_df["status"] == "rerouted"]

    edges = []
    for path_str in rerouted_df["final_path"].dropna().tolist():
        nodes = [node.strip() for node in str(path_str).split("->")]
        nodes = [node.strip() for node in nodes if node.strip()]
        if len(nodes) >= 2:
            for i in range(len(nodes) - 1):
                edges.append((nodes[i], nodes[i + 1]))

    # deduplicate while preserving order
    seen = set()
    unique_edges = []
    for edge in edges:
        if edge not in seen:
            seen.add(edge)
            unique_edges.append(edge)

    return unique_edges


def render_graph_tab(graph, node_result_df, controls):
    st.header("📡 Network Visualization")
    st.write("Interactive network graph with bottleneck, scenario, and cascade overlays.")

    scenario_node_summary_df = st.session_state.get("scenario_node_summary_df")
    scenario_edge_summary_df = st.session_state.get("scenario_edge_summary_df")

    cascade_result = st.session_state.get("cascade_result")
    cascade_flow_impact_df = st.session_state.get("cascade_flow_impact_df")

    bottleneck_nodes = extract_bottleneck_nodes(node_result_df, top_n=5)

    failed_nodes = []
    failed_edges = []
    rerouted_edges = []

    overlay_mode = controls.get("network_overlay_mode", "Baseline View")

    if overlay_mode == "Scenario View":
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

    elif overlay_mode == "Cascade View":
        if cascade_result is None:
            st.warning("⚠️ No cascade overlay data available.")
        else:
            failed_nodes = [str(x) for x in cascade_result.get("failed_nodes", [])]
            failed_edges = normalize_edges_for_visualization(cascade_result.get("failed_edges", []))
            rerouted_edges = normalize_edges_for_visualization(
                extract_rerouted_edges_from_flow_impact(cascade_flow_impact_df)
            )

    graph_viz = enrich_graph_for_visualization(
        graph,
        node_result_df=node_result_df,
        edge_result_df=st.session_state.get("edge_result_df"),
    )

    route_node_ids = [str(x) for x in st.session_state.get("baseline_route_ids", [])]
    highlighted_edges = [
        (str(route_node_ids[i]), str(route_node_ids[i + 1])) for i in range(len(route_node_ids) - 1)
    ]

    if overlay_mode == "Cascade View":
        combined_highlighted_edges = rerouted_edges
    else:
        combined_highlighted_edges = highlighted_edges
    combined_highlighted_edges = normalize_edges_for_visualization(combined_highlighted_edges)

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
            highlighted_edges=combined_highlighted_edges,
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
            route_names = [graph.nodes[n].get("name", n) if n in graph.nodes else n for n in route_node_ids]
            st.success(" → ".join(map(str, route_names)))
        else:
            st.info("No baseline route highlight available.")

        st.write("**Top Bottleneck Nodes**")
        if bottleneck_nodes:
            st.write(", ".join(map(str, bottleneck_nodes)))
        else:
            st.info("No bottleneck nodes available.")

        st.write("**Rerouted Flow Edges (Cascade)**")
        if rerouted_edges:
            st.write(", ".join(format_edge_tuple(edge) for edge in rerouted_edges))
        else:
            st.info("No rerouted flow overlay active.")

    with detail_col2:
        st.write(f"**{overlay_mode} Nodes**")
        if failed_nodes:
            st.write(", ".join(map(str, failed_nodes)))
        else:
            st.info("No node overlay active.")

        st.write(f"**{overlay_mode} Edges**")
        if failed_edges:
            st.write(", ".join(format_edge_tuple(edge) for edge in failed_edges))
        else:
            st.info("No edge overlay active.")
