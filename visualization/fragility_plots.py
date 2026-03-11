import plotly.express as px
import pandas as pd
import numpy as np


class FragilityVisualizer:
    def __init__(self, result_df, label_column, entity_name="Entity"):
        """
        result_df: DataFrame from node or edge bottleneck detector
        label_column: column to use on x-axis
            - "node_name" for node bottlenecks
            - "edge_id" for edge bottlenecks
        entity_name: display label for chart axis/title
        """
        self.df = result_df.copy()
        self.label_column = label_column
        self.entity_name = entity_name

        if self.label_column not in self.df.columns:
            raise ValueError(f"Label column '{self.label_column}' not found in DataFrame.")

    def _color_map(self):
        return {
            "Catastrophic": "#ef4444",
            "Severe Delay": "#f97316",
            "Moderate Delay": "#eab308",
            "Low Impact": "#22c55e",
            "Unknown": "#6b7280",
        }

    def plot_impact_score(self, title=None):
        """
        Create a bar chart ranking entities by impact score.
        """
        plot_df = self.df.sort_values("impact_score", ascending=False).copy()

        fig = px.bar(
            plot_df,
            x=self.label_column,
            y="impact_score",
            color="impact_category",
            color_discrete_map=self._color_map(),
            title=title or f"{self.entity_name} Vulnerability (Impact Score)",
            labels={
                self.label_column: self.entity_name,
                "impact_score": "Impact Score",
                "impact_category": "Risk Level",
            },
            text_auto=".2f",
            hover_data={
                "status": True,
                "baseline_time": True,
                "new_time": True,
                "lead_time_increase": True,
                "impact_score": ":.2f",
            },
        )

        fig.update_layout(
            xaxis={"categoryorder": "total descending"},
            template="plotly_white",
        )

        return fig

    def plot_lead_time_increase(self, title=None, include_zero_delay=True):
        """
        Create a bar chart showing additional lead time caused by disruption.
        Disconnected rows are excluded because delay is not finite.
        """
        plot_df = self.df[self.df["status"] == "Rerouted"].copy()

        if not include_zero_delay:
            plot_df = plot_df[plot_df["lead_time_increase"] > 0]

        plot_df = plot_df.sort_values("lead_time_increase", ascending=False)

        if plot_df.empty:
            raise ValueError("No rerouted rows available for lead time plotting.")

        fig = px.bar(
            plot_df,
            x=self.label_column,
            y="lead_time_increase",
            color="impact_category",
            color_discrete_map=self._color_map(),
            title=title or f"{self.entity_name} Delay Impact",
            labels={
                self.label_column: self.entity_name,
                "lead_time_increase": "Additional Lead Time (Days)",
            },
            text_auto=".2f",
            hover_data={
                "status": True,
                "baseline_time": True,
                "new_time": True,
                "impact_score": ":.2f",
            },
        )

        fig.update_layout(
            xaxis={"categoryorder": "total descending"},
            template="plotly_white",
        )

        return fig


if __name__ == "__main__":
    data = {
        "node_id": [2, 4, 1],
        "node_name": ["Rotterdam Port", "Factory B", "Shanghai Port"],
        "node_type": ["Port", "Factory", "Port"],
        "status": ["Disconnected", "Rerouted", "Rerouted"],
        "baseline_time": [11, 11, 11],
        "new_time": [np.nan, 41.0, 11.0],
        "lead_time_increase": [np.nan, 30.0, 0.0],
        "impact_score": [10.0000, 2.7273, 0.0000],
        "impact_category": ["Catastrophic", "Severe Delay", "Low Impact"],
    }

    mock_df = pd.DataFrame(data)

    visualizer = FragilityVisualizer(
        mock_df,
        label_column="node_name",
        entity_name="Supply Chain Node"
    )

    fig1 = visualizer.plot_impact_score()
    fig1.show()

    fig2 = visualizer.plot_lead_time_increase(include_zero_delay=True)
    fig2.show()