# Demo Video Script — Anomalyy

**Total runtime target:** 8–10 minutes (script comes in at ~9 minutes at a natural conversational pace, ~130 words per minute).

**Recording tips:**
- Each slide has a target time in brackets. If you hit the time roughly, you'll land in the 8–10 min window.
- The script is meant to be read **conversationally**, not memorized word-for-word. Read it through twice, then record and let your own phrasing replace stiff bits.
- If you stumble, just keep going — it's easier to do one continuous take and re-record only the worst slide than to splice many short clips.
- Open `presentation.pptx` in PowerPoint and use **Slide Show > Record Slide Show** to capture audio + slides in one pass.

---

## Slide 1 — Title  [≈ 20 sec]

Hi, I'm Purabh Singh. This is my CS 210 final project, **Anomalyy** — a data pipeline that detects anomalous trading days in historical stock data using three unsupervised machine learning methods, and then explains them using FOMC events, news sentiment, and cross-stock contagion.

---

## Slide 2 — The Problem  [≈ 45 sec]

Stock markets generate massive amounts of data every day, and a small number of anomalous trading days are responsible for an outsized share of investor risk and return. Detecting these days is half the problem. The other half is *explaining* them — a list of dates without context isn't actionable.

So my research question, taken straight from the proposal I submitted in February, is this: *can anomalous trading days be reliably identified using statistical and machine learning techniques, and can immediate news events, macroeconomic disclosures, and cross-stock contagion systematically explain those anomalies?*

---

## Slide 3 — Pipeline Architecture  [≈ 50 sec]

The pipeline runs in six stages.

First, ingestion: daily price data from yfinance and news sentiment from GDELT 2.0 via Google BigQuery.

Second, cleaning: schema validation, timezone stripping, V2Tone normalization, and dropping the rolling-window warm-up rows.

Third, feature engineering, which produces 40-plus technical indicators per ticker.

Fourth, three unsupervised detectors run in parallel — Z-Score, Isolation Forest, and Local Outlier Factor — and their flags are combined through agreement scoring.

Fifth, every high-confidence anomaly is classified into one of four labels.

And sixth, the results land in a SQLite database and a per-ticker price chart is generated.

---

## Slide 4 — Data Sources  [≈ 45 sec]

The project uses two data feeds plus one hardcoded list.

Yahoo Finance via the yfinance package gives me daily OHLCV data for five tickers — Apple, Microsoft, Tesla, Amazon, and the S&P 500 — over ten years, totaling 12,570 daily rows.

News sentiment comes from GDELT's Global Knowledge Graph version 2.0, queried over Google BigQuery. The query you see here aggregates tone scores per day. I picked GDELT over NewsAPI because NewsAPI's free tier only gives you the last 30 days of headlines, which doesn't work for a 10-year analysis. GDELT BigQuery gives full history and a generous 1 TB monthly free tier.

The 78 FOMC meeting dates are hardcoded in the repo.

---

## Slide 5 — Database Schema  [≈ 45 sec]

All pipeline state lives in a normalized SQLite database with four tables.

The `stocks` table stores company metadata once per ticker. The `price_data` table stores daily OHLCV rows, with a UNIQUE constraint on symbol-plus-date so re-runs don't double-count. The `news_articles` table stores daily GDELT aggregates with V2Tone sentiment, plus an `article_count` column carrying the real underlying volume. And the `anomalies` table stores one row per detected anomaly with the three method flags, an agreement score, a confidence value, and the assigned label.

Foreign keys on `symbol` enforce referential integrity, and indexes on the date columns speed up the queries that dominate downstream analysis.

---

## Slide 6 — Feature Engineering  [≈ 30 sec]

From the raw OHLCV data, the feature engineer computes more than 40 derived features per ticker, organized into eight groups: returns and ratios, moving averages, Bollinger Bands, volatility measures, momentum oscillators like RSI and MACD, volume-based features, statistical features, and binary candle-pattern flags. All features are computed within each ticker independently to prevent leakage.

---

## Slide 7 — Three Detection Methods  [≈ 60 sec]

The detection layer applies three unsupervised methods that are deliberately complementary, because each catches a different kind of unusual.

Z-Score thresholding is the simplest. It flags any day where any single feature exceeds three standard deviations from its mean. It's univariate, interpretable, and catches single-feature spikes.

Isolation Forest is an ensemble of random trees. It isolates rare points by random feature splits — multivariate, well-suited to high-dimensional data, and insensitive to feature scaling.

Local Outlier Factor is density-based. It flags points with substantially lower local density than their neighbors, which catches anomalies that are unusual *relative to a local cluster* rather than globally.

The output of `detect_anomalies` is the input feature frame plus three boolean columns and an `agreement_score`.

---

