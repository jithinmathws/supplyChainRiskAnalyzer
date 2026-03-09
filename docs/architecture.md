# System Architecture

## Supply Chain Fragility & Risk Analyzer

This document describes the system architecture of the **Supply Chain Fragility & Risk Analyzer**. The system models supply chain networks as graphs and evaluates how disruptions propagate through logistics infrastructure.

The architecture supports modular development of graph modeling, network analysis, dynamic disruption simulation ("What-If Engine"), and business-centric visualization capabilities.

---

# 1. Architectural Overview

The system follows a **Layered Analytical Pipeline Architecture**, where each stage processes and transforms a network representation of the supply chain.

The architecture is also **data-centric**, with the **NetworkX graph object acting as the central shared data structure** between modules.

The core workflow of the system is:

```
Dataset (CSV / OSMnx)
        ↓
Graph Construction
        ↓
Network Analysis
        ↓
Disruption Simulation
        ↓
Business Impact Translation
        ↓
Visualization
```

Each stage is implemented as an independent module that interacts through clearly defined interfaces.

---

# 2. High-Level Architecture

The system is divided into six primary layers.

```
+------------------------------------------------+
|                Visualization Layer             |
|    (Streamlit + Plotly + Congestion Heatmaps)  |
+------------------------------------------------+
|       Business Metric Translation Engine       |
|      (Translating Graph Metrics → Business)    |
+------------------------------------------------+
|               Simulation Engine                |
|  (Ripple Effect & Disruption Scenario Models)  |
+------------------------------------------------+
|              Network Analysis Engine           |
|   (Centrality, Shortest Paths, Connectivity)   |
+------------------------------------------------+
|              Graph Modeling Engine             |
|   (Network Construction using nx.DiGraph)      |
+------------------------------------------------+
|                   Data Layer                   |
|      (CSV Loaders + OSMnx Geospatial APIs)     |
+------------------------------------------------+
```

Each layer is responsible for a specific stage in the supply chain analysis pipeline.

---

# 3. Data Layer

## Responsibilities

The Data Layer is responsible for loading and validating supply chain datasets, including both structured tabular data and real-world infrastructure graphs.

---

## Input Data Sources

The system supports two primary data pipelines.

### 1. Structured CSV Data

Used to model logical supply chain relationships.

**nodes.csv**

Defines supply chain entities.

Example fields:

```
node_id
node_type
capacity
location
country
```

Node types may include:

* Supplier
* Factory
* Port
* Warehouse
* Distribution Center

**edges.csv**

Defines relationships between entities.

Example fields:

```
source
target
transport_type
distance
cost
transit_time
```

---

### 2. Geospatial Infrastructure Data (OSMnx)

The system can dynamically retrieve infrastructure networks from **OpenStreetMap** using OSMnx.

Examples:

* road networks around industrial hubs
* port logistics regions
* rail infrastructure networks

Example locations:

* Port of Long Beach
* Rotterdam logistics network
* Ruhr industrial region

This allows the system to analyze **real-world transport infrastructure**.

---

# 4. Graph Modeling Engine

## Responsibilities

The Graph Modeling Engine converts dataset inputs into a **directed supply chain network**.

---

## Graph Representation

The system uses the **NetworkX DiGraph structure** to enforce directional logistics flow.

Example:

```
G = nx.DiGraph()

G.add_node(node_id, type="port", country="Singapore")

G.add_edge(source, target, transport="sea", distance=1200)
```

---

## Core Data Structure

The **NetworkX DiGraph object acts as the central system data model**.

All modules operate on the same graph instance.

### Node Attributes

Nodes may include attributes such as:

```
type
capacity
location
country
risk_score
```

### Edge Attributes

Edges may include attributes such as:

```
transport_type
distance
cost
transit_time
congestion_factor
```

This graph becomes the **primary data structure used by all downstream modules**.

---

# 5. Network Analysis Engine

## Responsibilities

The Network Analysis Engine computes structural properties of the supply chain network to identify critical nodes, bottlenecks, and structural vulnerabilities.

---

## Key Metrics

### Degree Centrality

Identifies highly connected logistics hubs.

```
nx.degree_centrality(G)
```

---

### Betweenness Centrality

Identifies nodes that act as **critical transit bridges** in the network.

These nodes often represent:

* ports
* distribution hubs
* logistics gateways

During simulations, this metric is **recalculated dynamically** to identify new congestion points.

```
nx.betweenness_centrality(G)
```

---

### Shortest Path Analysis

The system uses **Dijkstra’s Algorithm** to identify optimal routes based on edge weights such as:

* distance
* transit time
* cost

```
nx.shortest_path(G, weight="distance")
```

---

