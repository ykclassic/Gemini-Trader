import ccxt
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    def __init__(self):
        """
        Initializes the exchange. 
        Note: We define the exchange without API keys first for public data 
        to avoid regional 'Private API' restrictions on GitHub Actions.
        """
        # Initialize for public data (No API keys = Fewer regional blocks for OHLCV)
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        
        # Only attach keys if they are present and needed for private endpoints
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_SECRET_KEY')
        
        if api_key and api_secret:
            self.exchange.apiKey = api_key
            self.exchange.secret = api_secret

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=500):
        """
        Fetches historical candle data. 
        Uses public endpoint to minimize regional restriction errors.
        """
        try:
            # Explicitly ensure we are using the public fetch_ohlcv
            data = self.exchange.public_get_klines({
                'symbol': symbol.replace('/', ''),
                'interval': timeframe,
                'limit': limit
            })
            
            # Binance public_get_klines returns a list of lists
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Format and convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            cols = ['open', 'high', 'low', 'close', 'volume']
            df[cols] = df[cols].apply(pd.to_numeric)
            
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"Public Fetch Error for {symbol}: {e}")
            # Fallback to standard CCXT method
            try:
                data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
            except Exception as e2:
                print(f"Critical Fetch Error for {symbol}: {e2}")
                return pd.DataFrame()

    def fetch_ticker_price(self, symbol):
        """Fetches the latest ticker price."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return None
