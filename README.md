# Supply Chain Fragility & Risk Analyzer

A **graph-based digital twin for supply chain resilience** that models multi-tier logistics networks and simulates disruption scenarios to quantify **operational and financial impact in real time**.

The system acts as an interactive **What-If simulation engine**, enabling analysts to:

* identify fragile nodes and edges
* simulate cascading failures under capacity constraints
* evaluate alternative routing strategies
* measure disruption impact in **cost, time, and service level**

Built using **NetworkX, Pandas, and Streamlit**, this project demonstrates how **network science + simulation + business metrics** can be combined into a practical decision-support system.

---

## 🚀 Key Capabilities

### 🔹 Graph-Based Supply Chain Modeling

* Models supply chains as **directed multi-layer networks**
* Supports suppliers, hubs, factories, ports, warehouses, and distribution centers
* Handles multi-route logistics using **MultiDiGraph**

---

### 🔹 Bottleneck & Fragility Detection

* Identifies structurally critical **nodes and edges**
* Measures disruption severity using:

  * connectivity loss
  * rerouting feasibility
  * lead-time increase
  * impact scoring

---

### 🔹 Scenario-Based What-If Engine

* Test multiple origin–destination flows simultaneously
* Evaluate disruption effects across scenarios
* Aggregate results across flows for decision-making

---

### 🔹 Capacity-Aware Cascade Simulator

Simulates real-world cascading failures:

* applies initial shocks (node/edge failures)
* reroutes flows dynamically
* tracks load buildup across routes
* removes overloaded infrastructure
* repeats until stable

Captures detailed outputs:

* delivered vs disrupted flows
* rerouted paths
* demand fulfillment levels
* step-by-step failure propagation

---

### 🔹 Flow-Level Impact Tracking

Each flow is analyzed with:

* baseline vs final path
* cost change
* **time (delay) change**
* hop change
* delivered vs unmet demand

---

### 🔹 Business Impact Engine

Translates graph disruptions into operational KPIs:

#### Economic Model

* **Reroute Cost** = (cost increase) × demand × rate
* **Delay Penalty** = (time increase) × demand × rate
* **Unmet Demand Loss** = unmet demand × loss rate
* **Total Economic Impact** = sum of all above

---

### 🔹 Time-Based Delay Modeling (Key Differentiator)

Unlike simple graph models, delay is computed using:

* edge weights representing **travel time / lead time**
* independent of hop count

This enables:

* realistic logistics modeling
* accurate delay penalties
* meaningful operational insights

---

### 🔹 Interactive Streamlit Dashboard

Includes modular UI views:

* Executive summary KPIs
* Node fragility analysis
* Edge bottleneck analysis
* Scenario testing engine
* Cascade simulation
* Network visualization

---

## 🧠 System Workflow

```
CSV Dataset → Graph Builder → Fragility Analysis → Scenario Engine → Cascade Simulator → Business KPIs → Dashboard
```

---

## 📂 Project Structure

```
supply_chain_risk_analyzer/

    data/
        nodes.csv
        edges.csv
        alternate_edges.csv
        flows.csv

    core/
        graph_builder.py
        network_metrics.py
        network_visualizer.py

    analysis/
        bottleneck_detection.py
        edge_bottleneck_detection.py
        business_metrics_translator.py
        cascade_simulator.py
        scenario_analysis.py

    visualization/
        graph_plot.py
        fragility_plots.py
        scenario_plots.py

    app/
        ui/
            bottleneck_view.py
            cascade_view.py
            graph_view.py
            scenario_view.py
            sidebar.py
        services/
            analysis_service.py
            bottleneck_service.py
            cascade_service.py
            scenario_service.py
        utils/
            session_state.py
        streamlit_app.py

    tests/
        test_graph_builder.py
        test_graph_service.py
        test_cascade_simulator.py
        test_cascade_analysis.py
        test_baseline_analysis.py

    docs/
        architecture.md
        mathematical_model.md
        system_design.md
        simulation_engine.md
        experiment_guide.md
        assumptions.md
        limitations.md
        development_roadmap.md

    README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/supply-chain-risk-analyzer.git
cd supply-chain-risk-analyzer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

Start the Streamlit dashboard:

```bash
streamlit run app/streamlit_app.py or
python -m streamlit run app/streamlit_app.py
```

The dashboard allows you to:

* select flows
* test disruption scenarios
* simulate cascading failures
* evaluate economic impact

---

## 🧪 Testing

Run the full test suite:

```bash
pytest -q
```

Tests cover:

* graph construction validation
* baseline routing correctness
* cascade simulation behavior
* scenario analysis consistency

---

## 📊 Example Use Cases

* Stress-testing logistics networks
* Identifying single points of failure
* Scenario planning for disruption events
* Supply chain risk advisory analysis
* Academic research in network resilience

---

## 🛠️ Technologies Used

* Python
* NetworkX
* Pandas
* Streamlit
* Plotly
* Pytest

---

## 📘 Documentation

Detailed technical documentation is available in the `docs/` folder:

| Document               | Description                    |
| ---------------------- | ------------------------------ |
| architecture.md        | High-level system architecture |
| system_design.md       | Detailed component design      |
| mathematical_model.md  | Network modeling framework     |
| simulation_engine.md   | Cascade simulation logic       |
| experiment_guide.md    | Running experiments            |
| assumptions.md         | Modeling assumptions           |
| limitations.md         | Known constraints              |
| development_roadmap.md | Future direction               |

---

## 💡 Why This Project Matters

Modern supply chains are highly interconnected and fragile.

This project demonstrates how:

* **graph theory**
* **simulation systems**
* **business impact modeling**

can be combined into a practical **decision-support tool** for real-world logistics risk analysis.

---

## 🔮 Future Improvements

* stochastic disruption modeling
* probabilistic demand simulation
* multi-layer supply chain graphs
* ML-based risk prediction
* cloud-scale deployment

---

## 🤝 Contributing

Contributions are welcome.
Feel free to open issues or submit pull requests.

---

## 📄 License

This project is released under the **MIT License**.
