# Validation Methodology
## Supply Chain Fragility & Risk Analyzer

This document describes the validation methodology used to ensure that the Supply Chain Fragility & Risk Analyzer produces reliable and interpretable analytical results.

Validation ensures that simulation outputs, network metrics, and disruption impact estimates accurately reflect expected topological and business behaviors in supply chain networks.

---

# 1. Purpose of Validation

The purpose of validation is to confirm that the system correctly models supply chain network behavior and produces meaningful disruption analysis.

Validation focuses on verifying:

- Correctness of graph construction from raw datasets
- Accuracy of network metric calculations
- Consistency of disruption simulation results
- Plausibility of routing and connectivity changes
- Reliability of business impact estimations

These checks help ensure that analytical outputs can be trusted for experimentation, decision-making, and supply chain risk analysis.

---

# 2. Validation Strategy

The system is validated using several complementary methods that test different components of the architecture.

Validation methods include:

- Graph Structure Validation
- Metric Verification
- Simulation Consistency Testing
- Scenario Validation
- Sensitivity Analysis

Each method evaluates a specific layer of the analytical pipeline.

---

# 3. Graph Construction Validation

The first validation step verifies that the supply chain network graph is correctly constructed from the dataset using the Graph Modeling Engine.

Validation checks include:

- Node count consistency
- Edge connectivity validation
- Absence of invalid node references
- Correct edge directionality (ensuring logistics flows remain directed)

### Core Validation Check


Total Nodes in Dataset == G.number_of_nodes()
Total Edges in Dataset == G.number_of_edges()


Incorrect mappings or missing nodes at this stage will affect all downstream simulations and metric calculations.

---

# 4. Network Metric Validation

The system computes several graph metrics commonly used in network science. These metrics are validated by comparing results against known theoretical expectations.

| Metric | Validation Principle |
|------|----------------------|
| Degree Centrality | Highly connected logistics hubs should exhibit the highest degree values |
| Betweenness Centrality | Critical transit nodes (such as major ports) should show high betweenness scores |
| Shortest Path Length | Routing must minimize defined edge weights using Dijkstra's Algorithm |
| Connected Components | Isolated supply chain clusters must appear as separate network components |

These checks ensure the network analysis engine is functioning correctly.

---

# 5. Simulation Consistency Testing

Simulation consistency testing verifies that disruption experiments produce logically consistent outcomes based on network structure.

### Expected System Behaviors

- Removal of nodes reduces the Largest Connected Component (LCC)
- Removal of central nodes increases average routing distances
- Network fragmentation increases fragility scores
- Traffic rerouting causes congestion shifts toward alternative routes

### Example Test Execution

1. Remove the node with the highest Betweenness Centrality
2. Assert that network fragmentation increases
3. Assert that Average Path Length (APL) increases
4. Assert that the Fragility Score increases

If these expected behaviors are not observed, the simulation engine requires further debugging.

---

# 6. Scenario Validation

The system is also validated using real-world inspired disruption scenarios.

## Case A — Port Shutdown

Simulates the closure of a major logistics hub.

Expected results:

- Routing detours increase average path length
- Alternative ports experience increased betweenness centrality
- Delivery delays increase

## Case B — Regional Infrastructure Failure

Simulates the disruption of multiple nodes within a region.

Expected results:

- Network fragmentation increases
- Multiple congestion hotspots appear
- The Largest Connected Component decreases significantly

Scenario validation helps confirm that the system behaves realistically under stress conditions.

---

# 7. Sensitivity Analysis

Sensitivity analysis measures how strongly simulation results change when model parameters are modified.

### Parameters Tested

- Number of disrupted nodes
- Network size and density
- Routing distance weights
- Transportation speed assumptions

### Example Sensitivity Experiment

Increase disrupted nodes from **1 → 5** and observe whether:

- Network fragility increases
- Average path length increases
- Congestion shifts become more severe

A stable analytical system should produce consistent patterns of increasing disruption impact.

---

# 8. Monte Carlo Validation

Repeated randomized simulations help evaluate the stability of the analytical model under uncertain conditions.

Example configuration:


iterations = 1000


### Procedure

1. Randomly select disruption nodes
2. Run the disruption simulation
3. Compute network metrics
4. Record fragility scores
5. Repeat across iterations

Statistical analysis of these runs helps identify:

- consistently critical infrastructure nodes
- high-risk regions in the network
- systemic vulnerabilities

---

# 9. Business Impact Validation

The system translates structural network disruptions into operational metrics such as delivery delays and financial cost impacts.

Validation ensures these translations remain logically consistent.

### Validation Rules

- Routing distance increases must correspond to increased delivery delays
- Larger infrastructure disruptions must produce higher financial cost estimates
- Output metrics should scale logically with disruption severity

### Example Validation Logic


Average Path Length increases by 20%
→ Delivery delay increases
→ Estimated cost impact increases


This ensures that business-level outputs remain interpretable and consistent with network disruptions.

---

# 10. Limitations of Validation

Validation in this system focuses on structural and simulation correctness rather than real-world predictive forecasting.

Known limitations include:

- Simplified supply chain network representations
- Limited access to proprietary real-world logistics datasets
- Estimated cost and delay parameters

Despite these limitations, the validation methodology ensures that the analytical framework behaves consistently with established network science principles.

---

# 11. Summary

The validation framework ensures that the Supply Chain Fragility & Risk Analyzer produces reliable and interpretable simulation results.

The methodology combines:

- graph integrity checks
- network metric verification
- disruption scenario testing
- sensitivity analysis
- repeated Monte Carlo simulations

Together, these techniques provide strong confidence that the system correctly models disruption dynamics within supply chain networks.