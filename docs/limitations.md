Limitations & Modeling Constraints
Supply Chain Fragility & Risk Analyzer

This document outlines the **primary limitations**, **modeling assumptions**, and **boundary conditions** of the Supply Chain Fragility & Risk Analyzer system.

While the framework provides a **mathematically grounded approach** to analyzing supply chain fragility, network resilience, and disruption propagation, it necessarily relies on a set of **simplifications**, **abstractions**, and **data constraints**. These limitations should be carefully considered when interpreting simulation outputs and risk metrics.

Understanding these constraints ensures that model results are interpreted appropriately, prevents over-generalization, and highlights opportunities for future system improvements.

---

# 1. Purpose of This Document

The objective of this document is to clearly define the **analytical boundaries** of the simulation framework.

Specifically, this document:

* **Identifies assumptions** embedded within the modeling architecture
* **Describes known limitations** of the underlying datasets
* **Explains simplifications** made for computational tractability
* **Clarifies** how real-world supply chain behavior may differ from simulated results

By explicitly documenting these constraints, the project maintains **methodological transparency** and supports responsible use of analytical outputs.

---

# 2. Data Limitations

The accuracy and realism of simulation outcomes depend heavily on the **quality**, **completeness**, and **granularity** of the input datasets used to construct the supply chain network.

Several data-related limitations currently exist.

## 2.1 Proprietary Nature of Supply Chain Data

Real-world enterprise supply chains are **highly proprietary and confidential**.

Organizations rarely disclose detailed information about:

* supplier relationships
* transportation contracts
* inventory strategies
* sourcing dependencies

As a result, fully realistic global supply chain datasets are **extremely difficult to obtain**. The current system therefore relies on synthetic or publicly available datasets to approximate network structure.

## 2.2 Public Infrastructure Data Limitations

Geographic infrastructure data sourced from platforms such as **OpenStreetMap (OSM)** provides excellent information about physical transport infrastructure, including:

* road networks
* ports
* railways
* airports

However, these datasets do not represent **commercial supply chain relationships**, such as:

* contractual shipping routes
* preferred logistics providers
* exclusive supplier partnerships

Consequently, transportation edges in the network represent **potential connectivity**, not guaranteed operational trade routes.

## 2.3 Simplified Transportation Cost Data

In the absence of live freight pricing data, transportation costs within the system are estimated using **static heuristic indices**.

Real-world freight costs vary dynamically due to factors such as:

* fuel price fluctuations
* seasonal demand spikes
* port congestion
* geopolitical disruptions
* carrier capacity shortages

Therefore, cost-related outputs should be interpreted as **relative risk indicators** rather than precise financial predictions.

---

# 3. Simplified Network Representation

The system models supply chains using a **directed graph structure**:

```
G = (V, E)
```

**Where:**

* `V` = set of infrastructure nodes
* `E` = set of transportation edges

This abstraction enables the application of **graph theory algorithms**, such as centrality analysis and shortest path calculations.

However, real supply chains are far more complex than a **single-layer network model**.

## 3.1 Single-Layer Network Flattening

Real-world supply chains operate across **multiple interconnected layers**, including:

* raw material extraction
* component manufacturing
* intermediate assembly
* transportation logistics
* distribution networks
* retail channels

The current MVP implementation **flattens these layers** into a single logistical network to simplify modeling and computation.

While this abstraction enables **tractable network analysis**, it may overlook inter-layer dependencies that influence disruption propagation.

## 3.2 Absence of Capacity Constraints

Nodes and edges in the current system are assumed to have **unlimited capacity**.

In reality, infrastructure elements are constrained by **operational limits**, such as:

* port TEU throughput limits
* warehouse storage capacity
* trucking fleet availability
* rail corridor capacity

Ignoring these constraints simplifies computation but may **underestimate congestion-related risks** during disruption scenarios.

---

# 4. Static Network Assumption

The current model operates on **static network snapshots** derived from preprocessed datasets.

This means that the structure of the supply chain network remains **fixed during simulation runs**.

