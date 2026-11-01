from typing import List, Dict, Any
from app.collectors.base import BaseCollector
from app.core.config import settings

class ThreatFoxCollector(BaseCollector):
    """Fetches recent malware hashes, URLs, and C2 IPs from abuse.ch ThreatFox."""
    
    def __init__(self):
        super().__init__(api_key=settings.THREATFOX_API_KEY)
        self.headers["Auth-Key"] = self.api_key

    async def get_recent_iocs(self) -> List[Dict[str, Any]]:
        """Retrieves IoCs added in the last 24 hours."""
        url = "https://threatfox-api.abuse.ch/api/v1/"
        payload = {"query": "get_iocs", "days": 1}
        
        try:
            data = await self.fetch_json(url, method="POST", json=payload)
            iocs = []
            for item in data.get("data", []):
                # Map ThreatFox types to STIX types
                raw_type = item.get("ioc_type")
                if raw_type == "url":
                    ioc_type = "url"
                elif raw_type == "ipv4:port":
                    ioc_type = "ipv4-addr"
                elif raw_type == "sha256_hash":
                    ioc_type = "file:hashes.'SHA-256'"
                else:
                    continue  # Skip unsupported types
                
                # Strip port numbers from IPs (e.g., "192.168.1.1:80" -> "192.168.1.1")
                ioc_value = item["ioc"].split(":")[0] if ioc_type == "ipv4-addr" else item["ioc"]
                
                iocs.append({
                    "ioc_value": ioc_value,
                    "ioc_type": ioc_type,
                    "confidence": item.get("confidence_level", 75),
                    "source": "ThreatFox"
                })
            return iocs
        except Exception as e:
            print(f"[ThreatFox] Collection failed: {e}")
            return []