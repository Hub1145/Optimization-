import pandas as pd
import ccxt
from datetime import datetime
from typing import Optional, Literal
import asyncio
from app.config import settings
from app.utils.validators import validate_date_range

class MarketDataService:
    """Service for fetching market data using CCXT (primarily Binance)"""

    def __init__(self, exchange_id: str = 'binance'):
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'enableRateLimit': True,
        })

    async def get_data(self, symbol: str, start_date: str, end_date: str,
                       timeframe: str = '1d') -> pd.DataFrame:
        """
        Fetch OHLCV data from Binance for crypto
        """
        # Validate data range
        validate_date_range(start_date, end_date, settings.MAX_DATA_DAYS)

        return await self._get_crypto_data(symbol, timeframe, start_date, end_date)

    async def _get_crypto_data(self, symbol: str, timeframe: str,
                               start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from CCXT exchange"""
        since = self.exchange.parse8601(f"{start_date}T00:00:00Z")
        end_timestamp = self.exchange.parse8601(f"{end_date}T23:59:59Z")

        all_ohlcv = []
        # Support common CCXT timeframes
        while since < end_timestamp:
            ohlcv = await asyncio.to_thread(self.exchange.fetch_ohlcv, symbol, timeframe, since)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1

            # If we reached current time or requested end, break
            if ohlcv[-1][0] >= end_timestamp:
                break

            # Anti-flood delay for large fetches
            await asyncio.sleep(self.exchange.rateLimit / 1000)

        if not all_ohlcv:
            return pd.DataFrame()

        df = pd.DataFrame(all_ohlcv, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df.set_index('Date', inplace=True)

        # Trim to exact range requested
        return df[start_date:end_date]
