import json
from app.normalizer.stix_mapper import STIXMapper

def test_generate_deterministic_id():
    """Verify that identical IoCs generate the exact same UUIDv5 STIX ID."""
    ip = "198.51.100.42"
    id_1 = STIXMapper.generate_deterministic_id("ipv4-addr", ip)
    id_2 = STIXMapper.generate_deterministic_id("ipv4-addr", ip)
    id_diff = STIXMapper.generate_deterministic_id("ipv4-addr", "198.51.100.43")

    assert id_1 == id_2
    assert id_1.startswith("indicator--")
    assert id_1 != id_diff

def test_map_ip_to_indicator():
    """Verify an IPv4 address generates a spec-compliant STIX 2.1 JSON string."""
    ip = "203.0.113.1"
    raw_json = STIXMapper.map_ip_to_indicator(ip, confidence=85, source="Test Source")
    
    # Parse back to dict to inspect structure
    indicator_dict = json.loads(raw_json)
    
    assert indicator_dict["type"] == "indicator"
    assert indicator_dict["spec_version"] == "2.1"
    assert "203.0.113.1" in indicator_dict["pattern"]
    assert indicator_dict["confidence"] == 85

def test_map_hash_to_indicator():
    """Verify SHA-256 hash formatting and labels."""
    sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    raw_json = STIXMapper.map_hash_to_indicator(sha256, confidence=90, source="ThreatFox")
    
    indicator_dict = json.loads(raw_json)
    assert "file:hashes.'SHA-256'" in indicator_dict["pattern"]
    assert "malware-hash" in indicator_dict["labels"]