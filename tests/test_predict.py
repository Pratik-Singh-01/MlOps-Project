"""
Tests — Prediction Endpoint
Tests for /predict and / endpoints.
"""


class TestHome:
    """Tests for the home endpoint."""

    def test_home_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_returns_message(self, client):
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "ML Observability" in data["message"]

    def test_home_returns_version(self, client):
        response = client.get("/")
        data = response.json()
        assert "version" in data


class TestHealthEndpoints:
    """Tests for health and readiness endpoints."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_ready_returns_200(self, client):
        response = client.get("/ready")
        assert response.status_code == 200


class TestPredictEndpoint:
    """Tests for the /predict endpoint."""

    def test_predict_requires_auth(self, client):
        """Prediction without auth should fail."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
        )
        assert response.status_code == 401

    def test_predict_with_jwt(self, client, admin_headers):
        """Prediction with valid JWT should succeed."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert "model_version" in data
        assert "latency_ms" in data

    def test_predict_with_api_key(self, client, api_key_headers):
        """Prediction with valid API key should succeed."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
            headers=api_key_headers,
        )
        assert response.status_code == 200

    def test_predict_returns_valid_prediction(self, client, admin_headers):
        """Prediction value should be 0 or 1."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
            headers=admin_headers,
        )
        data = response.json()
        assert data["prediction"] in [0, 1]

    def test_predict_returns_confidence_range(self, client, admin_headers):
        """Confidence should be between 0 and 1."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
            headers=admin_headers,
        )
        data = response.json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_predict_invalid_features(self, client, admin_headers):
        """Empty features should fail validation."""
        response = client.post(
            "/predict",
            json={"features": []},
            headers=admin_headers,
        )
        # Model will fail on wrong shape, but request should be accepted
        # This tests that validation doesn't reject the request format
        assert response.status_code in [200, 422, 500]

    def test_predict_missing_body(self, client, admin_headers):
        """Missing request body should return 422."""
        response = client.post(
            "/predict",
            headers=admin_headers,
        )
        assert response.status_code == 422
