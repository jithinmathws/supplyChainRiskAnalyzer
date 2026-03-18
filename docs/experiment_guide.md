# Experiment Guide

## Supply Chain Fragility & Risk Analyzer

This guide explains how to run simulations using the **Supply Chain Fragility & Risk Analyzer** and how to interpret results.

The system allows analysts to perform **flow-based disruption experiments** to evaluate:

* supply chain resilience
* rerouting behavior
* cascading failures
* economic impact

---

# 1. Purpose

Experiments help answer:

* What happens when a key node fails?
* Can demand still be delivered?
* How much delay is introduced?
* What is the economic impact?

---

# 2. Setup

Before running experiments, ensure:

* graph data is loaded (`nodes.csv`, `edges.csv`)
* flows are defined (default / custom / CSV)

---

## Required Inputs

### Nodes

Supply chain entities:

* suppliers
* factories
* ports
* warehouses

---

### Edges

Transport routes with:

* time (weight)
* capacity
* cost

---

### Flows

Each flow:

```id="exp1"
(source, target, demand)
```

---

# 3. Running an Experiment

In the Streamlit UI:

---

## Step 1 — Select Flows

Choose:

* Default flows
* Custom flows
* Upload flows.csv

---

## Step 2 — Define Disruptions

Select:

* disrupted nodes
* disrupted edges

---

## Step 3 — Configure Parameters

* demand per flow
* max simulation steps
* edge capacity

---

## Step 4 — Economic Parameters

* reroute cost rate
* delay penalty rate
* unmet demand loss rate

---

## Step 5 — Run Simulation

Click:

```id="exp2"
Run Cascade Simulation
```

---

# 4. Understanding Results

---

## 4.1 KPI Overview

Key metrics:

* **Service Level** → % demand delivered
* **Unmet Demand** → lost supply
* **Failed Nodes / Edges** → infrastructure loss
* **Total Economic Impact** → overall cost

---

## 4.2 Flow Impact Table

Each flow shows:

* baseline vs final path
* rerouting status
* delay (time increase)
* cost increase
* delivered vs unmet demand

---

### Interpretation

| Status    | Meaning                |
| --------- | ---------------------- |
| delivered | no disruption          |
| rerouted  | alternative path found |
| disrupted | no feasible route      |

---

## 4.3 Step Metrics

Tracks cascade evolution:

* routed demand per step
* new failures
* cumulative failures

---

### Interpretation

* rapid drop in routed demand → network collapse
* increasing failures → cascading effect

---

## 4.4 Demand Progression Chart

Shows:

* routed demand
* disrupted demand

👉 Helps visualize resilience over time.

---

## 4.5 Failure Progression Chart

Tracks:

* failed edges
* failed nodes

👉 Indicates cascade severity.

---

# 5. Experiment Types

---

## 5.1 Single Node Failure

Simulate failure of a critical node.

Example:

* port shutdown

---

## 5.2 Multi-Node Disruption

Simulate regional or systemic shocks.

---

## 5.3 Edge Disruption

Simulate route failures (e.g., blocked shipping lane).

---

## 5.4 Flow Stress Testing

Increase demand to test capacity limits.

---

# 6. Cascade Behavior Analysis

Key observations:

---

## Rerouting

Flows attempt alternative paths.

👉 Indicates network redundancy.

---

## Congestion

Load increases on remaining edges.

---

## Cascade Failure

Edges fail when:

```id="exp3"
load > capacity
```

---

## Network Collapse

Occurs when:

```id="exp4"
routed_demand → 0
```

---

# 7. Economic Impact Interpretation

The system quantifies disruption impact:

---

## Reroute Cost

Extra cost due to longer routes.

---

## Delay Penalty

Cost due to increased travel time.

---

## Unmet Demand Loss

Lost business due to failed delivery.

---

## Total Economic Impact

```id="exp5"
reroute_cost + delay_penalty + unmet_demand_loss
```

---

# 8. Recommended Experiments

Start with:

1. Single hub failure
2. Dual-node disruption
3. High-demand stress test
4. Edge disruption (critical route)

---

# 9. Key Insights to Look For

---

## Resilience

* high service level
* minimal rerouting

---

## Fragility

* high unmet demand
* rapid cascade

---

## Bottlenecks

* repeated edge failures
* high reroute dependency

---

## Economic Risk

* high delay penalty
* high unmet demand loss

---

# 10. Summary

This system enables:

* flow-based disruption analysis
* realistic cascade simulation
* time-based delay modeling
* economic impact evaluation

It provides a practical framework for **stress-testing supply chain networks under disruption scenarios**.
