from bot.data_fetcher import DataFetcher
from bot.indicator_engine import IndicatorEngine
from bot.strategy_engine import StrategyEngine
from bot.consensus_scorer import ConsensusScorer
from bot.risk_manager import RiskManager
from bot.signal_formatter import SignalFormatter
from bot.discord_notifier import DiscordNotifier

def run_pipeline():
    fetcher = DataFetcher()
    indicators = IndicatorEngine()
    strategies = StrategyEngine()
    scorer = ConsensusScorer()
    risk = RiskManager()
    
    symbols = ["BTC/USDT"] # From settings
    for symbol in symbols:
        df = fetcher.fetch_ohlcv(symbol, "1h")
        df = indicators.apply_indicators(df)
        
        # Run strategies
        sig_a = strategies.strategy_a_trend_rider(df)
        score = scorer.calculate_score(df, [sig_a])
        
        [span_16](start_span)if score >= 7.0: #[span_16](end_span)
            # Format and notify
            pass

if __name__ == "__main__":
    run_pipeline()
