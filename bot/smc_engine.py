import pandas as pd
import numpy as np
from scipy.signal import find_peaks

class SMCEngine:
    def __init__(self, lookback=50):
        """
        Engine for Smart Money Concepts (SMC).
        Analyzes Market Structure (CHoCH/BOS) and Fair Value Gaps (FVG).
        """
        self.lookback = lookback

    def find_fvg(self, df):
        """
        Identifies price imbalances (FVGs) where a gap exists between wick extremes.
        """
        # Bullish FVG: Low of current candle is higher than High of two candles ago
        df['fvg_bull'] = (df['low'] > df['high'].shift(2)) & (df['close'].shift(1) > df['open'].shift(1))
        # Bearish FVG: High of current candle is lower than Low of two candles ago
        df['fvg_bear'] = (df['high'] < df['low'].shift(2)) & (df['close'].shift(1) < df['open'].shift(1))
        return df

    def get_market_structure(self, df):
        """
        Detects objective market structure shifts and supply/demand zones.
        Uses scipy.signal to ensure institutional-grade swing detection.
        """
        if len(df) < self.lookback:
            return {
                "bullish_choch": False, 
                "bearish_choch": False, 
                "at_order_block": False, 
                "bias": "NEUTRAL", 
                "fvg_present": False
            }

        highs = df['high'].values
        lows = df['low'].values
        close = df['close'].values

        # 1. Detect Swing Points
        # Prominence prevents noise; distance ensures we catch macro structure
        peaks, _ = find_peaks(highs, distance=5, prominence=np.std(highs) * 0.2)
        troughs, _ = find_peaks(-lows, distance=5, prominence=np.std(lows) * 0.2)

        last_high = highs[peaks[-1]] if len(peaks) > 0 else df['high'].max()
        last_low = lows[troughs[-1]] if len(troughs) > 0 else df['low'].min()
        current_price = close[-1]

        # 2. Change of Character (CHoCH) Detection
        bullish_choch = current_price > last_high
        bearish_choch = current_price < last_low

        # 3. Order Block Detection
        # Bullish OB: Last down candle before a displacement upward
        prev_candle = df.iloc[-2]
        last_candle = df.iloc[-1]
        at_order_block = (prev_candle['close'] < prev_candle['open']) and \
                         (last_candle['close'] > prev_candle['high'])

        # 4. Integrate FVG Imbalances
        df = self.find_fvg(df)
        fvg_present = bool(df['fvg_bull'].iloc[-1] or df['fvg_bear'].iloc[-1])

        # 5. Final Bias determination
        bias = "NEUTRAL"
        if bullish_choch:
            bias = "BULLISH"
        elif bearish_choch:
            bias = "BEARISH"

        return {
            "bullish_choch": bullish_choch,
            "bearish_choch": bearish_choch,
            "at_order_block": at_order_block,
            "fvg_present": fvg_present,
            "bias": bias,
            "last_high": float(last_high),
            "last_low": float(last_low)
        }
