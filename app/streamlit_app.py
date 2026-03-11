import networkx as nx
import streamlit as st

from core.graph_builder import SupplyChainGraph
from analysis.bottleneck_detection import BottleneckDetector
from analysis.edge_bottleneck_detection import EdgeBottleneckDetector
from analysis.scenario_analysis import ScenarioAnalyzer
from visualization.fragility_plots import FragilityVisualizer
from visualization.scenario_plots import ScenarioVisualizer

st.set_page_config(
    page_title="Supply Chain Fragility Analyzer",
    layout="wide"
)

st.title("Supply Chain Fragility & Risk Analyzer")
st.write("Interactive analysis of node and edge disruptions in the supply chain network.")

@st.cache_resource
def load_graph():
    builder = SupplyChainGraph(
        "data/nodes.csv",
        ["data/edges.csv", "data/alternate_edges.csv"]
    )
    builder.load_data()
    return builder.build_graph()

def get_baseline_route(G, source_id, target_id):
    """Returns the baseline shortest path and total lead time."""
    H = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        weight = data.get("transport_time", float("inf"))
        if H.has_edge(u, v):
            if weight < H[u][v]["transport_time"]:
                H[u][v]["transport_time"] = weight
        else:
            H.add_edge(u, v, transport_time=weight)

    path = nx.dijkstra_path(H, source_id, target_id, weight="transport_time")
    time = nx.dijkstra_path_length(H, source_id, target_id, weight="transport_time")
    route_names = [G.nodes[n].get("name", n) for n in path]
    return route_names, time

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

# --- App Initialization ---
G = load_graph()
node_options = get_node_options(G)
labels = list(node_options.keys())

# --- Sidebar or Top Controls ---
col1, col2 = st.columns(2)
with col1:
    origin_label = st.selectbox("Select Origin", labels, index=0)
with col2:
    destination_label = st.selectbox("Select Destination", labels, index=1 if len(labels) > 1 else 0)

origin_id = node_options[origin_label]
destination_id = node_options[destination_label]

current_selection = (origin_id, destination_id)

if "last_selection" not in st.session_state:
    st.session_state.last_selection = current_selection

if current_selection != st.session_state.last_selection:
    st.session_state.analysis_ran = False
    st.session_state.last_selection = current_selection

# Initialize session state flags
if "analysis_ran" not in st.session_state:
    st.session_state.analysis_ran = False

run_analysis = st.button("Run Analysis", type="primary")

