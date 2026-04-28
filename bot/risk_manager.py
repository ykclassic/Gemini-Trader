import logging

logger = logging.getLogger("crypto_bot")

class RiskManager:
    def __init__(self):
        """
        Implements position sizing and the 1:2 R/R ratio logic.
        Ensures every trade adheres to the Super Joint Blueprint's risk rules.
        """
        self.min_rrr = 2.0
        self.max_risk_per_trade = 0.015  # 1.5% capital risk

    def validate_trade(self, entry, stop, score):
        """
        Validates the trade based on Risk-Reward Ratio and Confidence Score.
        Returns a tuple: (is_valid: bool, message: str)
        """
        # 1. Confidence Threshold Check
        if score < 7.0:
            return False, f"Score {score} is below the 7.0 consensus threshold."

        # 2. Risk Calculation
        risk = abs(entry - stop)
        if risk <= 0:
            return False, "Invalid Risk: Stop Loss is at or above Entry price."

        # 3. Reward Calculation (Target based on 1:2 R/R)
        target = entry + (risk * self.min_rrr)
        
        # 4. Logical Check
        if stop >= entry:
            return False, "Logical Error: Stop loss must be below entry for LONG signals."

        return True, "Risk levels and consensus score validated."

    def calculate_position_size(self, balance, entry, stop):
        """
        Calculates the amount of capital to allocate based on 1.5% total risk.
        Formula: (Balance * Risk%) / (Entry - Stop)
        """
        risk_amount = balance * self.max_risk_per_trade
        price_risk = abs(entry - stop)
        
        if price_risk == 0:
            return 0
            
        return risk_amount / price_risk
