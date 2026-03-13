from __future__ import annotations

import math
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import networkx as nx
from pyvis.network import Network


class NetworkVisualizer:
    """
    Builds interactive network visualizations for the
    Supply Chain Fragility & Risk Analyzer.

    Features:
    - Base directed graph rendering
    - Node sizing by selected metric
    - Node coloring by selected mode
    - Edge thickness by selected metric
    - Scenario failure highlighting
    - Optional edge/node labels
    - HTML export for Streamlit embedding
    """

    DEFAULT_NODE_COLOR = "#6baed6"
    FAILED_NODE_COLOR = "#d62728"
    BOTTLENECK_NODE_COLOR = "#ff7f0e"
    SOURCE_NODE_COLOR = "#2ca02c"
    SINK_NODE_COLOR = "#1f77b4"
    NORMAL_EDGE_COLOR = "#9e9e9e"
    FAILED_EDGE_COLOR = "#d62728"
    HIGHLIGHT_EDGE_COLOR = "#ff7f0e"

    def __init__(
        self,
        height: str = "700px",
        width: str = "100%",
        directed: bool = True,
        bgcolor: str = "#ffffff",
        font_color: str = "#222222",
    ) -> None:
        self.height = height
        self.width = width
        self.directed = directed
        self.bgcolor = bgcolor
        self.font_color = font_color

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def build_pyvis_network(
        self,
        G: nx.DiGraph,
        node_size_by: Optional[str] = None,
        node_color_by: str = "default",
        edge_width_by: Optional[str] = None,
        show_node_labels: bool = True,
        show_edge_labels: bool = False,
        failed_nodes: Optional[Iterable[Any]] = None,
        failed_edges: Optional[Iterable[Tuple[Any, Any]]] = None,
        highlighted_nodes: Optional[Iterable[Any]] = None,
        highlighted_edges: Optional[Iterable[Tuple[Any, Any]]] = None,
        bottleneck_nodes: Optional[Iterable[Any]] = None,
        source_nodes: Optional[Iterable[Any]] = None,
        sink_nodes: Optional[Iterable[Any]] = None,
        layout: str = "physics",
    ) -> Network:
        """
        Build a Pyvis network from a NetworkX graph.

        Parameters
        ----------
        G : nx.DiGraph
            Input supply chain graph.
        node_size_by : str | None
            Node attribute used to size nodes.
            Example: "betweenness", "flow", "throughput", "fragility_score"
        node_color_by : str
            Coloring mode. Supported:
            - "default"
            - "node_type"
            - "bottleneck"
            - "fragility"
            - "scenario_status"
        edge_width_by : str | None
            Edge attribute used to control edge thickness.
            Example: "weight", "flow", "criticality"
        show_node_labels : bool
            Whether to show node labels.
        show_edge_labels : bool
            Whether to show edge labels.
        failed_nodes : iterable
            Nodes failed in the selected scenario.
        failed_edges : iterable[(u, v)]
            Edges failed in the selected scenario.
        highlighted_nodes : iterable
            Nodes to visually highlight.
        highlighted_edges : iterable[(u, v)]
            Edges to visually highlight.
        bottleneck_nodes : iterable
            Nodes identified as bottlenecks.
        source_nodes : iterable
            Source/supply nodes.
        sink_nodes : iterable
            Sink/demand nodes.
        layout : str
            "physics", "hierarchical", or "static"
        """
        failed_nodes_set = self._normalize_node_set(failed_nodes)
        failed_edges_set = self._normalize_edge_set(failed_edges)
        highlighted_nodes_set = self._normalize_node_set(highlighted_nodes)
        highlighted_edges_set = self._normalize_edge_set(highlighted_edges)
        bottleneck_nodes_set = self._normalize_node_set(bottleneck_nodes)
        source_nodes_set = self._normalize_node_set(source_nodes)
        sink_nodes_set = self._normalize_node_set(sink_nodes)

        net = Network(
            height=self.height,
            width=self.width,
            directed=self.directed,
            bgcolor=self.bgcolor,
            font_color=self.font_color,
        )

        self._apply_layout_settings(net, layout=layout)

        # Precompute scales
        node_sizes = self._compute_node_sizes(G, node_size_by=node_size_by)
        edge_widths = self._compute_edge_widths(G, edge_width_by=edge_width_by)

        # Add nodes
        for node, attrs in G.nodes(data=True):
            node_color = self._resolve_node_color(
                node=node,
                attrs=attrs,
                node_color_by=node_color_by,
                failed_nodes=failed_nodes_set,
                bottleneck_nodes=bottleneck_nodes_set,
                source_nodes=source_nodes_set,
                sink_nodes=sink_nodes_set,
            )

            border_width = 3 if node in highlighted_nodes_set else 1
            shape = "dot"
            size = node_sizes.get(node, 20)

            label = str(attrs.get("label", node)) if show_node_labels else ""
            title = self._build_node_tooltip(node=node, attrs=attrs)

            net.add_node(
                n_id=str(node),
                label=label,
                title=title,
                color=node_color,
                size=size,
                shape=shape,
                borderWidth=border_width,
            )

        # Add edges
        for u, v, attrs in G.edges(data=True):
            edge_key = (str(u), str(v))
            is_failed = edge_key in failed_edges_set
            is_highlighted = edge_key in highlighted_edges_set

            color = self.FAILED_EDGE_COLOR if is_failed else self.NORMAL_EDGE_COLOR
            if is_highlighted and not is_failed:
                color = self.HIGHLIGHT_EDGE_COLOR

            width = edge_widths.get(edge_key, 2)

            label = ""
            if show_edge_labels:
                label = self._resolve_edge_label(attrs)

            title = self._build_edge_tooltip(u=u, v=v, attrs=attrs)

            net.add_edge(
                str(u),
                str(v),
                label=label,
                title=title,
                color=color,
                width=width,
                arrows="to" if self.directed else "",
                dashes=is_failed,
            )

        return net

    def export_html(
        self,
        net: Network,
        output_path: Optional[str | Path] = None,
    ) -> str:
        """
        Export the Pyvis network to HTML and return the HTML file path.
        """
        if output_path is None:
            temp_dir = Path(tempfile.mkdtemp())
            output_path = temp_dir / "network_visualization.html"
        else:
            output_path = Path(output_path)

        net.write_html(str(output_path))
        return str(output_path)

    def generate_html(
        self,
        G: nx.DiGraph,
        output_path: Optional[str | Path] = None,
        **kwargs: Any,
    ) -> str:
        """
        Convenience method:
        build network -> export html -> return html path
        """
        net = self.build_pyvis_network(G, **kwargs)
        return self.export_html(net, output_path=output_path)

    # -------------------------------------------------------------------------
    # Node styling
    # -------------------------------------------------------------------------

    def _compute_node_sizes(
        self,
        G: nx.DiGraph,
        node_size_by: Optional[str] = None,
        min_size: float = 15.0,
        max_size: float = 45.0,
    ) -> Dict[Any, float]:
        if not node_size_by:
            return {node: 20.0 for node in G.nodes()}

        values: Dict[Any, float] = {}
        for node, attrs in G.nodes(data=True):
            raw = attrs.get(node_size_by, 0.0)
            values[node] = self._safe_float(raw, default=0.0)

        return self._scale_dict(values, out_min=min_size, out_max=max_size)

    def _resolve_node_color(
        self,
        node: Any,
        attrs: Dict[str, Any],
        node_color_by: str,
        failed_nodes: Set[str],
        bottleneck_nodes: Set[str],
        source_nodes: Set[str],
        sink_nodes: Set[str],
    ) -> str:
        node_str = str(node)

        if node_str in failed_nodes:
            return self.FAILED_NODE_COLOR

        if node_color_by == "default":
            return self.DEFAULT_NODE_COLOR

        if node_color_by == "scenario_status":
            if node_str in bottleneck_nodes:
                return self.BOTTLENECK_NODE_COLOR
            return self.DEFAULT_NODE_COLOR

        if node_color_by == "node_type":
            node_type = str(attrs.get("node_type", "")).lower()
            if node_str in source_nodes or node_type in {"source", "supplier", "origin"}:
                return self.SOURCE_NODE_COLOR
            if node_str in sink_nodes or node_type in {"sink", "demand", "destination", "customer"}:
                return self.SINK_NODE_COLOR
            if node_str in bottleneck_nodes:
                return self.BOTTLENECK_NODE_COLOR
            return self.DEFAULT_NODE_COLOR

        if node_color_by == "bottleneck":
            score = self._safe_float(attrs.get("bottleneck_score", 0.0), default=0.0)
            return self._interpolate_red(score)

        if node_color_by == "fragility":
            score = self._safe_float(attrs.get("fragility_score", 0.0), default=0.0)
            return self._interpolate_red(score)

        return self.DEFAULT_NODE_COLOR

    # -------------------------------------------------------------------------
    # Edge styling
    # -------------------------------------------------------------------------

    def _compute_edge_widths(
        self,
        G: nx.DiGraph,
        edge_width_by: Optional[str] = None,
        min_width: float = 1.0,
        max_width: float = 8.0,
    ) -> Dict[Tuple[str, str], float]:
        if not edge_width_by:
            return {(str(u), str(v)): 2.0 for u, v in G.edges()}

        values: Dict[Tuple[str, str], float] = {}
        for u, v, attrs in G.edges(data=True):
            raw = attrs.get(edge_width_by, 0.0)
            values[(str(u), str(v))] = self._safe_float(raw, default=0.0)

        return self._scale_dict(values, out_min=min_width, out_max=max_width)

    def _resolve_edge_label(self, attrs: Dict[str, Any]) -> str:
        for candidate in ("label", "weight", "flow", "capacity", "criticality"):
            if candidate in attrs:
                return f"{candidate}: {attrs[candidate]}"
        return ""

    # -------------------------------------------------------------------------
    # Tooltips
    # -------------------------------------------------------------------------

    def _build_node_tooltip(self, node: Any, attrs: Dict[str, Any]) -> str:
        lines = [f"<b>Node:</b> {node}"]
        for key, value in attrs.items():
            lines.append(f"<b>{key}:</b> {value}")
        return "<br>".join(lines)

    def _build_edge_tooltip(self, u: Any, v: Any, attrs: Dict[str, Any]) -> str:
        lines = [f"<b>Edge:</b> {u} → {v}"]
        for key, value in attrs.items():
            lines.append(f"<b>{key}:</b> {value}")
        return "<br>".join(lines)

    # -------------------------------------------------------------------------
    # Layout settings
    # -------------------------------------------------------------------------

    def _apply_layout_settings(self, net: Network, layout: str = "physics") -> None:
        layout = (layout or "physics").lower()

        if layout == "hierarchical":
            net.set_options(
                """
                const options = {
                  "layout": {
                    "hierarchical": {
                      "enabled": true,
                      "direction": "LR",
                      "sortMethod": "directed"
                    }
                  },
                  "physics": {
                    "enabled": false
                  },
                  "interaction": {
                    "hover": true,
                    "navigationButtons": true,
                    "keyboard": true
                  }
                }
                """
            )
            return

        if layout == "static":
            net.set_options(
                """
                const options = {
                  "physics": {
                    "enabled": false
                  },
                  "interaction": {
                    "hover": true,
                    "navigationButtons": true,
                    "keyboard": true
                  }
                }
                """
            )
            return

        net.set_options(
            """
            const options = {
              "physics": {
                "enabled": true,
                "barnesHut": {
                  "gravitationalConstant": -2000,
                  "centralGravity": 0.2,
                  "springLength": 140,
                  "springConstant": 0.04,
                  "damping": 0.09
                },
                "minVelocity": 0.75
              },
              "interaction": {
                "hover": true,
                "navigationButtons": true,
                "keyboard": true
              }
            }
            """
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _normalize_node_set(self, nodes: Optional[Iterable[Any]]) -> Set[str]:
        if not nodes:
            return set()
        return {str(node) for node in nodes}

    def _normalize_edge_set(
        self,
        edges: Optional[Iterable[Tuple[Any, Any]]],
    ) -> Set[Tuple[str, str]]:
        if not edges:
            return set()
        return {(str(u), str(v)) for u, v in edges}

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _scale_dict(
        self,
        values: Dict[Any, float],
        out_min: float,
        out_max: float,
    ) -> Dict[Any, float]:
        if not values:
            return {}

        vmin = min(values.values())
        vmax = max(values.values())

        if math.isclose(vmin, vmax):
            midpoint = (out_min + out_max) / 2
            return {k: midpoint for k in values}

        scaled: Dict[Any, float] = {}
        for key, value in values.items():
            scaled[key] = out_min + ((value - vmin) / (vmax - vmin)) * (out_max - out_min)
        return scaled

    def _interpolate_red(self, score: float) -> str:
        """
        Convert a score in [0, 1] (or any number, clamped) to a red intensity scale.
        """
        score = max(0.0, min(1.0, score))
        base_r, base_g, base_b = 255, 245, 240
        deep_r, deep_g, deep_b = 165, 15, 21

        r = int(base_r + (deep_r - base_r) * score)
        g = int(base_g + (deep_g - base_g) * score)
        b = int(base_b + (deep_b - base_b) * score)

        return f"rgb({r},{g},{b})"