# --- Execute Analysis ---
if run_analysis:
    if origin_id == destination_id:
        st.error("Origin and Destination must be different.")
        st.stop()

    with st.spinner("Running fragility analysis..."):
        try:
            baseline_route, baseline_time = get_baseline_route(G, origin_id, destination_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            st.error("No valid baseline route exists between the selected origin and destination.")
            st.stop()

        # Initialize Analyzers
        node_detector = BottleneckDetector(G)
        edge_detector = EdgeBottleneckDetector(G)
        scenario_analyzer = ScenarioAnalyzer(G)
        scenario_flows = get_default_scenario_flows()

        # Save all results to session state
        st.session_state.baseline_route = baseline_route
        st.session_state.baseline_time = baseline_time
        
        st.session_state.node_result_df = node_detector.rank_node_bottlenecks(
            source_id=origin_id, target_id=destination_id, exclude_terminals=True
        )
        st.session_state.edge_result_df = edge_detector.rank_edge_bottlenecks(
            source_id=origin_id, target_id=destination_id, only_active_route_edges=False
        )
        
        node_scenario_results_df = scenario_analyzer.run_node_scenarios(scenario_flows, exclude_terminals=True)
        edge_scenario_results_df = scenario_analyzer.run_edge_scenarios(scenario_flows, only_active_route_edges=False)
        
        st.session_state.node_scenario_summary_df = scenario_analyzer.summarize_node_scenarios(node_scenario_results_df)
        st.session_state.edge_scenario_summary_df = scenario_analyzer.summarize_edge_scenarios(edge_scenario_results_df)
        st.session_state.scenario_overview = scenario_analyzer.scenario_overview(node_scenario_results_df, edge_scenario_results_df)
        
        st.session_state.analysis_ran = True

# --- Display Dashboard (Only if analysis has been run) ---
if st.session_state.analysis_ran:
    st.markdown("---")
    st.subheader("Executive Summary")

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns([1, 2, 1, 1])
    with summary_col1:
        st.metric("Baseline Lead Time", f"{st.session_state.baseline_time} days")
    with summary_col2:
        st.write("**Baseline Route**")
        st.info(" → ".join(st.session_state.baseline_route))
    with summary_col3:
        if not st.session_state.node_result_df.empty:
            st.metric("Most Critical Node", st.session_state.node_result_df.iloc[0]["node_name"])
        else:
            st.metric("Most Critical Node", "N/A")
    with summary_col4:
        if not st.session_state.edge_result_df.empty:
            st.metric("Most Critical Edge", st.session_state.edge_result_df.iloc[0]["edge_id"])
        else:
            st.metric("Most Critical Edge", "N/A")

    tab1, tab2, tab3 = st.tabs(["Node Analysis", "Edge Analysis", "Scenario Analysis"])

    # --- TAB 1: Node Analysis ---
    with tab1:
        st.subheader("Node Bottleneck Ranking")
        node_display_cols = ["node_name", "status", "impact_score", "impact_category", "lead_time_increase"]
        st.dataframe(st.session_state.node_result_df[node_display_cols], use_container_width=True)

        node_visualizer = FragilityVisualizer(
            st.session_state.node_result_df, label_column="node_name", entity_name="Supply Chain Node"
        )
        
        col_plot1, col_plot2 = st.columns(2)
        with col_plot1:
            st.plotly_chart(node_visualizer.plot_impact_score(title="Node Vulnerability (Impact Score)"), use_container_width=True)
        with col_plot2:
            try:
                st.plotly_chart(node_visualizer.plot_lead_time_increase(title="Node Delay Impact", include_zero_delay=False), use_container_width=True)
            except ValueError:
                st.info("No rerouted node delays to display.")

    # --- TAB 2: Edge Analysis ---
    with tab2:
        st.subheader("Edge Bottleneck Ranking")
        edge_display_cols = ["edge_id", "status", "impact_score", "impact_category", "lead_time_increase"]
        st.dataframe(st.session_state.edge_result_df[edge_display_cols], use_container_width=True)

        edge_visualizer = FragilityVisualizer(
            st.session_state.edge_result_df, label_column="edge_id", entity_name="Transport Link"
        )

        col_plot3, col_plot4 = st.columns(2)
        with col_plot3:
            st.plotly_chart(edge_visualizer.plot_impact_score(title="Link Vulnerability (Impact Score)"), use_container_width=True)
        with col_plot4:
            try:
                st.plotly_chart(edge_visualizer.plot_lead_time_increase(title="Link Delay Impact", include_zero_delay=False), use_container_width=True)
            except ValueError:
                st.info("No rerouted edge delays to display.")

    # --- TAB 3: Scenario Analysis ---
    with tab3:
        st.subheader("Scenario Analysis")
        st.write("Compare recurring fragility patterns across multiple source-destination flows.")

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        scenarios_eval = st.session_state.scenario_overview.get("node_scenarios_evaluated", 0)
        crit_node = st.session_state.scenario_overview.get("most_critical_node", "N/A")
        crit_edge = st.session_state.scenario_overview.get("most_critical_edge", "N/A")
        
        avg_impact = 0.0
        if not st.session_state.node_scenario_summary_df.empty:
            avg_impact = round(st.session_state.node_scenario_summary_df["avg_impact_score"].mean(), 2)

        metric_col1.metric("Scenarios Evaluated", scenarios_eval)
        metric_col2.metric("Most Critical Node", crit_node or "N/A")
        metric_col3.metric("Most Critical Edge", crit_edge or "N/A")
        metric_col4.metric("Avg Impact Score", avg_impact)
        
        scenario_mode = st.radio(
            "View Scenario Summaries",
            options=["Both", "Node Summary", "Edge Summary"],
            horizontal=True,
        )

        if scenario_mode in ["Both", "Node Summary"]:
            st.markdown("#### Node Scenario Summary")
            st.dataframe(st.session_state.node_scenario_summary_df, use_container_width=True)

        if scenario_mode in ["Both", "Edge Summary"]:
            st.markdown("#### Edge Scenario Summary")
            st.dataframe(st.session_state.edge_scenario_summary_df, use_container_width=True)

        st.markdown("### Scenario Charts")
        node_scenario_visualizer = ScenarioVisualizer(
            st.session_state.node_scenario_summary_df,
            label_column="node_name",
            entity_name="Supply Chain Node"
        )
        edge_scenario_visualizer = ScenarioVisualizer(
            st.session_state.edge_scenario_summary_df,
            label_column="edge_id",
            entity_name="Transport Link"
        )
        if scenario_mode in ["Both", "Node Summary"]:
            st.markdown("#### Node Scenario Charts")
            node_chart_col1, node_chart_col2 = st.columns(2)
            with node_chart_col1:
                st.plotly_chart(
                    node_scenario_visualizer.plot_catastrophic_count(
                        title="Node Catastrophic Failure Count"
                    ),
                    use_container_width=True
                )
            with node_chart_col2:
                st.plotly_chart(
                    node_scenario_visualizer.plot_average_impact(
                        title="Node Average Impact Score"
                    ),
                    use_container_width=True
                )
        if scenario_mode in ["Both", "Edge Summary"]:
            st.markdown("#### Edge Scenario Charts")
            edge_chart_col1, edge_chart_col2 = st.columns(2)
            with edge_chart_col1:
                st.plotly_chart(
                    edge_scenario_visualizer.plot_catastrophic_count(
                        title="Edge Catastrophic Failure Count"
                    ),
                    use_container_width=True
                )
            with edge_chart_col2:
                st.plotly_chart(
                    edge_scenario_visualizer.plot_average_impact(
                        title="Edge Average Impact Score"
                    ),
                    use_container_width=True
                )