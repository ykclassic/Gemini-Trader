import ccxt
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    def __init__(self):
        """
        Initializes the connection to the XT.com exchange.
        XT.com is used as the primary data source for OHLCV and Ticker data.
        """
        # XT.com requires apiKey and secret for authenticated requests.
        # Public data (OHLCV) can often be fetched without them.
        self.exchange = ccxt.xt({
            'apiKey': os.getenv('XT_API_KEY'),
            'secret': os.getenv('XT_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot' # Target the spot market
            }
        })

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=500):
        """
        Fetches historical candle data from XT.com.
        Converts the raw list output into a clean, typed Pandas DataFrame.
        """
        try:
            # XT.com fetch via CCXT standard interface
            data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not data or len(data) == 0:
                print(f"Warning: No OHLCV data returned from XT for {symbol}")
                return pd.DataFrame()

            # XT.com returns: [timestamp, open, high, low, close, volume]
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Format timestamp to datetime objects
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Force numeric types to ensure IndicatorEngine calculations work
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
            
            return df

        except Exception as e:
            print(f"Error fetching data from XT.com for {symbol}: {e}")
            return pd.DataFrame()

    def fetch_ticker_price(self, symbol):
        """
        Fetches the most recent traded price (last) for the given symbol.
        Used for real-time risk calculations and entry validation.
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            print(f"Error fetching XT ticker for {symbol}: {e}")
            return None

    def get_balance(self):
        """
        Fetches account balance. Requires valid XT_API_KEY and XT_SECRET_KEY.
        """
        try:
            if not self.exchange.apiKey or not self.exchange.secret:
                return None
            return self.exchange.fetch_balance()
        except Exception as e:
            print(f"Error fetching XT balance: {e}")
            return None
