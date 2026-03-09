                <div id="price-chart"></div>
            </div>
            
            <div class="chart-container">
                <h2>Anomaly Detection Analysis</h2>
                <div id="anomaly-details"></div>
            </div>
            
            <div class="chart-container">
                <h2>Method Comparison</h2>
                <div id="method-comparison"></div>
            </div>
            
            <script>
                // Load the Plotly figures
                const priceChart = {fig1.to_json()};
                const anomalyDetails = {fig2.to_json()};
                const methodComparison = {fig3.to_json()};
                
                // Render the charts
                Plotly.newPlot('price-chart', priceChart.data, priceChart.layout);
                Plotly.newPlot('anomaly-details', anomalyDetails.data, anomalyDetails.layout);
                Plotly.newPlot('method-comparison', methodComparison.data, methodComparison.layout);
                
                // Add resize handler
                window.addEventListener('resize', function() {{
                    Plotly.Plots.resize('price-chart');
                    Plotly.Plots.resize('anomaly-details');
                    Plotly.Plots.resize('method-comparison');
                }});
            </script>
            
            <div style="margin-top: 40px; padding: 20px; background-color: #2d2d2d; border-radius: 10px;">
                <h3>About This Analysis</h3>
                <p>This anomaly detection system uses three complementary methods:</p>
                <ul>
                    <li><strong>Z-Score:</strong> Statistical method detecting extreme values in individual features</li>
                    <li><strong>Isolation Forest:</strong> Tree-based method isolating anomalies in feature space</li>
                    <li><strong>Local Outlier Factor (LOF):</strong> Density-based method comparing local density</li>
                </ul>
                <p>Anomalies are flagged when at least 2 out of 3 methods agree (high-confidence anomalies).</p>
                <p><em>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            </div>
        </body>
        </html>
        """
        
        # Save dashboard
        dashboard_path = os.path.join(self.output_dir, f"{symbol}_dashboard.html")
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_html)
        
        logger.info(f"Dashboard saved to: {dashboard_path}")
        return dashboard_path


if __name__ == "__main__":
    # Test visualization
    import yfinance as yf
    from feature_engineering import FeatureEngineer
    from anomaly_detection import AnomalyDetector
    
    print("Testing visualization...")
    
    # Fetch sample data
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo", interval="1d")
    df = df.reset_index()
    
    # Engineer features
    engineer = FeatureEngineer()
    features_df = engineer.engineer_features(df)
    
    # Detect anomalies
    detector = AnomalyDetector(contamination=0.05)
    result_df = detector.detect_anomalies(features_df)
    
    # Create visualizations
    visualizer = AnomalyVisualizer("test_visualizations")
    
    # Price chart with anomalies
    fig1 = visualizer.create_price_chart_with_anomalies(features_df, result_df, "AAPL")
    visualizer.save_visualization(fig1, "test_price_chart", 'html')
    
    # Anomaly details
    fig2 = visualizer.create_anomaly_details_chart(result_df, detector.feature_importance)
    visualizer.save_visualization(fig2, "test_anomaly_details", 'html')
    
    # Method comparison
    fig3 = visualizer.create_method_comparison_chart(result_df)
    visualizer.save_visualization(fig3, "test_method_comparison", 'html')
    
    print("Visualization test completed! Check the 'test_visualizations' directory.")