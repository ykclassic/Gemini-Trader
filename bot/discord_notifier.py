import requests
import os
import logging

logger = logging.getLogger("crypto_bot")

class DiscordNotifier:
    def __init__(self):
        """
        Handles communication with Discord via Webhooks.
        """
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    def send_update(self, message):
        """Sends a plain text message to Discord."""
        if not self.webhook_url:
            logger.warning("Discord Webhook URL not found.")
            return
        payload = {"content": str(message)}
        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")

    def send_signal(self, embed):
        """Sends a rich embed signal to Discord."""
        if not self.webhook_url:
            return
        payload = {"embeds": [embed]}
        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Discord signal delivery failed: {e}")
