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
from ui.graph_view import render_graph_tab
from ui.scenario_view import render_scenario_analysis_tab, render_scenario_builder
from ui.sidebar import render_sidebar
from utils.session_state import initialize_session_state, reset_analysis_state


st.set_page_config(page_title="Supply Chain Fragility Analyzer", layout="wide")
st.title("Supply Chain Fragility & Risk Analyzer")
st.write("Interactive analysis of node and edge disruptions in the supply chain network.")

graph = load_graph()
graph_signature = get_graph_signature(graph)
node_options = get_node_options(graph)
labels = list(node_options.keys())

initialize_session_state()

controls = render_sidebar(node_options, labels)

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

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Node Analysis", "Edge Analysis", "Scenario Analysis", "Network Visualization"]
    )

    with tab1:
        render_node_analysis_tab(node_result_df)

    with tab2:
        render_edge_analysis_tab(edge_result_df)

    with tab3:
        render_scenario_analysis_tab(
            selected_flows=scenario_data["selected_flows"],
            node_scenario_summary_df=scenario_data["node_scenario_summary_df"],
            edge_scenario_summary_df=scenario_data["edge_scenario_summary_df"],
            scenario_overview=scenario_data["scenario_overview"],
        )

    with tab4:
        render_graph_tab(
            graph=graph,
            node_result_df=node_result_df,
            controls=controls,
        )
else:
    st.info("Run analysis to view bottleneck rankings, scenario analysis, and network visualization.")