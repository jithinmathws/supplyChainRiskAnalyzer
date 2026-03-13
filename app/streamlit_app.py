import networkx as nx
import streamlit as st
import streamlit.components.v1 as components

from core.graph_builder import SupplyChainGraph
from analysis.bottleneck_detection import BottleneckDetector
from analysis.edge_bottleneck_detection import EdgeBottleneckDetector
from analysis.scenario_analysis import ScenarioAnalyzer
from visualization.fragility_plots import FragilityVisualizer
from visualization.scenario_plots import ScenarioVisualizer
from core.network_visualizer import NetworkVisualizer


st.set_page_config(
    page_title="Supply Chain Fragility Analyzer",
    layout="wide",
)

st.title("Supply Chain Fragility & Risk Analyzer")
st.write("Interactive analysis of node and edge disruptions in the supply chain network.")


@st.cache_resource
def load_graph():
    builder = SupplyChainGraph(
        "data/nodes.csv",
        ["data/edges.csv", "data/alternate_edges.csv"],
    )
    builder.load_data()
    return builder.build_graph()


@st.cache_data(show_spinner=False)
def run_scenario_analysis_cached(graph_signature, selected_flows_tuple):
    """
    Cached scenario analysis helper.

    Parameters
    ----------
    graph_signature : tuple
        Lightweight signature of the graph so cache invalidates if topology changes.
    selected_flows_tuple : tuple
        Tuple of (origin_id, destination_id) flow tuples.

    Returns
    -------
    tuple
        node_scenario_results_df, edge_scenario_results_df,
        node_scenario_summary_df, edge_scenario_summary_df, scenario_overview
    """
    del graph_signature  # only used to invalidate cache when graph changes

    scenario_analyzer = ScenarioAnalyzer(G)

    node_scenario_results_df = scenario_analyzer.run_node_scenarios(
        list(selected_flows_tuple),
        exclude_terminals=True,
    )

    edge_scenario_results_df = scenario_analyzer.run_edge_scenarios(
        list(selected_flows_tuple),
        only_active_route_edges=False,
    )

    node_scenario_summary_df = scenario_analyzer.summarize_node_scenarios(
        node_scenario_results_df
    )

    edge_scenario_summary_df = scenario_analyzer.summarize_edge_scenarios(
        edge_scenario_results_df
    )

    scenario_overview = scenario_analyzer.scenario_overview(
        node_scenario_results_df,
        edge_scenario_results_df,
    )

    return (
        node_scenario_results_df,
        edge_scenario_results_df,
        node_scenario_summary_df,
        edge_scenario_summary_df,
        scenario_overview,
    )


def get_graph_signature(G):
    """
    Lightweight signature for scenario-analysis caching.
    """
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    edge_signature = tuple(
        sorted((str(u), str(v), str(data.get("transport_time", ""))) for u, v, data in G.edges(data=True))
    )
    return node_count, edge_count, edge_signature


def reset_analysis_state():
    st.session_state.analysis_ran = False
    st.session_state.baseline_route_names = []
    st.session_state.baseline_route_ids = []
    st.session_state.baseline_time = None
    st.session_state.node_result_df = None
    st.session_state.edge_result_df = None
    st.session_state.scenario_node_summary_df = None
    st.session_state.scenario_edge_summary_df = None
    st.session_state.scenario_overview = {}
    st.session_state.scenario_node_results_df = None
    st.session_state.scenario_edge_results_df = None


def get_baseline_route(G, source_id, target_id):
    """
    Returns:
    - route_ids: baseline shortest path node IDs
    - route_names: human-readable node names
    - total lead time

    Uses the fastest available edge between each source-target pair.
    """
    H = nx.DiGraph()

    for u, v, data in G.edges(data=True):
        weight = data.get("transport_time", float("inf"))

        if H.has_edge(u, v):
            if weight < H[u][v]["transport_time"]:
                H[u][v]["transport_time"] = weight
        else:
            H.add_edge(u, v, transport_time=weight)

    route_ids = nx.dijkstra_path(H, source_id, target_id, weight="transport_time")
    total_time = nx.dijkstra_path_length(H, source_id, target_id, weight="transport_time")

    route_names = [G.nodes[n].get("name", n) for n in route_ids]
    return route_ids, route_names, total_time


