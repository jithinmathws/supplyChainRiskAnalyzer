# Simulation Engine

## Supply Chain Fragility & Risk Analyzer

The Simulation Engine is the core analytical component of the **Supply Chain Fragility & Risk Analyzer**.

It evaluates how disruptions affect logistics networks by simulating **flow-driven routing behavior**, **capacity-constrained cascading failures**, and their resulting **operational and economic impacts**.

Unlike traditional network-failure models that focus on topology alone, this system models supply chains as dynamic systems where:

* demand flows determine network stress
* disruptions propagate through rerouting
* overload causes secondary failures
* impacts are measured at both network and business levels

---

# 1. Purpose

The simulation engine analyzes how disruptions propagate across supply chain networks under real-world operational constraints.

Its purpose is to help analysts understand:

* how flows reroute under disruption
* where congestion emerges
* how cascading failures evolve
* how disruptions translate into cost and delay

---

# 2. Core Design Principles

### Flow-Driven Simulation

The system models **demand flows explicitly**, rather than analyzing static topology.

---

### Time-Based Routing

All routing decisions use:

```id="simroute"
shortest path (weight = time)
```

This enables realistic delay modeling.

---

### Capacity-Constrained Cascades

Failures propagate through **load accumulation and overload**, not centrality shifts.

---

### Business-Oriented Outputs

Simulation results translate directly into:

* delay
* unmet demand
* economic loss

---

# 3. Network Representation

The supply chain network is represented as:

```id="simgraph"
G = (V, E)
```

Where:

* **V** = infrastructure nodes
* **E** = transport edges

The system uses:

```id="simgraph2"
NetworkX MultiDiGraph
```

---

## Node Examples

* suppliers
* factories
* ports
* warehouses

---

## Edge Attributes

* capacity
* cost
* **weight (time)**

---

# 4. Disruption Model

Disruptions are modeled as removal of:

* nodes
* edges

These represent real-world events such as:

* port closures
* infrastructure outages
* strikes
* disasters

---

# 5. Simulation Workflow

---

## Step 1 — Initialization

The engine loads the prepared graph and baseline flows.

Baseline routing is computed for each flow:

* baseline path
* baseline time
* baseline cost

---

## Step 2 — Disruption Injection

Selected nodes and/or edges are removed from the network.

This produces the initial disrupted state.

---

## Step 3 — Flow Routing

For each simulation step:

1. All flows attempt routing using shortest paths
2. Delivered and disrupted flows are recorded

Outputs tracked:

* final path
* delivered demand
* unmet demand

---

## Step 4 — Load Accumulation

Edge loads are computed:

```id="simload"
edge_load = Σ(flow_demand routed through edge)
```

---

## Step 5 — Overload Detection

Edges exceeding capacity fail:

```id="simfail"
edge_load > capacity → edge removed
```

This triggers cascading propagation.

---

## Step 6 — Iteration

Steps repeat until:

* no new failures occur
  OR
* maximum steps reached

---

# 6. Output Metrics

---

## 6.1 Flow-Level Metrics

For each flow:

* baseline vs final path
* rerouting status
* delivered vs unmet demand
* **time increase (delay)**
* cost increase
* hop change

---

## 6.2 System-Level Metrics

* service level
* disrupted flows
* unmet demand
* failed nodes/edges
* total economic impact

---

## 6.3 Step-Level Metrics

* routed demand per step
* new failures
* cumulative failures

---

# 7. Economic Impact Modeling

The engine translates disruptions into decision-ready KPIs.

---

## Reroute Cost

```id="simcost1"
(cost increase × demand × reroute_cost_rate)
```

---

## Delay Penalty

```id="simcost2"
(time increase × demand × delay_penalty_rate)
```

---

## Unmet Demand Loss

```id="simcost3"
(unmet demand × unmet_demand_loss_rate)
```

---

## Total Economic Impact

```id="simcost4"
reroute_cost + delay_penalty + unmet_demand_loss
```

---

# 8. Scenario Support

The engine supports:

---

## Single Disruption

Localized failures such as port closures.

---

## Multi-Component Disruption

Regional shocks or system failures.

---

## Flow-Based Stress Testing

Evaluates performance under demand scenarios.

---

# 9. Future Extensions

Planned enhancements:

* stochastic disruptions
* Monte Carlo simulations
* recovery-time modeling
* multi-layer supply chain networks

---

# Conclusion

The Simulation Engine combines:

* flow-based modeling
* capacity-aware cascading logic
* time-based routing
* business impact translation

into a unified simulation framework for analyzing real-world supply chain resilience.
