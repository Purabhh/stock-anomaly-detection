# Stock Market Anomaly Detection System (ADS)

A complete data science project for detecting anomalies in stock market data using free tools and local execution.

## 📊 Project Overview

This system detects anomalies in stock market data using three complementary methods:
1. **Z-Score** - Statistical outlier detection
2. **Isolation Forest** - Tree-based anomaly detection  
3. **Local Outlier Factor (LOF)** - Density-based anomaly detection

Anomalies are flagged when at least 2 out of 3 methods agree, providing high-confidence detection.

## 🛠️ Tech Stack (100% Free)

- **Data Collection**: yfinance (free Yahoo Finance API)
- **News Integration**: NewsAPI free tier
- **Database**: SQLite (local, no server needed)
- **Machine Learning**: scikit-learn
- **NLP/Sentiment**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **Visualization**: Plotly (interactive charts)
- **Storage**: Local filesystem

## 📁 Project Structure

```
ADS/
├── src/
│   ├── database.py           # SQLite database schema (4 tables)
│   ├── data_ingestion.py     # yfinance + NewsAPI pipeline
│   ├── feature_engineering.py # Technical indicators & features
│   ├── anomaly_detection.py  # 3-method detection with agreement scoring
│   └── visualization.py      # Plotly interactive charts
├── data/                     # SQLite database & raw data
├── notebooks/                # Jupyter notebooks for analysis
├── visualizations/           # Generated charts and dashboards
├── tests/                    # Unit tests
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ADS.git
cd ADS

# Install dependencies
pip install -r requirements.txt

# Download NLTK data for VADER
python -c "import nltk; nltk.download('vader_lexicon')"
```

### 2. Basic Usage
```bash
# Run the complete pipeline
python src/pipeline.py --symbol AAPL --period 1y

# Generate visualizations
python src/visualization.py --symbol AAPL --output charts/
```

### 3. Database Schema
The system uses 4 SQLite tables:
- `stocks` - Stock metadata
- `price_data` - Historical price data  
- `news_articles` - News with sentiment scores
- `anomalies` - Detected anomalies with agreement scores

## 📈 Features

### Data Pipeline
- Automated data ingestion from yfinance
- News collection with sentiment analysis (VADER)
- Feature engineering (50+ technical indicators)
- SQLite storage for reproducibility

### Anomaly Detection
- Three complementary detection methods
- Agreement scoring across methods
- Confidence levels for each detection
- Feature importance analysis

### Visualization
- Interactive Plotly charts
- Anomaly highlighting on price charts
- Method comparison visualizations
- HTML dashboard generation

## 📋 Requirements

See `requirements.txt` for complete list:
- pandas, numpy, scikit-learn
- yfinance, requests
- plotly, kaleido
- vaderSentiment, nltk
- sqlite3 (built-in)

## 🎯 Academic Use

This project is designed for data science courses with:
- **Full reproducibility** - All local tools, no cloud dependencies
- **Academic integrity** - No paid APIs or services
- **Clear documentation** - Commented code and explanations
- **Modular design** - Easy to extend and modify

## 📊 Example Output

1. **Price charts** with anomalies highlighted
2. **Agreement scores** across detection methods  
3. **Feature importance** for anomaly detection
4. **News sentiment** correlation with anomalies
5. **Performance metrics** for each method

## 🔧 Customization

### Add New Stocks
```python
from src.data_ingestion import DataIngestion
ingestor = DataIngestion()
ingestor.fetch_stock_data("TSLA", period="2y")
```

### Modify Detection Parameters
```python
from src.anomaly_detection import AnomalyDetector
detector = AnomalyDetector(contamination=0.05)  # Adjust expected outlier rate
```

### Add New Features
```python
from src.feature_engineering import FeatureEngineer
engineer = FeatureEngineer(window_sizes=[5, 10, 20, 50, 100, 200])
```

## 📚 Methodology

### 1. Data Collection
- Historical prices (open, high, low, close, volume)
- News headlines with sentiment scoring
- Corporate actions and events

### 2. Feature Engineering  
- Price transformations (returns, ratios)
- Technical indicators (SMA, EMA, Bollinger Bands, RSI, MACD)
- Statistical features (volatility, skewness, kurtosis)
- Volume indicators (OBV, VWAP)

### 3. Anomaly Detection
- **Z-Score**: Statistical outliers in individual features
- **Isolation Forest**: Tree-based isolation in feature space  
- **LOF**: Density-based local outlier detection
- **Agreement Scoring**: Consensus across methods

### 4. Validation
- Cross-referencing with news events
- Price action analysis around anomalies
- Method performance comparison

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for academic use. Please cite if used in research or publications.

## 🙏 Acknowledgments

- yfinance for free market data
- NewsAPI for news headlines
- scikit-learn for ML algorithms
- VADER for sentiment analysis
- Plotly for visualization

## 📧 Contact

For questions about this academic project, please open an issue on GitHub.

---
*Built for Data Science Course Project - 100% Free Tools*