def get_node_options(G):
    options = {}
    for node_id, attrs in G.nodes(data=True):
        label = f"{node_id} - {attrs.get('name', node_id)}"
        options[label] = str(node_id)
    return options


def get_default_scenario_flows():
    return [
        ("3", "5"),  # Supplier A -> Warehouse D
        ("3", "2"),  # Supplier A -> Rotterdam Port
        ("4", "5"),  # Factory B -> Warehouse D
    ]


def get_available_scenario_flows(G, node_options):
    """
    Returns all reachable origin-destination pairs from current nodes.
    Excludes same-node pairs and unreachable directed flows.
    """
    flows = []
    items = list(node_options.items())

    for origin_label, origin_id in items:
        for destination_label, destination_id in items:
            origin_id = str(origin_id)
            destination_id = str(destination_id)

            if origin_id == destination_id:
                continue

            if nx.has_path(G, origin_id, destination_id):
                flows.append(
                    {
                        "label": f"{origin_label} → {destination_label}",
                        "flow": (origin_id, destination_id),
                    }
                )

    return flows


def enrich_graph_for_visualization(G, node_result_df=None, edge_result_df=None):
    """
    Add visualization-friendly attributes to a copy of the graph
    without mutating the original graph.
    """
    G_viz = G.copy()

    # ---- node attributes ----
    betweenness = nx.betweenness_centrality(G_viz)
    degree_dict = dict(G_viz.degree())

    for node in G_viz.nodes():
        G_viz.nodes[node]["betweenness"] = float(betweenness.get(node, 0.0))
        G_viz.nodes[node]["degree"] = float(degree_dict.get(node, 0))
        G_viz.nodes[node]["fragility_score"] = 0.0
        G_viz.nodes[node]["bottleneck_score"] = 0.0

        if "label" not in G_viz.nodes[node]:
            G_viz.nodes[node]["label"] = str(G_viz.nodes[node].get("name", node))

    if node_result_df is not None and not node_result_df.empty:
        node_name_to_score = {}
        if {"node_name", "impact_score"}.issubset(node_result_df.columns):
            node_name_to_score = dict(
                zip(node_result_df["node_name"], node_result_df["impact_score"])
            )

        node_id_to_score = {}
        if {"node_id", "impact_score"}.issubset(node_result_df.columns):
            node_id_to_score = {
                str(node_id): score
                for node_id, score in zip(
                    node_result_df["node_id"], node_result_df["impact_score"]
                )
            }

        for node, attrs in G_viz.nodes(data=True):
            node_id_str = str(node)
            node_name = attrs.get("name", node_id_str)

            score = 0.0
            if node_id_str in node_id_to_score:
                score = node_id_to_score[node_id_str]
            elif node_name in node_name_to_score:
                score = node_name_to_score[node_name]

            G_viz.nodes[node]["fragility_score"] = float(score)
            G_viz.nodes[node]["bottleneck_score"] = float(score)

    # ---- edge attributes ----
    edge_lookup = {}
    if edge_result_df is not None and not edge_result_df.empty:
        if {"edge_id", "impact_score"}.issubset(edge_result_df.columns):
            for _, row in edge_result_df.iterrows():
                edge_lookup[str(row["edge_id"])] = float(row["impact_score"])

    for u, v, attrs in G_viz.edges(data=True):
        attrs["weight"] = float(
            attrs.get(
                "weight",
                attrs.get("transport_time", attrs.get("flow", 1.0)),
            )
        )
        attrs["flow"] = float(attrs.get("flow", attrs.get("capacity", 1.0)))
        attrs["criticality"] = 0.0

        edge_id = attrs.get("edge_id")
        if edge_id is None:
            edge_id = f"{u}->{v}"
            attrs["edge_id"] = edge_id

        if str(edge_id) in edge_lookup:
            attrs["criticality"] = edge_lookup[str(edge_id)]

        if "label" not in attrs:
            attrs["label"] = str(edge_id)

    return G_viz


