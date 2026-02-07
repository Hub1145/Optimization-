import pandas as pd
import ccxt
import yfinance as yf
from datetime import datetime
from typing import Optional, Literal
import asyncio

class MarketDataService:
    """Service for fetching market data"""

    def __init__(self):
        self.binance = ccxt.binance()

    async def get_data(self, symbol: str, start_date: str, end_date: str,
                       timeframe: str = '1d',
                       provider: Literal["crypto", "stock", "forex"] = "crypto",
                       exchange: str = 'binance') -> pd.DataFrame:
        """
        Fetch OHLCV data
        """
        if provider == "crypto":
            return await self._get_crypto_data(symbol, timeframe, start_date, end_date, exchange)
        else:
            return self._get_yfinance_data(symbol, timeframe, start_date, end_date)

    async def _get_crypto_data(self, symbol: str, timeframe: str,
                               start_date: str, end_date: str,
                               exchange_id: str) -> pd.DataFrame:
        """Fetch data from CCXT"""
        exchange_class = getattr(ccxt, exchange_id)()

        since = exchange_class.parse8601(f"{start_date}T00:00:00Z")
        end_timestamp = exchange_class.parse8601(f"{end_date}T23:59:59Z")

        all_ohlcv = []
        while since < end_timestamp:
            ohlcv = await asyncio.to_thread(exchange_class.fetch_ohlcv, symbol, timeframe, since)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1
            if len(ohlcv) < 100: # Assuming limit is usually higher
                break

        df = pd.DataFrame(all_ohlcv, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df.set_index('Date', inplace=True)

        return df[start_date:end_date]

    def _get_yfinance_data(self, symbol: str, timeframe: str,
                           start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from yfinance"""
        # Map timeframe to yfinance format
        tf_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '4h': '1h', # yfinance doesn't support 4h directly easily
            '1d': '1d'
        }
        interval = tf_map.get(timeframe, '1d')

        df = yf.download(symbol, start=start_date, end=end_date, interval=interval)

        # yfinance columns: Open, High, Low, Close, Adj Close, Volume
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
            df.drop('Adj Close', axis=1, inplace=True)

        return df
