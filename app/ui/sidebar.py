import streamlit as st


def render_sidebar(node_options, labels):
    """
    Render sidebar controls for graph visualization and app actions.

    Parameters
    ----------
    node_options : dict
        Mapping of display label -> node id.
    labels : list[str]
        Ordered node labels for origin/destination selection context.

    Returns
    -------
    dict
        UI control values consumed by graph_view and app shell.
    """
    del node_options, labels  # reserved for future sidebar expansion

    with st.sidebar:
        st.header("Controls")

        st.subheader("Visualization")
        layout_mode = st.selectbox(
            "Layout Mode",
            options=["physics", "hierarchical"],
            index=0,
            help="Network layout style for the interactive graph.",
        )

        node_size_by = st.selectbox(
            "Node Size By",
            options=["None", "degree", "betweenness", "fragility_score", "bottleneck_score"],
            index=3,
        )
        node_size_by = None if node_size_by == "None" else node_size_by

        node_color_by = st.selectbox(
            "Node Color By",
            options=["fragility_score", "betweenness", "degree", "bottleneck_score"],
            index=0,
        )

        edge_width_by = st.selectbox(
            "Edge Width By",
            options=["None", "flow", "weight", "criticality"],
            index=3,
        )
        edge_width_by = None if edge_width_by == "None" else edge_width_by

        show_node_labels = st.checkbox("Show Node Labels", value=True)
        show_edge_labels = st.checkbox("Show Edge Labels", value=False)

        st.subheader("Overlay")
        network_overlay_mode = st.radio(
            "Network Overlay Mode",
            options=["Baseline View", "Scenario View"],
            index=0,
            help="Overlay either baseline bottleneck context or scenario-driven failures.",
        )

        st.markdown("---")
        st.caption("Use the main panel to select origin, destination, and run analysis.")

    return {
        "layout_mode": layout_mode,
        "node_size_by": node_size_by,
        "node_color_by": node_color_by,
        "edge_width_by": edge_width_by,
        "show_node_labels": show_node_labels,
        "show_edge_labels": show_edge_labels,
        "network_overlay_mode": network_overlay_mode,
    }