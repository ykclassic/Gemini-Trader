import logging
import yaml
import os
from bot.data_fetcher import DataFetcher
from bot.indicator_engine import IndicatorEngine
from bot.smc_engine import SMCEngine
from bot.mtf_engine import MTFEngine
from bot.neural_layer import NeuralLayer
from bot.consensus_scorer import ConsensusScorer
from bot.risk_manager import RiskManager
from bot.discord_notifier import DiscordNotifier
from bot.performance_tracker import PerformanceTracker

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("crypto_bot")

def run_pipeline():
    # 1. Load Configuration
    with open("config/settings.yaml", 'r') as f:
        config = yaml.safe_load(f)

    # 2. Initialize All Engines
    fetcher = DataFetcher()
    indicators = IndicatorEngine()
    smc = SMCEngine()
    mtf = MTFEngine()
    neural = NeuralLayer()
    scorer = ConsensusScorer()
    risk_mgr = RiskManager()
    notifier = DiscordNotifier()
    tracker = PerformanceTracker()

    # 3. Phase 4: Self-Optimization (Train on historical DB)
    neural.train_on_history()

    # Fetch total USDT balance for dynamic position sizing (Fallback to 1000 if using free tier)
    balance_data = fetcher.get_balance()
    usdt_balance = 1000.0
    if balance_data and 'USDT' in balance_data and 'free' in balance_data['USDT']:
        usdt_balance = float(balance_data['USDT']['free'])

    symbols = config.get('trading', {}).get('symbols', [])
    
    for symbol in symbols:
        # Phase 3: Macro Confluence Check
        is_aligned, mtf_data = mtf.validate_confluence(fetcher, symbol)
        if not is_aligned:
            logger.info(f"Skipping {symbol}: No MTF Confluence {mtf_data}")
            continue

        # Data Processing
        df = fetcher.fetch_ohlcv(symbol, '1h')
        if df.empty:
            logger.warning(f"Empty DataFrame returned for {symbol}. Skipping.")
            continue
            
        df = indicators.apply_indicators(df)
        
        # Extract basic technicals for the scorer
        tech_results = {}
        if 'RSI' in df.columns:
            rsi = df['RSI'].iloc[-1]
            tech_results['RSI'] = "LONG" if rsi < 30 else ("SHORT" if rsi > 70 else "NEUTRAL")

        # Phase 2: SMC Structure
        smc_data = smc.get_market_structure(df)

        # Phase 4: Neural Confidence Filtering
        rsi_val = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50.0
        volume_delta = df['volume'].pct_change().iloc[-1] if 'volume' in df.columns else 0.0
        
        # We pass a neutral base score of 5.0 to the model for the prediction feature
        features = [5.0, rsi_val, volume_delta]
        neural_conf = neural.predict_confidence(features)
        
        # Calculate Final Consensus Score with updated signature
        final_score = scorer.calculate_score(tech_results, smc_data, neural_conf, is_aligned)

        # Execution Logic
        if final_score >= config['trading']['consensus_threshold']:
            last_price = df['close'].iloc[-1]
            
            # Phase 2: Dynamic Risk Management based on balance
            risk_data = risk_mgr.calculate_position(df, last_price, usdt_balance, final_score, side="LONG")
            
            if not risk_data:
                logger.warning(f"Risk calculation failed for {symbol}. ATR likely missing.")
                continue

            # Final validation check (Risk:Reward)
            is_valid, msg = risk_mgr.validate_trade(risk_data)
            if not is_valid:
                logger.info(f"Trade rejected for {symbol}: {msg}")
                continue
            
            signal_data = {
                "symbol": symbol, 
                "side": risk_data["side"], 
                "entry": risk_data["entry"],
                "stop": risk_data["stop"], 
                "tp": risk_data["tp"],
                "score": round(final_score, 2),
                "quantity": risk_data["quantity"]
            }
            
            # Save and Notify
            tracker.log_signal(signal_data)
            notifier.send_signal(signal_data)
            logger.info(f"🚀 FINALIZED SIGNAL: {symbol} Score: {final_score}")
        else:
            logger.info(f"Skipping {symbol}: Consensus Score ({final_score}) below threshold.")

if __name__ == "__main__":
    run_pipeline()
