from locust import HttpUser, task, between

class ThreatIntelAnalyst(HttpUser):
    # Simulate a user waiting 1 to 3 seconds between clicks
    wait_time = between(1, 3)

    @task(3)
    def check_health(self):
        """Simulate monitoring dashboards pinging health"""
        self.client.get("/api/v1/health/", name="Health Check")

    @task(2)
    def fetch_stix_bundle(self):
        """Simulate SIEMs pulling the latest threat bundle"""
        self.client.get("/api/v1/stix/bundle", name="Fetch STIX Bundle")