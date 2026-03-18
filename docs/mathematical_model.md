# Mathematical Model

## Supply Chain Fragility & Risk Analyzer

This document describes the mathematical foundations of the **Supply Chain Fragility & Risk Analyzer**.

The system models supply chains as **flow-driven, capacity-constrained, time-weighted networks**, enabling realistic simulation of disruption propagation and business impact.

Unlike traditional structural network models, this framework emphasizes:

* demand-driven routing
* time-based logistics modeling
* cascading failures through overload
* flow-level economic impact

---

# 1. Supply Chain Network Representation

The supply chain is modeled as a directed graph:

```id="math1"
G = (V, E)
```

Where:

* **V** = set of infrastructure nodes
* **E** = set of transportation edges

---

## 1.1 Nodes

Each node represents a logistics entity:

* suppliers
* factories
* ports
* warehouses
* distribution hubs

```id="math2"
V = {v_1, v_2, ..., v_n}
```

Each node contains attributes:

```id="math3"
v_i = (type, capacity, location)
```

---

## 1.2 Edges

Edges represent transport relationships:

```id="math4"
E = {(v_i, v_j)}
```

Each edge contains:

* capacity
* cost
* **time weight**

```id="math5"
e_{ij} = (capacity, cost, time)
```

---

# 2. Time-Weighted Routing Model

Routing decisions are based on **minimum travel time**, not hops or distance.

---

## Edge Weight

```id="math6"
w_{ij} = t_{ij}
```

Where:

* **tᵢⱼ** = travel time (lead time)

---

## Shortest Path Model

For flow from source `s` to destination `t`:

```id="math7"
P(s,t) = \arg\min \sum_{(i,j)\in path} w_{ij}
```

Solved using:

```id="math8"
Dijkstra's Algorithm
```

---

# 3. Flow-Based Demand Model

The system explicitly models demand flows:

```id="math9"
F = {f_1, f_2, ..., f_k}
```

Each flow:

```id="math10"
f_k = (s_k, t_k, d_k)
```

Where:

* **sₖ** = source
* **tₖ** = destination
* **dₖ** = demand

---

# 4. Load Accumulation Model

Edge load is computed as:

```id="math11"
L_e = \sum_{f_k \in R_e} d_k
```

Where:

* **Rₑ** = flows routed through edge e

---

# 5. Capacity Constraint Model

Each edge has capacity:

```id="math12"
C_e
```

Failure occurs when:

```id="math13"
L_e > C_e
```

The edge is then removed from the graph.

---

# 6. Cascading Failure Model

The cascade evolves iteratively:

---

## Step Model

For step `t`:

1. Route flows on current graph
2. Compute loads
3. Remove overloaded edges

```id="math14"
G_{t+1} = G_t - \{e \mid L_e > C_e\}
```

Repeat until:

* no new failures
  OR
* max steps reached

---

# 7. Flow Outcome Metrics

---

## Delivered Demand

```id="math15"
D_{delivered} = \sum d_k^{delivered}
```

---

## Unmet Demand

```id="math16"
D_{unmet} = \sum d_k^{unmet}
```

---

## Service Level

```id="math17"
SL = \frac{D_{delivered}}{D_{total}}
```

---

# 8. Delay Model

For each flow:

```id="math18"
Delay_k = T_k^{final} - T_k^{baseline}
```

Where:

* **T_baseline** = pre-disruption travel time
* **T_final** = post-disruption travel time

---

# 9. Cost Impact Model

---

## Reroute Cost

```id="math19"
RC_k = (C_k^{final} - C_k^{baseline}) \cdot d_k \cdot \lambda_r
```

---

## Delay Penalty

```id="math20"
DP_k = Delay_k \cdot d_k \cdot \lambda_d
```

---

## Unmet Demand Loss

```id="math21"
UL_k = d_k^{unmet} \cdot \lambda_u
```

---

## Total Economic Impact

```id="math22"
TEI = \sum_k (RC_k + DP_k + UL_k)
```

---

# 10. Summary

The mathematical framework integrates:

* time-weighted routing
* flow-driven modeling
* capacity-constrained cascading failures
* economic impact translation

This enables realistic evaluation of supply chain fragility under disruption.
