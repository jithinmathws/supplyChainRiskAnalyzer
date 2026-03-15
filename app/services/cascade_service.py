import pandas as pd
import streamlit as st

from analysis.cascade_simulator import CascadeSimulator

def _normalize_flows(selected_flows, default_demand=40.0):
    normalized = []
    for origin_id, destination_id in selected_flows:
        normalized.append(
            {
                "source": str(origin_id),
                "target": str(destination_id),
                "demand": float(default_demand),
            }
        )
    return normalized

def _normalize_disrupted_edges(disrupted_edges):
    normalized = []
    for edge in disrupted_edges:
        if len(edge) == 3:
            u, v, k = edge
            normalized.append((str(u), str(v), k))
        elif len(edge) == 2:
            u, v = edge
            normalized.append((str(u), str(v)))
        else:
            raise ValueError(f"Invalid disrupted edge format: {edge}")
    return normalized

@st.cache_data(show_spinner=False)
def run_cascade_analysis_cached(
    graph_signature,
    selected_flows_tuple,
    disrupted_nodes_tuple,
    disrupted_edges_tuple,
    max_steps,
    default_capacity,
    default_weight,
    demand_per_flow,
    _graph,
):
    del graph_signature

    simulator = CascadeSimulator(
        _graph,
        default_capacity=float(default_capacity),
        default_weight=float(default_weight),
    )

    flow_dicts = _normalize_flows(
        selected_flows_tuple,
        default_demand=float(demand_per_flow),
    )

    disrupted_nodes = [str(node) for node in disrupted_nodes_tuple]
    disrupted_edges = _normalize_disrupted_edges(disrupted_edges_tuple)

    result = simulator.run_simulation(
        disrupted_nodes=disrupted_nodes,
        disrupted_edges=disrupted_edges,
        flows=flow_dicts,
        max_steps=int(max_steps),
    )

    # Step metrics dataframe
    step_metrics_df = pd.DataFrame(simulator.get_step_metrics_table(result))

    # ✅ NEW — Flow impact dataframe
    flow_impact_df = pd.DataFrame(simulator.get_flow_impact_table(result))

    return result, step_metrics_df, flow_impact_df

def build_cascade_overview(result, step_metrics_df):
    metrics = result.get("metrics", {})
    
    # Calculate collapse step directly from the dataframe
    collapse_step = None
    if not step_metrics_df.empty:
        collapsed_rows = step_metrics_df[step_metrics_df["routed_demand"] == 0]
        if not collapsed_rows.empty:
            collapse_step = collapsed_rows.iloc[0]["step"]

    return {
        "total_flows": metrics.get("total_flows", 0),
        "disrupted_flows": metrics.get("disrupted_flows", 0),
        "service_level": metrics.get("service_level", 0.0),
        "unmet_demand": metrics.get("unmet_demand", 0.0),
        "failed_node_count": metrics.get("failed_node_count", 0),
        "failed_edge_count": metrics.get("failed_edge_count", 0),
        "collapse_step": int(collapse_step) if collapse_step is not None else None,
    }