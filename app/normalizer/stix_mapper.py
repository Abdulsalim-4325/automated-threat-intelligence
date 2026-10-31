# app/normalizer/stix_mapper.py
import uuid
from typing import Dict, Any, List
from stix2 import Indicator, Bundle

# OASIS STIX deterministic namespace UUID for custom indicator generation
STIX_NAMESPACE = uuid.UUID("00abedb4-aa42-466c-9c01-fed23315a9b7")

class STIXMapper:
    """Translates heterogeneous OSINT indicators into validated OASIS STIX 2.1 JSON bundles."""

    @staticmethod
    def generate_deterministic_id(ioc_type: str, ioc_value: str) -> str:
        """Generates a stable UUIDv5 for an indicator based on its type and value."""
        unique_string = f"{ioc_type}--{ioc_value.lower().strip()}"
        generated_uuid = uuid.uuid5(STIX_NAMESPACE, unique_string)
        return f"indicator--{generated_uuid}"

    @classmethod
    def map_ip_to_indicator(
        cls, ip_address: str, confidence: int, source: str, labels: List[str] = None
    ) -> Dict[str, Any]:
        """Maps an IPv4 address to a STIX 2.1 Indicator SDO."""
        if labels is None:
            labels = ["malicious-activity", "ip-reputation"]

        stix_id = cls.generate_deterministic_id("ipv4-addr", ip_address)
        
        indicator = Indicator(
            id=stix_id,
            spec_version="2.1",
            pattern=f"[ipv4-addr:value = '{ip_address.strip()}']",
            pattern_type="stix",
            valid_from="2026-01-01T00:00:00.000Z",
            confidence=max(0, min(100, confidence)),
            labels=labels,
            description=f"Automated threat intelligence sighting from {source}"
        )
        return indicator.serialize(pretty=True)

    @classmethod
    def map_url_to_indicator(cls, url_value: str, confidence: int, source: str) -> Dict[str, Any]:
        """Maps a malicious URL to a STIX 2.1 Indicator SDO."""
        stix_id = cls.generate_deterministic_id("url", url_value)
        
        indicator = Indicator(
            id=stix_id,
            spec_version="2.1",
            pattern=f"[url:value = '{url_value.strip()}']",
            pattern_type="stix",
            valid_from="2026-01-01T00:00:00.000Z",
            confidence=max(0, min(100, confidence)),
            labels=["malicious-activity", "url-watch"],
            description=f"Malicious C2 URL feed ingested from {source}"
        )
        return indicator.serialize(pretty=True)

    @classmethod
    def map_hash_to_indicator(cls, sha256_hash: str, confidence: int, source: str) -> Dict[str, Any]:
        """Maps a file SHA-256 hash to a STIX 2.1 Indicator SDO."""
        stix_id = cls.generate_deterministic_id("file", sha256_hash)
        
        indicator = Indicator(
            id=stix_id,
            spec_version="2.1",
            pattern=f"[file:hashes.'SHA-256' = '{sha256_hash.strip().lower()}']",
            pattern_type="stix",
            valid_from="2026-01-01T00:00:00.000Z",
            confidence=max(0, min(100, confidence)),
            labels=["malicious-artifact", "malware-hash"],
            description=f"Malware sample hash ingested from {source}"
        )
        return indicator.serialize(pretty=True)

    @staticmethod
    def create_bundle(indicators: List[Dict[str, Any]]) -> str:
        """Wraps multiple STIX objects into a standardized STIX 2.1 Bundle JSON string."""
        objects = [Indicator(json_stix) for json_stix in indicators]
        bundle = Bundle(objects=objects, allow_custom=True)
        return bundle.serialize(pretty=True)