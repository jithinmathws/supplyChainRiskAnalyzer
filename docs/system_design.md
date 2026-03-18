# System Design

## Supply Chain Fragility & Risk Analyzer

The **Supply Chain Fragility & Risk Analyzer** is a modular analytical platform designed to evaluate supply chain resilience using **graph-based digital twin modeling** and **disruption simulation**.

The system models supply chains as **directed multi-route networks** and evaluates fragility using:

* scenario-based disruption testing
* capacity-aware cascading simulations
* **time-based routing (lead-time modeling)**
* **flow-level economic impact analysis**

Unlike traditional structural network tools, the platform emphasizes:

* **flow-driven behavior** (demand routing, not static topology)
* **rerouting feasibility under disruption**
* **business impact translation (cost, delay, unmet demand)**

This document describes the system’s **design principles**, **components**, and **analytical pipeline**.

---

# 1. Design Objectives

### Modularity

Each analytical component operates independently with clear interfaces.

### Reproducibility

Simulations are deterministic and reproducible with fixed inputs.

### Extensibility

New simulation models, metrics, and datasets can be added easily.

### Transparency

Uses interpretable graph-based logic instead of black-box models.

### Realism

Incorporates **time-based routing, capacity constraints, and demand flow behavior**.

---

# 2. System Overview

The platform follows a structured analytical pipeline:

```id="sysflow1"
CSV Dataset  
     ↓  
Graph Construction  
     ↓  
Baseline Network Analysis  
     ↓  
Scenario Analysis  
     ↓  
Cascade Simulation  
     ↓  
Business Impact Engine  
     ↓  
Interactive Visualization  
```

Each stage transforms the network into progressively higher-level insights.

---

# 3. Core Design Components

---

## 3.1 Data Ingestion Layer

### Responsibilities

Loads and validates structured datasets describing supply chain infrastructure.

---

### Input Types

| Dataset             | Description                       |
| ------------------- | --------------------------------- |
| nodes.csv           | Supply chain entities             |
| edges.csv           | Primary transport routes          |
| alternate_edges.csv | Backup routes                     |
| flows.csv           | Demand flows (origin–destination) |

---

### Validation Pipeline

* schema validation
* type normalization
* duplicate detection
* referential integrity checks
* missing value handling

---

## 3.2 Graph Construction Layer

### Responsibilities

Transforms structured data into a **directed network model**.

---

### Graph Representation

```id="sysgraph1"
NetworkX MultiDiGraph
```

Supports:

* parallel routes
* multiple transport modes
* redundancy modeling
* capacity-aware simulation

---

### Key Design Decision

> Edge **weight represents time (lead time)** — not distance or hop count.

This enables:

* realistic routing
* delay-aware simulation
* meaningful business metrics

---

### Node Attributes

* type
* capacity
* location
* tier
* recovery_time

---

### Edge Attributes

* transport_mode
* distance
* **weight (time)**
* capacity
* cost
* reliability

---

## 3.3 Baseline Network Analysis

### Responsibilities

Establishes baseline network behavior before disruptions.

---

### Core Capabilities

* shortest path computation (time-based)
* baseline lead-time estimation
* route feasibility validation

---

### Routing Method

```id="sysroute1"
Dijkstra Shortest Path (weight = time)
```

---

## 3.4 Scenario Analysis Engine

### Responsibilities

Evaluates fragility across multiple flows under disruptions.

---

### Capabilities

* node disruption simulation
* edge disruption simulation
* multi-flow evaluation
* aggregated impact scoring

---

### Outputs

* bottleneck rankings
* disruption classification (delivered / rerouted / disconnected)
* lead-time increase
* cost change

---

## 3.5 Cascade Simulation Engine

### Responsibilities

Models **dynamic cascading failures** driven by demand and capacity.

---

### Core Simulation Loop

1. Apply initial disruption
2. Recompute shortest paths
3. Route flows
4. Accumulate edge loads
5. Remove overloaded edges
6. Repeat until stable

---

### Key Design Feature

> Simulation is **flow-driven**, not purely structural.

Meaning:

* demand flows determine stress
* network evolves dynamically
* failures propagate realistically

---

### Outputs

#### Flow-Level Metrics

* baseline vs final path
* rerouting status
* delivered vs unmet demand
* **time increase (delay)**
* cost increase
* hop increase

---

#### System-Level Metrics

* service level
* disrupted flows
* unmet demand
* total economic impact

---

#### Step-Level Metrics

* routed demand per step
* new failures
* cumulative failures

---

## 3.6 Business Impact Engine

### Responsibilities

Converts simulation outputs into **decision-relevant KPIs**.

---

### Economic Model

#### Reroute Cost

```id="syscost1"
(cost increase × demand × reroute_cost_rate)
```

#### Delay Penalty

```id="syscost2"
(time increase × demand × delay_penalty_rate)
```

#### Unmet Demand Loss

```id="syscost3"
(unmet demand × unmet_demand_loss_rate)
```

---

### Aggregate Outputs

* total economic impact
* service level
* unmet demand
* disruption ratio

---

### Key Insight

> The system bridges **network behavior → business outcomes**, enabling practical decision support.

---

# 4. Visualization & Application Layer

### Responsibilities

Provides an interactive interface for analysis and simulation.

---

### Technologies

* Streamlit
* Plotly

---

### UI Architecture

* service-layer abstraction
* modular UI components
* session state management

---

### UI Modules

* Node Analysis
* Edge Analysis
* Scenario Analysis
* Cascade Simulation
* Network Visualization

---

### User Capabilities

* define demand flows
* simulate disruptions
* analyze cascading failures
* evaluate economic impact

---

# 5. Data Flow Design

```id="sysflow2"
Input Data
     ↓
Graph Builder
     ↓
Baseline Analysis
     ↓
Scenario Engine
     ↓
Cascade Simulator
     ↓
Business Metrics Engine
     ↓
Visualization
```

---

# 6. Scalability Considerations

Current system supports **small-to-medium networks**.

Future improvements:

* stochastic demand modeling
* Monte Carlo simulation
* distributed computation
* multi-layer supply chain graphs
* graph databases (Neo4j)

---

# 7. Extensibility

The modular design supports:

* probabilistic disruption models
* real-time data integration
* ML-based risk prediction
* agent-based simulations

---

# 8. Summary

The Supply Chain Fragility & Risk Analyzer provides a **digital twin framework** for supply chain resilience.

By combining:

* graph modeling
* flow-based simulation
* economic impact analysis

the system enables **deep, actionable insights into network fragility and disruption risk**.
