import pandas as pd
import logging

logger = logging.getLogger("crypto_bot")

class MTFEngine:
    def __init__(self):
        """
        Validates signals across multiple timeframes to ensure macro-alignment.
        """
        self.timeframes = ['15m', '1h', '4h']

    def validate_confluence(self, fetcher, symbol):
        """
        Checks if the 4h trend is Bullish before allowing a 15m Long.
        """
        results = {}
        for tf in self.timeframes:
            df = fetcher.fetch_ohlcv(symbol, tf, limit=100)
            if df.empty:
                continue
            
            # Simple trend check: Price vs EMA 50
            ema50 = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            current_price = df['close'].iloc[-1]
            results[tf] = "BULLISH" if current_price > ema50 else "BEARISH"
        
        # Confluence logic: Macro (4h) and Medium (1h) must match the trade side
        is_aligned = (results.get('4h') == "BULLISH") and (results.get('1h') == "BULLISH")
        return is_aligned, results
