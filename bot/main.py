from bot.data_fetcher import DataFetcher
from bot.indicator_engine import IndicatorEngine
from bot.strategy_engine import StrategyEngine
from bot.consensus_scorer import ConsensusScorer
from bot.risk_manager import RiskManager
from bot.signal_tracker import SignalTracker
from bot.performance_tracker import PerformanceTracker
from bot.logger_setup import setup_logger

logger = setup_logger()

def run_pipeline():
    # 1. Initialize Components
    tracker = PerformanceTracker()
    signal_checker = SignalTracker()
    
    # 2. Check for Weekly Drawdown Kill Switch
    if tracker.check_weekly_drawdown():
        logger.warning("WEEKLY DRAWDOWN LIMIT REACHED. System halted.")
        return

    # 3. Step One: Track and Close Existing Signals
    logger.info("Auditing active signals...")
    signal_checker.check_active_signals()

    # 4. Step Two: Scan for New Opportunities
    fetcher = DataFetcher()
    indicators = IndicatorEngine()
    strategies = StrategyEngine()
    scorer = ConsensusScorer()
    risk = RiskManager()
    
    # Configuration (usually from settings.yaml)
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    
    for symbol in symbols:
        try:
            logger.info(f"Scanning {symbol}...")
            df = fetcher.fetch_ohlcv(symbol, "1h")
            df = indicators.apply_indicators(df)
            
            # Aggregate Strategy Signals
            res_a = strategies.strategy_a_trend_rider(df)
            res_b = strategies.strategy_b_breakout(df)
            
            # Calculate Consensus Score
            score = scorer.calculate_score(df, [res_a, res_b])
            
            if score >= 7.0:
                side = "LONG" # Derived from strategy logic
                entry = df['close'].iloc[-1]
                atr = df['ATR'].iloc[-1]
                stop = entry - (atr * 2)
                tp = entry + (atr * 4) # 1:2 R/R

                # Final Risk Validation
                is_valid, msg = risk.validate_trade(entry, stop, score)
                if is_valid:
                    tracker.log_signal({
                        "symbol": symbol, "side": side, "entry": entry, 
                        "stop": stop, "tp": tp, "score": score
                    })
                    logger.info(f"New Signal Logged: {symbol} @ {entry}")
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")

if __name__ == "__main__":
    run_pipeline()
