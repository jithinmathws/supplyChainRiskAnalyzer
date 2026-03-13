"""
Sidebar UI components for Streamlit app.
"""
import streamlit as st


def render_sidebar(node_options, labels):
    """Render all sidebar controls."""
    st.sidebar.header("Controls")
    st.sidebar.subheader("Network Visualization")

    layout_mode = st.sidebar.selectbox(
        "Layout",
        ["physics", "hierarchical", "static"],
        index=0,
    )

    node_size_by = st.sidebar.selectbox(
        "Node Size By",
        ["None", "betweenness", "degree", "fragility_score"],
        index=1,
    )

    node_color_by = st.sidebar.selectbox(
        "Node Color By",
        ["default", "node_type", "bottleneck", "fragility", "scenario_status"],
        index=2,
    )

    edge_width_by = st.sidebar.selectbox(
        "Edge Width By",
        ["None", "weight", "flow", "criticality"],
        index=1,
    )

    show_node_labels = st.sidebar.checkbox("Show Node Labels", True)
    show_edge_labels = st.sidebar.checkbox("Show Edge Labels", False)

    network_overlay_mode = st.sidebar.radio(
        "Visualization Overlay",
        ["Baseline Analysis", "Scenario View"],
        index=0,
    )

    node_size_by = None if node_size_by == "None" else node_size_by
    edge_width_by = None if edge_width_by == "None" else edge_width_by

    return {
        "layout_mode": layout_mode,
        "node_size_by": node_size_by,
        "node_color_by": node_color_by,
        "edge_width_by": edge_width_by,
        "show_node_labels": show_node_labels,
        "show_edge_labels": show_edge_labels,
        "network_overlay_mode": network_overlay_mode,
    }