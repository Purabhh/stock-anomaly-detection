"""
Data ingestion pipeline for stock market anomaly detection.
Uses yfinance for price data and NewsAPI for news headlines.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional
from .database import StockDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestion:
    """Handles data collection from yfinance and NewsAPI."""
    
    def __init__(self, db_path: str = "stock_anomaly.db"):
        """Initialize with database connection."""
        self.db = StockDatabase(db_path)
        self.news_api_key = None  # Will be loaded from environment
    
    def fetch_stock_data(self, symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical stock data from yfinance.
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with historical data
        """
        try:
            logger.info(f"Fetching data for {symbol} (period: {period}, interval: {interval})")
            
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()
            
            # Reset index to make Date a column
            df = df.reset_index()
            
            # Add metadata
            info = ticker.info
            stock_name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            country = info.get('country', 'US')
            market_cap = info.get('marketCap')
            
            # Add stock to database
            self.db.add_stock(symbol, stock_name, sector, industry, country, market_cap)
            
            # Add price data to database
            self.db.add_price_data(symbol, df)
            
            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_stocks(self, symbols: List[str], period: str = "2y", 
                             interval: str = "1d", delay: float = 1.0):
        """
        Fetch data for multiple stocks with rate limiting.
        
        Args:
            symbols: List of stock ticker symbols
            period: Time period
            interval: Data interval
            delay: Delay between requests (seconds)
        """
        results = {}
        
        for symbol in symbols:
            df = self.fetch_stock_data(symbol, period, interval)
            results[symbol] = df
            
            # Rate limiting
            time.sleep(delay)
        
        return results
    
    def fetch_news_data(self, symbol: str, days_back: int = 30, api_key: str = None):
        """
        Fetch news articles for a stock using NewsAPI free tier.
        
        Note: NewsAPI free tier has limitations (100 requests/day, articles from last month)
        
        Args:
            symbol: Stock ticker symbol
            days_back: Number of days to look back (max 30 for free tier)
            api_key: NewsAPI key (optional, can be set via environment)
        """
        if api_key is None:
            api_key = self.news_api_key
        
        if not api_key:
            logger.warning("No NewsAPI key provided. Skipping news fetch.")
            return []
        
        try:
            import requests
            from datetime import datetime, timedelta
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=min(days_back, 30))  # Free tier limit
            
            # Format dates for NewsAPI
            from_date = start_date.strftime("%Y-%m-%d")
            to_date = end_date.strftime("%Y-%m-%d")
            
            # NewsAPI endpoint
            url = "https://newsapi.org/v2/everything"
            
            # Parameters
            params = {
                'q': symbol,  # Search for stock symbol
                'from': from_date,
                'to': to_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': api_key,
                'pageSize': 100  # Max for free tier
            }
            
            logger.info(f"Fetching news for {symbol} from {from_date} to {to_date}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'ok':
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
            
            articles = data.get('articles', [])
            logger.info(f"Found {len(articles)} news articles for {symbol}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def update_all_data(self, symbols: List[str], update_frequency: str = "daily"):
        """
        Update all data for tracked stocks based on frequency.
        
        Args:
            symbols: List of stock symbols to update
            update_frequency: 'daily', 'weekly', or 'monthly'
        """
        logger.info(f"Starting {update_frequency} data update for {len(symbols)} stocks")
        
        # Determine period based on frequency
        if update_frequency == "daily":
            period = "1mo"  # Get last month for daily updates
        elif update_frequency == "weekly":
            period = "3mo"
        else:  # monthly
            period = "1y"
        
        # Fetch price data
        price_results = self.fetch_multiple_stocks(symbols, period=period, delay=1.5)
        
        # Fetch news data (if API key available)
        news_results = {}
        if self.news_api_key:
            for symbol in symbols:
                articles = self.fetch_news_data(symbol, days_back=30)
                news_results[symbol] = articles
                
                # Process and store articles with sentiment
                self._process_and_store_news(symbol, articles)
        
        logger.info(f"Data update completed. Price data for {len(price_results)} stocks.")
        return price_results, news_results
    
    def _process_and_store_news(self, symbol: str, articles: List[Dict]):
        """Process news articles with VADER sentiment analysis and store in database."""
        if not articles:
            return
        
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            
            for article in articles:
                # Extract relevant fields
                title = article.get('title', '')
                description = article.get('description', '')
                content = f"{title}. {description}"
                
                # Get sentiment scores
                sentiment = analyzer.polarity_scores(content)
                
                # Prepare article data
                article_data = {
                    'published_at': article.get('publishedAt'),
                    'title': title,
                    'description': description,
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url'),
                    'sentiment_compound': sentiment['compound'],
                    'sentiment_positive': sentiment['pos'],
                    'sentiment_neutral': sentiment['neu'],
                    'sentiment_negative': sentiment['neg']
                }
                
                # Store in database
                self.db.add_news_article(symbol, article_data)
                
        except ImportError:
            logger.warning("vaderSentiment not installed. Skipping sentiment analysis.")
        except Exception as e:
            logger.error(f"Error processing news for {symbol}: {e}")
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    # Test the data ingestion
    ingestor = DataIngestion("test_ingestion.db")
    
    # Test with a few stocks
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    print("Testing data ingestion...")
    results = ingestor.fetch_multiple_stocks(test_symbols, period="1mo", delay=2)
    
    for symbol, df in results.items():
        if not df.empty:
            print(f"{symbol}: {len(df)} records, from {df['Date'].min()} to {df['Date'].max()}")
    
    ingestor.close()
    print("Test completed!")