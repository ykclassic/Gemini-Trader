import ccxt
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    def __init__(self):
        """
        Initializes the exchange connection using KuCoin.
        KuCoin is generally more permissive with GitHub Action IP ranges 
        compared to Binance and Bybit.
        """
        self.exchange = ccxt.kucoin({
            'apiKey': os.getenv('KUCOIN_API_KEY'),
            'secret': os.getenv('KUCOIN_SECRET_KEY'),
            'password': os.getenv('KUCOIN_PASSPHRASE'), # KuCoin requires a third 'Passphrase' key
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=500):
        """
        Fetches historical candle data from KuCoin.
        Handles data mapping for the Indicator Engine.
        """
        try:
            # KuCoin fetch via CCXT
            data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not data:
                print(f"Warning: No data returned for {symbol}")
                return pd.DataFrame()

            # Creating DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Converting timestamp to readable datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Ensure numeric types
            cols = ['open', 'high', 'low', 'close', 'volume']
            df[cols] = df[cols].apply(pd.to_numeric)
            
            return df
        except Exception as e:
            print(f"Error fetching data from KuCoin for {symbol}: {e}")
            return pd.DataFrame()

    def fetch_ticker_price(self, symbol):
        """Fetches the latest ticker price."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return None
