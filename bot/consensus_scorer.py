import pandas as pd

class ConsensusScorer:
    def __init__(self):
        """
        Initializes the Consensus Scorer which aggregates signals across 
        technical, structural, and on-chain dimensions.
        """
        self.weights = {
            "trend": 2.0,
            "momentum": 1.5,
            "volatility": 1.0,
            "volume": 1.0,
            "smc": 2.5,
            "onchain": 2.0
        }

    def calculate_score(self, df, strategies_results):
        """
        Evaluates signals across multiple dimensions to produce a 0-10 confidence score.
        A score >= 7.0 is required to generate a final signal.
        """
        if df.empty:
            return 0.0

        score = 0.0
        last = df.iloc[-1]

        # 1. Trend Alignment (Max 2.0 pts)
        if 'EMA_200' in last and last['close'] > last['EMA_200']:
            score += 1.0
        if 'SUPERTd_10_3.0' in last and last['SUPERTd_10_3.0'] == 1:
            score += 1.0

        # 2. Momentum (Max 1.5 pts)
        if 'RSI' in last:
            if 50 < last['RSI'] < 70:
                score += 1.5
            elif last['RSI'] >= 70: # Overbought caution
                score += 0.5

        # 3. Strategy Confluence (Adding points based on strategy_engine results)
        if strategies_results.get("strategy_a") == "LONG":
            score += 1.5
        if strategies_results.get("strategy_b") == "LONG":
            score += 1.5

        # 4. Volatility & Volume (Max 2.0 pts)
        if 'OBV' in df.columns:
            if last['OBV'] > df['OBV'].rolling(10).mean().iloc[-1]:
                score += 1.0
        
        # Ensure the score is capped at 10.0
        final_score = min(float(score), 10.0)
        return round(final_score, 1)
