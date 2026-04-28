import pandas_ta as ta
import yaml

class IndicatorEngine:
    def __init__(self, config_path="config/settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['indicators']

    def apply_indicators(self, df):
        [span_6](start_span)"""[span_6](end_span)"""
        # Trend Layer
        for period in self.config['ema_ribbon']:
            df[f'EMA_{period}'] = ta.ema(df['close'], length=period)
        
        st = ta.supertrend(df['high'], df['low'], df['close'], 
                          length=self.config['supertrend']['period'], 
                          multiplier=self.config['supertrend']['multiplier'])
        df = pd.concat([df, st], axis=1)

        # Momentum Layer
        df['RSI'] = ta.rsi(df['close'], length=self.config['rsi']['period'])
        
        # Volatility Layer
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=self.config['atr_period'])
        bbands = ta.bbands(df['close'], length=20, std=2)
        df = pd.concat([df, bbands], axis=1)
        
        # Volume Layer
        df['OBV'] = ta.obv(df['close'], df['volume'])
        
        return df
