"""
Tests — Authentication & Authorization
Tests for JWT tokens, API keys, and role-based access.
"""


class TestTokenEndpoint:
    """Tests for /auth/token."""

    def test_login_valid_admin(self, client):
        """Admin login should return a token."""
        response = client.post(
            "/auth/token",
            json={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"

    def test_login_valid_viewer(self, client):
        """Viewer login should return a token with viewer role."""
        response = client.post(
            "/auth/token",
            json={"username": "viewer", "password": "viewer123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "viewer"

    def test_login_invalid_password(self, client):
        """Wrong password should return 401."""
        response = client.post(
            "/auth/token",
            json={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_login_invalid_username(self, client):
        """Unknown username should return 401."""
        response = client.post(
            "/auth/token",
            json={"username": "unknown", "password": "test"},
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        """Missing fields should return 422."""
        response = client.post(
            "/auth/token",
            json={},
        )
        assert response.status_code == 422


class TestAPIKeyAuth:
    """Tests for API Key authentication."""

    def test_valid_api_key(self, client, api_key_headers):
        """Valid API key should allow access."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
            headers=api_key_headers,
        )
        assert response.status_code == 200

    def test_invalid_api_key(self, client):
        """Invalid API key should return 401."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
            headers={"X-API-Key": "invalid-key"},
        )
        assert response.status_code == 401


class TestRoleBasedAccess:
    """Tests for admin vs viewer access control."""

    def test_viewer_cannot_trigger_monitoring(self, client, viewer_headers):
        """Viewers should not be able to trigger monitoring."""
        response = client.post(
            "/run-monitoring",
            headers=viewer_headers,
        )
        assert response.status_code == 403

    def test_api_key_cannot_trigger_monitoring(self, client, api_key_headers):
        """API key users (viewer role) cannot trigger monitoring."""
        response = client.post(
            "/run-monitoring",
            headers=api_key_headers,
        )
        assert response.status_code == 403

    def test_no_auth_returns_401(self, client):
        """No authentication should return 401."""
        response = client.post("/predict", json={"features": [0.0] * 30})
        assert response.status_code == 401

    def test_expired_token_returns_401(self, client):
        """Expired/invalid token should return 401."""
        response = client.post(
            "/predict",
            json={"features": [0.0] * 30},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401
