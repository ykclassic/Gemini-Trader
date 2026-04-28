import pandas as pd
import numpy as np

class SMCEngine:
    """
    Detects Order Blocks (OB), Fair Value Gaps (FVG), Break of Structure (BOS), 
    [span_0](start_span)[span_1](start_span)[span_2](start_span)and Change of Character (CHOCH)[span_0](end_span)[span_1](end_span)[span_2](end_span).
    """
    def __init__(self, lookback=50):
        self.lookback = lookback

    def find_fvg(self, df):
        [span_3](start_span)[span_4](start_span)"""Identifies price imbalances (FVGs) where a gap exists between wick extremes[span_3](end_span)[span_4](end_span)."""
        df['fvg_bull'] = (df['low'].shift(-1) > df['high'].shift(1)) & (df['close'] > df['open'])
        df['fvg_bear'] = (df['high'].shift(-1) < df['low'].shift(1)) & (df['close'] < df['open'])
        
        # Store the gap levels
        df['fvg_top'] = np.where(df['fvg_bull'], df['low'].shift(-1), np.where(df['fvg_bear'], df['low'].shift(1), 0))
        df['fvg_bottom'] = np.where(df['fvg_bull'], df['high'].shift(1), np.where(df['fvg_bear'], df['high'].shift(-1), 0))
        return df

    def detect_structure(self, df):
        [span_5](start_span)[span_6](start_span)"""Detects BOS and CHOCH by tracking swing highs and lows[span_5](end_span)[span_6](end_span)."""
        df['swing_high'] = df['high'][(df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))]
        df['swing_low'] = df['low'][(df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))]
        
        last_high = df['swing_high'].ffill()
        last_low = df['swing_low'].ffill()

        # [span_7](start_span)Break of Structure (BOS): Trend Continuation[span_7](end_span)
        df['BOS'] = (df['close'] > last_high.shift(1)) | (df['close'] < last_low.shift(1))
        
        # [span_8](start_span)Change of Character (CHOCH): Initial Reversal[span_8](end_span)
        # Detected when price breaks a swing point in the opposite direction of the local trend
        df['CHOCH'] = (df['close'] > last_high.shift(1)) & (df['close'].shift(5) < last_low.shift(5))
        return df

    def find_order_blocks(self, df):
        [span_9](start_span)[span_10](start_span)"""Detects the last candle before a structural break[span_9](end_span)[span_10](end_span)."""
        df['OB'] = False
        for i in range(1, len(df)):
            # Bullish OB: Last down candle before a BOS to the upside
            if df['BOS'].iloc[i] and df['close'].iloc[i] > df['open'].iloc[i-1]:
                if df['close'].iloc[i-1] < df['open'].iloc[i-1]:
                    df.at[df.index[i-1], 'OB'] = True
        return df

    def get_smc_signals(self, df):
        df = self.find_fvg(df)
        df = self.detect_structure(df)
        df = self.find_order_blocks(df)
        return df
