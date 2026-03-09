# Experiment Guide
## Supply Chain Fragility & Risk Analyzer

This document describes how to run disruption simulations using the Supply Chain Fragility & Risk Analyzer and how to interpret the resulting outputs.

The guide provides step-by-step procedures for performing controlled experiments on supply chain networks to evaluate their resilience, vulnerability, and cascading failure risks.

---

# 1. Purpose

The purpose of this guide is to demonstrate how the system can be used to analyze supply chain fragility through controlled simulation scenarios.

Experiments allow analysts to:

- Evaluate network resilience
- Identify critical infrastructure nodes
- Measure disruption impact
- Compare alternative logistics routing configurations
- Estimate operational and financial risk

---

# 2. Experiment Setup

Before running experiments, the system must be initialized with a supply chain dataset.

Required input files:


data/nodes.csv
data/edges.csv


---

## Node Dataset

Nodes represent supply chain entities such as suppliers, factories, ports, warehouses, and distribution centers.

Example structure:

| node_id | node_type | region |
|--------|-----------|--------|
| N1 | supplier | Asia |
| N2 | factory | Europe |
| N3 | port | Netherlands |

---

## Edge Dataset

Edges represent transportation connections and dependencies between nodes.

Example structure:

| source | target | transport_mode | distance |
|-------|--------|---------------|----------|
| N1 | N2 | shipping | 8200 |
| N2 | N3 | rail | 450 |

---

# 3. Running an Experiment

A typical experiment follows the workflow below:


Load Dataset
↓
Construct Network Graph
↓
Compute Baseline Metrics
↓
Inject Disruption
↓
Recalculate Network Metrics
↓
Measure Disruption Impact


Each stage allows analysts to observe how disruptions affect the structure and efficiency of the supply chain network.

---

# 4. Baseline Analysis

Before introducing disruptions, the system computes baseline network metrics representing normal supply chain operations.

Baseline metrics include:

- Node degree centrality
- Betweenness centrality
- Shortest path routes using Dijkstra's Algorithm
- Average path length
- Network connectivity components

These metrics serve as a reference point for comparing post-disruption conditions.

---

# 5. Disruption Experiments

The system supports several types of disruption experiments to test different risk profiles.

---

## 5.1 Single Node Failure Experiment

This experiment simulates the failure of a single infrastructure node.

Example scenario:


Remove node: Port_Rotterdam


Procedure:

1. Load the network dataset
2. Compute baseline metrics
3. Remove the selected node
4. Recalculate network connectivity
5. Measure routing changes
6. Compute the fragility score

Insight:

This experiment reveals how dependent the network is on a specific infrastructure component.

---

## 5.2 Random Failure Experiment

This experiment models unexpected disruptions such as natural disasters, accidents, or equipment failures.

Procedure:

1. Randomly select nodes
2. Remove the selected nodes from the graph
3. Recompute network metrics
4. Record connectivity loss
5. Measure routing efficiency changes

Insight:

Random failure experiments help estimate the overall robustness of the network.

---

## 5.3 Targeted Attack Experiment

This experiment evaluates worst-case scenarios where critical nodes are deliberately removed based on importance metrics.

Procedure:

1. Rank nodes by degree or betweenness centrality
2. Remove the highest-centrality nodes
3. Recompute network metrics
4. Measure fragility and congestion shifts

Insight:

This experiment helps identify severe structural weaknesses in the network.

---

## 5.4 Multi-Node Disruption Experiment

This experiment simulates large-scale disruptions affecting multiple infrastructure nodes.

Examples include:

- Regional disasters
- Geopolitical conflicts
- Transport route interruptions

Procedure:

1. Select multiple nodes
2. Remove the nodes simultaneously
3. Recompute network connectivity
4. Measure network fragmentation
5. Analyze routing detours

---

# 6. Cascading Failure Experiments

Large disruptions may cause cascading congestion across the network.

Procedure:

1. Simulate a major node failure
2. Recompute routing paths
3. Measure betweenness centrality shifts
4. Identify secondary bottleneck nodes

Nodes experiencing significant increases in centrality indicate a high congestion risk.

---

# 7. Measuring Network Fragility

Network fragility measures how severely connectivity is reduced after a disruption.

Fragility is derived from the Largest Connected Component (LCC).


Fragility = 1 - ( |Clargest'| / |Clargest| )


Where:

- **Clargest** = largest connected component before disruption  
- **Clargest'** = largest connected component after disruption  

### Fragility Interpretation

| Fragility Score | Meaning |
|----------------|--------|
| Low | Network remains stable and highly connected |
| Medium | Partial connectivity loss or fragmentation |
| High | Severe network breakdown (LCC approaches zero) |

---

# 8. Evaluating Routing Efficiency

Disruptions often force goods to travel longer routes, reducing supply chain efficiency.

Routing efficiency is measured using the change in average path length.


ΔL = L_after - L_before


Where:

- **L_before** = baseline average path length
- **L_after** = post-disruption path length

Large increases in path length indicate significant logistics disruption.

---

# 9. Business Impact Interpretation

The system converts structural disruptions into operational metrics.

Key outputs include:

- Delivery delay estimates
- Congestion hotspots
- Affected infrastructure nodes
- Disruption impact analysis

Example output:


Disrupted Node: Port_Rotterdam
Network Fragility: 0.32
Average Path Increase: 18%
Estimated Delay: 3 days
Estimated Cost Impact: $1.2M


These results help decision-makers evaluate supply chain risks in operational terms.

---

# 10. Repeated Experiments (Monte Carlo)

To evaluate systemic vulnerability, experiments can be repeated multiple times using randomized disruptions.

Example:


iterations = 1000


Procedure:

1. Randomly select disruption nodes
2. Simulate the failure
3. Compute network metrics
4. Record fragility scores
5. Repeat across iterations

This produces statistical estimates of network resilience.

---

# 11. Experiment Outputs

Each experiment generates analytical outputs used for further analysis and visualization.

Typical outputs include:

- Disrupted nodes
- Fragility indicators
- Node importance ranking
- Network connectivity metrics
- Resilience analysis

These outputs can be visualized using the project's interactive Plotly and Streamlit dashboards.

---

# 12. Recommended Experiments

Suggested starting experiments for evaluating supply chain resilience:

1. Remove the most central node
2. Simulate the failure of major ports
3. Run random failure simulations
4. Test regional multi-node disruptions
5. Compare baseline versus disrupted routing efficiency

These experiments help analysts understand how supply chain networks behave under stress.