In practice, supply chains are **dynamic adaptive systems**.

During disruptions, organizations often respond by:

* identifying alternative suppliers
* switching logistics routes
* sourcing from emergency suppliers
* purchasing spot-market transport capacity

These adaptive behaviors are **not dynamically modeled** in the current framework.

---

# 5. Simplified Disruption Modeling

Disruption events in the simulation engine are currently represented as **binary failures**.

This means that nodes or edges are treated as either:

* fully operational
* completely removed from the network

This binary model simplifies implementation but does not capture the **gradual and partial nature** of many real-world disruptions.

**Examples of real disruptions include:**

* ports operating at reduced efficiency (e.g., 40% capacity)
* temporary labor strikes causing partial delays
* infrastructure congestion increasing transit times
* phased recovery after natural disasters

Future versions may introduce **probabilistic capacity degradation models** to better reflect these conditions.

---

# 6. Estimated Business Impact Metrics

Operational and financial impacts in the system are calculated using **simplified deterministic estimators**.

**For example:**

```
Cost Impact = Delay × Daily Throughput Value
```

These formulas provide **approximate directional indicators** of disruption severity.

However, real-world financial consequences are influenced by many additional factors not currently modeled, including:

* safety stock inventory buffers
* contractual force majeure clauses
* flexible production scheduling
* supplier redundancy strategies
* insurance coverage

As a result, financial outputs should be interpreted as **analytical approximations** rather than exact economic forecasts.

---

# 7. Limited Behavioral Modeling

The system functions as a **structural network analyzer**, not a behavioral simulation platform.

Real supply chains involve **human decision-making and strategic responses**.

For example, procurement and logistics teams may respond to disruptions by:

* activating backup suppliers
* expediting shipments via air freight
* negotiating alternative transportation contracts
* reallocating inventory across distribution centers

These adaptive strategies and **game-theoretic behaviors** are currently outside the scope of the simulation engine.

---

# 8. Computational Constraints

The computational complexity of network analysis increases rapidly with network size.

Large global supply chain graphs may contain:

* millions of nodes
* tens of millions of edges

Certain algorithms used in the system are **computationally expensive**, including:

* Betweenness Centrality
* Monte Carlo disruption simulations
* large-scale shortest path recalculations

Performance bottlenecks may arise when running simulations on extremely large networks without distributed computing resources.

---

# 9. Model Scope and Intended Use

The Supply Chain Fragility & Risk Analyzer is designed as a **research-oriented analytical framework**, not a real-time operational decision system.

**Its intended use cases include:**

* studying supply chain network structure
* identifying systemic fragility points
* analyzing disruption propagation patterns
* evaluating theoretical resilience strategies

The system should therefore be viewed as a **strategic analytical tool** rather than a fully operational enterprise logistics platform.

---

# 10. Future Improvements

Several enhancements are planned to address the limitations identified in this document.

**Potential future developments include:**

## Real-Time Logistics Integration

Incorporating live data feeds from logistics APIs to capture real-time network conditions.

## Machine Learning Risk Prediction

Applying predictive models to estimate disruption probabilities and cascading failure risks.

## Multi-Layer Supply Chain Modeling

Extending the graph representation to explicitly model production, transport, and distribution layers.

## Capacity-Constrained Network Simulation

Introducing node and edge capacity limits to capture congestion dynamics.

## Distributed Computing Support

Deploying the simulation framework on cloud-based distributed systems to support large-scale global networks.

---

# 11. Summary

The Supply Chain Fragility & Risk Analyzer provides a **structured and mathematically rigorous framework** for studying supply chain disruption dynamics through the lens of network science.

However, the system relies on several **necessary simplifications**, including:

* **static network assumptions**
* **binary disruption modeling**
* **simplified cost estimation**
* **absence of behavioral adaptation**

By acknowledging these limitations, analysts can appropriately interpret fragility scores, disruption metrics, and financial estimates produced by the simulation engine.

Ongoing development aims to progressively bridge the gap between theoretical network analysis and real-world supply chain complexity.