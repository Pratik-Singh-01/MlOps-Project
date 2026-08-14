import logging
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

import config
from app.auth import (
    TokenRequest,
    TokenResponse,
    UserInfo,
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
)
from app.database import SessionLocal, engine
from app.logging_config import setup_logging
from app.model_loader import model
from app.models import Base, PredictionLog
from app.predict import make_prediction
from app.prometheus_metrics import (
    fraud_predictions_total,
    model_info,
    prediction_confidence,
)
from app.schemas import PredictionRequest, PredictionResponse
from monitoring.metrics import compute_metrics
from monitoring.monitoring_service import run_monitoring


setup_logging()
logger = logging.getLogger("ml_observability")

app = FastAPI(
    title="ML Observability Platform",
    description="Fraud Detection API with monitoring and automated retraining",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)
Base.metadata.create_all(bind=engine)
dashboard_path = Path(__file__).with_name("static") / "index.html"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["General"])
def home():
    return {
        "message": "ML Observability Platform - Fraud Detection API",
        "version": config.MODEL_VERSION,
        "docs": "/docs",
        "dashboard": "/dashboard",
    }


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(dashboard_path)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "ml-observability-platform",
        "version": config.MODEL_VERSION,
    }


@app.get("/ready", tags=["Health"])
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "database": db_status,
        "model_loaded": model is not None,
    }


@app.post("/auth/token", response_model=TokenResponse, tags=["Auth"])
def login(request: TokenRequest):
    user = authenticate_user(request.username, request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(username=user["username"], role=user["role"])
    return TokenResponse(
        access_token=token,
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user["role"],
    )


@app.get("/auth/me", tags=["Auth"])
def get_authenticated_user(user: UserInfo = Depends(get_current_user)):
    return {
        "username": user.username,
        "role": user.role,
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
def predict(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    user: UserInfo = Depends(get_current_user),
):
    start_time = time.time()
    prediction, confidence = make_prediction(model, request.features)
    latency_ms = (time.time() - start_time) * 1000

    prediction_confidence.set(confidence)
    if prediction == 1:
        fraud_predictions_total.inc()
    model_info.info({"version": config.MODEL_VERSION})

    log = PredictionLog(
        input_data={"features": request.features},
        prediction=str(prediction),
        confidence=float(confidence),
        latency_ms=float(latency_ms),
        model_version=config.MODEL_VERSION,
    )
    db.add(log)
    db.commit()

    logger.info(
        "Prediction completed",
        extra={
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "latency_ms": round(latency_ms, 2),
            "user": user.username,
        },
    )

    return PredictionResponse(
        prediction=prediction,
        confidence=round(confidence, 4),
        model_version=config.MODEL_VERSION,
        latency_ms=round(latency_ms, 2),
    )


@app.post("/run-monitoring", tags=["Monitoring"])
def trigger_monitoring(user: UserInfo = Depends(require_admin)):
    try:
        result = run_monitoring()
        logger.info("Monitoring completed", extra={"user": user.username, "result": result})
        return {
            "status": "success",
            "monitoring": result,
            "triggered_by": user.username,
        }
    except Exception as exc:
        logger.error("Monitoring failed", extra={"error": str(exc), "user": user.username})
        return {
            "status": "failed",
            "error": str(exc),
        }


@app.get("/model-metrics", tags=["Monitoring"])
def get_model_metrics(user: UserInfo = Depends(get_current_user)):
    return {
        "status": "success",
        "metrics": compute_metrics(),
        "requested_by": user.username,
    }


@app.get("/predictions/recent", tags=["Predictions"])
def get_recent_predictions(
    limit: int = 10,
    db: Session = Depends(get_db),
    user: UserInfo = Depends(get_current_user),
):
    safe_limit = max(1, min(limit, 50))
    rows = (
        db.query(PredictionLog)
        .order_by(PredictionLog.created_at.desc())
        .limit(safe_limit)
        .all()
    )

    return {
        "status": "success",
        "requested_by": user.username,
        "predictions": [
            {
                "id": row.id,
                "prediction": row.prediction,
                "confidence": round(float(row.confidence), 4),
                "latency_ms": round(float(row.latency_ms), 2),
                "model_version": row.model_version,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "feature_count": len(row.input_data.get("features", [])) if row.input_data else 0,
            }
            for row in rows
        ],
    }


@app.post("/webhooks/alerts", tags=["Alerts"])
async def receive_alert(alert_data: dict):
    alerts = alert_data.get("alerts", [])
    for alert in alerts:
        logger.warning(
            "Alert received",
            extra={
                "status": alert.get("status", "unknown"),
                "severity": alert.get("labels", {}).get("severity", "unknown"),
                "alertname": alert.get("labels", {}).get("alertname", "unknown"),
                "summary": alert.get("annotations", {}).get("summary", "N/A"),
            },
        )

    return {
        "status": "received",
        "alerts_processed": len(alerts),
    }
