import plotly.express as px


class ScenarioVisualizer:
    def __init__(self, summary_df, label_column, entity_name="Entity"):
        self.df = summary_df.copy()
        self.label_column = label_column
        self.entity_name = entity_name

        if self.label_column not in self.df.columns:
            raise ValueError(f"Label column '{self.label_column}' not found in DataFrame.")

    def plot_catastrophic_count(self, title=None):
        plot_df = self.df.sort_values("catastrophic_count", ascending=False).copy()

        fig = px.bar(
            plot_df,
            x=self.label_column,
            y="catastrophic_count",
            title=title or f"{self.entity_name} Catastrophic Failure Count",
            labels={
                self.label_column: self.entity_name,
                "catastrophic_count": "Catastrophic Count",
            },
            text_auto=True,
        )

        fig.update_layout(
            xaxis={"categoryorder": "total descending"},
            template="plotly_white",
        )
        return fig

    def plot_average_impact(self, title=None):
        plot_df = self.df.sort_values("avg_impact_score", ascending=False).copy()

        fig = px.bar(
            plot_df,
            x=self.label_column,
            y="avg_impact_score",
            title=title or f"{self.entity_name} Average Impact Score",
            labels={
                self.label_column: self.entity_name,
                "avg_impact_score": "Average Impact Score",
            },
            text_auto=".2f",
        )

        fig.update_layout(
            xaxis={"categoryorder": "total descending"},
            template="plotly_white",
        )
        return fig

if __name__ == "__main__":
    import pandas as pd

    # Mock summary data based on your real results
    node_summary_data = {
        "node_name": ["Rotterdam Port", "Factory B", "Shanghai Port"],
        "catastrophic_count": [2, 0, 0],
        "avg_impact_score": [10.0, 2.86, 0.0],
    }

    node_summary_df = pd.DataFrame(node_summary_data)

    from visualization.scenario_plots import ScenarioVisualizer

    visualizer = ScenarioVisualizer(
        node_summary_df,
        label_column="node_name",
        entity_name="Supply Chain Node"
    )

    fig1 = visualizer.plot_catastrophic_count()
    fig1.show()

    fig2 = visualizer.plot_average_impact()
    fig2.show()