from copy import deepcopy

import networkx as nx


class CascadeSimulator:
    """
    Capacity-aware cascading disruption simulator.

    Phase 2 logic:
    - Apply initial node/edge shocks
    - Recompute shortest paths for demand flows
    - Accumulate edge loads
    - Remove overloaded edges
    - Repeat until stable or max_steps reached

    Flow Impact Tracking:
    - Capture baseline path/cost/hops for each flow
    - Compare final surviving path against baseline
    - Mark each flow as delivered, rerouted, or disrupted

    Economic Impact:
    - reroute_cost
    - delay_penalty
    - unmet_demand_loss
    - total_economic_impact
    """

    def __init__(
        self,
        G,
        default_capacity=100.0,
        default_weight=1.0,
        reroute_cost_rate=1.0,
        delay_penalty_rate=2.0,
        unmet_demand_loss_rate=5.0,
    ):
        if not G.is_directed():
            raise ValueError("CascadeSimulator currently requires a directed graph (DiGraph or MultiDiGraph).")

        self.original_graph = deepcopy(G)
        self.default_capacity = float(default_capacity)
        self.default_weight = float(default_weight)

        self.reroute_cost_rate = float(reroute_cost_rate)
        self.delay_penalty_rate = float(delay_penalty_rate)
        self.unmet_demand_loss_rate = float(unmet_demand_loss_rate)

        self._initialize_graph_attributes(self.original_graph)
        self.reset()

    # --------------------------------------------------
    # Setup
    # --------------------------------------------------

    def _initialize_graph_attributes(self, G):
        """
        Ensure every edge has required attributes.
        """
        if G.is_multigraph():
            for _, _, _, data in G.edges(keys=True, data=True):
                data.setdefault("capacity", self.default_capacity)
                data.setdefault("weight", self.default_weight)
        else:
            for _, _, data in G.edges(data=True):
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
        self.reset()

        disrupted_nodes = [str(n).strip() for n in (disrupted_nodes or [])]
        disrupted_edges = disrupted_edges or []
        flows = flows or []

        self._validate_flows(flows)

        baseline_map = self._build_baseline_flow_map(flows)

        self.apply_initial_shock(disrupted_nodes, disrupted_edges)

        for step in range(max_steps):
            step_result = self._run_single_step(flows, step)
            self.timeline.append(step_result)

            if not step_result["new_failed_edges"] and not step_result["new_failed_nodes"]:
                break

        flow_impacts = self._build_flow_impact_table_data(flows, baseline_map)
        metrics = self.compute_metrics(flows, flow_impacts)

        return {
            "timeline": self.timeline,
            "failed_nodes": sorted(self.failed_nodes),
            "failed_edges": sorted(self.failed_edges),
            "metrics": metrics,
            "flow_impacts": flow_impacts,
        }

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def _validate_flows(self, flows):
        for i, flow in enumerate(flows):
            if not isinstance(flow, dict):
                raise ValueError(f"Flow at index {i} must be a dict like " f"{{'source': 'A', 'target': 'D', 'demand': 40}}")

            required_keys = {"source", "target", "demand"}
            missing = required_keys - set(flow.keys())
            if missing:
                raise ValueError(f"Flow {i} missing keys: {missing}")

            flow["source"] = str(flow["source"]).strip()
            flow["target"] = str(flow["target"]).strip()

            s, t = flow["source"], flow["target"]

            try:
                d = float(flow["demand"])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid demand for flow {i}: {flow['demand']}")

            flow["demand"] = d

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
        for n in disrupted_nodes:
            if self.G.has_node(n):
                self.G.remove_node(n)
                self.failed_nodes.add(n)

        for edge in disrupted_edges:
            if self.G.is_multigraph():
                if len(edge) == 3:
                    u, v, k = edge
                    if self.G.has_edge(u, v, key=k):
                        self.G.remove_edge(u, v, key=k)
                        self.failed_edges.add((u, v, k))
                elif len(edge) == 2:
                    u, v = edge
                    if self.G.has_edge(u, v):
                        keys = list(self.G[u][v].keys())
                        for k in keys:
                            if self.G.has_edge(u, v, key=k):
                                self.G.remove_edge(u, v, key=k)
                                self.failed_edges.add((u, v, k))
                else:
                    raise ValueError(f"Invalid disrupted edge format: {edge}")
            else:
                if len(edge) != 2:
                    raise ValueError(f"Invalid disrupted edge format for DiGraph: {edge}")
                u, v = edge
                if self.G.has_edge(u, v):
                    self.G.remove_edge(u, v)
                    self.failed_edges.add((u, v))

    # --------------------------------------------------
    # Core step logic
    # --------------------------------------------------

    def _run_single_step(self, flows, step):
        self._reset_edge_loads()

        routed_flows = []
        disrupted_flows = []

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

        edge_loads_snapshot = {}

        if self.G.is_multigraph():
            for u, v, k, data in self.G.edges(keys=True, data=True):
                load = data.get("load", 0.0)
                capacity = data.get("capacity", self.default_capacity)
                edge_loads_snapshot[(u, v, k)] = {
                    "load": load,
                    "capacity": capacity,
                    "utilization": load / capacity if capacity > 0 else None,
                }
        else:
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
        if self.G.is_multigraph():
            for u, v, k in self.G.edges(keys=True):
                self.G[u][v][k]["load"] = 0.0
        else:
            for u, v in self.G.edges():
                self.G[u][v]["load"] = 0.0

    def _assign_flow_to_path(self, path, demand):
        for u, v in zip(path[:-1], path[1:]):
            if self.G.is_multigraph():
                best_key = min(
                    self.G[u][v],
                    key=lambda k: self.G[u][v][k].get("weight", self.default_weight),
                )
                self.G[u][v][best_key]["load"] += demand
            else:
                self.G[u][v]["load"] += demand

    def _fail_overloaded_edges(self):
        overloaded = []

        if self.G.is_multigraph():
            for u, v, k, data in list(self.G.edges(keys=True, data=True)):
                load = float(data.get("load", 0.0))
                capacity = float(data.get("capacity", self.default_capacity))
                if load > capacity:
                    overloaded.append((u, v, k))

            for u, v, k in overloaded:
                if self.G.has_edge(u, v, key=k):
                    self.G.remove_edge(u, v, key=k)
                    self.failed_edges.add((u, v, k))
        else:
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

    def compute_metrics(self, flows, flow_impacts=None):
        total_flows = len(flows)
        disrupted_flows = 0
        delivered_demand = 0.0
        total_demand = 0.0

        total_reroute_cost = 0.0
        total_delay_penalty = 0.0
        total_unmet_demand_loss = 0.0
        total_economic_impact = 0.0

        if flow_impacts is None:
            flow_impacts = []

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

        for item in flow_impacts:
            total_reroute_cost += float(item.get("reroute_cost", 0.0) or 0.0)
            total_delay_penalty += float(item.get("delay_penalty", 0.0) or 0.0)
            total_unmet_demand_loss += float(item.get("unmet_demand_loss", 0.0) or 0.0)
            total_economic_impact += float(item.get("total_economic_impact", 0.0) or 0.0)

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
            "total_reroute_cost": total_reroute_cost,
            "total_delay_penalty": total_delay_penalty,
            "total_unmet_demand_loss": total_unmet_demand_loss,
            "total_economic_impact": total_economic_impact,
        }

    # --------------------------------------------------
    # Table helpers
    # --------------------------------------------------

    def get_step_metrics_table(self, result):
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

    def get_flow_impact_table(self, result):
        rows = []

        for item in result.get("flow_impacts", []):
            rows.append(
                {
                    "source": item.get("source"),
                    "target": item.get("target"),
                    "demand": float(item.get("demand", 0.0)),
                    "status": item.get("status"),
                    "rerouted": item.get("rerouted", False),
                    "baseline_path": (" → ".join(map(str, item["baseline_path"])) if item.get("baseline_path") else None),
                    "final_path": (" → ".join(map(str, item["final_path"])) if item.get("final_path") else None),
                    "baseline_cost": item.get("baseline_cost"),
                    "final_cost": item.get("final_cost"),
                    "cost_increase": item.get("cost_increase"),
                    "baseline_hops": item.get("baseline_hops"),
                    "final_hops": item.get("final_hops"),
                    "hop_increase": item.get("hop_increase"),
                    "delivered_demand": float(item.get("delivered_demand", 0.0)),
                    "unmet_demand": float(item.get("unmet_demand", 0.0)),
                    "reroute_cost": float(item.get("reroute_cost", 0.0)),
                    "delay_penalty": float(item.get("delay_penalty", 0.0)),
                    "unmet_demand_loss": float(item.get("unmet_demand_loss", 0.0)),
                    "total_economic_impact": float(item.get("total_economic_impact", 0.0)),
                }
            )

        return rows

    # --------------------------------------------------
    # Flow impact helpers
    # --------------------------------------------------

    def _compute_path_cost(self, graph, path):
        if not path or len(path) < 2:
            return 0.0

        total_cost = 0.0

        for u, v in zip(path[:-1], path[1:]):
            if graph.is_multigraph():
                best_weight = min(graph[u][v][k].get("weight", self.default_weight) for k in graph[u][v])
                total_cost += float(best_weight)
            else:
                total_cost += float(graph[u][v].get("weight", self.default_weight))

        return total_cost

    def _build_baseline_flow_map(self, flows):
        baseline_map = {}

        for flow in flows:
            source = flow["source"]
            target = flow["target"]
            demand = float(flow["demand"])
            flow_key = (source, target)

            try:
                baseline_path = nx.shortest_path(
                    self.original_graph,
                    source,
                    target,
                    weight="weight",
                )
                baseline_cost = self._compute_path_cost(self.original_graph, baseline_path)
                baseline_hops = max(len(baseline_path) - 1, 0)

                baseline_map[flow_key] = {
                    "source": source,
                    "target": target,
                    "demand": demand,
                    "baseline_path": baseline_path,
                    "baseline_cost": baseline_cost,
                    "baseline_hops": baseline_hops,
                }
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                baseline_map[flow_key] = {
                    "source": source,
                    "target": target,
                    "demand": demand,
                    "baseline_path": None,
                    "baseline_cost": None,
                    "baseline_hops": None,
                }

        return baseline_map

    def _build_flow_impact_table_data(self, flows, baseline_map):
        records = []

        for flow in flows:
            source = flow["source"]
            target = flow["target"]
            demand = float(flow["demand"])
            flow_key = (source, target)

            baseline = baseline_map.get(flow_key, {})
            baseline_path = baseline.get("baseline_path")
            baseline_cost = baseline.get("baseline_cost")
            baseline_hops = baseline.get("baseline_hops")

            final_path = None
            final_cost = None
            final_hops = None
            status = "disrupted"
            rerouted = False
            delivered_demand = 0.0

            if self.G.has_node(source) and self.G.has_node(target):
                try:
                    final_path = nx.shortest_path(self.G, source, target, weight="weight")
                    final_cost = self._compute_path_cost(self.G, final_path)
                    final_hops = max(len(final_path) - 1, 0)
                    delivered_demand = demand

                    if baseline_path is None:
                        status = "delivered"
                    elif final_path == baseline_path:
                        status = "delivered"
                    else:
                        status = "rerouted"
                        rerouted = True

                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    status = "disrupted"

            cost_increase = final_cost - baseline_cost if baseline_cost is not None and final_cost is not None else None
            hop_increase = final_hops - baseline_hops if baseline_hops is not None and final_hops is not None else None
            unmet_demand = demand - delivered_demand

            positive_cost_increase = max(float(cost_increase or 0.0), 0.0)

            reroute_cost = positive_cost_increase * self.reroute_cost_rate * delivered_demand
            delay_penalty = positive_cost_increase * self.delay_penalty_rate * delivered_demand
            unmet_demand_loss = unmet_demand * self.unmet_demand_loss_rate
            total_economic_impact = reroute_cost + delay_penalty + unmet_demand_loss

            records.append(
                {
                    "source": source,
                    "target": target,
                    "demand": demand,
                    "status": status,
                    "rerouted": rerouted,
                    "baseline_path": baseline_path,
                    "final_path": final_path,
                    "baseline_cost": baseline_cost,
                    "final_cost": final_cost,
                    "cost_increase": cost_increase,
                    "baseline_hops": baseline_hops,
                    "final_hops": final_hops,
                    "hop_increase": hop_increase,
                    "delivered_demand": delivered_demand,
                    "unmet_demand": unmet_demand,
                    "reroute_cost": reroute_cost,
                    "delay_penalty": delay_penalty,
                    "unmet_demand_loss": unmet_demand_loss,
                    "total_economic_impact": total_economic_impact,
                }
            )

        return records
