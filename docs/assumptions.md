# Modeling Assumptions

## Supply Chain Fragility & Risk Analyzer

This document outlines **core modeling assumptions** underlying the Supply Chain Fragility & Risk Analyzer.

All simulation systems require **simplifying assumptions** in order to make complex real-world systems computationally tractable. These assumptions define how the supply chain network is represented, how disruptions are modeled, and how operational and financial impacts are estimated.

Clearly documenting these assumptions ensures:

* **Transparency** in analytical methodology
* **Reproducibility** of simulation experiments
* **Proper interpretation** of model outputs

The assumptions described here apply to the **current system implementation (MVP)**.

---

# 1. Overview

This document outlines the core modeling assumptions underlying the Supply Chain Fragility & Risk Analyzer.

All simulation systems require simplifying assumptions in order to make complex real-world systems computationally tractable. These assumptions define how the supply chain network is represented, how disruptions are modeled, and how operational and financial impacts are estimated.

Clearly documenting these assumptions ensures:

Transparency in analytical methodology

Reproducibility of simulation experiments

Proper interpretation of model outputs

The assumptions described here apply to the current system implementation (MVP).

# 2. Network Representation Assumptions

The system models supply chains as **directed graphs**:

```
G = (V, E)
```

**Where:**

* `V` represents infrastructure nodes
* `E` represents transportation connections

Several assumptions are made regarding this network structure.

## 2.1 Infrastructure as Discrete Nodes

Each supply chain location is modeled as a **single node** within the network.

**Examples include:**

* ports
* manufacturing plants
* warehouses
* distribution centers

The model assumes that each node represents a **distinct, atomic operational entity**, even though real-world facilities may consist of multiple subcomponents.

## 2.2 Transportation as Directed Edges

Transportation routes are represented as **directed edges** connecting nodes.

Edges represent potential logistics flows such as:

* maritime shipping routes
* trucking corridors
* rail connections
* air freight routes

Edges are assumed to represent **available transport pathways**, although model does not explicitly represent contractual shipping relationships.

## 2.3 Single-Layer Network Model

The current implementation represents supply chain as a **single-layer logistical network**.

Real supply chains consist of **multiple interconnected layers**, including:

* raw material extraction
* manufacturing
* transportation
* distribution
* retail

These layers are **flattened into a single network** to simplify graph structure and analytical computations.

# 3. Static Network Structure

The model assumes that **network topology remains fixed** during a single simulation run.

This means that:

* Nodes do not dynamically appear or disappear (except during targeted disruption injections)
* New transportation routes are not created dynamically during simulations
* Organizations do not dynamically reroute shipments mid-transit

In real-world supply chains, companies actively adapt to disruptions by sourcing alternative suppliers or rerouting shipments. These adaptive behaviors are **not currently modeled**.

---

# 4. Infrastructure Capacity Assumptions

The current model assumes that all nodes and edges have **unlimited capacity**.

This implies that:

* ports can process unlimited cargo
* warehouses can store unlimited goods
* transportation routes cannot become congested to point of total gridlock

In practice, supply chain infrastructure has **strict operational limits**, such as:

* port TEU throughput limits
* warehouse storage capacity
* trucking fleet availability
* rail corridor capacity

Ignoring capacity constraints simplifies network analysis but relies on centrality metrics to infer congestion risk rather than modeling explicit throughput limits.

---

# 5. Disruption Modeling Assumptions

Disruptions are represented using **simplified structural models**.

---

## 5.1 Binary Failure Model

Infrastructure disruptions are modeled as **binary failures**.

A node or edge is assumed to be either:

* fully operational
* completely removed from network

Partial failures (such as reduced capacity, congestion, or labor slowdowns) are **not represented** in the current model.

---

## 5.2 Instantaneous Disruptions

Disruptions are assumed to occur **instantaneously** during simulation.

The model does not currently simulate:

* gradual infrastructure degradation
* phased disruption events
* recovery timelines

# 6. Routing Assumptions

Supply chain flows are assumed to follow **shortest-path routing** within the network.

Routing decisions are determined using **Dijkstra's Algorithm**, optimizing for minimal transportation distance or travel time.

Real-world routing decisions may also consider:

* contractual obligations
* inventory levels
* geopolitical constraints
* carrier availability

These factors are **not explicitly represented** in the current framework.

---

# 7. Risk and Cost Estimation Assumptions

Operational and financial impacts are estimated using **simplified linear models**.

---

## 7.1 Throughput-Based Value Estimation

Each node is assigned an estimated **daily throughput value**, representing the economic value of goods moving through that location.

This value is used to approximate the financial impact of disruptions.

---

## 7.2 Linear Cost Estimation

Financial disruption impacts are estimated using a **simplified linear equation**:

```
Cost_Impact = Delay × Daily_Throughput_Value
```

This assumes that financial losses increase linearly with supply chain delays.

Real-world financial outcomes may involve:

* nonlinear economic effects
* contractual penalties
* inventory buffers
* supply substitution strategies

These factors are **not currently modeled**.

---

# 8. Disruption Scenario Assumptions

The simulation engine evaluates network fragility using **randomized and targeted disruption scenarios**.

**Examples include:**

* random infrastructure failures
* targeted attacks on highly central nodes
* transportation route disruptions

These scenarios are used to explore **systemic vulnerabilities**, rather than predict specific real-world future events.

---

# 9. Simulation Experiment Assumptions

Monte Carlo simulation experiments assume that **disruption events occur independently** across iterations.

Each simulation run:

* randomly selects disruption targets
* recalculates network metrics
* records resulting impacts

The statistical outputs therefore represent **probabilistic estimates** of network resilience, rather than deterministic predictions.

# 10. Scope of Modeling Framework

The Supply Chain Fragility & Risk Analyzer is designed primarily as a **structural network analysis framework**.

The system focuses on:

* supply chain topology
* infrastructure connectivity
* disruption propagation through network structure

The model does not currently represent **behavioral or organizational decision-making processes**, such as procurement strategy or logistics management.

---

# 11. Summary

The Supply Chain Fragility & Risk Analyzer relies on several **simplifying assumptions** to enable tractable simulation of complex supply chain networks.

**Key assumptions include:**

* **supply chains represented as directed graphs**
* **static network topology during simulation**
* **unlimited infrastructure capacity**
* **binary disruption models**
* **shortest-path routing behavior**
* **simplified financial impact estimation**

These assumptions allow the system to focus on **structural fragility** and **disruption propagation dynamics** while maintaining computational efficiency.

Future system enhancements may relax several of these assumptions by incorporating:

* **multi-layer supply chain models**
* **capacity constraints**
* **partial infrastructure failures**
* **behavioral adaptation models**