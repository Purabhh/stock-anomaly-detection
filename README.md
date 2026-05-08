# Anomalyy
### CS 210: Data Management for Data Science

A data pipeline that detects anomalous trading days in historical stock data using three complementary unsupervised machine learning methods, then classifies detected anomalies using FOMC meeting dates, GDELT news sentiment, and cross-stock contagion analysis.

---

## Installation

```bash
git clone https://github.com/Purabhh/Anomalyy.git
cd Anomalyy
pip install -r requirements.txt
```

### Google BigQuery setup (required for news ingestion)

News headlines and sentiment come from [GDELT 2.0 GKG](https://www.gdeltproject.org/) via Google BigQuery. To run the news leg of the pipeline you need a Google Cloud service account:

1. Create a Google Cloud project (free tier is sufficient — BigQuery gives 1 TB of query data per month for free, well above what this pipeline uses).
2. Enable the BigQuery API on that project.
3. Create a service account with the **BigQuery Job User** + **BigQuery Data Viewer** roles.
4. Download the JSON key file and save it as `bq_credentials.json` in the repo root (already gitignored).

Price data comes from `yfinance`, which needs no auth.

---

## Quick Start

```bash
python main.py
```

This runs the full pipeline: fetches 10 years of price data for AAPL, MSFT, TSLA, AMZN, and ^GSPC, fetches GDELT news sentiment over the same window, detects anomalies, classifies them, and writes a console summary report + per-ticker HTML charts to `visualizations/`.

Re-running is cheap: news rows already in the SQLite cache short-circuit BigQuery, and price data is overwritten in place.

---

## Project Structure

```
Anomalyy/
├── main.py                     # End-to-end pipeline runner
├── requirements.txt
├── README.md
├── bq_credentials.json         # Google Cloud service-account key (gitignored)
├── src/
│   ├── data_ingestion.py       # yfinance price data + GDELT BQ news fetching
│   ├── news_bq.py              # GDELT 2.0 GKG fetcher via Google BigQuery
│   ├── feature_engineering.py  # 40+ technical indicators
│   ├── anomaly_detection.py    # Z-Score, Isolation Forest, LOF + classifier
│   ├── database.py             # SQLite schema + CRUD
│   ├── visualization.py        # Plotly price-with-anomalies chart
│   ├── fomc_events.py          # FOMC meeting dates 2015-2024
│   └── contagion_analysis.py   # Cross-stock correlation + contagion detection
├── notebooks/
│   └── analysis.ipynb          # Exploratory analysis notebook
├── tests/
│   └── test_pipeline.py        # pytest test suite
└── visualizations/             # Generated charts (created on run)
```

---

## Methodology

### Data Sources
- **Historical prices**: `yfinance` — daily OHLCV for AAPL, MSFT, TSLA, AMZN, ^GSPC (Jan 2015 – Dec 2024)
- **News + sentiment**: GDELT 2.0 GKG via BigQuery (`gdelt-bq.gdeltv2.gkg_partitioned`) — daily aggregates of GDELT's V2Tone score (sentiment pre-computed on full article body, normalized from [-100, 100] to [-1, 1]) plus per-day article counts. Indexed since Feb 18, 2015.
- **FOMC dates**: hardcoded list of all 70+ Fed meeting dates from 2015–2024 in `src/fomc_events.py`

### Feature Engineering
From raw OHLCV data, `FeatureEngineer.engineer_features` computes:
- **Returns**: daily and log returns, rolling returns
- **Moving averages**: SMA + EMA for 5, 10, 20, 50, 200-day windows
- **Volatility**: ATR-14, rolling annualized volatility, drawdown
- **Bollinger Bands**: upper/lower, bandwidth, position
- **Momentum**: RSI-14/28, MACD, MACD histogram
- **Volume**: OBV, VWAP, volume ratio
- **Statistical**: skewness, kurtosis, return z-scores, Hurst exponent
- **Patterns**: gap up/down, doji, marubozu, engulfing patterns

### Anomaly Detection (three methods + agreement scoring)

| Method | Type | Key Parameter |
|--------|------|--------------|
| Z-Score Thresholding | Statistical (univariate) | threshold = 3.0 σ |
| Isolation Forest | Ensemble / tree-based | contamination = 10% |
| Local Outlier Factor | Density-based | n_neighbors = 20 |

Each method produces a per-day boolean flag. `agreement_score` is the count (0–3) of methods that flagged that day. **Anomalies confirmed by ≥ 2 methods** are treated as high-confidence and persisted to the database. The multi-method consensus reduces false positives that any single detector would miss in isolation.

### Anomaly Classification

Every high-confidence anomaly is assigned one label via `AnomalyDetector.classify_anomaly_type`, with the following precedence:

1. **`macroeconomic_event`** — anomaly date within ±2 days of an FOMC meeting
2. **`sector_contagion`** — date appears in the contagion list (≥ 3 stocks flagged within a 3-day window)
3. **`vader_sentiment_spike`** — within the ±1 day news window, article count ≥ 5 *and* the window's mean sentiment is ≥ 2 standard deviations from the ticker's full-history baseline
4. **`unexplained`** — none of the above

The sentiment-spike rule uses a per-ticker z-score against the historical mean rather than an absolute threshold because GDELT V2Tone daily averages cluster tightly near zero — an absolute cutoff (e.g. `|compound| > 0.3`) would essentially never fire.

### Evaluation

Because this is unsupervised, conventional precision/recall don't apply. Two proxy metrics are reported:

- **Precision-by-explanation**: percentage of high-confidence anomalies that received a non-`unexplained` label (i.e. matched a known market event).
- **Cross-method agreement rate**: percentage of anomalies flagged by ≥ 2 of the 3 methods.

---

## Database Schema

Four normalized SQLite tables:

```sql
stocks(
  symbol PK, name, sector, industry, country, market_cap,
  created_at, last_updated
)

price_data(
  id PK, symbol FK, date, open, high, low, close, adj_close, volume,
  created_at,
  UNIQUE(symbol, date)
)

news_articles(
  id PK, symbol FK, published_at, title, description, source, url UNIQUE,
  sentiment_compound, sentiment_positive, sentiment_neutral, sentiment_negative,
  article_count, created_at
)

anomalies(
  id PK, symbol FK, anomaly_date,
  z_score_flag, isolation_forest_flag, lof_flag,
  agreement_score, confidence, label,
  price_change_1d, price_change_5d, price_change_20d,
  avg_sentiment, news_count, created_at,
  UNIQUE(symbol, anomaly_date)
)
```

For GDELT BigQuery rows, each `news_articles` record is a synthetic *daily aggregate*: the URL is `gdelt://aggregate/{ticker}/{date}`, sentiment columns hold averaged V2Tone values, and `article_count` carries the real underlying article volume for that day.

---

## Tests

```bash
pytest tests/test_pipeline.py -v
```

Tests cover: feature engineering output, three-method flag presence, four-table DB schema, FOMC date count, classifier label values, FOMC labeling, GDELT BQ filter mapping, and contagion detection.

---

## Limitations

1. **GDELT coverage start date.** The GDELT 2.0 GKG index begins Feb 18, 2015. The first ~6 weeks of the analysis window (Jan 1 – Feb 17, 2015) have no news coverage; the `vader_sentiment_spike` classifier cannot fire there.
2. **GDELT entity matching.** Per-ticker filters use `V2Organizations LIKE '%COMPANY NAME%'` against GDELT's normalized entity strings (e.g. `'%APPLE INC%'`). Some legitimate articles may not reach the filter if GDELT extracted the entity under a slightly different surface form. ^GSPC has no entity equivalent and falls back to broad market themes (`ECON_STOCKMARKET`, `ECON_INTEREST_RATES`).
3. **V2Tone is corpus-aggregated.** The sentiment values are *averages* over all matching articles for a given day, not per-article scores, so individual outlier articles get smoothed out before they reach the classifier.
4. **yfinance data quality.** Adjusted close prices may differ from raw prices; split/dividend adjustments are applied automatically.
5. **Unsupervised evaluation.** No ground-truth anomaly labels exist, so precision-by-explanation is a proxy metric — a high score means most anomalies coincide with a plausible cause, not that the underlying detection is "correct" in an absolute sense.
6. **Contamination assumption.** Isolation Forest's `contamination=0.1` parameter strongly affects sensitivity; LOF inherits the same assumption.
7. **Survivorship bias.** Only currently-listed tickers are analyzed.

---

## Citations

Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. *ACM Computing Surveys, 41*(3), 1–58.

Sezer, O. B., Gudelek, M. U., & Ozbayoglu, A. M. (2020). Financial time series forecasting with deep learning: A systematic literature review. *Applied Soft Computing, 90*, 106181.

Nassirtoussi, A. K., Aghabozorgi, S., Wah, T. Y., & Ngo, D. C. L. (2014). Text mining for market prediction: A systematic review. *Expert Systems with Applications, 41*(16), 7653–7670.

GDELT Project. (2015). The GDELT Global Knowledge Graph (GKG) 2.0 codebook. *https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/*

Leetaru, K. (2015). Mining libraries: Lessons learned from 20 years of massive computing on the world's information. *D-Lib Magazine, 21*(9/10).
