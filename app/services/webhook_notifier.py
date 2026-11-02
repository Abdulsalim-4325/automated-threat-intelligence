import httpx
import json
from typing import Optional
from app.core.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebhookNotifier:
    def __init__(self):
        self.discord_webhook = settings.DISCORD_WEBHOOK_URL
        self.slack_webhook = settings.SLACK_WEBHOOK_URL
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=5)
        )

    async def send_critical_alert(
        self, 
        ioc_value: str, 
        ioc_type: str, 
        confidence_score: int,
        is_new: bool = False
    ):
        """Send webhook alert for new or critical indicators (non-blocking)"""
        try:
            title = "🚨 New Critical IoC Detected" if is_new else "⚠️ Critical IoC Threshold Reached"
            
            discord_embed = {
                "title": title,
                "color": 0xFF0000 if is_new else 0xFFA500,  # Red for new, Orange for threshold
                "fields": [
                    {
                        "name": "IoC Value",
                        "value": f"`{ioc_value}`",
                        "inline": False
                    },
                    {
                        "name": "Type",
                        "value": ioc_type,
                        "inline": True
                    },
                    {
                        "name": "Confidence Score",
                        "value": f"{confidence_score}/100",
                        "inline": True
                    },
                    {
                        "name": "Status",
                        "value": "New Indicator" if is_new else "Threshold Crossed",
                        "inline": True
                    },
                    {
                        "name": "Timestamp",
                        "value": datetime.utcnow().isoformat() + "Z",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Threat Intelligence Aggregator"
                }
            }

            # Slack format
            slack_payload = {
                "text": f"{title}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": title
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*IoC Value:*\n`{ioc_value}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Type:*\n{ioc_type}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Confidence:*\n{confidence_score}/100"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Status:*\n{'New' if is_new else 'Threshold Crossed'}"
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Timestamp: {datetime.utcnow().isoformat()}Z"
                            }
                        ]
                    }
                ]
            }

            if self.discord_webhook:
                await self.client.post(
                    self.discord_webhook,
                    json={"embeds": [discord_embed]},
                    headers={"Content-Type": "application/json"}
                )

            if self.slack_webhook:
                await self.client.post(
                    self.slack_webhook,
                    json=slack_payload,
                    headers={"Content-Type": "application/json"}
                )

            logger.info(f"Webhook alert sent for {ioc_type}: {ioc_value}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


webhook_notifier = WebhookNotifier()