import networkx as nx
from copy import deepcopy


class CascadeSimulator:
    """
    Capacity-aware cascading disruption simulator.

    Phase 2 logic:
    - Apply initial node/edge shocks
    - Recompute shortest paths for demand flows
    - Accumulate edge loads
    - Remove overloaded edges
    - Repeat until stable or max_steps reached
    """

    def __init__(
        self,
        G,
        default_capacity=100.0,
        default_weight=1.0,
    ):
        if not G.is_directed():
            raise ValueError("CascadeSimulator currently requires a directed graph (DiGraph).")

        self.original_graph = deepcopy(G)
        self.default_capacity = float(default_capacity)
        self.default_weight = float(default_weight)
        self._initialize_graph_attributes(self.original_graph)
        self.reset()

    # --------------------------------------------------
    # Setup
    # --------------------------------------------------

    def _initialize_graph_attributes(self, G):
        """
        Ensure every edge has required attributes.
        """
        for u, v, data in G.edges(data=True):
            data.setdefault("capacity", self.default_capacity)
            data.setdefault("weight", self.default_weight)

    def reset(self):
        """
        Reset simulation state.
        """
        self.G = deepcopy(self.original_graph)
        self.failed_nodes = set()
        self.failed_edges = set()
        self.timeline = []

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def run_simulation(
        self,
        disrupted_nodes=None,
        disrupted_edges=None,
        flows=None,
        max_steps=10,
    ):
        """
        Run the cascade simulation.

        Parameters
        ----------
        disrupted_nodes : list[str]
        disrupted_edges : list[tuple[str, str]]
        flows : list[dict]
            Example:
            [
                {"source": "A", "target": "D", "demand": 40},
                {"source": "B", "target": "E", "demand": 30},
            ]
        max_steps : int

        Returns
        -------
        dict
        """
        self.reset()

        disrupted_nodes = disrupted_nodes or []
        disrupted_edges = disrupted_edges or []
        flows = flows or []

        self._validate_flows(flows)

        # Initial shock
        self.apply_initial_shock(disrupted_nodes, disrupted_edges)

        # Cascade loop
        for step in range(max_steps):
            step_result = self._run_single_step(flows, step)
            self.timeline.append(step_result)

            if not step_result["new_failed_edges"] and not step_result["new_failed_nodes"]:
                break

        metrics = self.compute_metrics(flows)

        return {
            "timeline": self.timeline,
            "failed_nodes": sorted(self.failed_nodes),
            "failed_edges": sorted(self.failed_edges),
            "metrics": metrics,
        }

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def _validate_flows(self, flows):
        """
        Validate flow inputs against original graph.
        """
        for i, flow in enumerate(flows):
            if not isinstance(flow, dict):
                raise ValueError(
                    f"Flow at index {i} must be a dict like "
                    f"{{'source': 'A', 'target': 'D', 'demand': 40}}"
                )

            required_keys = {"source", "target", "demand"}
            missing = required_keys - set(flow.keys())
            if missing:
                raise ValueError(f"Flow {i} missing keys: {missing}")

            s, t = flow["source"], flow["target"]

            try:
                d = float(flow["demand"])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid demand for flow {i}: {flow['demand']}")

            if s not in self.original_graph or t not in self.original_graph:
                raise ValueError(f"Invalid flow: ({s}, {t}) not in original graph")
            if s == t:
                raise ValueError(f"Invalid flow: source and target are same for ({s}, {t})")
            if d < 0:
                raise ValueError(f"Invalid demand: {d}")

    # --------------------------------------------------
    # Initial shock
    # --------------------------------------------------

    def apply_initial_shock(self, disrupted_nodes, disrupted_edges):
        """
        Remove initially disrupted nodes and directed edges.
        """
        for n in disrupted_nodes:
            if self.G.has_node(n):
                self.G.remove_node(n)
                self.failed_nodes.add(n)

        for u, v in disrupted_edges:
            if self.G.has_edge(u, v):
                self.G.remove_edge(u, v)
                self.failed_edges.add((u, v))

    # --------------------------------------------------
    # Core step logic
    # --------------------------------------------------

    def _run_single_step(self, flows, step):
        """
        One cascade step:
        1. Reset edge loads
        2. Route all feasible flows
        3. Mark disrupted flows
        4. Remove overloaded edges
        5. Remove isolated nodes
        6. Compute step-level metrics
        """
        self._reset_edge_loads()

        routed_flows = []
        disrupted_flows = []
        edge_loads_snapshot = {}

        for flow in flows:
            source = flow["source"]
            target = flow["target"]
            demand = float(flow["demand"])

            if not self.G.has_node(source) or not self.G.has_node(target):
                disrupted_flows.append(
                    {
                        "source": source,
                        "target": target,
                        "demand": demand,
                        "reason": "missing_node",
                    }
                )
                continue

            try:
                path = nx.shortest_path(self.G, source, target, weight="weight")
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                disrupted_flows.append(
                    {
                        "source": source,
                        "target": target,
                        "demand": demand,
                        "reason": "no_path",
                    }
                )
                continue

            self._assign_flow_to_path(path, demand)
            routed_flows.append(
                {
                    "source": source,
                    "target": target,
                    "demand": demand,
                    "path": path,
                }
            )

        # Snapshot loads before removals
        for u, v, data in self.G.edges(data=True):
            load = data.get("load", 0.0)
            capacity = data.get("capacity", self.default_capacity)

            edge_loads_snapshot[(u, v)] = {
                "load": load,
                "capacity": capacity,
                "utilization": load / capacity if capacity > 0 else None,
            }

        new_failed_edges = self._fail_overloaded_edges()
        new_failed_nodes = self._fail_isolated_nodes()

        routed_demand = float(sum(flow["demand"] for flow in routed_flows))
        disrupted_demand = float(sum(flow["demand"] for flow in disrupted_flows))

        step_metrics = {
            "routed_flow_count": len(routed_flows),
            "disrupted_flow_count": len(disrupted_flows),
            "routed_demand": routed_demand,
            "disrupted_demand": disrupted_demand,
            "new_failed_edge_count": len(new_failed_edges),
            "new_failed_node_count": len(new_failed_nodes),
            "cumulative_failed_edge_count": len(self.failed_edges),
            "cumulative_failed_node_count": len(self.failed_nodes),
            "active_edge_count": self.G.number_of_edges(),
            "active_node_count": self.G.number_of_nodes(),
        }

        return {
            "step": step,
            "routed_flows": routed_flows,
            "disrupted_flows": disrupted_flows,
            "new_failed_edges": new_failed_edges,
            "new_failed_nodes": new_failed_nodes,
            "all_failed_edges": sorted(self.failed_edges),
            "all_failed_nodes": sorted(self.failed_nodes),
            "edge_loads": edge_loads_snapshot,
            "step_metrics": step_metrics,
        }

    def _reset_edge_loads(self):
        """
        Set all current graph edge loads to zero before rerouting.
        """
        for u, v in self.G.edges():
            self.G[u][v]["load"] = 0.0

    def _assign_flow_to_path(self, path, demand):
        """
        Assign flow demand along each edge in the selected shortest path.
        """
        for u, v in zip(path[:-1], path[1:]):
            self.G[u][v]["load"] += demand

    def _fail_overloaded_edges(self):
        """
        Remove edges whose load exceeds capacity.
        """
        overloaded = []

        for u, v, data in list(self.G.edges(data=True)):
            load = float(data.get("load", 0.0))
            capacity = float(data.get("capacity", self.default_capacity))

            if load > capacity:
                overloaded.append((u, v))

        for u, v in overloaded:
            if self.G.has_edge(u, v):
                self.G.remove_edge(u, v)
                self.failed_edges.add((u, v))

        return overloaded

    def _fail_isolated_nodes(self):
        """
        Remove nodes that become isolated after edge failures.
        """
        isolated = []

        for node in list(self.G.nodes()):
            if self.G.degree(node) == 0:
                isolated.append(node)

        for node in isolated:
            if self.G.has_node(node):
                self.G.remove_node(node)
                self.failed_nodes.add(node)

        return isolated

    # --------------------------------------------------
    # Metrics
    # --------------------------------------------------

    def compute_metrics(self, flows):
        """
        Compute final simulation metrics.
        """
        total_flows = len(flows)
        disrupted_flows = 0
        delivered_demand = 0.0
        total_demand = 0.0

        for flow in flows:
            source = flow["source"]
            target = flow["target"]
            demand = float(flow["demand"])
            total_demand += demand

            if not self.G.has_node(source) or not self.G.has_node(target):
                disrupted_flows += 1
                continue

            try:
                nx.shortest_path(self.G, source, target, weight="weight")
                delivered_demand += demand
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                disrupted_flows += 1

        return {
            "total_flows": total_flows,
            "disrupted_flows": disrupted_flows,
            "disruption_ratio": disrupted_flows / total_flows if total_flows else 0.0,
            "total_demand": total_demand,
            "delivered_demand": delivered_demand,
            "unmet_demand": total_demand - delivered_demand,
            "service_level": delivered_demand / total_demand if total_demand else 0.0,
            "failed_node_count": len(self.failed_nodes),
            "failed_edge_count": len(self.failed_edges),
        }

    def get_step_metrics_table(self, result):
        """
        Convert simulation timeline into a dataframe-friendly list of dicts.

        Parameters
        ----------
        result : dict
            Output returned by run_simulation()

        Returns
        -------
        list[dict]
            One flat record per simulation step.
        """
        rows = []

        for step_data in result.get("timeline", []):
            metrics = step_data.get("step_metrics", {})

            rows.append(
                {
                    "step": step_data.get("step"),
                    "routed_flow_count": metrics.get("routed_flow_count", 0),
                    "disrupted_flow_count": metrics.get("disrupted_flow_count", 0),
                    "routed_demand": float(metrics.get("routed_demand", 0.0)),
                    "disrupted_demand": float(metrics.get("disrupted_demand", 0.0)),
                    "new_failed_edge_count": metrics.get("new_failed_edge_count", 0),
                    "new_failed_node_count": metrics.get("new_failed_node_count", 0),
                    "cumulative_failed_edge_count": metrics.get("cumulative_failed_edge_count", 0),
                    "cumulative_failed_node_count": metrics.get("cumulative_failed_node_count", 0),
                    "active_edge_count": metrics.get("active_edge_count", 0),
                    "active_node_count": metrics.get("active_node_count", 0),
                }
            )

        return rows