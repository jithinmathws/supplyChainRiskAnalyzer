# Mathematical Model

## Supply Chain Fragility & Risk Analyzer

This document describes the mathematical foundations used in the Supply Chain Fragility & Risk Analyzer. The system models supply chain infrastructure using **graph theory** and **network science** to evaluate network resilience, critical infrastructure nodes, and disruption propagation.

The framework represents supply chains as **directed weighted networks** where nodes represent logistics entities and edges represent transportation or dependency relationships.

---

# 1. Supply Chain Network Representation

A supply chain network is modeled as a **directed weighted graph**.

G = (V, E)

**Where:**

* `V` = set of nodes in the network
* `E` = set of edges connecting nodes

---

## 1.1 Nodes

Each node represents a supply chain entity such as:

* suppliers
* factories
* ports
* warehouses
* distribution hubs

V = {v1, v2, v3, ..., vn}

Each node contains attributes describing infrastructure properties:

vi = (type, capacity, location, risk_score)

**Example:**

Node v1 = (Port, capacity = 100000, location = Singapore)

---

## 1.2 Edges

Edges represent **transportation links** or **supply relationships** between entities.

E = {(vi, vj)}

Each edge contains attributes such as:

* distance
* cost
* transit time

eij = (distance, cost, transit_time)

**Example:**

Edge eij represents Factory_A → Port_B
distance = 1200 km
transit_time = 3 days

---

# 2. Weighted Network Model

The supply chain graph is treated as a **weighted directed graph**. Edge weights represent logistical cost or travel difficulty.

wij = f(distance, transit_time, cost)

A simple linear weighting function is defined as:

wij = α * distance + β * transit_time + γ * cost

**Where:**

* `α` = distance weight
* `β` = time weight
* `γ` = cost weight

This allows the system to evaluate routes based on **distance**, **time**, and **financial cost** simultaneously.

---

# 3. Shortest Path Model

Efficient supply chain routing is modeled as a **shortest path optimization problem**.

Given graph `G`, the system computes the optimal path between nodes using **Dijkstra's Algorithm**.

P(s,t) = min Σ wij

Where the sum is taken over all edges `(i,j)` in the path.

**Where:**

* `s` = source node
* `t` = destination node
* `wij` = weight of edge between nodes i and j

The algorithm identifies the route with the **minimum cumulative cost**.

---

# 4. Network Centrality Metrics

Centrality measures identify **important nodes** within the supply chain network. These metrics help detect critical infrastructure such as major ports, logistics corridors, and distribution hubs.

---

## 4.1 Degree Centrality

Degree centrality measures how **connected** a node is.

CD(v) = deg(v) / (n − 1)

**Where:**

* `deg(v)` = number of connections of node v
* `n` = total number of nodes

Nodes with high degree centrality often represent **major logistics hubs**.

---

## 4.2 Betweenness Centrality

Betweenness centrality measures how **frequently** a node appears on shortest paths between other nodes.

CB(v) = Σ [σst(v) / σst]

**Where:**

* `σst` = number of shortest paths between nodes s and t
* `σst(v)` = number of those paths that pass through node v

Nodes with high betweenness centrality often represent **critical transit infrastructure** such as:

* ports
* rail hubs
* logistics gateways

---

## 4.3 Closeness Centrality

Closeness centrality measures how **efficiently** a node can reach all other nodes.

CC(v) = (n − 1) / Σ d(v,u)

**Where:**

* `d(v,u)` = shortest path distance between nodes v and u

Nodes with high closeness centrality provide **efficient access** to the network.

---

# 5. Network Connectivity Metrics

Network resilience can also be evaluated using **global structural metrics**.

---

## 5.1 Average Path Length

Average path length measures the **mean distance** between all node pairs.

L = (1 / (n(n−1))) * Σ d(vi, vj)

Where `i ≠ j`.

If disruptions increase `L`, **logistics efficiency decreases**.

---

## 5.2 Network Density

Density measures the **level of connectivity** in the network.

D = |E| / (|V| (|V| − 1))

Higher density indicates:

* greater redundancy
* more alternative routing paths

---

## 5.3 Network Efficiency

Network efficiency measures how **efficiently** goods travel through the network.

E(G) = (1 / (n(n−1))) * Σ (1 / d(i,j))

Higher values indicate more **efficient logistics connectivity**.

---

# 6. Disruption Modeling

Supply chain disruptions are modeled as **node removal operations**.

Given graph:

G = (V,E)

Removing node `vk` produces a modified graph:

G' = (V − {vk}, E')

**Where:**

E' = {(vi,vj) ∈ E | vi ≠ vk and vj ≠ vk}

The resulting graph represents the network **after disruption**.

---

# 7. Cascading Failure Model

The system models **ripple effects** caused by infrastructure failure.

---

## Simulation Procedure

1. Remove node `vk`
2. Recompute shortest paths
3. Recalculate centrality metrics
4. Identify newly overloaded nodes

Nodes experiencing large increases in centrality are treated as **secondary risk nodes**.

---

## Congestion Shift Metric

Congestion increase at node `v` is estimated as:

```
ΔCB(v) = CB_after − CB_before
```

Large values indicate **new bottlenecks** in the network.

---

# 8. Supply Chain Fragility Metric

To measure supply chain robustness, the system evaluates how disruptions affect **connectivity**.

Fragility is measured using the **Largest Connected Component (LCC)**.

```
Fragility = 1 − (|Clargest'| / |Clargest|)
```

**Where:**

* `Clargest` = size of largest component before disruption
* `Clargest'` = size after disruption

Higher values indicate **greater structural vulnerability**.

---

# 9. Business Impact Translation

Graph-level metrics are translated into **operational impacts**.

---

## 9.1 Lead Time Impact

Delivery delay is estimated using the change in average path length.

```
Delay = ΔL * Tedge
```

**Where:**

* `ΔL` = increase in average path length
* `Tedge` = average transit time per edge

---

## 9.2 Cost Impact

Financial impact is estimated as:

```
Cost_Impact = Delay * Daily_Throughput_Value
```

**Example:**

```
Delay = 3 days
Daily throughput value = $400,000
Estimated cost impact = $1.2M
```

---

# 10. Summary

The Supply Chain Fragility & Risk Analyzer combines:

* **graph theory**
* **network science** 
* **disruption modeling**

to evaluate how supply chain networks behave under stress.

The mathematical framework enables analysis of:

* **logistics efficiency**
* **infrastructure criticality**
* **cascading disruption effects**
* **economic impact of supply chain failures**

This foundation supports simulation of complex supply chain disruptions across logistics networks.