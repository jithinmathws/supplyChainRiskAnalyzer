# System Architecture

## Supply Chain Fragility & Risk Analyzer

This document describes the architecture of the **Supply Chain Fragility & Risk Analyzer**, a **graph-based digital twin system** for modeling supply chain networks and simulating disruption-driven fragility.

The platform models logistics systems as **directed multi-route graphs** and evaluates how disruptions propagate through infrastructure using:

* scenario-based simulation
* capacity-aware cascading failures
* **time-based delay modeling**
* **economic impact translation**

The system follows a **layered, modular architecture** built around a shared NetworkX graph model and supports interactive analysis through a Streamlit-based UI.

---

# 1. Architectural Overview

The system follows a **Layered Analytical Pipeline Architecture**, where each stage transforms a shared network representation into progressively higher-level insights.

The central data structure is a:

```
NetworkX MultiDiGraph
```

This enables:

* multiple parallel routes
* attribute-rich edges (time, cost, capacity)
* realistic logistics modeling

---

## Core Workflow

```
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
Interactive Dashboard  
```

Each stage is **loosely coupled**, allowing independent extension and testing.

---

# 2. High-Level Architecture

```
+--------------------------------------------------+
|               Application Layer                  |
|     (Streamlit UI + Service Abstraction Layer)  |
+--------------------------------------------------+
|             Visualization Layer                 |
|        (KPIs, Tables, Network Graphs)           |
+--------------------------------------------------+
|         Business Impact Engine                  |
|   (Cost, Delay, Service-Level Modeling)         |
+--------------------------------------------------+
|             Simulation Engine                   |
|    (Scenario Engine + Cascade Simulator)        |
+--------------------------------------------------+
|           Network Analysis Engine               |
|   (Routing, Connectivity, Fragility Metrics)    |
+--------------------------------------------------+
|            Graph Modeling Engine                |
|     (MultiDiGraph Construction & Validation)    |
+--------------------------------------------------+
|                  Data Layer                     |
|               (Structured CSV)                  |
+--------------------------------------------------+
```

---

# 3. Data Layer

## Responsibilities

The Data Layer loads, validates, and normalizes structured datasets representing supply chain infrastructure.

---

## Supported Inputs

### Nodes (`nodes.csv`)

Defines supply chain entities:

* suppliers
* factories
* ports
* warehouses
* distribution hubs

**Core fields:**

```
node_id, name, type, location, capacity
```

**Optional fields:**

```
tier, region, recovery_time, criticality
```

---

### Edges (`edges.csv`, `alternate_edges.csv`)

Defines logistics relationships between nodes.

**Core fields:**

```
source, target, transport_mode, distance, transport_time
```

**Optional fields:**

```
capacity, cost, reliability, recovery_time
```

---

## Validation Pipeline

The system performs:

* schema validation
* type normalization
* duplicate detection
* missing value handling
* graph consistency checks

---

# 4. Graph Modeling Engine

## Responsibilities

Transforms structured data into a **directed supply chain network**.

---

## Graph Representation

```
nx.MultiDiGraph
```

Supports:

* multiple parallel routes
* different transport modes
* redundancy modeling

---

## Core Data Model

The graph acts as the **shared state across all modules**.

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
* **weight (time / lead time)**
* capacity
* cost

> ⚠️ The `weight` attribute represents **time**, not hops — enabling realistic delay modeling.

---

# 5. Network Analysis Engine

## Responsibilities

Computes baseline structural and routing properties.

---

## Core Functions

### Shortest Path Routing

Uses:

```
Dijkstra Algorithm (weight = time)
```

Enables:

* fastest path selection
* delay-aware rerouting
* realistic logistics behavior

---

### Fragility Indicators

* connectivity loss
* alternative path availability
* rerouting feasibility
* lead-time increase

---

# 6. Simulation Engine

The Simulation Engine contains two major components:

---

## 6.1 Scenario Analysis Engine

Evaluates disruption scenarios across multiple flows.

### Capabilities

* multi-flow simulation
* node and edge disruption modeling
* rerouting feasibility analysis
* impact aggregation

### Outputs

* bottleneck rankings
* disruption classifications
* delay and cost changes

---

## 6.2 Cascade Simulator (Capacity-Aware)

Models **dynamic cascading failures**.

---

### Core Algorithm

1. Apply initial disruptions
2. Recompute shortest paths
3. Route demand flows
4. Accumulate edge loads
5. Remove overloaded edges
6. Repeat until stable

---

### Real-World Effects Captured

* congestion spillover
* infrastructure overload
* secondary failures
* network fragmentation

---

## Cascade Outputs

### Flow-Level Metrics

* baseline vs final path
* rerouting status
* delivered vs unmet demand
* **time increase (delay)**
* cost increase
* hop change

---

### System-Level Metrics

* service level
* disrupted flows
* unmet demand
* total economic impact

---

### Step-Level Metrics

* routed demand per step
* new failures per step
* cumulative failures

---

# 7. Business Impact Engine

## Responsibilities

Translates simulation results into **decision-ready KPIs**.

---

## Economic Model

### Reroute Cost

```
(cost increase × demand × reroute_cost_rate)
```

### Delay Penalty

```
(time increase × demand × delay_penalty_rate)
```

### Unmet Demand Loss

```
(unmet demand × unmet_demand_loss_rate)
```

---

## Aggregate Outputs

* total economic impact
* service level
* unmet demand
* disruption ratio

---

## Key Insight

> The system bridges **network-level disruption** with **business-level consequences**, making it usable beyond pure graph analysis.

---

# 8. Visualization Layer

## Responsibilities

Transforms analytical outputs into interactive insights.

---

## Technologies

* Streamlit
* Plotly

---

## Capabilities

### KPI Dashboard

* service level
* economic impact
* disruption metrics

---

### Analytical Tables

* flow impact tables
* cascade step metrics
* bottleneck rankings

---

### Network Visualization

* topology display
* disruption highlighting
* fragility overlays

---

# 9. Application Layer (Streamlit)

## Responsibilities

Provides an interactive simulation environment.

---

## Architecture

* service-layer abstraction
* modular UI components
* session state management

---

## UI Modules

* Node Analysis
* Edge Analysis
* Scenario Analysis
* Cascade Simulation
* Network Visualization

---

## User Capabilities

* define flows
* simulate disruptions
* analyze cascading effects
* evaluate economic impact

---

# 10. Module Interaction Flow

```
CSV Data
   ↓
Graph Builder
   ↓
Analysis Engines
   ↓
Simulation Engines
   ↓
Service Layer
   ↓
Streamlit UI
```

---

# 11. Design Principles

### Modularity

Each component is independently testable.

### Extensibility

New simulation models can be added easily.

### Determinism

Simulations are reproducible.

### Realism

Time-based routing and capacity constraints improve fidelity.

---

# 12. Scalability Considerations

Future enhancements:

* stochastic disruptions
* Monte Carlo simulation
* multi-layer supply chain networks
* graph databases (Neo4j)
* distributed simulation

---

# Conclusion

The Supply Chain Fragility & Risk Analyzer integrates:

* graph modeling
* disruption simulation
* economic impact translation

into a unified **digital twin framework**.

By combining network science with business metrics, the system enables **actionable insights for real-world supply chain resilience**.
