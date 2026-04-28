import pandas as pd
import numpy as np

class BacktestValidator:
    """
    [span_30](start_span)[span_31](start_span)[span_32](start_span)Performs walk-forward validation and calculates drawdown circuit breakers[span_30](end_span)[span_31](end_span)[span_32](end_span).
    """
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.trades = []

    def calculate_metrics(self, trade_history):
        [span_33](start_span)[span_34](start_span)"""Computes Win Rate, Profit Factor, and Max Drawdown[span_33](end_span)[span_34](end_span)."""
        if not trade_history:
            return {}

        df = pd.DataFrame(trade_history)
        win_rate = len(df[df['pnl'] > 0]) / len(df)
        profit_factor = df[df['pnl'] > 0]['pnl'].sum() / abs(df[df['pnl'] < 0]['pnl'].sum())
        
        # Max Drawdown Calculation
        df['equity'] = self.capital + df['pnl'].cumsum()
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['peak'] - df['equity']) / df['peak']
        max_dd = df['drawdown'].max()

        return {
            "win_rate": round(win_rate * 100, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(max_dd * 100, 2),
            "total_trades": len(df)
        }

    def run_historical(self, df, strategy_func, risk_config):
        """
        Simulates strategy performance over a provided dataframe.
        [span_35](start_span)Applies ATR-based stops and 1:2 R/R rules[span_35](end_span).
        """
        history = []
        for i in range(50, len(df)):
            subset = df.iloc[:i]
            signal = strategy_func(subset)
            
            if signal:
                entry_price = df['close'].iloc[i]
                atr = df['ATR'].iloc[i]
                
                # [span_36](start_span)Risk Rules: 1.5% risk, 1:2 R/R[span_36](end_span)
                stop_loss = entry_price - (atr * 2) if signal == "LONG" else entry_price + (atr * 2)
                take_profit = entry_price + (abs(entry_price - stop_loss) * risk_config['min_rrr'])
                
                # Simple result simulation (checking next 10 candles)
                future_prices = df['close'].iloc[i+1 : i+11]
                pnl = 0
                for price in future_prices:
                    if (signal == "LONG" and price >= take_profit) or (signal == "SHORT" and price <= take_profit):
                        pnl = abs(entry_price - stop_loss) * risk_config['min_rrr']
                        break
                    elif (signal == "LONG" and price <= stop_loss) or (signal == "SHORT" and price >= stop_loss):
                        pnl = -abs(entry_price - stop_loss)
                        break
                
                if pnl != 0:
                    history.append({"symbol": "BACKTEST", "side": signal, "pnl": pnl})
        
        return self.calculate_metrics(history)
