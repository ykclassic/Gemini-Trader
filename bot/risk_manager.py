import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("crypto_bot")

class RiskManager:
    def __init__(self, risk_per_trade=0.015, default_rr=2.0):
        """
        Handles trade validation, ATR-based exits, and position sizing.
        :param risk_per_trade: Percentage of total balance to risk (1.5%)
        :param default_rr: Minimum Risk:Reward ratio
        """
        self.risk_per_trade = risk_per_trade
        self.min_rr = default_rr

    def calculate_position(self, df, entry_price, balance, score, side="LONG"):
        """
        Calculates the exact Stop Loss, Take Profit, and Quantity to buy.
        """
        if df.empty or 'ATR' not in df.columns:
            logger.warning("ATR missing from DataFrame. Using fallback risk.")
            atr = entry_price * 0.02
        else:
            atr = df['ATR'].iloc[-1]

        # 1. Calculate ATR-Based Exits
        # We use a 2x ATR Stop and a multiplier based on the Consensus Score
        # A higher score allows for a more aggressive Take Profit (up to 4x ATR)
        tp_multiplier = max(2.5, (score / 2)) 
        
        if side == "LONG":
            stop_loss = entry_price - (atr * 2)
            take_profit = entry_price + (atr * tp_multiplier)
        else:
            stop_loss = entry_price + (atr * 2)
            take_profit = entry_price - (atr * tp_multiplier)

        # 2. Dynamic Position Sizing
        # Risk Amount = Balance * 1.5%
        # Quantity = Risk Amount / (Entry - StopLoss)
        risk_amount_usdt = balance * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return None

        quantity = risk_amount_usdt / price_risk

        # 3. Final Validation
        rr_ratio = abs(take_profit - entry_price) / price_risk
        
        return {
            "side": side,
            "entry": round(entry_price, 4),
            "stop": round(stop_loss, 4),
            "tp": round(take_profit, 4),
            "quantity": round(quantity, 6),
            "risk_usdt": round(risk_amount_usdt, 2),
            "rr_ratio": round(rr_ratio, 2)
        }

    def validate_trade(self, risk_data):
        """
        Final filter before execution. 
        Ensures Risk:Reward meets the minimum threshold.
        """
        if risk_data['rr_ratio'] < self.min_rr:
            return False, f"Risk/Reward too low: {risk_data['rr_ratio']}"
        
        if risk_data['quantity'] <= 0:
            return False, "Invalid quantity calculated."

        return True, "Trade validated."
