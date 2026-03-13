import streamlit as st

from analysis.scenario_analysis import ScenarioAnalyzer


@st.cache_data(show_spinner=False)
def run_scenario_analysis_cached(graph_signature, selected_flows_tuple, _graph):
    """Cached scenario analysis helper."""
    del graph_signature

    scenario_analyzer = ScenarioAnalyzer(_graph)

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
