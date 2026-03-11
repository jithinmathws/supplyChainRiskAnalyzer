# Supply Chain Fragility & Risk Analyzer

Supply Chain Fragility & Risk Analyzer is a **graph-based analytical system** that models supply chain infrastructure as networks and analyzes their vulnerability to disruptions.

The system acts as a **"What-If" simulation engine**, evaluating how failures in critical logistics infrastructure affect the stability, efficiency, and financial performance of supply chains.

By combining **network science, disruption simulation, and business impact translation**, the tool provides insights into how supply chain networks behave under stress.

---

# Motivation

Modern supply chains are highly interconnected and globally distributed. Disruptions at critical nodes—such as ports, suppliers, or logistics hubs—can propagate across the entire network.

Major global events such as the **Ever Given Suez Canal blockage** and the **COVID-19 pandemic** demonstrated how fragile global supply chains can be.

Organizations need analytical tools to:

* Identify critical infrastructure nodes
* Simulate disruption scenarios
* Measure network resilience
* Evaluate alternative routing strategies

This project provides an **open-source analytical prototype** for modeling and evaluating supply chain fragility using graph theory and network analysis.

---

# Key Features

* Build supply chain networks from structured datasets
* Identify critical nodes using graph centrality analysis
* Simulate disruptions such as node or route failures
* Model cascading failures across logistics infrastructure
* Measure supply chain fragility and connectivity loss
* Translate network disruptions into business-level impact
* Visualize network structure and disruption outcomes
* Provide an interactive analysis dashboard

---

# High-Impact Features

## 1. Ripple Effect Simulator (What-If Engine)

The system includes a **Ripple Effect Simulator**, designed to model how disruptions propagate through supply chain networks.

Instead of simply visualizing a network, the simulator allows users to test **"What-If" scenarios**.

### Example scenario

1. Remove a critical logistics hub such as a port or transport corridor
2. Recalculate network metrics in real time
3. Identify nodes that become overloaded or critical

When a node is removed, the system recalculates metrics such as **Betweenness Centrality** to detect congestion shifts across the network.

Output includes a **congestion heatmap** highlighting nodes that experience increased traffic or dependency after the disruption.

Example:

```
Remove Node: Rotterdam Port
→ Recalculate centrality metrics
→ Identify alternative logistics hubs now carrying excess load
```

This helps model **cascading failures**, where disruption in one node causes stress on other parts of the network.

---

## 2. Real Infrastructure Data

The project can analyze **real transportation networks**, not just synthetic examples.

Network datasets can be collected using the `osmnx` Python library, which extracts road and rail networks from **OpenStreetMap**.

Example case studies include logistics regions such as:

* Ruhr Valley industrial corridor (Germany)
* Port of Long Beach logistics network (United States)

This allows the project to simulate real-world disruptions such as:

* port shutdowns
* transport corridor failures
* labor strikes affecting logistics hubs

Example analysis question:

```
How resilient is the US West Coast logistics network if a major port shuts down?
```

---

## 3. Business-Oriented Risk Metrics

Traditional graph analysis produces technical metrics such as:

```
Node X has the highest betweenness centrality
```

However, decision makers require **business impact insights**.

This project converts graph metrics into operational consequences such as:

* increased transport time
* congestion in logistics corridors
* delivery delays
* financial disruption costs

Example insight:

```
Failure of Node X increases average delivery lead time by 42%
Estimated operational impact: $1.2M in daily logistics delays
```

By connecting network analysis to **time and cost impacts**, the system provides insights useful for:

* logistics planners
* infrastructure analysts
* supply chain risk managers

---

# Core Concepts

The system models supply chains as **directed graphs**.

### Nodes represent supply chain entities

* suppliers
* factories
* ports
* warehouses
* distribution hubs

### Edges represent relationships

* shipping routes
* supplier dependencies
* transport links

Graph analysis techniques are then used to identify **critical components and structural vulnerabilities**.

---

# System Workflow

