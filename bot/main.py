import logging
import yaml
import os
from dotenv import load_dotenv

# Import bot modules
from bot.data_fetcher import DataFetcher
from bot.indicator_engine import IndicatorEngine
from bot.strategy_engine import StrategyEngine
from bot.consensus_scorer import ConsensusScorer
from bot.risk_manager import RiskManager
from bot.signal_formatter import SignalFormatter
from bot.discord_notifier import DiscordNotifier
from bot.performance_tracker import PerformanceTracker

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("crypto_bot")

load_dotenv()

def run_pipeline():
    # 1. Load Configuration
    config_path = "config/settings.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found at {config_path}")
        return

    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            return

    # Safely extract trading parameters
    trading_cfg = config.get('trading', {})
    # This check prevents the 'list' object has no attribute 'get' error
    if isinstance(trading_cfg, list):
        logger.error("Configuration Error: 'trading' section in settings.yaml should be a dictionary, not a list.")
        return
        
    symbols = trading_cfg.get('symbols', ["BTC/USDT"])
    timeframes = trading_cfg.get('timeframes', ["1h"])
    threshold = trading_cfg.get('consensus_threshold', 7.0)

    # 2. Initialize Engines
    fetcher = DataFetcher()
    indicators = IndicatorEngine()
    strategies = StrategyEngine()
    scorer = ConsensusScorer()
    risk_mgr = RiskManager()
    notifier = DiscordNotifier()
    perf_tracker = PerformanceTracker()

    # 3. Audit Active Signals (Check for TPs/SLs)
    logger.info("Auditing active signals...")
    # Add tracker audit logic here if signals exist in DB

    # 4. Main Scan Loop
    for symbol in symbols:
        for tf in timeframes:
            try:
                logger.info(f"Scanning {symbol} on {tf}...")
                
                # Fetch Data
                df = fetcher.fetch_ohlcv(symbol, tf)
                if df.empty:
                    continue

                # Apply Indicators
                df = indicators.apply_indicators(df)

                # Execute Strategy Modules
                strategy_hits = strategies.run_all_strategies(df)

                # Calculate Consensus Score
                score = scorer.calculate_score(df, strategy_hits)

                if score >= threshold:
                    # Logic to determine Side, Entry, Stop, and TP
                    last_price = df.iloc[-1]['close']
                    atr = df.iloc[-1].get('ATR', last_price * 0.02)
                    
                    signal_data = {
                        "symbol": symbol,
                        "side": "LONG",
                        "entry": last_price,
                        "stop": last_price - (atr * 2),
                        "tp": last_price + (atr * 4),
                        "score": score
                    }

                    # Validate Risk
                    is_valid, msg = risk_mgr.validate_trade(
                        signal_data['entry'], 
                        signal_data['stop'], 
                        score
                    )

                    if is_valid:
                        embed = SignalFormatter.format_discord_embed(signal_data)
                        notifier.send_signal(embed)
                        logger.info(f"✅ Signal Sent for {symbol}")
                    else:
                        logger.info(f"⚠️ Signal rejected for {symbol}: {msg}")

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")

if __name__ == "__main__":
    run_pipeline()
