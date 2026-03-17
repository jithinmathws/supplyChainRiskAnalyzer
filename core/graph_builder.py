import networkx as nx
import pandas as pd


class SupplyChainGraph:
    REQUIRED_NODE_COLUMNS = {"node_id", "name", "type", "location", "capacity"}
    REQUIRED_EDGE_COLUMNS = {"source", "target", "transport_mode", "distance", "transport_time"}

    OPTIONAL_NODE_COLUMNS = {"tier", "region", "criticality", "recovery_time"}
    OPTIONAL_EDGE_COLUMNS = {"capacity", "edge_id", "weight", "cost", "reliability", "recovery_time"}

    def __init__(self, nodes_filepath, edges_filepaths):
        self.nodes_filepath = nodes_filepath
        self.edges_filepaths = edges_filepaths if isinstance(edges_filepaths, list) else [edges_filepaths]

        self.graph = nx.MultiDiGraph()
        self.nodes_df = None
        self.edges_df = None

    def load_data(self):
        try:
            self.nodes_df = pd.read_csv(self.nodes_filepath)

            edge_dfs = [pd.read_csv(path) for path in self.edges_filepaths]
            self.edges_df = pd.concat(edge_dfs, ignore_index=True)

            self._validate_columns()
            self._normalize_types()
            self._validate_values()

            print(f"Loaded {len(self.nodes_df)} nodes")
            print(f"Loaded {len(self.edges_df)} edges (combined)")

        except Exception as e:
            raise RuntimeError(f"Error loading data: {e}") from e

    def _validate_columns(self):
        missing_node_cols = self.REQUIRED_NODE_COLUMNS - set(self.nodes_df.columns)
        missing_edge_cols = self.REQUIRED_EDGE_COLUMNS - set(self.edges_df.columns)

        if missing_node_cols:
            raise ValueError(f"Missing node columns: {sorted(missing_node_cols)}")
        if missing_edge_cols:
            raise ValueError(f"Missing edge columns: {sorted(missing_edge_cols)}")

    def _normalize_types(self):
        # Nodes
        self.nodes_df["node_id"] = self.nodes_df["node_id"].astype(str).str.strip()
        self.nodes_df["name"] = self.nodes_df["name"].astype(str).str.strip()
        self.nodes_df["type"] = self.nodes_df["type"].astype(str).str.strip()
        self.nodes_df["location"] = self.nodes_df["location"].astype(str).str.strip()
        self.nodes_df["capacity"] = pd.to_numeric(self.nodes_df["capacity"], errors="raise")

        # Optional node numeric columns
        for col in ["criticality", "recovery_time"]:
            if col in self.nodes_df.columns:
                self.nodes_df[col] = pd.to_numeric(self.nodes_df[col], errors="raise")

        # Edges
        self.edges_df["source"] = self.edges_df["source"].astype(str).str.strip()
        self.edges_df["target"] = self.edges_df["target"].astype(str).str.strip()
        self.edges_df["transport_mode"] = self.edges_df["transport_mode"].astype(str).str.strip()

        self.edges_df["distance"] = pd.to_numeric(self.edges_df["distance"], errors="raise")
        self.edges_df["transport_time"] = pd.to_numeric(self.edges_df["transport_time"], errors="raise")

        # Optional edge numeric columns
        for col in ["capacity", "weight", "cost", "reliability", "recovery_time"]:
            if col in self.edges_df.columns:
                self.edges_df[col] = pd.to_numeric(self.edges_df[col], errors="raise")

        # Auto-create edge_id if not provided
        if "edge_id" not in self.edges_df.columns:
            self.edges_df["edge_id"] = [f"E{i + 1}" for i in range(len(self.edges_df))]
        else:
            self.edges_df["edge_id"] = self.edges_df["edge_id"].astype(str).str.strip()

        # Auto-create weight from transport_time if not provided
        if "weight" not in self.edges_df.columns:
            self.edges_df["weight"] = self.edges_df["transport_time"]
        else:
            self.edges_df["weight"] = self.edges_df["weight"].fillna(self.edges_df["transport_time"])

    def _validate_values(self):
        # Duplicate node IDs
        if self.nodes_df["node_id"].duplicated().any():
            dupes = self.nodes_df.loc[self.nodes_df["node_id"].duplicated(), "node_id"].tolist()
            raise ValueError(f"Duplicate node_id values found: {sorted(set(dupes))}")

        # Duplicate edge IDs
        if self.edges_df["edge_id"].duplicated().any():
            dupes = self.edges_df.loc[self.edges_df["edge_id"].duplicated(), "edge_id"].tolist()
            raise ValueError(f"Duplicate edge_id values found: {sorted(set(dupes))}")

        # Invalid numeric values
        if (self.nodes_df["capacity"] < 0).any():
            raise ValueError("Node capacity cannot be negative.")

        if (self.edges_df["distance"] < 0).any():
            raise ValueError("Edge distance cannot be negative.")

        if (self.edges_df["transport_time"] < 0).any():
            raise ValueError("Edge transport_time cannot be negative.")

        if "capacity" in self.edges_df.columns and (self.edges_df["capacity"] < 0).any():
            raise ValueError("Edge capacity cannot be negative.")

        if "weight" in self.edges_df.columns and (self.edges_df["weight"] < 0).any():
            raise ValueError("Edge weight cannot be negative.")

        if self.nodes_df.empty:
            raise ValueError("nodes.csv is empty.")

        if self.edges_df.empty:
            raise ValueError("edges.csv is empty.")

    def build_graph(self):
        if self.nodes_df is None or self.edges_df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        self.graph.clear()
        node_ids = set(self.nodes_df["node_id"])

        # Add nodes
        for node in self.nodes_df.to_dict("records"):
            node_id = node.pop("node_id")
            self.graph.add_node(node_id, **node)

        # Add edges
        for edge in self.edges_df.to_dict("records"):
            source = edge.pop("source")
            target = edge.pop("target")

            if source not in node_ids or target not in node_ids:
                raise ValueError(f"Edge references undefined node: source={source}, target={target}")

            edge_key = edge.get("edge_id") or edge.get("transport_mode", "default")
            self.graph.add_edge(source, target, key=edge_key, **edge)

        return self.graph

    def summary(self):
        print("Graph Summary")
        print("-------------------")
        print(f"Nodes: {self.graph.number_of_nodes()}")
        print(f"Edges: {self.graph.number_of_edges()}")

    def print_edges(self):
        print("\nFinal Graph Edges")
        print("-------------------")
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            print(f"{u} -> {v} | key={key} | {data}")

    def get_graph(self):
        return self.graph


if __name__ == "__main__":
    builder = SupplyChainGraph(
        "data/nodes.csv",
        ["data/edges.csv", "data/alternate_edges.csv"],
    )
    builder.load_data()
    G = builder.build_graph()
    builder.summary()
    builder.print_edges()
