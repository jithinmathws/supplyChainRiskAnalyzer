import streamlit as st

DEFAULT_SESSION_STATE = {
    "graph_source": "default",
    "analysis_ran": False,
    "baseline_route_names": [],
    "baseline_route_ids": [],
    "baseline_time": None,
    "node_result_df": None,
    "edge_result_df": None,
    "scenario_node_summary_df": None,
    "scenario_edge_summary_df": None,
    "scenario_overview": {},
    "scenario_node_results_df": None,
    "scenario_edge_results_df": None,
    "selected_scenario_flows": [],
    "cascade_result": None,
    "cascade_step_metrics_df": None,
    "cascade_overview": {},
    "cascade_flow_impact_df": None,
    "cascade_insight": "",
    "uploaded_flow_dicts": None,
}


def initialize_session_state():
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value


def reset_analysis_state():
    for key, value in DEFAULT_SESSION_STATE.items():
        if key == "graph_source":
            continue
        st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value