### Connectivity Metrics

Additional structural indicators include:

* number of connected components
* network density
* average path length
* network diameter

These metrics quantify overall network resilience.

---

# 6. Simulation Engine (The "What-If" Engine)

## Responsibilities

The Simulation Engine models disruption scenarios and evaluates how failures propagate through the supply chain network.

The engine allows users to test **hypothetical disruption scenarios** and observe how the network responds.

---

## Types of Simulations

### Targeted Attack

Removes nodes based on importance metrics.

Example:

* removing the top 5 ports by Betweenness Centrality

This simulates events such as:

* major port shutdown
* geopolitical trade disruption
* infrastructure failure

---

### Random Failure

Randomly removes nodes or edges.

Used to simulate:

* natural disasters
* accidents
* unexpected supplier failures

---

### Ripple Effect Simulator (Cascading Failures)

Models **secondary disruptions caused by rerouting and congestion**.

Procedure:

1. Remove a critical node
2. Recalculate shortest paths
3. Recompute centrality metrics
4. Detect newly overloaded nodes

This identifies **emergent bottlenecks** created by disruption.

After each disruption event, the system recomputes:

* centrality metrics
* shortest paths
* connectivity metrics

This captures **dynamic topology changes** in the supply chain network.

---

# 7. Business Metric Translation Engine

## Responsibilities

This module translates raw graph metrics into **business-relevant insights**.

Graph metrics alone are difficult for decision-makers to interpret.
This layer converts structural changes in the network into **economic and operational impacts**.

---

## Key Outputs

### Lead Time Impact

Increased path lengths translate into delivery delays.

Approximate model:

```
Lead Time Increase ≈ Δ(Average Path Length) × Average Transit Time per Edge
```

Example output:

```
+14 Days Transit Delay
```

---

### Cost Equivalents

Delays are translated into financial estimates.

Approximate model:

```
Estimated Cost Impact ≈ Delay Days × Daily Throughput Value
```

Example:

```
$1.2M daily delay cost
```

---

### Operational Risk Indicators

Additional indicators may include:

* congestion risk scores
* route redundancy levels
* infrastructure criticality ranking

---

# 8. Visualization Layer

## Responsibilities

The Visualization Layer presents network structures, disruption simulations, and business impacts interactively.

---

## Technologies

* Plotly
* Streamlit

---

## Capabilities

### Network Graph Visualization

Displays supply chain topology and node importance.

---

### Congestion Heatmaps

Visualizes ripple effects from disruptions.

Newly overloaded routes are highlighted in red.

---

### Interactive Dashboards

Users can simulate disruptions by interacting with the network:

Example:

* select a node
* simulate failure
* observe changes in routes and business metrics

The system updates results **in real time**.

---

# 9. System Execution Pipeline

The system executes the following workflow:

```
Load Dataset
      ↓
Construct Graph
      ↓
Compute Baseline Metrics
      ↓
Run Disruption Simulation
      ↓
Recalculate Network Metrics
      ↓
Translate Graph Metrics → Business Impact
      ↓
Interactive Visualization
```

---

# 10. Data Flow & Module Interaction

Modules interact primarily through the **NetworkX graph object**.

```
osmnx_loader.py / csv_loader.py
        ↓
graph_builder.py
        ↓
network_metrics.py
        ↓
cascading_failure.py / targeted_attack.py
        ↓
business_metrics_translator.py
        ↓
graph_plot.py
        ↓
streamlit_app.py
```

This modular structure enables easy testing, debugging, and extension of individual components.

---

# 11. Scalability Considerations

Future improvements may include:

### Large Network Handling

Migration to graph databases such as:

* Neo4j

for large-scale global supply chain networks.

---

### Parallel Simulations

Running large numbers of disruption scenarios using:

* multiprocessing
* distributed computing frameworks
* Monte Carlo simulations

---

### Real-Time Data Integration

Potential integration with:

* maritime shipping APIs
* logistics tracking systems
* infrastructure monitoring services

---

# 12. Design Principles

The system architecture follows several design principles.

### Modularity

Each module performs a single responsibility.

---

### Extensibility

New simulation models or metrics can be added without modifying existing modules.

---

### Reproducibility

Simulation results can be reproduced using fixed seeds and deterministic graph operations.

---

### Transparency

All analyses rely on established methods from **network science and graph theory**.

---

# Conclusion

The Supply Chain Fragility & Risk Analyzer combines graph modeling, network science metrics, disruption simulations, and business-impact translation to analyze supply chain resilience.

By modeling supply chains as dynamic networks, the system provides a framework for understanding how infrastructure failures propagate through complex logistics systems and how these disruptions affect operational and economic outcomes.
