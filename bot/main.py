import logging
import yaml
from bot.data_fetcher import DataFetcher
from bot.indicator_engine import IndicatorEngine
from bot.smc_engine import SMCEngine
from bot.mtf_engine import MTFEngine # Phase 3
from bot.neural_layer import NeuralLayer # Phase 4
from bot.consensus_scorer import ConsensusScorer
from bot.risk_manager import RiskManager
from bot.discord_notifier import DiscordNotifier
from bot.performance_tracker import PerformanceTracker

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("crypto_bot")

def run_pipeline():
    # Load Config
    with open("config/settings.yaml", 'r') as f:
        config = yaml.safe_load(f)

    # Initialize All Engines
    fetcher = DataFetcher()
    indicators = IndicatorEngine()
    smc = SMCEngine()
    mtf = MTFEngine()
    neural = NeuralLayer()
    scorer = ConsensusScorer()
    risk_mgr = RiskManager()
    notifier = DiscordNotifier()
    tracker = PerformanceTracker()

    # Phase 4: Self-Optimization
    neural.train_on_history()

    symbols = config.get('trading', {}).get('symbols', [])
    
    for symbol in symbols:
        # Phase 3: Macro Confluence Check
        is_aligned, mtf_data = mtf.validate_confluence(fetcher, symbol)
        if not is_aligned:
            logger.info(f"Skipping {symbol}: No MTF Confluence {mtf_data}")
            continue

        # Data Processing
        df = fetcher.fetch_ohlcv(symbol, '1h')
        df = indicators.apply_indicators(df)
        
        # Analysis
        smc_data = smc.get_market_structure(df)
        base_score = scorer.calculate_score(df, {}, smc_data)

        # Phase 4: Neural Confidence Filtering
        features = [base_score, df['RSI'].iloc[-1], df['volume'].pct_change().iloc[-1]]
        neural_conf = neural.predict_confidence(features)
        
        final_score = base_score * neural_conf

        if final_score >= config['trading']['consensus_threshold']:
            # Execution
            last_price = df['close'].iloc[-1]
            risk_data = risk_mgr.get_position_details(df, last_price)
            
            signal_data = {
                "symbol": symbol, "side": "LONG", "entry": last_price,
                "stop": risk_data['stop_loss'], "tp": risk_data['take_profit'],
                "score": round(final_score, 2)
            }
            
            # Save and Notify
            tracker.log_signal(signal_data)
            notifier.send_signal(signal_data)
            logger.info(f"🚀 FINALIZED SIGNAL: {symbol} Score: {final_score}")

if __name__ == "__main__":
    run_pipeline()
