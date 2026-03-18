# Validation Methodology

## Supply Chain Fragility & Risk Analyzer

This document describes how the Supply Chain Fragility & Risk Analyzer is validated to ensure correctness, consistency, and reliability of simulation outputs.

The system follows a **deterministic, test-driven validation approach**, combining automated testing and manual verification of simulation behavior.

---

# 1. Purpose of Validation

Validation ensures that:

* graph construction is correct
* routing logic behaves as expected
* disruption simulations produce consistent outcomes
* cascade dynamics are realistic
* business impact metrics are logically derived

The goal is **engineering reliability**, not predictive forecasting.

---

# 2. Validation Strategy Overview

The system uses three complementary validation layers:

### 1. Automated Unit Testing (Primary)

* deterministic pytest suite
* covers core simulation logic

### 2. Scenario-Based Validation

* fixed test cases with known outcomes
* validates rerouting and disruption behavior

### 3. UI-Level Validation

* manual verification via Streamlit dashboard
* ensures correct presentation of KPIs and outputs

---

# 3. Automated Test Suite (Pytest)

The project includes a **high-value test suite** covering core system components.

---

## 3.1 Graph Construction Validation

File:

```
tests/test_graph_builder.py
```

Validates:

* nodes and edges are correctly loaded
* graph structure matches dataset
* invalid inputs are handled

---

## 3.2 Baseline Routing Validation

File:

```
tests/test_baseline_analysis.py
```

Validates:

* shortest path correctness
* routing consistency
* deterministic baseline outputs

---

## 3.3 Cascade Simulation Validation

Files:

```
tests/test_cascade_simulator.py  
tests/test_cascade_analysis.py
```

Validates:

* rerouting when nodes fail
* correct fallback path selection
* cost and time recalculation
* unmet demand handling

---

### Example Assertion

```
baseline_path = ["A", "B", "D"]
final_path    = ["A", "C", "D"]

assert rerouted == True
assert cost_increase > 0
```

This ensures the cascade engine behaves deterministically.

---

# 4. Scenario-Based Validation

The system is tested using **controlled graph fixtures**.

---

## Example Scenario

* Graph:
  A → B → D
  A → C → D

* Disruption:
  Node B removed

---

### Expected Behavior

* baseline path: A → B → D
* rerouted path: A → C → D
* cost increases
* demand still delivered

---

This validates:

* rerouting logic
* fallback path discovery
* cost computation

---

# 5. Cascade Simulation Validation

The cascade engine is validated against expected system dynamics:

---

## Expected Behaviors

* disrupted routes trigger rerouting
* overloaded edges are removed
* failures propagate step-by-step
* system stabilizes within max_steps

---

## Step-Level Validation

The simulator produces:

* routed demand
* disrupted demand
* failed nodes/edges

Validation ensures:

* monotonic failure accumulation
* consistent demand accounting
* no negative or invalid values

---

# 6. Business Metric Validation

The system translates simulation outputs into KPIs.

---

## Validation Rules

* rerouting → increases cost
* longer paths → increase delay
* unmet demand → increases loss

---

## Example Logic

```
if final_cost > baseline_cost:
    reroute_cost > 0
```

```
if unmet_demand > 0:
    unmet_demand_loss > 0
```

---

# 7. UI-Level Validation (Streamlit)

Manual validation is performed through the dashboard.

---

## Verified Components

### KPI Cards

* service level
* unmet demand
* failed nodes/edges
* economic impact

---

### Flow Impact Table

* baseline vs final path
* cost/time increase
* rerouting flag
* demand delivery

---

### Step Metrics Table

* cascade progression
* demand tracking
* failure accumulation

---

## Validation Goal

Ensure:

* values match backend simulation
* no inconsistencies across views
* metrics update correctly per scenario

---

# 8. Deterministic Behavior Guarantee

The system is designed to be **fully deterministic**:

* no randomness in simulations
* same input → same output
* reproducible test cases

This ensures:

* reliable debugging
* consistent analysis results

---

# 9. Limitations of Validation

The validation approach focuses on **correctness of implementation**, not real-world prediction.

Limitations include:

* synthetic datasets
* simplified economic models
* no probabilistic behavior

---

# 10. Future Validation Extensions

Planned improvements:

* Monte Carlo simulations
* probabilistic disruption modeling
* sensitivity analysis
* real-world dataset benchmarking

---

# 11. Summary

The validation methodology combines:

* deterministic unit testing
* scenario-based verification
* UI validation

This ensures that the system:

* behaves consistently
* produces interpretable outputs
* correctly models disruption dynamics

The result is a **robust, test-driven simulation framework** for supply chain fragility analysis.