def extract_bottleneck_nodes(node_result_df, top_n=5):
    """
    Return top bottleneck node IDs if available, otherwise node names.
    """
    if node_result_df is None or node_result_df.empty:
        return []

    top_df = node_result_df.head(top_n)

    if "node_id" in top_df.columns:
        return [str(x) for x in top_df["node_id"].tolist()]

    if "node_name" in top_df.columns:
        return [str(x) for x in top_df["node_name"].tolist()]

    return []


def extract_failed_nodes_from_node_summary(node_scenario_summary_df, top_n=5):
    """
    Heuristic overlay for scenario mode:
    treat the most catastrophic/frequent node failures as highlighted failed nodes.
    """
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
        summary_sorted = node_scenario_summary_df.sort_values(
            by=sort_cols,
            ascending=False,
        )
    else:
        summary_sorted = node_scenario_summary_df.copy()

    return [str(x) for x in summary_sorted[candidate_col].head(top_n).tolist()]


def extract_failed_edges_from_edge_summary(edge_scenario_summary_df, top_n=5):
    """
    Heuristic overlay for scenario mode:
    treat the most catastrophic/frequent edge failures as highlighted failed edges.
    """
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
        summary_sorted = edge_scenario_summary_df.sort_values(
            by=sort_cols,
            ascending=False,
        )
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


# -----------------------------
# App Initialization
# -----------------------------
G = load_graph()
graph_signature = get_graph_signature(G)
node_options = get_node_options(G)
labels = list(node_options.keys())

if "analysis_ran" not in st.session_state:
    st.session_state.analysis_ran = False

if "baseline_route_names" not in st.session_state:
    st.session_state.baseline_route_names = []

if "baseline_route_ids" not in st.session_state:
    st.session_state.baseline_route_ids = []

if "baseline_time" not in st.session_state:
    st.session_state.baseline_time = None

if "node_result_df" not in st.session_state:
    st.session_state.node_result_df = None

if "edge_result_df" not in st.session_state:
    st.session_state.edge_result_df = None

if "scenario_node_summary_df" not in st.session_state:
    st.session_state.scenario_node_summary_df = None

if "scenario_edge_summary_df" not in st.session_state:
    st.session_state.scenario_edge_summary_df = None

if "scenario_overview" not in st.session_state:
    st.session_state.scenario_overview = {}

if "scenario_node_results_df" not in st.session_state:
    st.session_state.scenario_node_results_df = None

if "scenario_edge_results_df" not in st.session_state:
    st.session_state.scenario_edge_results_df = None


# -----------------------------
# Sidebar Controls
# -----------------------------
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


# -----------------------------
# Main Content Controls
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    origin_label = st.selectbox("Select Origin", labels, index=0)

with col2:
    destination_label = st.selectbox(
        "Select Destination",
        labels,
        index=1 if len(labels) > 1 else 0,
    )

origin_id = node_options[origin_label]
destination_id = node_options[destination_label]

current_selection = (origin_id, destination_id)

if "last_selection" not in st.session_state:
    st.session_state.last_selection = current_selection

if current_selection != st.session_state.last_selection:
    reset_analysis_state()
    st.session_state.last_selection = current_selection

run_analysis = st.button("Run Analysis", type="primary")