## Slide 8 — Agreement Scoring + Classification  [≈ 50 sec]

The agreement score is just the count of methods that flagged a given day, between zero and three. I keep the threshold conservative at greater-than-or-equal-to two — at least two of the three methods have to agree. Across the dataset, this caught 1,573 days, about 12% of all trading days, which aligns with the 10% contamination parameter passed to Isolation Forest and LOF.

Then every high-confidence anomaly gets one of four labels with strict precedence: `macroeconomic_event` if it's within two days of an FOMC meeting; `sector_contagion` if three or more tickers are simultaneously anomalous; `vader_sentiment_spike` if news volume and tone z-score both clear thresholds; otherwise `unexplained`.

The sentiment rule uses a per-ticker z-score rather than an absolute threshold, because daily V2Tone averages cluster tightly near zero and an absolute cutoff would essentially never fire.

---

## Slide 9 — Pivots From Proposal  [≈ 45 sec]

Three things changed between the February proposal and the final implementation.

The news source went through three iterations. NewsAPI hit a 30-day cap. GDELT's DOC API throttled aggressively. The final solution was GDELT BigQuery, with results cached in SQLite so re-runs don't hit the API and graders don't need credentials.

Sentiment scoring switched from VADER on headlines to GDELT's V2Tone on full article bodies. VADER is kept as a fallback path so the schema and downstream classifier are unchanged regardless of source.

And classification moved from manual labeling to automatic precedence rules — manual was no longer practical at 1,573 anomalies.

---

## Slide 10 — Results  [≈ 60 sec]

Here are the results. The full pipeline detected 1,573 high-confidence anomalies across the five tickers and the 10-year window.

Looking at the breakdown, sector contagion is the dominant label across every ticker, accounting for about 54% of all anomalies. That makes sense — large-cap U.S. equities are heavily correlated, so a real anomaly day is almost always a market-wide anomaly day.

Macroeconomic events explain another 18% of anomalies. Sentiment spikes explain less than 1%, which is partly because the threshold is strict, and partly because daily V2Tone averages are too smooth to register most company-specific sentiment events.

The headline metric is **precision-by-explanation**, defined as the fraction of anomalies that received a non-`unexplained` label. For this run, it's **72.1%** — roughly seven out of every ten detected anomalies coincide with a known cause.

---

## Slide 11 — Validation  [≈ 30 sec]

To check the FOMC overlap rate isn't just chance, I ran a quick null-hypothesis baseline. Each ticker has 2,514 trading days. About 234 fall in any FOMC ±2-day window, which is 9.3% by random chance. The observed overlap is 18.1% — roughly 2× the baseline, which supports the conclusion that the detector is preferentially picking up real macroeconomic event days. The full pytest suite — eight tests covering features, detection, schema, and classification — passes end-to-end.

---

## Slide 12 — Limitations & Future Work  [≈ 40 sec]

A few limitations worth calling out. The pipeline doesn't track an earnings calendar, which is the single most likely source of the 28% unexplained anomalies. V2Tone is corpus-aggregated rather than per-article, which smooths out individual outlier articles. The contamination hyperparameter is fixed at 10% with no formal tuning. And five tickers is a small, tech-tilted universe.

The biggest-impact follow-on item is adding an earnings calendar — that alone would likely re-explain most of the unexplained bucket. After that: per-article V2Tone instead of daily aggregates, walk-forward sentiment baselines, a sector-diverse 50-plus ticker universe, and GARCH-family volatility models as a fourth detector.

---

## Slide 13 — Conclusion  [≈ 20 sec]

To wrap up: the project answers the research question on both halves. Detection works — the three-method consensus identifies the right share of days. And explanation works — about 72% of those days map to a specific known cause. The combined detection-plus-classification pipeline is more useful than either component alone, because a labeled date like *"Mar 16, 2020: sector_contagion"* is directly actionable, whereas *"Mar 16, 2020: anomaly"* is not. Thanks for watching.

---

## Word & Time Reference

| Slide | Topic | Words | Target sec |
|---:|---|---:|---:|
| 1 | Title | 45 | 20 |
| 2 | Problem | 95 | 45 |
| 3 | Pipeline | 105 | 50 |
| 4 | Data sources | 105 | 45 |
| 5 | Schema | 110 | 45 |
| 6 | Feature engineering | 70 | 30 |
| 7 | Three detectors | 145 | 60 |
| 8 | Agreement + classification | 130 | 50 |
| 9 | Pivots | 100 | 45 |
| 10 | Results | 135 | 60 |
| 11 | Validation | 75 | 30 |
| 12 | Limitations | 100 | 40 |
| 13 | Conclusion | 60 | 20 |
| **Total** | | **~1,275** | **~540 (9 min)** |
