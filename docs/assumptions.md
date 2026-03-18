# Modeling Assumptions

## Supply Chain Fragility & Risk Analyzer

This document outlines the **core modeling assumptions** underlying the Supply Chain Fragility & Risk Analyzer.

All simulation systems require simplifying assumptions to make complex real-world supply chains computationally tractable. These assumptions define how the network is modeled, how disruptions are simulated, and how operational and financial impacts are estimated.

Documenting these assumptions ensures:

* **Transparency** in methodology
* **Reproducibility** of simulations
* **Correct interpretation** of results

These assumptions apply to the **current system implementation (MVP)**.

---

# 1. Overview

The system models supply chains as:

* **flow-driven networks**
* **time-weighted graphs**
* **capacity-constrained systems**

While realistic, the model still simplifies several real-world behaviors.

---

# 2. Network Representation Assumptions

---

## 2.1 Infrastructure as Discrete Nodes

Each facility is modeled as a **single node**.

Examples:

* ports
* factories
* warehouses

👉 Real-world facilities may contain multiple subsystems, but are treated as **atomic units**.

---

## 2.2 Transportation as Directed Edges

Edges represent transport routes:

* shipping
* rail
* road
* air

👉 Edges represent **available paths**, not contractual logistics relationships.

---

## 2.3 Single-Layer Network

The model uses a **single-layer network**.

👉 Real supply chains are multi-layered (supplier → manufacturing → distribution → retail), but are flattened for simplicity.

---

# 3. Static Topology Assumption

During a simulation:

* no new nodes are created
* no new routes are added
* only disruptions remove components

👉 Real systems adapt dynamically, but **adaptive logistics strategies are not modeled**.

---

# 4. Capacity Modeling Assumptions

---

## 4.1 Edge Capacity Constraints (Modeled)

Each edge has a fixed capacity:

```id="assump1"
C_e
```

Flow exceeding capacity results in failure:

```id="assump2"
L_e > C_e
```

---

## 4.2 Node Capacity Simplification

Node-level capacity is not explicitly enforced during routing.

👉 Congestion is modeled primarily at the **edge level**, not at facilities.

---

## 4.3 No Partial Capacity Reduction

Edges either:

* operate normally
* fail completely

👉 Gradual degradation (e.g., 50% capacity) is not modeled.

---

# 5. Disruption Modeling Assumptions

---

## 5.1 Binary Failure Model

Components are either:

* operational
* removed

👉 Partial disruptions (delays, slowdowns) are not represented.

---

## 5.2 Instantaneous Disruption

Disruptions occur instantly at simulation start.

👉 No modeling of:

* gradual failure
* recovery timelines
* phased disruptions

---

# 6. Routing Assumptions

---

## 6.1 Shortest-Time Routing

Flows are routed using:

```id="assump3"
shortest path (weight = time)
```

👉 Other real-world constraints are not modeled:

* contracts
* pricing agreements
* geopolitical restrictions

---

## 6.2 Deterministic Routing

All routing is deterministic.

👉 No stochastic variation or uncertainty is included.

---

# 7. Flow Modeling Assumptions

---

## 7.1 Fixed Demand

Each flow has fixed demand:

```id="assump4"
d_k
```

👉 Demand does not change dynamically during simulation.

---

## 7.2 No Inventory Buffering

The model assumes:

* no storage buffering
* no delayed fulfillment

👉 Unmet demand is immediately counted as loss.

---

# 8. Cascade Simulation Assumptions

---

## 8.1 Load-Based Failure

Failures propagate via:

```id="assump5"
edge load → capacity violation → edge removal
```

👉 This models congestion-driven collapse.

---

## 8.2 Discrete Time Steps

Simulation evolves in discrete steps.

👉 Continuous-time dynamics are not modeled.

---

# 9. Economic Modeling Assumptions

---

## 9.1 Linear Cost Functions

Economic impact is computed using linear models:

* reroute cost
* delay penalty
* unmet demand loss

👉 Nonlinear effects (e.g., cascading financial shocks) are not included.

---

## 9.2 No Market Dynamics

The model does not consider:

* pricing changes
* supply substitution
* demand elasticity

---

# 10. Scenario Assumptions

Simulations represent **hypothetical stress tests**, not predictions.

Scenarios include:

* node disruptions
* edge failures
* multi-point failures

👉 Results should be interpreted as **analytical insights**, not forecasts.

---

# 11. Scope Limitations

The system focuses on:

* network structure
* flow dynamics
* disruption propagation
* economic impact

It does NOT model:

* organizational decision-making
* procurement strategies
* real-time logistics adaptation

---

# 12. Summary

The system makes several simplifying assumptions:

* supply chains represented as graphs
* time-based deterministic routing
* capacity-driven cascading failures
* binary disruption modeling
* linear economic impact estimation

These assumptions enable a balance between:

* **model realism**
* **computational tractability**
* **interpretability**

Future improvements may include:

* stochastic demand
* partial capacity failures
* recovery modeling
* multi-layer supply chain representation
