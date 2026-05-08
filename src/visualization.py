"""
Visualization module for Anomalyy.
Renders the per-ticker price-with-anomalies chart that main.py writes to disk.
"""

import os
import logging
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Visualization:
    """Renders the anomaly-overlay price chart emitted per ticker."""

    def __init__(self, output_dir: str = "visualizations"):
        """Initialize visualizer with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_price_with_anomalies(self, features_df: pd.DataFrame,
                                  anomalies_df: pd.DataFrame,
                                  symbol: str = "Stock",
                                  save_path: Optional[str] = None) -> go.Figure:
        """
        Create interactive price chart with anomalies highlighted.

        Args:
            features_df: DataFrame with price data and features
            anomalies_df: DataFrame with anomaly detection results
            symbol: Stock symbol for title
            save_path: Optional path to save the figure

        Returns:
            Plotly figure object
        """
        if features_df.empty:
            logger.warning("Empty features dataframe provided")
            return go.Figure()

        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.05,
            subplot_titles=(f"{symbol} Price with Anomalies", "Volume"),
            shared_xaxes=True
        )

        # Price trace: candlestick if OHLC present, else line.
        if all(col in features_df.columns for col in ['open', 'high', 'low', 'close']):
            fig.add_trace(
                go.Candlestick(
                    x=features_df['date'],
                    open=features_df['open'],
                    high=features_df['high'],
                    low=features_df['low'],
                    close=features_df['close'],
                    name="Price",
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ),
                row=1, col=1
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=features_df['date'],
                    y=features_df['close'] if 'close' in features_df.columns else features_df.iloc[:, 0],
                    mode='lines',
                    name='Price',
                    line=dict(color='#1f77b4', width=2)
                ),
                row=1, col=1
            )

        # Anomaly markers (agreement >= 2 only).
        if not anomalies_df.empty and 'agreement_score' in anomalies_df.columns:
            high_conf_anomalies = anomalies_df[anomalies_df['agreement_score'] >= 2]
            if not high_conf_anomalies.empty:
                fig.add_trace(
                    go.Scatter(
                        x=high_conf_anomalies['date'],
                        y=high_conf_anomalies['close'] if 'close' in high_conf_anomalies.columns else high_conf_anomalies.iloc[:, 0],
                        mode='markers',
                        name='High-Confidence Anomalies',
                        marker=dict(
                            color='red',
                            size=10,
                            symbol='diamond',
                            line=dict(color='white', width=1)
                        ),
                        hovertemplate='<b>Anomaly Detected</b><br>' +
                                     'Date: %{x}<br>' +
                                     'Price: %{y:.2f}<br>' +
                                     'Agreement Score: %{text}<extra></extra>',
                        text=high_conf_anomalies['agreement_score']
                    ),
                    row=1, col=1
                )

        # Volume trace, colored by up/down close vs open.
        if 'volume' in features_df.columns:
            colors = ['#26a69a' if close >= open else '#ef5350'
                     for close, open in zip(features_df['close'], features_df['open'])]
            fig.add_trace(
                go.Bar(
                    x=features_df['date'],
                    y=features_df['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )

        fig.update_layout(
            title=f"{symbol} - Price Chart with Anomaly Detection",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            yaxis2_title="Volume",
            hovermode='x unified',
            template='plotly_dark',
            height=800,
            showlegend=True
        )
        fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
        fig.update_xaxes(rangeslider_visible=False, row=2, col=1)

        if save_path:
            fig.write_html(save_path)
            logger.info(f"Price chart saved to: {save_path}")

        return fig


if __name__ == "__main__":
    # Standalone smoke test. Real coverage lives in tests/test_pipeline.py.
    import yfinance as yf
    from feature_engineering import FeatureEngineer
    from anomaly_detection import AnomalyDetector

    print("Testing visualization...")
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo", interval="1d").reset_index()
    df = df.rename(columns={'Date': 'date'})

    engineer = FeatureEngineer()
    features_df = engineer.engineer_features(df)
    detector = AnomalyDetector(contamination=0.05)
    result_df = detector.detect_anomalies(features_df)

    visualizer = Visualization("test_visualizations")
    visualizer.plot_price_with_anomalies(
        features_df, result_df, "AAPL",
        save_path="test_visualizations/test_price_chart.html"
    )
    print("Visualization smoke test completed.")