# -----------------------------
# Execute Single-Scenario Analysis
# -----------------------------
if run_analysis:
    if origin_id == destination_id:
        st.error("Origin and Destination must be different.")
        st.stop()

    with st.spinner("Running fragility analysis..."):
        try:
            baseline_route_ids, baseline_route_names, baseline_time = get_baseline_route(
                G,
                origin_id,
                destination_id,
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            st.error("No valid baseline route exists between the selected origin and destination.")
            st.stop()

        node_detector = BottleneckDetector(G)
        edge_detector = EdgeBottleneckDetector(G)

        node_result_df = node_detector.rank_node_bottlenecks(
            source_id=origin_id,
            target_id=destination_id,
            exclude_terminals=True,
        )

        edge_result_df = edge_detector.rank_edge_bottlenecks(
            source_id=origin_id,
            target_id=destination_id,
            only_active_route_edges=False,
        )

        st.session_state.baseline_route_names = baseline_route_names
        st.session_state.baseline_route_ids = baseline_route_ids
        st.session_state.baseline_time = baseline_time
        st.session_state.node_result_df = node_result_df
        st.session_state.edge_result_df = edge_result_df
        st.session_state.analysis_ran = True


# -----------------------------
# Render Dashboard
# -----------------------------
if st.session_state.analysis_ran:
    baseline_route_names = st.session_state.baseline_route_names
    baseline_route_ids = st.session_state.baseline_route_ids
    baseline_time = st.session_state.baseline_time
    node_result_df = st.session_state.node_result_df
    edge_result_df = st.session_state.edge_result_df

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

    # -----------------------------
    # Shared Scenario Builder + Computation
    # -----------------------------
    st.markdown("---")
    st.subheader("Scenario Builder")

    available_flows = get_available_scenario_flows(G, node_options)
    flow_labels = [item["label"] for item in available_flows]

    builder_mode = st.radio(
        "Scenario Input Mode",
        options=["Default Flows", "Custom Flows"],
        horizontal=True,
        key="scenario_builder_mode",
    )

    if builder_mode == "Default Flows":
        selected_flows = get_default_scenario_flows()

        st.info(
            "Default scenario set uses predefined origin-destination flows such as "
            "Supplier A → Warehouse D, Supplier A → Rotterdam Port, and Factory B → Warehouse D."
        )
    else:
        selected_flow_labels = st.multiselect(
            "Select one or more scenario flows",
            options=flow_labels,
            default=flow_labels[:3] if len(flow_labels) >= 3 else flow_labels,
            key="scenario_flow_selection",
        )

        selected_flows = [
            item["flow"]
            for item in available_flows
            if item["label"] in selected_flow_labels
        ]

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
        ) = run_scenario_analysis_cached(graph_signature, selected_flows_tuple)

    st.session_state.scenario_node_results_df = node_scenario_results_df
    st.session_state.scenario_edge_results_df = edge_scenario_results_df
    st.session_state.scenario_node_summary_df = node_scenario_summary_df
    st.session_state.scenario_edge_summary_df = edge_scenario_summary_df
    st.session_state.scenario_overview = scenario_overview

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Node Analysis", "Edge Analysis", "Scenario Analysis", "Network Visualization"]
    )

    # -----------------------------
    # TAB 1: Node Analysis
    # -----------------------------
    with tab1:
        st.subheader("Node Bottleneck Ranking")

        node_display_cols = [
            "node_name",
            "status",
            "impact_score",
            "impact_category",
            "lead_time_increase",
        ]

        available_node_cols = [c for c in node_display_cols if c in node_result_df.columns]

        st.dataframe(
            node_result_df[available_node_cols],
            use_container_width=True,
        )

        node_visualizer = FragilityVisualizer(
            node_result_df,
            label_column="node_name",
            entity_name="Supply Chain Node",
        )

        col_plot1, col_plot2 = st.columns(2)

        with col_plot1:
            st.plotly_chart(
                node_visualizer.plot_impact_score(
                    title="Node Vulnerability (Impact Score)"
                ),
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

    # -----------------------------
    # TAB 2: Edge Analysis
    # -----------------------------
    with tab2:
        st.subheader("Edge Bottleneck Ranking")

        edge_display_cols = [
            "edge_id",
            "status",
            "impact_score",
            "impact_category",
            "lead_time_increase",
        ]

        available_edge_cols = [c for c in edge_display_cols if c in edge_result_df.columns]

        st.dataframe(
            edge_result_df[available_edge_cols],
            use_container_width=True,
        )

        edge_visualizer = FragilityVisualizer(
            edge_result_df,
            label_column="edge_id",
            entity_name="Transport Link",
        )

        col_plot3, col_plot4 = st.columns(2)

        with col_plot3:
            st.plotly_chart(
                edge_visualizer.plot_impact_score(
                    title="Link Vulnerability (Impact Score)"
                ),
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

    # -----------------------------
    # TAB 3: Scenario Analysis
    # -----------------------------
    with tab3:
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
                        node_scenario_visualizer.plot_catastrophic_count(
                            title="Node Catastrophic Failure Count"
                        ),
                        use_container_width=True,
                    )

                with node_chart_col2:
                    st.plotly_chart(
                        node_scenario_visualizer.plot_average_impact(
                            title="Node Average Impact Score"
                        ),
                        use_container_width=True,
                    )

            if scenario_mode in ["Both", "Edge Summary"]:
                st.markdown("#### Edge Scenario Charts")

                edge_chart_col1, edge_chart_col2 = st.columns(2)

                with edge_chart_col1:
                    st.plotly_chart(
                        edge_scenario_visualizer.plot_catastrophic_count(
                            title="Edge Catastrophic Failure Count"
                        ),
                        use_container_width=True,
                    )

                with edge_chart_col2:
                    st.plotly_chart(
                        edge_scenario_visualizer.plot_average_impact(
                            title="Edge Average Impact Score"
                        ),
                        use_container_width=True,
                    )
        else:
            st.info("Select at least one scenario flow to run scenario analysis.")

    # -----------------------------
    # TAB 4: Network Visualization
    # -----------------------------
    with tab4:
        st.header("📡 Network Visualization")
        st.write("Interactive network graph with bottleneck and scenario overlays.")

        scenario_node_summary_df = st.session_state.get("scenario_node_summary_df")
        scenario_edge_summary_df = st.session_state.get("scenario_edge_summary_df")

        bottleneck_nodes = extract_bottleneck_nodes(node_result_df, top_n=5)

        failed_nodes = []
        failed_edges = []

        if network_overlay_mode == "Scenario View":
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

        G_viz = enrich_graph_for_visualization(
            G,
            node_result_df=node_result_df,
            edge_result_df=edge_result_df,
        )

        route_node_ids = st.session_state.get("baseline_route_ids", [])
        highlighted_edges = [
            (str(route_node_ids[i]), str(route_node_ids[i + 1]))
            for i in range(len(route_node_ids) - 1)
        ]

        st.markdown("### Visualization Settings Summary")
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        info_col1.info(f"Layout: {layout_mode}")
        info_col2.info(f"Node Size: {node_size_by or 'fixed'}")
        info_col3.info(f"Node Color: {node_color_by}")
        info_col4.info(f"Edge Width: {edge_width_by or 'fixed'}")

        visualizer = NetworkVisualizer(height="760px", width="100%")

        try:
            html_path = visualizer.generate_html(
                G_viz,
                node_size_by=node_size_by,
                node_color_by=node_color_by,
                edge_width_by=edge_width_by,
                show_node_labels=show_node_labels,
                show_edge_labels=show_edge_labels,
                failed_nodes=failed_nodes,
                failed_edges=failed_edges,
                highlighted_nodes=route_node_ids,
                highlighted_edges=highlighted_edges,
                bottleneck_nodes=bottleneck_nodes,
                layout=layout_mode,
            )

            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            components.html(html_content, height=780, scrolling=True)

        except Exception as e:
            st.error(f"Failed to render network visualization: {e}")

        st.markdown("### Overlay Details")

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            st.write("**Highlighted Baseline Route Nodes**")
            if route_node_ids:
                route_names = [G.nodes[n].get("name", n) for n in route_node_ids]
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
else:
    st.info("Run analysis to view bottleneck rankings, scenario analysis, and network visualization.")