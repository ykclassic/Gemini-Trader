class StrategyEngine:
    [span_7](start_span)"""[cite: 12-18]"""
    def __init__(self):
        pass

    def strategy_a_trend_rider(self, df):
        """Trigger: Price > 200 EMA; 50 EMA > 200 EMA; [cite_start]RSI 50-70[span_7](end_span)"""
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        condition = (
            last['close'] > last['EMA_200'] and 
            last['EMA_50'] > last['EMA_200'] and 
            50 < last['RSI'] < 70 and
            last['volume'] > df['volume'].rolling(20).mean().iloc[-1]
        )
        return "LONG" if condition else None

    def strategy_b_breakout(self, df):
        [span_8](start_span)"""Trigger: BB Squeeze + Volume spike[span_8](end_span)"""
        last = df.iloc[-1]
        # Simplified squeeze logic
        bb_width = (last['BBU_20_2.0'] - last['BBL_20_2.0']) / last['BBM_20_2.0']
        if bb_width < 0.05 and last['close'] > last['BBU_20_2.0']:
            return "LONG"
        return None
