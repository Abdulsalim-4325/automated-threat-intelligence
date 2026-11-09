import httpx

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Verify the API, Postgres, and Redis are all healthy."""
    response = httpx.get(f"{BASE_URL}/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data["checks"]
    assert "redis" in data["checks"]

def test_stix_bundle_generation():
    """Verify the STIX engine correctly formats the database records."""
    response = httpx.get(f"{BASE_URL}/api/v1/stix/bundle?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    # Assert STIX 2.1 Compliance
    assert data["type"] == "bundle"
    assert str(data["id"]).startswith("bundle--")
    assert isinstance(data["objects"], list)

def test_batch_import_validation():
    """Verify the API rejects invalid indicator payloads."""
    bad_payload = [{"ioc_type": "invalid-type", "ioc_value": "127.0.0.1"}]
    response = httpx.post(f"{BASE_URL}/api/v1/indicators/import", json=bad_payload)
    # Should fail Pydantic validation (422 Unprocessable Entity)
    assert response.status_code == 422