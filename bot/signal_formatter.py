class SignalFormatter:
    [span_15](start_span)"""[span_15](end_span)"""
    @staticmethod
    def format_discord_embed(data):
        return {
            "title": f"🔔 {data['symbol']} | {data['side']} | {data['timeframe']}",
            "fields": [
                {"name": "📍 Entry Zone", "value": f"${data['entry']}", "inline": True},
                {"name": "🛑 Stop Loss", "value": f"${data['stop']}", "inline": True},
                {"name": "🧠 Confidence", "value": f"{data['score']} / 10", "inline": False}
            ],
            "color": 3066993 if data['side'] == "LONG" else 15158332
        }
