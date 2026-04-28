import ccxt
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    def __init__(self):
        """
        Initializes the exchange connection using Bybit.
        Bybit is used here to bypass regional restrictions often encountered 
        with Binance on GitHub Actions.
        """
        self.exchange = ccxt.bybit({
            'apiKey': os.getenv('BYBIT_API_KEY'),
            'secret': os.getenv('BYBIT_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=500):
        """
        Fetches historical candle data from Bybit.
        Automatically handles symbol formatting (e.g., BTC/USDT).
        """
        try:
            # Bybit OHLCV fetch via CCXT
            data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not data:
                print(f"Warning: No data returned for {symbol}")
                return pd.DataFrame()

            # Creating DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Converting timestamp to readable datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Ensure numeric types for calculations
            cols = ['open', 'high', 'low', 'close', 'volume']
            df[cols] = df[cols].apply(pd.to_numeric)
            
            return df
        except Exception as e:
            print(f"Error fetching data from Bybit for {symbol}: {e}")
            return pd.DataFrame()

    def fetch_ticker_price(self, symbol):
        """Fetches the latest ticker price for real-time tracking."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return None
