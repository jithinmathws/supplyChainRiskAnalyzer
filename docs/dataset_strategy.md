# Dataset Strategy & Data Sources

## Supply Chain Fragility & Risk Analyzer

This document describes the data architecture and acquisition strategy used in the Supply Chain Fragility & Risk Analyzer. The goal is to construct network graphs that represent global and regional logistics infrastructure.

The dataset strategy supports:

* **disruption simulations**
* **critical bottleneck identification**
* **routing delay estimation**
* **translation of network failures into business impact metrics**

---

# 1. Dataset Objectives

To successfully model cascading failures and routing delays, dataset must represent **key structural components** of supply chains.

**Required data characteristics:**

* logistics infrastructure nodes (ports, hubs, factories)
* transportation connectivity (roads, rail, shipping lanes)
* routing costs (distance, financial cost, transit time)
* geographic distribution for geospatial mapping

These elements allow the system to build a **realistic transportation network graph**.

---

# 2. Data Architecture

The system models supply chains using a **Node–Edge tabular structure**, which is converted into a directed graph.

NetworkX Graph Type: nx.DiGraph

## 2.1 Node Data (Infrastructure)

Nodes represent **physical supply chain entities**.

Examples include:

* ports
* factories
* suppliers
* warehouses
* logistics hubs

### Node Dataset Structure

| Field | Description | Example |
|-------|-------------|---------|
| node_id | Unique identifier | N102 |
| name | Infrastructure name | Port of Long Beach |
| type | Entity type (port, factory, warehouse, supplier) | port |
| latitude | Geographic latitude | 33.7541 |
| longitude | Geographic longitude | -118.2165 |
| capacity | Estimated throughput capacity | 130000 |
| region | Geographic region or cluster | US West Coast |

**Example record:**

```
node_id: N102
name: Port of Long Beach
type: port
latitude: 33.7541
longitude: -118.2165
capacity: 130000
region: US West Coast
```

## 2.2 Edge Data (Transportation Links)

Edges represent **transportation corridors** and **logistics dependencies** between nodes.

These connections define pathways used for routing goods across the network.

### Edge Dataset Structure

| Field | Description | Example |
|-------|-------------|---------|
| source_node | Origin node_id | Factory_A |
| destination_node | Destination node_id | N102 |
| distance_km | Distance between nodes | 1200 |
| transit_time_days | Estimated travel time | 3 |
| transport_type | Transport modality (shipping, rail, road, air) | rail |
| cost_index | Relative financial cost | 0.7 |

**Example record:**

```
source_node: Factory_A
destination_node: N102
distance_km: 1200
transit_time_days: 3
transport_type: rail
cost_index: 0.7
```

## 3. Data Acquisition Strategy

The project uses a **hybrid data strategy** that combines:

* **real-world logistics infrastructure**
* **synthetic network generation**

This approach enables both realistic analysis and scalable simulation.

## 3.1 Real-World Geospatial Data (OSMnx)

To analyze real-world logistics choke points, the system extracts infrastructure networks using the **OSMnx Python library**.

OSMnx provides access to transportation infrastructure from **OpenStreetMap (OSM)**.

### Data Sources

* **OpenStreetMap APIs**
* global road networks
* railway infrastructure
* industrial districts

### Example Target Regions

* major port logistics networks
* industrial manufacturing clusters
* global freight corridors

**Examples:**

* Port of Rotterdam logistics network
* Ruhr Valley industrial corridor
* Southeast Asian port networks

### Benefits

* high-resolution transportation graphs
* realistic routing structures
* accurate geospatial representation

## 3.2 Synthetic Data Generation

Real supply chain data is often **proprietary or incomplete**.
To address this limitation, the system supports synthetic dataset generation.

Synthetic datasets allow the system to:

* simulate large-scale logistics networks
* stress-test algorithms
* run large disruption simulations

**Synthetic generation includes:**

* randomized geographic node placement
* clustered industrial zones
* simulated logistics hubs
* scalable network expansion

Example large-scale test networks may include **5,000+ nodes**.

---

# 4. Graph Construction Pipeline

The dataset is transformed into a computational model using the following pipeline.

---

## Step 1 — Data Ingestion

Load datasets into the system.

```
nodes.csv
edges.csv
```

These files are loaded into **Pandas DataFrames**.

---

## Step 2 — Data Normalization

Preprocessing operations include:

* removing duplicate nodes
* validating edge references
* handling missing values
* normalizing geographic coordinates

---

## Step 3 — Edge Weight Calculation

Each edge receives a weight representing **transportation friction**.

This value is used by shortest-path algorithms such as **Dijkstra's algorithm**.

**Weight formula:**

```
weight =
(alpha * distance_km) +
(beta * transit_time_days) +
(gamma * cost_index)
```

**Where:**

* `alpha` = distance importance
* `beta` = transit time importance
* `gamma` = financial cost importance

---

## Step 4 — Graph Instantiation

The processed dataset is converted into a **directed graph**.

**Example:**

```
G = nx.DiGraph()
```

Nodes and edges are added with their attributes.

**Example:**

```
G.add_node(node_id, type=type, capacity=capacity)

G.add_edge(source, destination,
           distance=distance_km,
           transit_time=transit_time_days,
           cost_index=cost_index)
```

## 5. Dataset Scaling Configurations

The system supports multiple dataset sizes depending on simulation complexity.

Network Size	Nodes	Edges	Use Case
Small	50	150	Algorithm testing
Medium	200	800	Regional modeling
Large	1000+	5000+	Global disruption simulations

Larger networks allow more realistic modeling of cascading supply chain failures.

## 6. Dataset Storage Format

Datasets are stored as portable CSV files.

Example directory structure:

dataset/
    nodes.csv
    edges.csv

These files are loaded during runtime and converted into network graph used for analysis.

## 7. Dataset Limitations & Mitigation

Real-world logistics data presents several challenges.

### Incomplete Private Data

Many enterprise supply chains are proprietary and not publicly accessible.

Mitigation:

* statistical estimation
* trade flow reports
* synthetic augmentation

### Static Cost Assumptions

Transportation costs fluctuate in real markets.

Mitigation:

Future versions may integrate:

* live logistics APIs
* shipping rate feeds
* fuel cost updates

### Simplified Network Layers

Real supply chains consist of multiple layers:

* production
* transportation
* distribution
* retail

Current architecture simplifies this into a single directed network layer.

Mitigation:

Future versions will support multi-layer supply chain graphs.

## 8. Summary

The dataset strategy combines:

* **real-world geospatial infrastructure**
* **transportation network data**
* **synthetic network generation**
* **scalable dataset construction**

This approach enables the Supply Chain Fragility & Risk Analyzer to simulate disruptions and analyze resilience across complex logistics networks.

The resulting datasets support:

* **routing analysis**
* **bottleneck detection**
* **cascading failure simulations**
* **supply chain fragility assessment**