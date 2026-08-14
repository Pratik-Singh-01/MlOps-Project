"""
ML Observability Platform - Centralized Configuration

Configuration is loaded from environment variables so the repository can be
published safely without embedding working credentials or local secrets.
"""

import os


APP_ENV: str = os.getenv("APP_ENV", "development")
IS_TEST_ENV: bool = APP_ENV == "test"


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    raise RuntimeError(
        f"{name} must be set. Copy .env.example to .env and provide a real value."
    )


def _required_secret(name: str, test_default: str) -> str:
    if IS_TEST_ENV:
        return os.getenv(name, test_default)
    return _required_env(name)


def _secret_with_dev_default(name: str, dev_default: str, test_default: str) -> str:
    if IS_TEST_ENV:
        return os.getenv(name, test_default)
    if APP_ENV == "development":
        return os.getenv(name, dev_default)
    return _required_env(name)


# DATABASE
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///ml_observability.db",
)


# MODEL
MODEL_PATH: str = os.getenv(
    "MODEL_PATH",
    "saved_models/model.pkl",
)

MODEL_VERSION: str = os.getenv(
    "MODEL_VERSION",
    "v1",
)


# DATA
DATA_PATH: str = os.getenv(
    "DATA_PATH",
    "data/creditcard.csv",
)


# MONITORING THRESHOLDS
CONFIDENCE_THRESHOLD: float = float(
    os.getenv("CONFIDENCE_THRESHOLD", "0.85")
)

FRAUD_RATE_THRESHOLD: float = float(
    os.getenv("FRAUD_RATE_THRESHOLD", "35.0")
)


# MLFLOW
MLFLOW_TRACKING_URI: str = os.getenv(
    "MLFLOW_TRACKING_URI",
    "sqlite:///mlflow.db",
)

MLFLOW_EXPERIMENT_NAME: str = os.getenv(
    "MLFLOW_EXPERIMENT_NAME",
    "Fraud_Detection_Retraining",
)


# AUTH
SECRET_KEY: str = _secret_with_dev_default(
    "SECRET_KEY",
    "local-dev-secret-key-change-me",
    "test-secret-key",
)

ALGORITHM: str = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

ADMIN_USERNAME: str = os.getenv(
    "ADMIN_USERNAME",
    "pratiksingh" if APP_ENV == "development" else "admin",
)
ADMIN_PASSWORD: str = _secret_with_dev_default(
    "ADMIN_PASSWORD",
    "pratik123",
    "admin123",
)

VIEWER_USERNAME: str = os.getenv("VIEWER_USERNAME", "viewer")
VIEWER_PASSWORD: str = _secret_with_dev_default(
    "VIEWER_PASSWORD",
    "viewer123",
    "viewer123",
)

_api_keys = os.getenv("API_KEYS", "test-api-key-001" if IS_TEST_ENV else "")
API_KEYS: list[str] = [key.strip() for key in _api_keys.split(",") if key.strip()]


# APPLICATION
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
