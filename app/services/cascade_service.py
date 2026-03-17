import pandas as pd
import streamlit as st

from analysis.cascade_simulator import CascadeSimulator


def _normalize_flows(selected_flows, default_demand=40.0, flows_from_csv=False):
    normalized = []

    if flows_from_csv:
        for source, target, demand in selected_flows:
            normalized.append(
                {
                    "source": str(source),
                    "target": str(target),
                    "demand": float(demand),
                }
            )
    else:
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
            normalized.append((str(u), str(v), str(k)))
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
    flows_from_csv=False,
    reroute_cost_rate=1.0,
    delay_penalty_rate=2.0,
    unmet_demand_loss_rate=5.0,
):
    del graph_signature

    simulator = CascadeSimulator(
        _graph,
        default_capacity=float(default_capacity),
        default_weight=float(default_weight),
        reroute_cost_rate=float(reroute_cost_rate),
        delay_penalty_rate=float(delay_penalty_rate),
        unmet_demand_loss_rate=float(unmet_demand_loss_rate),
    )

    if flows_from_csv:
        flow_dicts = _normalize_flows(
            selected_flows_tuple,
            flows_from_csv=True,
        )
    else:
        flow_dicts = _normalize_flows(
            selected_flows_tuple,
            default_demand=float(demand_per_flow),
            flows_from_csv=False,
        )

    disrupted_nodes = [str(node).strip() for node in disrupted_nodes_tuple]
    disrupted_edges = _normalize_disrupted_edges(disrupted_edges_tuple)

    result = simulator.run_simulation(
        disrupted_nodes=disrupted_nodes,
        disrupted_edges=disrupted_edges,
        flows=flow_dicts,
        max_steps=int(max_steps),
    )

    step_metrics_df = pd.DataFrame(simulator.get_step_metrics_table(result))
    flow_impact_df = pd.DataFrame(simulator.get_flow_impact_table(result))

    return result, step_metrics_df, flow_impact_df


def build_cascade_overview(result, step_metrics_df):
    metrics = result.get("metrics", {})

    collapse_step = None
    if step_metrics_df is not None and not step_metrics_df.empty:
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
        "total_reroute_cost": metrics.get("total_reroute_cost", 0.0),
        "total_delay_penalty": metrics.get("total_delay_penalty", 0.0),
        "total_unmet_demand_loss": metrics.get("total_unmet_demand_loss", 0.0),
        "total_economic_impact": metrics.get("total_economic_impact", 0.0),
        "collapse_step": int(collapse_step) if collapse_step is not None else None,
    }


def build_cascade_insight(result, flow_impact_df, step_metrics_df):
    """
    Build a compact human-readable insight summary for cascade results.
    """
    metrics = result.get("metrics", {})

    total_flows = int(metrics.get("total_flows", 0))
    disrupted_flows = int(metrics.get("disrupted_flows", 0))
    failed_nodes = int(metrics.get("failed_node_count", 0))
    failed_edges = int(metrics.get("failed_edge_count", 0))
    service_level = float(metrics.get("service_level", 0.0))

    total_economic_impact = float(metrics.get("total_economic_impact", 0.0))
    total_unmet_demand_loss = float(metrics.get("total_unmet_demand_loss", 0.0))

    rerouted_count = 0
    delivered_count = 0

    if flow_impact_df is not None and not flow_impact_df.empty and "status" in flow_impact_df.columns:
        rerouted_count = int((flow_impact_df["status"] == "rerouted").sum())
        delivered_count = int((flow_impact_df["status"] == "delivered").sum())

    secondary_failures = False
    if (
        step_metrics_df is not None
        and not step_metrics_df.empty
        and "step" in step_metrics_df.columns
        and "new_failed_edge_count" in step_metrics_df.columns
        and "new_failed_node_count" in step_metrics_df.columns
    ):
        later_steps = step_metrics_df[step_metrics_df["step"] > 0]
        if not later_steps.empty:
            secondary_failures = bool((later_steps["new_failed_edge_count"].sum() > 0) or (later_steps["new_failed_node_count"].sum() > 0))

    parts = []

    if total_flows > 0:
        parts.append(
            f"The disruption affected {disrupted_flows} of {total_flows} tracked flows, " f"leaving a service level of {service_level:.1%}."
        )

    if rerouted_count > 0:
        parts.append(
            f"{rerouted_count} surviving flow{'s were' if rerouted_count != 1 else ' was'} rerouted, "
            "indicating partial resilience through alternate paths."
        )
    elif delivered_count > 0:
        parts.append(f"{delivered_count} flow{'s remained' if delivered_count != 1 else ' remained'} serviceable " "without rerouting.")

    if secondary_failures:
        parts.append("Secondary failures occurred after the initial shock, showing that disruption propagated through the network.")
    else:
        parts.append("No secondary failures were observed beyond the initial disruption, suggesting the impact remained localized.")

    if failed_nodes > 0 or failed_edges > 0:
        parts.append(
            f"Final network losses included {failed_nodes} failed node{'s' if failed_nodes != 1 else ''} "
            f"and {failed_edges} failed edge{'s' if failed_edges != 1 else ''}."
        )

    if total_economic_impact > 0:
        parts.append(
            f"Estimated total economic impact was {total_economic_impact:.2f}, "
            f"including unmet demand loss of {total_unmet_demand_loss:.2f}."
        )

    return " ".join(parts)
