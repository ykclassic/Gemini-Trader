import requests
import pandas as pd

class OnChainFetcher:
    def __init__(self):
        # No API Key needed for DeFiLlama
        self.base_url = "https://api.llama.fi"

    def get_ecosystem_health(self, chain="solana"):
        """
        Fetches TVL (Total Value Locked) for a specific chain.
        Increasing TVL = Bullish institutional interest.
        """
        try:
            response = requests.get(f"{self.base_url}/tvl/{chain}")
            if response.status_code == 200:
                tvl = float(response.text)
                return tvl
            return 0
        except Exception:
            return 0

    def get_global_sentiment(self):
        """
        Checks global stablecoin movement via CoinPaprika (Free).
        """
        try:
            # Public endpoint for global market data
            res = requests.get("https://api.coinpaprika.com/v1/global")
            data = res.json()
            # Market Cap Dominance of BTC
            return data.get("bitcoin_dominance_percentage", 0)
        except Exception:
            return 50.0
