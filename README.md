# Gemini-Trader: Unified Intelligence Engine

A production-grade, multi-asset quantitative trading pipeline built for automated market analysis and signal generation. This bot implements the **Super Joint Blueprint**, utilizing a layered approach of technical indicators, consensus scoring, and risk management.

## 🚀 Features

- **Multi-Exchange Integration:** Currently optimized for KuCoin to bypass regional cloud restrictions (Binance/Bybit block GitHub Actions IPs).
- **Layered Indicator Engine:** Calculates 40+ indicators across Trend, Momentum, Volatility, and Volume layers.
- **Consensus Scoring:** Aggregates strategy results into a 0-10 confidence score; only signals with a score >= 7.0 are dispatched.
- **Automated Risk Management:** Implements a strict 1.5% capital risk per trade and a 1:2 Risk/Reward ratio.
- **Discord Integration:** Real-time signal delivery with rich embeds and performance updates.
- **GitHub Actions Ready:** Designed for headless execution on a scheduled cron job.

## 🛠 Project Structure

```text
Gemini-Trader/
├── .github/workflows/   # CI/CD and Automation schedules
├── bot/                 # Core Engine Modules
│   ├── main.py          # Pipeline entry point
│   ├── data_fetcher.py  # Exchange connectivity (KuCoin)
│   ├── indicator_engine.py
│   ├── strategy_engine.py
│   ├── consensus_scorer.py
│   ├── risk_manager.py
│   ├── signal_formatter.py
│   └── performance_tracker.py
├── config/
│   └── settings.yaml    # Indicator and Risk thresholds
├── data/                # SQLite Database persistence
├── requirements.txt
└── .env                 # Local environment variables
