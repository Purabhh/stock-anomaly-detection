import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def cross_stock_correlation(price_data_dict: Dict, window: int = 20) -> pd.DataFrame:
    """Compute rolling Pearson correlation of daily returns across tickers."""
    returns = {}
    for ticker, df in price_data_dict.items():
        col = "close" if "close" in df.columns else df.columns[-1]
        returns[ticker] = df[col].pct_change().dropna()
    returns_df = pd.DataFrame(returns).dropna()
    if returns_df.empty:
        return pd.DataFrame()
    return returns_df.rolling(window=window).corr().dropna()


def detect_sector_contagion(anomalies_dict: Dict, window_days: int = 3, min_stocks: int = 3) -> List:
    """Return dates where min_stocks+ tickers had anomalies within window_days of each other."""
    all_dates_by_ticker = {}
    for ticker, df in anomalies_dict.items():
        date_col = "anomaly_date" if "anomaly_date" in df.columns else "date"
        if date_col not in df.columns:
            continue
        dates = []
        for d in df[date_col].dropna():
            try:
                dates.append(pd.to_datetime(d).date())
            except Exception:
                pass
        all_dates_by_ticker[ticker] = dates

    all_dates = [d for dates in all_dates_by_ticker.values() for d in dates]
    if not all_dates:
        return []

    contagion_dates = []
    for base_date in sorted(set(all_dates)):
        tickers_hit = sum(
            1 for ticker_dates in all_dates_by_ticker.values()
            if any(abs((d - base_date).days) <= window_days for d in ticker_dates)
        )
        if tickers_hit >= min_stocks and base_date not in contagion_dates:
            contagion_dates.append(base_date)
    return contagion_dates


if __name__ == "__main__":
    print("contagion_analysis module OK")
