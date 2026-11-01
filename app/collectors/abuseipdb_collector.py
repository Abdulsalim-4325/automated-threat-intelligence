from typing import List, Dict, Any
from app.collectors.base import BaseCollector
from app.core.config import settings

class AbuseIPDBCollector(BaseCollector):
    """Fetches high-confidence malicious IPs from AbuseIPDB."""
    
    def __init__(self):
        super().__init__(api_key=settings.ABUSEIPDB_API_KEY)
        self.headers["Key"] = self.api_key
        self.headers["Accept"] = "application/json"

    async def get_blacklist(self) -> List[Dict[str, Any]]:
        """Retrieves the daily blacklist and formats it for STIX normalization."""
        url = "https://api.abuseipdb.com/api/v2/blacklist"
        # Only pull IPs with a confidence score of 75 or higher
        params = {"confidenceMinimum": 75, "limit": 1000}
        
        try:
            data = await self.fetch_json(url, params=params)
            iocs = []
            for item in data.get("data", []):
                iocs.append({
                    "ioc_value": item["ipAddress"],
                    "ioc_type": "ipv4-addr",
                    "confidence": item["abuseConfidenceScore"],
                    "source": "AbuseIPDB"
                })
            return iocs
        except Exception as e:
            print(f"[AbuseIPDB] Collection failed: {e}")
            return []