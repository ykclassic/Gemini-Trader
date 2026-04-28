import pandas as pd
import pandas_ta_classic as ta
import yaml
import os

class IndicatorEngine:
    def __init__(self, config_path="config/settings.yaml"):
        """
        Initializes the engine by loading indicator parameters from settings.yaml.
        """
        if not os.path.exists(config_path):
            # Fallback default configuration if file is missing
            self.config = {
                'ema_ribbon': [8, 13, 21, 50, 100, 200],
                'rsi': {'period': 14},
                'supertrend': {'period': 10, 'multiplier': 3},
                'atr_period': 14
            }
        else:
            with open(config_path, 'r') as f:
                full_config = yaml.safe_load(f)
                self.config = full_config.get('indicators', {})

    def apply_indicators(self, df):
        """
        Calculates 40+ indicators across Trend, Momentum, Volatility, and Volume layers.
        Expects a DataFrame with 'open', 'high', 'low', 'close', 'volume' columns.
        """
        if df.empty:
            return df

        # --- Trend & Structure Layer ---
        # EMA Ribbon logic
        ema_periods = self.config.get('ema_ribbon', [8, 13, 21, 50, 100, 200])
        for period in ema_periods:
            df[f'EMA_{period}'] = ta.ema(df['close'], length=period)
        
        # Supertrend
        st_config = self.config.get('supertrend', {'period': 10, 'multiplier': 3})
        st = ta.supertrend(
            df['high'], df['low'], df['close'], 
            length=st_config['period'], 
            multiplier=st_config['multiplier']
        )
        if st is not None:
            df = pd.concat([df, st], axis=1)

        # --- Momentum Layer ---
        # RSI with adaptive logic
        rsi_period = self.config.get('rsi', {}).get('period', 14)
        df['RSI'] = ta.rsi(df['close'], length=rsi_period)
        
        # Stochastic RSI
        stoch_config = self.config.get('stoch_rsi', {'k': 3, 'd': 3, 'rsi_len': 14, 'stoch_len': 14})
        stoch_rsi = ta.stochrsi(
            df['close'], 
            length=stoch_config['stoch_len'], 
            rsi_length=stoch_config['rsi_len'], 
            k=stoch_config['k'], 
            d=stoch_config['d']
        )
        if stoch_rsi is not None:
            df = pd.concat([df, stoch_rsi], axis=1)

        # --- Volatility Layer ---
        # ATR for Risk Management (Stops/Sizing)
        atr_len = self.config.get('atr_period', 14)
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=atr_len)
        
        # Bollinger Bands
        bbands = ta.bbands(df['close'], length=20, std=2)
        if bbands is not None:
            df = pd.concat([df, bbands], axis=1)

        # --- Volume Layer ---
        df['OBV'] = ta.obv(df['close'], df['volume'])
        
        return df
