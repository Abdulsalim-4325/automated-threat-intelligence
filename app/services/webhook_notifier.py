import httpx
from app.core.config import settings

class WebhookNotifier:
    """Async service for dispatching high-priority threat alerts via Discord Webhooks."""
    
    def __init__(self):
        self.webhook_url = settings.DISCORD_WEBHOOK_URL

    async def send_alert(self, ioc_value: str, ioc_type: str, confidence: int, sources: list):
        """Sends a rich formatted alert to a Discord channel."""
        # Skip if the user hasn't configured a real webhook URL yet
        if not self.webhook_url or "paste_your_" in self.webhook_url:
            print(f"[Webhook] Alert skipped for {ioc_value} (Webhook URL not configured).")
            return

        payload = {
            "content": "🚨 **CRITICAL THREAT DETECTED** 🚨",
            "embeds": [{
                "title": "New High-Confidence Indicator",
                "color": 16711680,  # Hex #FF0000 (Red)
                "fields": [
                    {"name": "IoC Value", "value": f"`{ioc_value}`", "inline": False},
                    {"name": "Type", "value": ioc_type, "inline": True},
                    {"name": "Confidence Score", "value": f"{confidence}/100", "inline": True},
                    {"name": "Corroborated Sources", "value": ", ".join(sources), "inline": False}
                ],
                "footer": {"text": "Automated Threat Intelligence Engine"}
            }]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.webhook_url, json=payload, timeout=10.0)
                response.raise_for_status()
                print(f"[Webhook] Successfully dispatched alert for {ioc_value}")
            except Exception as e:
                print(f"[Webhook] Failed to dispatch alert: {e}")

webhook_notifier = WebhookNotifier()