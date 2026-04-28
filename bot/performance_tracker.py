import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class PerformanceTracker:
    def __init__(self, db_path="data/signals.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
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
            conn.execute('CREATE TABLE IF NOT EXISTS equity_log (timestamp DATETIME, equity REAL)')

    def log_signal(self, data):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO signals (timestamp, symbol, side, entry_price, stop_loss, take_profit, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), data['symbol'], data['side'], data['entry'], 
                  data['stop'], data['tp'], data['score']))

    def get_pending_signals(self):
        """Returns all signals currently awaiting a price target hit."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM signals WHERE status = 'PENDING'")
            return [dict(row) for row in cursor.fetchall()]

    def update_signal_status(self, signal_id, status, pnl):
        """Closes a signal and updates the equity log for drawdown tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE signals SET status = ?, pnl = ? WHERE id = ?",
                (status, pnl, signal_id)
            )
            # Log new equity state (Assume starting 10,000 + total pnl)
            total_pnl = conn.execute("SELECT SUM(pnl) FROM signals").fetchone()[0] or 0
            conn.execute(
                "INSERT INTO equity_log (timestamp, equity) VALUES (?, ?)",
                (datetime.now(), 10000 + total_pnl)
            )

    def check_weekly_drawdown(self, max_allowed_percent=0.10):
        with sqlite3.connect(self.db_path) as conn:
            one_week_ago = datetime.now() - timedelta(days=7)
            df = pd.read_sql_query("SELECT equity FROM equity_log WHERE timestamp > ?", 
                                   conn, params=(one_week_ago,))
            if df.empty or len(df) < 2: return False
            peak = df['equity'].max()
            current = df['equity'].iloc[-1]
            return ((peak - current) / peak) >= max_allowed_percent
