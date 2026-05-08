"""
GDELT 2.0 GKG news fetcher via Google BigQuery.

Why BigQuery instead of the DOC API:
- DOC API only serves the last 3 months; useless for our 10-year backfill
- DOC API has aggressive per-IP rate limiting that triggers tens-of-minutes
  cooldowns (no Retry-After header, no documented quota)
- BigQuery exposes the full GKG index from Feb 18 2015 onward, with a generous
  1 TB/month free tier; one compound query across all tickers fits easily

Sentiment source: GDELT's own V2Tone (range -100..+100), pre-computed on the
full article body. Normalized to [-1, 1] so it slots into the existing
`sentiment_compound` field that the classifier reads — no downstream changes
required beyond consuming an aggregated `article_count` column.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# GKG 2.0 index begins Feb 18, 2015. Earlier partitions return empty.
GKG_EARLIEST = datetime(2015, 2, 18)

# Per-ticker filter clauses against GKG's V2Organizations / V2Themes columns.
# V2Organizations is a semicolon-separated list of upper-cased entity names.
# ^GSPC (S&P 500) isn't an entity; fall back to broad market themes.
TICKER_TO_FILTER = {
    'AAPL': "UPPER(V2Organizations) LIKE '%APPLE INC%'",
    'MSFT': "UPPER(V2Organizations) LIKE '%MICROSOFT CORP%'",
    'TSLA': "UPPER(V2Organizations) LIKE '%TESLA INC%' OR UPPER(V2Organizations) LIKE '%TESLA MOTORS%'",
    'AMZN': "UPPER(V2Organizations) LIKE '%AMAZON.COM%' OR UPPER(V2Organizations) LIKE '%AMAZON COM%'",
    '^GSPC': "V2Themes LIKE '%ECON_STOCKMARKET%' OR V2Themes LIKE '%ECON_INTEREST_RATES%'",
}


def _get_client(credentials_path: Optional[str] = None):
    """Lazy-load the BigQuery client. Imported here so the rest of the
    pipeline runs even when google-cloud-bigquery isn't installed."""
    from google.cloud import bigquery
    if credentials_path and os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    return bigquery.Client()


def _build_query(ticker: str, start: str, end: str) -> str:
    """Build the daily-aggregated GKG query for one ticker.

    Returns one row per day with the average V2Tone (normalized to [-1, 1])
    and the article count. Aggregating in-query keeps the result set tiny;
    BQ cost is determined by bytes scanned (the column projection), not
    bytes returned.
    """
    where_clause = TICKER_TO_FILTER[ticker]
    return f"""
    SELECT
      DATE(_PARTITIONTIME) AS date,
      AVG(SAFE_CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64)) / 100.0 AS sentiment_compound,
      AVG(SAFE_CAST(SPLIT(V2Tone, ',')[OFFSET(1)] AS FLOAT64)) / 100.0 AS sentiment_positive,
      AVG(SAFE_CAST(SPLIT(V2Tone, ',')[OFFSET(2)] AS FLOAT64)) / 100.0 AS sentiment_negative,
      COUNT(*) AS article_count
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE _PARTITIONTIME BETWEEN TIMESTAMP("{start}") AND TIMESTAMP("{end}")
      AND ({where_clause})
    GROUP BY date
    HAVING article_count >= 1
    ORDER BY date
    """


def fetch_for_ticker(
    ticker: str,
    start: str,
    end: str,
    credentials_path: str = "bq_credentials.json",
) -> List[Dict]:
    """Fetch daily-aggregated GDELT news sentiment for one ticker.

    Returns a list of NewsAPI-shape dicts (one per day) so the existing
    `_process_and_store_news` adapter consumes them with no changes. Each
    "article" is a synthetic daily aggregate; `article_count` carries the
    real underlying volume.
    """
    if ticker not in TICKER_TO_FILTER:
        logger.warning(f"No GDELT BQ filter mapping for {ticker}; skipping")
        return []

    # Clamp start to GKG 2.0 origin (Feb 18, 2015).
    start_dt = max(datetime.strptime(start, '%Y-%m-%d'), GKG_EARLIEST)
    start_iso = start_dt.strftime('%Y-%m-%d')
    if start_iso != start:
        logger.info(f"GDELT BQ: clamped start {start} -> {start_iso} (GKG 2.0 origin)")

    if not Path(credentials_path).exists():
        logger.error(f"GDELT BQ: credentials file not found at {credentials_path}; "
                     "set up Google Cloud service account first")
        return []

    try:
        client = _get_client(credentials_path)
    except Exception as e:
        logger.error(f"GDELT BQ: client init failed: {e}")
        return []

    query = _build_query(ticker, start_iso, end)
    logger.info(f"GDELT BQ: querying {ticker} from {start_iso} to {end}")

    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        logger.error(f"GDELT BQ query failed for {ticker}: {e}")
        return []

    if df.empty:
        logger.warning(f"GDELT BQ: no articles found for {ticker}")
        return []

    bytes_str = "(cached)"
    logger.info(f"GDELT BQ: {ticker} returned {len(df)} day-rows {bytes_str}")

    # Reshape into NewsAPI-shape dicts so _process_and_store_news works
    # unchanged. One synthetic "article" per day carrying the daily aggregate.
    articles = []
    for _, row in df.iterrows():
        date_str = pd.Timestamp(row['date']).strftime('%Y-%m-%d')
        articles.append({
            'title': f'GDELT daily sentiment aggregate for {ticker} on {date_str}',
            'description': f"{int(row['article_count'])} articles aggregated",
            'source': {'name': 'gdelt-bq.gdeltv2.gkg'},
            'url': f'gdelt://aggregate/{ticker}/{date_str}',
            'publishedAt': f'{date_str}T12:00:00Z',
            # Pre-computed sentiment (V2Tone normalized to [-1, 1]).
            # _process_and_store_news will overwrite these with VADER if it
            # picks up only title+description, so we pass them through
            # explicitly via the article_count signal too.
            'gdelt_sentiment_compound': float(row['sentiment_compound']),
            'gdelt_sentiment_positive': float(row['sentiment_positive']),
            'gdelt_sentiment_negative': float(row['sentiment_negative']),
            'gdelt_article_count': int(row['article_count']),
        })

    return articles