The system processes supply chain data through the following analytical pipeline:

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
Visualization Dashboard
```

Each stage transforms the network representation and passes it to downstream modules.

---

# Project Architecture

The system follows a **layered modular architecture**.

### Data Layer

Loads supply chain datasets and infrastructure networks from CSV files or geospatial sources.

### Graph Modeling Engine

Constructs the supply chain network using directed graph structures.

### Network Analysis Engine

Computes graph metrics such as centrality, shortest paths, and connectivity.

### Simulation Engine

Runs disruption simulations including random failures, targeted attacks, and cascading ripple effects.

### Business Metric Translation Engine

Translates graph-level metrics into operational and financial impacts.

### Visualization Layer

Displays network structures, congestion heatmaps, and disruption results using interactive dashboards.

---

# Project Structure

```
supply_chain_risk_analyzer/

data/
    nodes.csv
    edges.csv

core/
    graph_builder.py
    network_metrics.py

simulations/
    random_failure.py
    targeted_attack.py
    cascading_failure.py

analysis/
    edge_bottleneck_detection.py
    bottleneck_detection.py
    business_metrics_translator.py
    scenario_analysis.py

visualization/
    graph_plot.py
    fragility_plots.py
    scenario_plots.py

app/
    streamlit_app.py
    run_fragility_analysis.py

notebooks/
    exploratory_analysis.ipynb

docs/
    architecture.md
    mathematical_model.md
    dataset_strategy.md
    assumptions.md
    experiment_guide.md
    simulation_engine.md
    limitations.md
    dataset_strategy.md
    system_design.md
    development_roadmap.md

README.md
```

---

# Example Network Representation

A simplified supply chain network may look like this:

```
Supplier → Factory → Port → Warehouse
```

This structure can be represented as a **directed graph**, where goods flow from upstream suppliers to downstream distribution centers.

---

# Example Disruption Scenario

Example analysis workflow:

1. Load supply chain dataset
2. Construct the supply chain graph
3. Compute baseline network metrics
4. Remove a critical node (e.g., port)
5. Recalculate network connectivity
6. Measure disruption impact

The analysis reveals:

* how much of the supply chain becomes disconnected
* which routes become overloaded
* how delivery times increase

---

# Installation

Clone the repository:

```
git clone https://github.com/yourusername/supply-chain-risk-analyzer.git
cd supply-chain-risk-analyzer
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Quick Start

Run the graph construction module:

```
python core/graph_builder.py
```

This will:

1. Load node and edge datasets
2. Construct the supply chain network graph
3. Display basic graph information

---

# Technologies Used

* Python
* Pandas
* NetworkX
* Plotly
* Streamlit
* OSMnx

---

# Development Roadmap

Phase 1 – Graph construction and dataset integration
Phase 2 – Network metrics and critical node detection
Phase 3 – Disruption simulation engine
Phase 4 – Visualization dashboard
Phase 5 – Full analytical workflow integration

---

# Future Improvements

* Cascading supply chain failure simulations
* Multi-layer supply chain networks
* Machine learning based risk prediction
* Integration with real logistics datasets
* Cloud deployment for large network simulations

---

# Applications

* Supply chain risk analysis
* Logistics network optimization
* Infrastructure resilience modeling
* Academic research in network science

---

# Documentation

Detailed technical documentation for the project is located in the `docs/` directory.

These documents describe the system architecture, mathematical modeling, datasets, simulations, and development roadmap.

| Document | Description |
|--------|-------------|
| [architecture.md](docs/architecture.md) | High-level system architecture and module interactions |
| [system_design.md](docs/system_design.md) | Detailed technical design of system components |
| [mathematical_model.md](docs/mathematical_model.md) | Mathematical framework behind network analysis and disruption modeling |
| [dataset_strategy.md](docs/dataset_strategy.md) | Data sources, dataset formats, and network construction methods |
| [simulation_engine.md](docs/simulation_engine.md) | Design and logic of disruption simulations |
| [experiment_guide.md](docs/experiment_guide.md) | Step-by-step instructions for running experiments |
| [validation_methodology.md](docs/validation_methodology.md) | Methods used to validate simulation results |
| [limitations.md](docs/limitations.md) | Known limitations and modeling assumptions |
| [development_roadmap.md](docs/development_roadmap.md) | Planned development stages for the project |
| [assumptions.md](docs/assumptions.md) | Modeling assumptions used throughout the system |

# Contributing

Contributions are welcome.

Please feel free to open issues or submit pull requests to improve the project.

---

# License

This project is released under the **MIT License**.
