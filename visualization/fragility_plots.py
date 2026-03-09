import plotly.express as px
import pandas as pd
import numpy as np


class FragilityVisualizer:
    def __init__(self, bottleneck_df):
        """
        Initialize the visualizer with the DataFrame output
        from BottleneckDetector.
        """
        self.df = bottleneck_df.copy()

    def plot_impact_score(self):
        """
        Create a bar chart ranking nodes by impact score.
        Bars are colored by impact category.
        """
        color_map = {
            "Catastrophic": "#ef4444",
            "Severe Delay": "#f97316",
            "Moderate Delay": "#eab308",
            "Low Impact": "#22c55e",
            "Unknown": "#6b7280",
        }

        plot_df = self.df.sort_values("impact_score", ascending=False).copy()

        fig = px.bar(
            plot_df,
            x="node_name",
            y="impact_score",
            color="impact_category",
            color_discrete_map=color_map,
            title="Supply Chain Node Vulnerability (Impact Score)",
            labels={
                "node_name": "Supply Chain Node",
                "impact_score": "Impact Score",
                "impact_category": "Risk Level",
            },
            text_auto=".2f",
            hover_data={
                "node_type": True,
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

    def plot_lead_time_increase(self, include_zero_delay=True):
        """
        Create a bar chart showing additional lead time caused by node failure.
        Disconnected nodes are excluded because their delay is not finite.
        """
        rerouted_df = self.df[self.df["status"] == "Rerouted"].copy()

        if not include_zero_delay:
            rerouted_df = rerouted_df[rerouted_df["lead_time_increase"] > 0]

        rerouted_df = rerouted_df.sort_values("lead_time_increase", ascending=False)

        if rerouted_df.empty:
            raise ValueError("No rerouted nodes available for lead time increase plotting.")

        fig = px.bar(
            rerouted_df,
            x="node_name",
            y="lead_time_increase",
            color="impact_category",
            color_discrete_map={
                "Catastrophic": "#ef4444",
                "Severe Delay": "#f97316",
                "Moderate Delay": "#eab308",
                "Low Impact": "#22c55e",
                "Unknown": "#6b7280",
            },
            title="Delay Impact: Additional Lead Time per Node Failure",
            labels={
                "node_name": "Rerouted Node",
                "lead_time_increase": "Additional Lead Time (Days)",
            },
            text_auto=".2f",
            hover_data={
                "node_type": True,
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

    visualizer = FragilityVisualizer(mock_df)

    fig1 = visualizer.plot_impact_score()
    fig1.show()

    fig2 = visualizer.plot_lead_time_increase(include_zero_delay=True)
    fig2.show()