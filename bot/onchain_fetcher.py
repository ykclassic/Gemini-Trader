import requests
import os
import pandas as pd

class OnChainFetcher:
    def __init__(self):
        self.api_key = os.getenv('GLASSNODE_API_KEY')
        self.url = "https://api.glassnode.com/v1/metrics/distribution/exchange_net_flow_sum"

    def get_sentiment_score(self, asset="BTC"):
        """
        Fetches real on-chain netflow data.
        Returns a score: 1.0 (Bullish), 0.0 (Neutral), -1.0 (Bearish).
        """
        if not self.api_key:
            return 0.0

        try:
            params = {
                'a': asset,
                'api_key': self.api_key,
                'f': 'json',
                'i': '24h'
            }
            response = requests.get(self.url, params=params)
            data = response.json()

            if not data or 'v' not in data[-1]:
                return 0.0

            # Latest net flow value
            net_flow = data[-1]['v']
            
            # Logic: If net_flow < 0, whales are withdrawing (Bullish)
            if net_flow < -500: # Threshold of 500 BTC/day
                return 1.0
            elif net_flow > 500: # Whales depositing
                return -1.0
            return 0.0

        except Exception as e:
            print(f"Glassnode API Error: {e}")
            return 0.0
