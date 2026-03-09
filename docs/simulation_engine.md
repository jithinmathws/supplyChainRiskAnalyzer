# Simulation Engine
## Supply Chain Fragility & Risk Analyzer

The Simulation Engine is the core analytical component of the Supply Chain Fragility & Risk Analyzer. It evaluates how disruptions affect logistics networks by simulating infrastructure failures and measuring their impact on routing efficiency, network connectivity, and supply chain resilience.

By performing graph-based simulations, the engine identifies critical infrastructure nodes, detects cascading failures, and translates network topology changes into operational delays.

---

# 1. Purpose

The simulation engine analyzes how disruptions propagate through supply chain networks.

Its purpose is to help analysts understand how localized failures can spread through logistics infrastructure and impact the entire supply chain system.

---

# 2. Simulation Objectives

The system evaluates disruption scenarios to measure supply chain vulnerability.

Primary objectives include:

- Identifying critical infrastructure nodes  
- Simulating node failures (random and targeted)  
- Detecting cascading congestion  
- Measuring network fragility  
- Estimating operational delays  
- Translating disruptions into financial impact  

These capabilities allow decision-makers to understand how localized disruptions can propagate across global logistics networks.

---

# 3. Network Representation

The supply chain network is represented as a directed graph.

G = (V, E)

Where:

- **V** = set of infrastructure nodes  
- **E** = set of transportation edges  

### Example Node Types

- ports  
- factories  
- warehouses  
- logistics hubs  

### Example Edge Types

- shipping routes  
- rail corridors  
- road freight routes  

This graph representation allows the system to apply network science methods for disruption analysis.

---

# 4. Disruption Simulation Framework

Disruptions are modeled as **node removal events** within the network graph.

These events represent real-world failures such as:

- port closures  
- factory shutdowns  
- infrastructure damage  
- labor strikes  
- geopolitical trade restrictions  

When a node fails, the simulation evaluates how the remaining network reorganizes its routing structure.

---

# 5. Simulation Workflow

The simulation process follows a multi-stage analytical workflow.

---

## Step 1 — Graph Initialization

The simulation loads the processed datasets:

- `nodes.csv`
- `edges.csv`

These datasets are converted into a directed graph using NetworkX.

Example:

```python
G = nx.DiGraph()
```

Nodes and edges are added along with their associated attributes.

---

## Step 2 — Baseline Network Analysis

Before disruptions occur, the system calculates baseline network metrics representing the normal operating state.

Baseline metrics include:

- shortest path routing
- degree centrality
- betweenness centrality
- closeness centrality
- average path length
- network efficiency

These values represent the **reference state of the network** before disruptions.

---

## Step 3 — Disruption Injection

A disruption is introduced by removing a selected node.

Example:

Remove node: Port_Rotterdam

Graph update:

$$
G' = G - \{v_k\}
$$

All edges connected to the disrupted node are removed.

This produces the **post-disruption network state**.

---

## Step 4 — Network Recalculation

After the disruption, the system recomputes routing paths across the network.

Updated metrics include:

- new shortest paths
- routing detours
- congestion redistribution
- updated centrality values

These recalculations reveal how traffic is redistributed across the remaining infrastructure.

---

## Step 5 — Cascading Failure Detection

When a major node fails, traffic is rerouted through alternative infrastructure.

This can overload secondary nodes.

The system detects secondary bottlenecks by measuring changes in **betweenness centrality**.

Congestion shift metric:

$$
\Delta CB(v) = CB_{\text{after}}(v) - CB_{\text{before}}(v)
$$

Where:

- **CB_before** = betweenness centrality before disruption  
- **CB_after** = betweenness centrality after disruption  

Nodes with large increases in centrality are classified as **secondary risk nodes**.

---

# 6 — Fragility Assessment

The system evaluates how disruptions affect overall network connectivity.

Fragility is measured using the **Largest Connected Component (LCC)**.

$$
\text{Fragility} = 1 - \frac{|C_{\text{largest}}'|}{|C_{\text{largest}}|}
$$

Where:

- **Clargest** = largest connected component before disruption  
- **Clargest'** = largest connected component after disruption  

### Fragility Interpretation

| Fragility Value | Interpretation |
|----------------|---------------|
| Near 0 | Network remains resilient |
| Moderate | Partial fragmentation |
| High | Severe network breakdown |

---

# 7 — Routing Impact Analysis

Disruptions often increase transportation distances and delivery times.

Routing efficiency is evaluated using the change in average path length.

$$
\Delta L = L_{\text{after}} - L_{\text{before}}
$$

Where:

- **L_before** = baseline average path length  
- **L_after** = post-disruption path length  

Large increases indicate logistics inefficiency caused by forced rerouting.

---

# 8. Business Impact Estimation

The simulation translates network disruptions into operational and financial metrics.

---

## 8.1 Delivery Delay

Estimated delay caused by the disruption:

$$
\text{Delay} = \Delta L \times T_{\text{edge}}
$$

Where:

- **ΔL** = increase in average path length  
- **T_edge** = average transit time per edge  

---

## 8.2 Financial Impact

Cost impact is estimated using throughput values.

$$
\text{Cost\_Impact} = \text{Delay} \times \text{Daily\_Throughput\_Value}
$$

Example:
- Delay = 3 days
- Daily throughput value = $400,000
- Estimated cost impact = $1.2M


---

# 9. Simulation Scenarios

The system supports multiple disruption scenarios.

---

## Single Node Failure

Simulates isolated events such as:

- port closures  
- factory shutdowns  

---

## Multi-Node Disruption

Simulates large-scale events such as:

- regional disasters  
- geopolitical conflicts  
- infrastructure failures across multiple nodes  

---

## Targeted Infrastructure Attack

Tests the impact of removing highly central nodes such as:

- major global ports  
- key logistics hubs  
- international rail junctions  

---

# 10. Monte Carlo Simulation (Future Extension)

To evaluate systemic risk, future versions of the system may run repeated simulations using randomized disruptions.

### Monte Carlo Procedure

1. Randomly select disruption nodes  
2. Run failure simulation  
3. Record network metrics  
4. Repeat across multiple iterations  

Example:
- iterations = 1000

This approach helps identify:

- statistically critical infrastructure  
- high-risk network regions  
- systemic vulnerabilities  

---

# 11. Output Metrics

Each simulation produces several analytical outputs.

Key outputs include:

- disrupted nodes  
- network fragility score  
- congestion shift values  
- routing delay  
- cost impact estimate  

These outputs allow analysts to understand both the **structural and economic consequences** of supply chain disruptions.