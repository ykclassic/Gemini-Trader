import requests
import os
from dotenv import load_dotenv

load_dotenv()

class OnChainEngine:
    """
    Analyzes MVRV, SOPR, and Exchange Netflows to gauge whale accumulation 
    [span_13](start_span)[span_14](start_span)vs. distribution[span_13](end_span)[span_14](end_span).
    """
    def __init__(self):
        self.glassnode_api = os.getenv('GLASSNODE_API_KEY')
        self.coinglass_api = os.getenv('COINGLASS_API_KEY')
        self.base_url = "https://api.glassnode.com/v1/metrics/"

    def get_mvrv_z_score(self, asset="BTC"):
        """
        Calculates the MVRV Z-Score: 
        $$Z = \frac{Market\ Cap - Realized\ Cap}{StdDev(Market\ Cap)}$$
        [span_15](start_span)[span_16](start_span)Used to identify cycle tops and bottoms[span_15](end_span)[span_16](end_span).
        """
        try:
            params = {'a': asset, 'api_key': self.glassnode_api}
            res = requests.get(f"{self.base_url}market/mvrv_z_score", params=params)
            return res.json()[-1]['v'] # Return latest value
        except Exception:
            return 0.0 # Neutral if API fails

    def get_exchange_netflow(self, asset="BTC"):
        """
        Returns net flows (Inflows - Outflows). 
        [span_17](start_span)[span_18](start_span)[span_19](start_span)Negative values = Coins leaving exchanges (Bullish)[span_17](end_span)[span_18](end_span)[span_19](end_span).
        """
        try:
            params = {'a': asset, 'api_key': self.glassnode_api}
            res = requests.get(f"{self.base_url}distribution/exchange_net_flow_sum", params=params)
            return res.json()[-1]['v']
        except Exception:
            return 0.0

    def get_funding_rates(self, symbol="BTCUSDT"):
        [span_20](start_span)[span_21](start_span)[span_22](start_span)"""Fetches aggregate funding rates for contrarian signals[span_20](end_span)[span_21](end_span)[span_22](end_span)."""
        # Integration with Coinglass or CCXT derivatives data
        try:
            url = f"https://open-api.coinglass.com/public/v2/funding?symbol={symbol}"
            headers = {"accept": "application/json", "coinglass_token": self.coinglass_api}
            res = requests.get(url, headers=headers)
            return res.json()['data'][0]['fundingRate']
        except Exception:
            return 0.0

    def get_onchain_bias(self, asset="BTC"):
        [span_23](start_span)[span_24](start_span)"""Aggregates metrics into a single bias score[span_23](end_span)[span_24](end_span)."""
        mvrv = self.get_mvrv_z_score(asset)
        netflow = self.get_exchange_netflow(asset)
        
        bias = 0
        [span_25](start_span)if mvrv < 0: bias += 1  # Undervalued[span_25](end_span)
        [span_26](start_span)if netflow < 0: bias += 1 # Accumulation[span_26](end_span)
        
        [span_27](start_span)return bias # Max score of 2 for on-chain support[span_27](end_span)
