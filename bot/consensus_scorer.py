import logging

logger = logging.getLogger("crypto_bot")

class ConsensusScorer:
    def __init__(self):
        """
        The 'Brain' of the system. Aggregates technical, structural, 
        and intelligence layers into a single decision score (0-10).
        """
        # Weights assigned based on historical reliability
        self.weights = {
            "technicals": 3.0,  # Strategy Engine (RSI, EMA, etc.)
            "structure": 4.0,   # SMC Engine (CHoCH, Order Blocks)
            "intelligence": 3.0 # Neural Layer & MTF Alignment
        }

    def calculate_score(self, tech_results, smc_data, neural_conf, mtf_aligned):
        """
        Calculates the final consensus score.
        :param tech_results: Dict from StrategyEngine
        :param smc_data: Dict from SMCEngine
        :param neural_conf: Float (0.0-1.0) from NeuralLayer
        :param mtf_aligned: Boolean from MTFEngine
        """
        score = 0.0
        tech_hits = 0  # Pre-define to ensure the logger always has a value

        # 1. Technical Contribution (Max 3.0)
        if tech_results:
            # Replaced 'long_hits' with 'tech_hits' to fix the NameError
            tech_hits = list(tech_results.values()).count("LONG")
            tech_ratio = tech_hits / len(tech_results)
            score += tech_ratio * self.weights["technicals"]

        # 2. Structural Contribution (Max 4.0)
        if smc_data.get("bullish_choch"):
            score += 2.5
        if smc_data.get("at_order_block"):
            score += 1.5
        elif smc_data.get("bias") == "BULLISH":
            score += 0.5

        # 3. Intelligence Contribution (Max 3.0)
        # Combines Neural Confidence and MTF Alignment
        intel_score = (neural_conf * 2.0) + (1.0 if mtf_aligned else 0.0)
        score += min(intel_score, self.weights["intelligence"])

        final_score = round(min(score, 10.0), 2)
        
        # Safely log the breakdown now that tech_hits is strictly defined
        logger.info(f"Consensus Breakdown: Tech({tech_hits}), "
                    f"SMC({smc_data.get('bias')}), Neural({round(neural_conf, 2)}) -> Score: {final_score}")
        
        return final_score
