"""
Data ingestion pipeline for Anomalyy.
Uses yfinance for price data and GDELT 2.0 GKG (via src.news_bq, BigQuery) for headlines.
"""

import yfinance as yf
import pandas as pd
import logging
from typing import List, Dict
from .database import StockDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module constants as required
DEFAULT_TICKERS = ['AAPL', 'MSFT', 'TSLA', 'AMZN', '^GSPC']
DEFAULT_START = '2015-01-01'
DEFAULT_END = '2024-12-31'


class DataIngestion:
    """Collects price data via yfinance and news/sentiment via GDELT BQ."""
    
    def __init__(self, db_path: str = "anomalyy.db"):
        """Initialize with database connection."""
        self.db = StockDatabase(db_path)
    
    def fetch_stock_data_by_date(self, symbol: str, start_date: str = DEFAULT_START,
                                end_date: str = DEFAULT_END, interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical stock data from yfinance using date range.

        Returns a DataFrame with lowercase columns
        ('date','open','high','low','close','adj_close','volume') so downstream
        consumers (FeatureEngineer) can use it directly. The DB write happens
        before normalization since `add_price_data` expects yfinance's
        title-case columns.
        """
        try:
            logger.info(f"Fetching data for {symbol} ({start_date} to {end_date}, interval: {interval})")

            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)

            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()

            df = df.reset_index()

            # Newer yfinance versions auto-adjust Close and drop "Adj Close".
            # Synthesize it so add_price_data's required-columns check passes.
            if 'Adj Close' not in df.columns and 'Close' in df.columns:
                df['Adj Close'] = df['Close']

            info = ticker.info
            stock_name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            country = info.get('country', 'US')
            market_cap = info.get('marketCap')

            self.db.add_stock(symbol, stock_name, sector, industry, country, market_cap)
            self.db.add_price_data(symbol, df)

            # Normalize to lowercase column names for downstream FeatureEngineer
            column_map = {'Date': 'date', 'Open': 'open', 'High': 'high',
                          'Low': 'low', 'Close': 'close', 'Volume': 'volume',
                          'Adj Close': 'adj_close'}
            df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

            logger.info(f"Successfully fetched {len(df)} records for {symbol} from {start_date} to {end_date}")
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_news_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch news articles for a stock from GDELT 2.0 GKG via BigQuery.

        Short-circuits when the SQLite cache already has rows for this
        (symbol, window) combo — BQ is metered and the data doesn't change.
        Returns NewsAPI-shape dicts (one synthetic aggregate per day) carrying
        GDELT V2Tone scores in the `gdelt_*` keys; `_process_and_store_news`
        detects these and uses V2Tone directly instead of running VADER on
        the synthetic title.
        """
        cached = self.db.get_news_for_period(symbol, start_date, end_date)
        if cached is not None and not cached.empty:
            logger.info(f"GDELT BQ: cache hit for {symbol} ({len(cached)} rows); skipping BQ query")
            return []  # cached rows already in DB; nothing to re-store

        from .news_bq import fetch_for_ticker
        return fetch_for_ticker(symbol, start_date, end_date)

    def _process_and_store_news(self, symbol: str, articles: List[Dict]):
        """Process news articles and store in database.

        For GDELT BQ aggregates (carrying `gdelt_*` keys with V2Tone scores
        pre-computed on full article bodies), use V2Tone directly. Otherwise
        fall back to running VADER on title+description. The dual path lets
        the same DB row format serve both data sources.
        """
        if not articles:
            return

        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()

            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                article_count = article.get('gdelt_article_count', 1)

                if 'gdelt_sentiment_compound' in article:
                    # GDELT V2Tone path: pre-computed on full article body.
                    # Tone components are in [-1, 1]; neutral isn't reported
                    # by GDELT so we synthesize it as 1 - |compound|.
                    compound = article['gdelt_sentiment_compound']
                    pos = article['gdelt_sentiment_positive']
                    neg = article['gdelt_sentiment_negative']
                    neu = max(0.0, 1.0 - abs(compound))
                else:
                    # Legacy VADER path on raw headline+description.
                    sentiment = analyzer.polarity_scores(f"{title}. {description}")
                    compound = sentiment['compound']
                    pos = sentiment['pos']
                    neu = sentiment['neu']
                    neg = sentiment['neg']

                article_data = {
                    'published_at': article.get('publishedAt'),
                    'title': title,
                    'description': description,
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url'),
                    'sentiment_compound': compound,
                    'sentiment_positive': pos,
                    'sentiment_neutral': neu,
                    'sentiment_negative': neg,
                    'article_count': article_count,
                }

                self.db.add_news_article(symbol, article_data)

        except ImportError:
            logger.warning("vaderSentiment not installed. Skipping sentiment analysis.")
        except Exception as e:
            logger.error(f"Error processing news for {symbol}: {e}")
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    # Standalone smoke test. Real coverage lives in tests/test_pipeline.py.
    ingestor = DataIngestion("test_ingestion.db")
    print("Testing data ingestion...")
    df = ingestor.fetch_stock_data_by_date("AAPL", "2024-01-01", "2024-02-01")
    if not df.empty:
        print(f"AAPL: {len(df)} records from {df['date'].min()} to {df['date'].max()}")
    ingestor.close()
    print("Test completed!")