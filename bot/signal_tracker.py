import logging
from bot.data_fetcher import DataFetcher
from bot.performance_tracker import PerformanceTracker
from bot.discord_notifier import DiscordNotifier

logger = logging.getLogger("crypto_bot")

class SignalTracker:
    """
    Monitors 'PENDING' signals by comparing live market data against TP/SL levels.
    """
    def __init__(self):
        self.fetcher = DataFetcher()
        self.tracker = PerformanceTracker()
        self.notifier = DiscordNotifier()

    def check_active_signals(self):
        """Processes all pending signals and updates their status based on price action."""
        pending_signals = self.tracker.get_pending_signals()
        
        if not pending_signals:
            logger.info("No active signals to track.")
            return

        # Group by symbol to minimize API calls
        symbols = list(set([s['symbol'] for s in pending_signals]))
        current_prices = {}
        
        for symbol in symbols:
            try:
                # Fetch latest ticker for the most recent price
                ticker = self.fetcher.exchange.fetch_ticker(symbol)
                current_prices[symbol] = ticker['last']
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")

        for signal in pending_signals:
            symbol = signal['symbol']
            if symbol not in current_prices:
                continue

            price = current_prices[symbol]
            side = signal['side']
            tp = signal['take_profit']
            sl = signal['stop_loss']
            
            outcome = None
            pnl = 0.0

            if side == "LONG":
                if price >= tp:
                    outcome = "HIT_TP"
                    pnl = abs(tp - signal['entry_price'])
                elif price <= sl:
                    outcome = "HIT_SL"
                    pnl = -abs(signal['entry_price'] - sl)
            
            elif side == "SHORT":
                if price <= tp:
                    outcome = "HIT_TP"
                    pnl = abs(signal['entry_price'] - tp)
                elif price >= sl:
                    outcome = "HIT_SL"
                    pnl = -abs(sl - signal['entry_price'])

            if outcome:
                self.tracker.update_signal_status(signal['id'], outcome, pnl)
                self.notifier.send_update(
                    f"✅ {symbol} {outcome}! | PnL: {pnl:.2f} | Current Price: {price}"
                )
                logger.info(f"Signal {signal['id']} ({symbol}) closed with {outcome}")
