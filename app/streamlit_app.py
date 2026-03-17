import streamlit as st
from services.analysis_service import run_baseline_analysis
from services.graph_service import (
    get_graph_signature,
    get_node_options,
    load_graph,
)
from ui.bottleneck_view import (
    render_edge_analysis_tab,
    render_executive_summary,
    render_node_analysis_tab,
)
from ui.cascade_view import render_cascade_analysis_tab, render_cascade_builder
from ui.graph_view import render_graph_tab
from ui.scenario_view import render_scenario_analysis_tab, render_scenario_builder
from ui.sidebar import render_sidebar
from utils.session_state import initialize_session_state, reset_analysis_state

st.set_page_config(page_title="Supply Chain Fragility Analyzer", layout="wide")
st.title("Supply Chain Fragility & Risk Analyzer")
st.write("Interactive analysis of node and edge disruptions in the supply chain network.")

initialize_session_state()

graph = st.session_state.get("graph")
if graph is None:
    graph = load_graph()
    st.session_state.graph_source = "default"

graph_signature = get_graph_signature(graph)
node_options = get_node_options(graph)
labels = list(node_options.keys())

controls = render_sidebar(node_options, labels)

# Re-read graph after sidebar actions, because user may have uploaded a new one
graph = st.session_state.get("graph")
if graph is None:
    graph = load_graph()
    st.session_state.graph_source = "default"

graph_signature = get_graph_signature(graph)
node_options = get_node_options(graph)
labels = list(node_options.keys())

source_label = st.session_state.get("graph_source", "default")
if source_label == "uploaded":
    st.success("Using uploaded graph for analysis.")
else:
    st.info("Using default sample graph for analysis.")

if len(labels) < 2:
    st.error("Graph must contain at least two nodes to run analysis.")
    st.stop()

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

current_selection = (origin_id, destination_id, graph_signature)

if "last_selection" not in st.session_state:
    st.session_state.last_selection = current_selection

if current_selection != st.session_state.last_selection:
    reset_analysis_state()
    st.session_state.last_selection = current_selection

run_analysis = st.button("Run Analysis", type="primary")

if run_analysis:
    if origin_id == destination_id:
        st.error("Origin and Destination must be different.")
        st.stop()

    with st.spinner("Running fragility analysis..."):
        try:
            analysis_result = run_baseline_analysis(graph, origin_id, destination_id)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        st.session_state.baseline_route_names = analysis_result["baseline_route_names"]
        st.session_state.baseline_route_ids = analysis_result["baseline_route_ids"]
        st.session_state.baseline_time = analysis_result["baseline_time"]
        st.session_state.node_result_df = analysis_result["node_result_df"]
        st.session_state.edge_result_df = analysis_result["edge_result_df"]
        st.session_state.analysis_ran = True

if st.session_state.analysis_ran:
    baseline_route_names = st.session_state.baseline_route_names
    baseline_time = st.session_state.baseline_time
    node_result_df = st.session_state.node_result_df
    edge_result_df = st.session_state.edge_result_df

    render_executive_summary(
        baseline_time=baseline_time,
        baseline_route_names=baseline_route_names,
        node_result_df=node_result_df,
        edge_result_df=edge_result_df,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Node Analysis",
            "Edge Analysis",
            "Scenario Analysis",
            "Cascade Simulation",
            "Network Visualization",
        ]
    )

    with tab1:
        render_node_analysis_tab(node_result_df)

    with tab2:
        render_edge_analysis_tab(edge_result_df)

    with tab3:
        scenario_data = render_scenario_builder(
            graph=graph,
            graph_signature=graph_signature,
            node_options=node_options,
        )

        st.session_state.scenario_node_results_df = scenario_data["node_scenario_results_df"]
        st.session_state.scenario_edge_results_df = scenario_data["edge_scenario_results_df"]
        st.session_state.scenario_node_summary_df = scenario_data["node_scenario_summary_df"]
        st.session_state.scenario_edge_summary_df = scenario_data["edge_scenario_summary_df"]
        st.session_state.scenario_overview = scenario_data["scenario_overview"]
        st.session_state.selected_scenario_flows = scenario_data["selected_flows"]

        render_scenario_analysis_tab(
            selected_flows=st.session_state.selected_scenario_flows,
            node_scenario_summary_df=st.session_state.scenario_node_summary_df,
            edge_scenario_summary_df=st.session_state.scenario_edge_summary_df,
            scenario_overview=st.session_state.scenario_overview,
        )

    with tab4:
        cascade_data = render_cascade_builder(
            graph=graph,
            graph_signature=graph_signature,
            node_options=node_options,
        )

        if cascade_data["cascade_result"] is not None:
            st.session_state.cascade_result = cascade_data["cascade_result"]
            st.session_state.cascade_step_metrics_df = cascade_data["step_metrics_df"]
            st.session_state.cascade_overview = cascade_data["cascade_overview"]
            st.session_state.cascade_flow_impact_df = cascade_data["flow_impact_df"]
            st.session_state.cascade_insight = cascade_data["cascade_insight"]

        render_cascade_analysis_tab(
            cascade_result=st.session_state.cascade_result,
            step_metrics_df=st.session_state.cascade_step_metrics_df,
            cascade_overview=st.session_state.cascade_overview,
            flow_impact_df=st.session_state.cascade_flow_impact_df,
            cascade_insight=st.session_state.cascade_insight,
        )

    with tab5:
        render_graph_tab(
            graph=graph,
            node_result_df=node_result_df,
            controls=controls,
        )
else:
    st.info("Run analysis to view bottleneck rankings, scenario analysis, and network visualization.")
