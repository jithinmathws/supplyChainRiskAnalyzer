import streamlit as st
from services.graph_service import (
    get_graph_summary,
    load_uploaded_graph,
    preview_uploaded_csv,
)
from utils.session_state import reset_analysis_state


def render_sidebar(node_options, labels):
    del node_options, labels

    with st.sidebar:
        st.header("Controls")

        st.subheader("CSV Import")
        st.caption("Upload nodes.csv and edges.csv to analyze your own supply chain network.")

        nodes_file = st.file_uploader("Upload nodes.csv", type="csv", key="nodes_csv_upload")
        edges_file = st.file_uploader("Upload edges.csv", type="csv", key="edges_csv_upload")
        alt_edges_file = st.file_uploader(
            "Upload alternate_edges.csv (optional)",
            type="csv",
            key="alt_edges_csv_upload",
        )

        with st.expander("Required CSV columns"):
            st.markdown(
                """
**nodes.csv**
- `node_id`
- `name`
- `type`
- `location`
- `capacity`

**edges.csv**
- `source`
- `target`
- `transport_mode`
- `distance`
- `transport_time`

**Recommended for richer cascade analysis**
- `capacity`
- `edge_id`
                """
            )

        if nodes_file is not None:
            st.write("Preview: nodes.csv")
            st.dataframe(preview_uploaded_csv(nodes_file), use_container_width=True)

        if edges_file is not None:
            st.write("Preview: edges.csv")
            st.dataframe(preview_uploaded_csv(edges_file), use_container_width=True)

        if alt_edges_file is not None:
            st.write("Preview: alternate_edges.csv")
            st.dataframe(preview_uploaded_csv(alt_edges_file), use_container_width=True)

        col_load, col_reset = st.columns(2)

        with col_load:
            if st.button("Load Uploaded Graph", use_container_width=True):
                if nodes_file is None or edges_file is None:
                    st.error("Please upload both nodes.csv and edges.csv.")
                else:
                    try:
                        edge_files = [edges_file]
                        if alt_edges_file is not None:
                            edge_files.append(alt_edges_file)

                        graph = load_uploaded_graph(nodes_file, edge_files)
                        summary = get_graph_summary(graph)

                        reset_analysis_state()
                        st.session_state.graph = graph
                        st.session_state.graph_source = "uploaded"

                        st.success(f"Uploaded graph loaded: {summary['nodes']} nodes, {summary['edges']} edges.")
                    except Exception as exc:
                        st.error(f"Failed to load uploaded graph: {exc}")

        with col_reset:
            if st.button("Use Default Graph", use_container_width=True):
                reset_analysis_state()
                st.session_state.pop("graph", None)
                st.session_state.graph_source = "default"
                st.success("Switched back to default graph.")

        st.markdown("---")

        st.subheader("Visualization")

        presentation_mode = st.toggle(
            "🎥 Presentation Mode",
            value=False,
            help="Simplifies the graph for demos by reducing visual clutter.",
        )

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
            options=["Baseline View", "Scenario View", "Cascade View"],
            index=0,
            help="Overlay either baseline bottleneck context or scenario-driven failures.",
        )

        # Presentation Mode overrides
        if presentation_mode:
            layout_mode = "physics"
            node_size_by = "fragility_score"
            node_color_by = "fragility_score"
            edge_width_by = None
            show_node_labels = False
            show_edge_labels = False

            st.success("Presentation Mode enabled: simplified demo-friendly graph settings applied.")

        st.markdown("---")
        st.caption("Use the main panel to select origin, destination, and run analysis.")

    return {
        "presentation_mode": presentation_mode,
        "layout_mode": layout_mode,
        "node_size_by": node_size_by,
        "node_color_by": node_color_by,
        "edge_width_by": edge_width_by,
        "show_node_labels": show_node_labels,
        "show_edge_labels": show_edge_labels,
        "network_overlay_mode": network_overlay_mode,
    }
