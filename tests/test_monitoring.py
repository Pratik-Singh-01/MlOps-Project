"""
Tests — Monitoring & Alerts
Tests for /model-metrics and /webhooks/alerts endpoints.
"""


class TestModelMetrics:
    """Tests for /model-metrics endpoint."""

    def test_metrics_requires_auth(self, client):
        """Metrics without auth should fail."""
        response = client.get("/model-metrics")
        assert response.status_code == 401

    def test_metrics_with_auth(self, client, admin_headers):
        """Metrics with auth should succeed."""
        response = client.get("/model-metrics", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data

    def test_metrics_structure(self, client, admin_headers):
        """Metrics response should have expected fields."""
        response = client.get("/model-metrics", headers=admin_headers)
        metrics = response.json()["metrics"]
        assert "total_predictions" in metrics
        assert "avg_confidence" in metrics
        assert "avg_latency_ms" in metrics
        assert "fraud_rate" in metrics

    def test_metrics_with_api_key(self, client, api_key_headers):
        """Viewers can access metrics."""
        response = client.get("/model-metrics", headers=api_key_headers)
        assert response.status_code == 200


class TestAlertWebhook:
    """Tests for /webhooks/alerts endpoint."""

    def test_webhook_receives_alerts(self, client):
        """Webhook should accept alert payloads."""
        payload = {
            "alerts": [
                {
                    "status": "firing",
                    "labels": {
                        "alertname": "HighFraudRate",
                        "severity": "critical",
                    },
                    "annotations": {
                        "summary": "Fraud rate exceeded threshold",
                    },
                }
            ]
        }
        response = client.post("/webhooks/alerts", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["alerts_processed"] == 1

    def test_webhook_empty_alerts(self, client):
        """Webhook should handle empty alerts."""
        response = client.post(
            "/webhooks/alerts",
            json={"alerts": []},
        )
        assert response.status_code == 200
        assert response.json()["alerts_processed"] == 0

    def test_webhook_multiple_alerts(self, client):
        """Webhook should handle multiple alerts."""
        payload = {
            "alerts": [
                {
                    "status": "firing",
                    "labels": {"alertname": "A", "severity": "critical"},
                    "annotations": {"summary": "Alert A"},
                },
                {
                    "status": "resolved",
                    "labels": {"alertname": "B", "severity": "warning"},
                    "annotations": {"summary": "Alert B"},
                },
            ]
        }
        response = client.post("/webhooks/alerts", json=payload)
        assert response.status_code == 200
        assert response.json()["alerts_processed"] == 2
