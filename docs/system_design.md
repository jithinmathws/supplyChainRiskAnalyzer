# System Design

## Supply Chain Fragility & Risk Analyzer

The Supply Chain Fragility & Risk Analyzer is a **computational framework** designed to analyze the structural resilience of supply chain networks and simulate disruption scenarios.

The system models supply chains as **directed graphs**, where infrastructure locations and logistics facilities form nodes, and transportation routes form edges. Using **graph-theoretic analysis** and simulation techniques, the platform identifies critical infrastructure, evaluates network fragility, and estimates potential operational and financial impacts caused by disruptions.

The system architecture is designed with the following principles:

* **Modularity** – Each analytical component operates independently
* **Reproducibility** – Experiments can be repeated using standardized datasets
* **Extensibility** – New models and analytics can be integrated easily
* **Transparency** – All assumptions and algorithms are explicitly documented

This document describes the system's **architectural components**, **data flow**, and **analytical pipeline**.

---

# 1. System Overview

The Supply Chain Fragility & Risk Analyzer is a computational framework designed to analyze the structural resilience of supply chain networks and simulate disruption scenarios.

The system models supply chains as directed graphs, where infrastructure locations and logistics facilities form nodes, and transportation routes form edges. Using graph-theoretic analysis and simulation techniques, the platform identifies critical infrastructure, evaluates network fragility, and estimates potential operational and financial impacts caused by disruptions.

The system architecture is designed with the following principles:

Modularity – Each analytical component operates independently.

Reproducibility – Experiments can be repeated using standardized datasets.


This document describes the system’s architectural components, data flow, and analytical pipeline.

---

# 2. System Architecture

The platform follows a **modular pipeline architecture** composed of multiple processing stages. Each component operates as a separate functional module within the simulation workflow.

                +----------------------+
                |  Input Data Sources  |
                |  (CSV / OSM Data)    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Data Ingestion     |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Network Construction |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |  Network Analysis    |
                |  (Centrality etc.)   |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Disruption Simulation|
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Impact Assessment    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Visualization Layer  |
                +----------------------+

---

# 3. Data Ingestion Layer

The Data Ingestion Layer is responsible for **loading**, **validating**, and **preprocessing** supply chain datasets before network construction.

## Input Data Types

The system accepts structured datasets describing supply chain infrastructure and transportation connectivity.

| Dataset | Description |
|---------|-------------|
| Nodes dataset | Ports, warehouses, factories, logistics hubs |
| Edges dataset | Transport routes between nodes |
| Geographic data | Coordinates for mapping and routing |
| Throughput values | Estimated daily logistics volumes |

## Data Format

The system currently uses **CSV-based datasets** for reproducibility.

**Example Node Schema:**

```
node_id, node_type, latitude, longitude, throughput_value
```

**Example Edge Schema:**

```
source_node, target_node, transport_mode, distance_km, cost_index
```

## Preprocessing Tasks

The ingestion module performs:

* Data validation
* Missing value handling
* Coordinate verification
* Graph-ready formatting

---

# 4. Network Construction Layer

The Network Construction Module transforms the ingested datasets into a **graph representation** suitable for network analysis.

The supply chain network is modeled as a **directed graph**:

```
G = (V, E)
```

**Where:**

* `V` represents infrastructure nodes
* `E` represents transportation connections

The system uses the **NetworkX Python library** to construct and analyze the graph.

| Property | Description |
|----------|-------------|
| Graph type | Directed (nx.DiGraph) |
| Node attributes | Location, infrastructure type, throughput |
| Edge attributes | Distance, cost estimate, transport mode |

---

# 5. Network Analysis Module

The Network Analysis Module evaluates **structural properties** of the supply chain graph to identify critical nodes and structural vulnerabilities.

## Key Metrics

### Degree Centrality

Measures how many direct connections a node has.

High values often indicate **major logistics hubs**.

### Betweenness Centrality

