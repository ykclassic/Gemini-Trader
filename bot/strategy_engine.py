import pandas as pd
import numpy as np

class StrategyEngine:
    def __init__(self):
        """
        Initializes the Strategy Engine containing the 8 core strategy modules 
        defined in the Super Joint Blueprint.
        """
        pass

    def strategy_a_trend_rider(self, df):
        """
        Trigger: Price > 200 EMA; 50 EMA > 200 EMA; RSI between 50 and 70.
        Focuses on high-probability trend continuation.
        """
        if len(df) < 200:
            return None
            
        last = df.iloc[-1]
        
        # Check for presence of required indicators
        if 'EMA_200' not in df or 'EMA_50' not in df or 'RSI' not in df:
            return None

        condition = (
            last['close'] > last['EMA_200'] and 
            last['EMA_50'] > last['EMA_200'] and 
            50 < last['RSI'] < 70
        )
        return "LONG" if condition else None

    def strategy_b_breakout(self, df):
        """
        Trigger: Bollinger Band Squeeze + Volume spike.
        Identifies volatility expansion after consolidation.
        """
        if len(df) < 20 or 'BBU_20_2.0' not in df:
            return None
            
        last = df.iloc[-1]
        bb_upper = last['BBU_20_2.0']
        bb_lower = last['BBL_20_2.0']
        bb_middle = last['BBM_20_2.0']
        
        # Calculate Bandwidth (Squeeze)
        bandwidth = (bb_upper - bb_lower) / bb_middle
        
        # Simple volume spike: 50% higher than 20-period average
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        volume_spike = last['volume'] > (avg_volume * 1.5)
        
        if bandwidth < 0.05 and last['close'] > bb_upper and volume_spike:
            return "LONG"
        return None

    def run_all_strategies(self, df):
        """
        Executes all active strategy modules and returns their results for scoring.
        """
        results = {
            "strategy_a": self.strategy_a_trend_rider(df),
            "strategy_b": self.strategy_b_breakout(df),
            # Add placeholders/calls for strategies C through H as they are developed
        }
        return results
