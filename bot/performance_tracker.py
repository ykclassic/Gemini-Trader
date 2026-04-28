import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class PerformanceTracker:
    """
    Handles performance auditing and the 10% weekly drawdown circuit breaker.
    """
    def __init__(self, db_path="data/signals.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Creates tables for signals and performance tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    symbol TEXT,
                    side TEXT,
                    entry_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    score REAL,
                    status TEXT DEFAULT 'PENDING',
                    pnl REAL DEFAULT 0.0
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS equity_log (
                    timestamp DATETIME,
                    equity REAL
                )
            ''')

    def log_signal(self, data):
        """Logs a new signal to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO signals (timestamp, symbol, side, entry_price, stop_loss, take_profit, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), data['symbol'], data['side'], data['entry'], 
                  data['stop'], data['tp'], data['score']))

    def check_weekly_drawdown(self, max_allowed_percent=0.10):
        """
        Calculates drawdown over the last 7 days. 
        Returns True if the circuit breaker is triggered.
        """
        with sqlite3.connect(self.db_path) as conn:
            one_week_ago = datetime.now() - timedelta(days=7)
            df = pd.read_sql_query(
                "SELECT equity FROM equity_log WHERE timestamp > ?", 
                conn, params=(one_week_ago,)
            )
            
            if df.empty or len(df) < 2:
                return False

            peak = df['equity'].max()
            current = df['equity'].iloc[-1]
            drawdown = (peak - current) / peak
            
            return drawdown >= max_allowed_percent

    def get_stats(self):
        """Aggregates win rate and total PnL for the Discord formatter."""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM signals WHERE status = 'CLOSED'", conn)
            if df.empty:
                return {"win_rate": 0, "total_pnl": 0}
            
            wins = len(df[df['pnl'] > 0])
            total = len(df)
            return {
                "win_rate": (wins / total) * 100,
                "total_pnl": df['pnl'].sum()
            }