Measures how frequently a node appears on shortest paths between other nodes.

Nodes with high betweenness act as **network bottlenecks**.

### Closeness Centrality

Measures how quickly a node can reach all other nodes in the network.

Nodes with high closeness are typically **efficient distribution points**.

## Network Connectivity Metrics

Global network metrics include:

* Number of connected components
* Average path length
* Network density

These metrics describe the **overall structural robustness** of the network.

---

# 6. Disruption Simulation Engine

The Disruption Simulation Engine models **supply chain failures** by removing nodes or edges from the network and observing the resulting structural changes.

## 6.1 Node Failure Simulation

Node failure represents the disruption of **critical infrastructure** such as:

* ports
* manufacturing facilities
* distribution centers

When a node is removed:

* All connected edges are removed
* Shortest paths are recalculated
* Network fragmentation is measured

## 6.2 Edge Failure Simulation

Edge failure represents **transportation route disruptions** such as:

* shipping lane closures
* rail corridor interruptions
* road network blockages

Edge removal may increase travel distances or disconnect parts of the network.

## 6.3 Monte Carlo Simulations

To evaluate systemic fragility, the engine performs **randomized Monte Carlo disruption experiments**.

**Typical simulation workflow:**

* Randomly select nodes or edges
* Apply disruption
* Recalculate network metrics
* Record system performance
* Repeat across multiple iterations

This produces **statistical estimates** of network resilience.

---

# 7. Impact Assessment Module

The Impact Assessment Module translates **structural disruptions** into operational and financial consequences.

## 7.1 Operational Impact

Operational impact is estimated using:

* network fragmentation
* path length increases
* unreachable nodes

These metrics estimate potential **supply chain delays**.

## 7.2 Financial Impact Estimation

The system estimates economic impact using **simplified throughput-based models**.

```
Cost_Impact = Delay × Daily_Throughput_Value
```

**Where:**

* `Delay` is estimated based on increased path length
* `Throughput Value` approximates the economic value moving through a node

These estimates provide **directional risk indicators** rather than precise financial forecasts.

---

# 8. Visualization & Reporting Layer

The system includes tools to visualize network structure and disruption effects using libraries such as:

* **Plotly**
* **Streamlit**

The platform generates:

* network topology maps
* critical node highlighting
* disruption impact charts
* resilience distribution plots

These visualizations help analysts interpret simulation results.

---

# 9. Data Flow Pipeline

The complete analytical pipeline follows a **strict, sequential workflow**:

```
Input Datasets
      ↓
Data Ingestion
      ↓
Network Construction
      ↓
Network Analysis
      ↓
Disruption Simulation
      ↓
Impact Assessment
      ↓
Visualization & Reporting
```

Each stage produces **intermediate outputs** used by subsequent modules.

---

# 10. Scalability Considerations

The current implementation is optimized for **small-to-medium supply chain networks**.

Large-scale networks may require:

* distributed graph processing
* parallel Monte Carlo simulations
* cloud-based compute infrastructure

Future versions may integrate scalable graph frameworks such as **Neo4j** or distributed graph processing systems.

---

# 11. Extensibility

The modular design allows for **future expansion** of system capabilities.

**Potential extensions include:**

* **real-time logistics data integration**
* **machine learning risk prediction models**
* **multi-layer supply chain graph modeling**
* **capacity-constrained transportation networks**
* **agent-based supply chain behavior simulation**

---

# 12. Summary

The Supply Chain Fragility & Risk Analyzer provides a **structured analytical platform** for studying supply chain resilience using network science.

Through **modular system architecture** and **reproducible simulation pipelines**, the system enables researchers and analysts to:

* **identify critical infrastructure nodes**
* **simulate disruption scenarios**
* **quantify systemic fragility**
* **estimate operational risk**

The framework serves as a foundation for future research in supply chain resilience, network fragility, and disruption mitigation strategies.