# Dataset Strategy & Data Sources

## Supply Chain Fragility & Risk Analyzer

This document describes the dataset design and preparation strategy used in the Supply Chain Fragility & Risk Analyzer.

The system constructs supply chain networks from structured tabular datasets and converts them into a **directed multi-route graph** for disruption simulation.

---

# 1. Dataset Objectives

The dataset must support:

* flow-based routing
* cascade simulation
* delay estimation
* economic impact modeling

To achieve this, datasets represent:

* infrastructure nodes
* transport connectivity
* routing time
* capacity constraints

---

# 2. Data Architecture

The system uses a **node–edge tabular structure** converted into:

```id="data1"
nx.MultiDiGraph
```

This enables:

* parallel routes
* multi-modal transport
* capacity-aware simulation

---

# 3. Node Dataset (nodes.csv)

Nodes represent supply chain infrastructure:

* suppliers
* factories
* ports
* warehouses
* distribution hubs

---

## Required Fields

| Field   | Description         |
| ------- | ------------------- |
| node_id | Unique identifier   |
| name    | Infrastructure name |
| type    | Entity category     |
| region  | Geographic grouping |

---

## Optional Fields

| Field                | Description           |
| -------------------- | --------------------- |
| capacity             | Throughput estimate   |
| latitude / longitude | Visualization support |

---

# 4. Edge Dataset (edges.csv)

Edges represent transport relationships.

---

## Required Fields

| Field        | Description                    |
| ------------ | ------------------------------ |
| source       | Origin node                    |
| target       | Destination node               |
| transit_time | Travel time (used for routing) |

---

## Optional Fields

| Field          | Description                 |
| -------------- | --------------------------- |
| capacity       | Throughput constraint       |
| cost           | Transport cost              |
| distance       | Distance metric             |
| transport_mode | Mode (rail, road, sea, air) |

---

# 5. Routing Weight Design

Routing uses:

```id="data2"
weight = transit_time
```

👉 Time is chosen because it best reflects logistics performance.

Distance and cost are stored for:

* reporting
* economic modeling

---

# 6. Data Preparation Pipeline

---

## Step 1 — Load Data

```id="data3"
nodes.csv  
edges.csv
```

Loaded into Pandas.

---

## Step 2 — Validation

Checks include:

* duplicate nodes
* missing references
* numeric consistency

---

## Step 3 — Graph Construction

Graph created as:

```id="data4"
nx.MultiDiGraph()
```

Edges include:

* time weight
* capacity
* cost

---

# 7. Dataset Scaling Strategy

Typical dataset sizes:

| Scale  | Nodes | Use Case       |
| ------ | ----- | -------------- |
| Small  | 50    | testing        |
| Medium | 200   | regional       |
| Large  | 1000+ | stress testing |

---

# 8. Data Sources Strategy

---

## 8.1 Current Approach (Implemented)

The project currently uses:

* curated synthetic datasets
* manually structured logistics networks

👉 These support controlled experimentation.

---

## 8.2 Future Data Integration (Planned)

Potential sources:

* OpenStreetMap (OSMnx)
* UN trade flow datasets
* port throughput statistics

---

# 9. Dataset Limitations

---

## Incomplete Real-World Coverage

Most supply chain data is proprietary.

👉 synthetic augmentation is used.

---

## Static Assumptions

Datasets are static during simulation.

👉 no dynamic updates modeled.

---

## Single-Layer Simplification

Real supply chains are multi-layered.

👉 current model flattens layers.

---

# 10. Summary

The dataset strategy enables:

* realistic routing simulation
* cascade modeling
* delay estimation
* business impact analysis

The design balances:

* realism
* simplicity
* scalability

Future improvements will expand real-world integration and multi-layer modeling.
