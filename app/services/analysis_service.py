import networkx as nx

from analysis.bottleneck_detection import BottleneckDetector
from analysis.edge_bottleneck_detection import EdgeBottleneckDetector
from services.graph_service import get_baseline_route


def run_baseline_analysis(graph, origin_id, destination_id):
    """
    Run baseline route, node bottleneck, and edge bottleneck analysis.

    Returns
    -------
    dict
        {
            "baseline_route_ids": ...,
            "baseline_route_names": ...,
            "baseline_time": ...,
            "node_result_df": ...,
            "edge_result_df": ...,
        }
    """
    try:
        baseline_route_ids, baseline_route_names, baseline_time = get_baseline_route(
            graph,
            origin_id,
            destination_id,
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise ValueError(
            "No valid baseline route exists between the selected origin and destination."
        ) from exc

    node_detector = BottleneckDetector(graph)
    edge_detector = EdgeBottleneckDetector(graph)

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

    return {
        "baseline_route_ids": baseline_route_ids,
        "baseline_route_names": baseline_route_names,
        "baseline_time": baseline_time,
        "node_result_df": node_result_df,
        "edge_result_df": edge_result_df,
    }