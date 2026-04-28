import ccxt
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET_KEY'),
            'enableRateLimit': True
        })

    def fetch_ohlcv(self, symbol, timeframe, limit=500):
        [span_5](start_span)"""Fetches historical candle data[span_5](end_span)"""
        data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
