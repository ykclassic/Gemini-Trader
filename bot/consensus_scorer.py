class ConsensusScorer:
    [span_9](start_span)[span_10](start_span)"""Evaluates signals across 8 dimensions[span_9](end_span)[span_10](end_span)"""
    def calculate_score(self, df, strategies_results):
        score = 0.0
        last = df.iloc[-1]
        
        # 1. [span_11](start_span)Trend Alignment (Max 2 pts)[span_11](end_span)
        if last['close'] > last['EMA_200']: score += 1.0
        if last['SUPERTd_10_3.0'] == 1: score += 1.0
        
        # 2. Momentum (Max 1.5 pts)
        if 50 < last['RSI'] < 70: score += 1.5
        
        # ... logic for other 6 dimensions ...
        
        return round(score, 1)
