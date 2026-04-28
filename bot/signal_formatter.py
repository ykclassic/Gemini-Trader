class SignalFormatter:
    def __init__(self):
        """
        Prepares and cleans trade data for Discord visualization.
        """
        pass

    @staticmethod
    def format_discord_embed(data):
        """
        Creates a structured dictionary for the Discord Webhook payload.
        """
        symbol = data.get('symbol', 'Unknown')
        side = data.get('side', 'N/A')
        score = data.get('score', 0.0)
        
        # 3066993 is a green-ish color, 15158332 is a red-ish color
        color = 3066993 if side == "LONG" else 15158332
        
        embed = {
            "title": f"🚀 NEW SIGNAL: {symbol} ({side})",
            "description": f"The engine has reached a consensus score of **{score}/10**.",
            "color": color,
            "fields": [
                {"name": "Entry Price", "value": f"${data.get('entry', 0):,.2f}", "inline": True},
                {"name": "Stop Loss", "value": f"${data.get('stop', 0):,.2f}", "inline": True},
                {"name": "Take Profit", "value": f"${data.get('tp', 0):,.2f}", "inline": True}
            ],
            "footer": {"text": "Gemini-Trader | Unified Intelligence Engine"}
        }
        return embed
