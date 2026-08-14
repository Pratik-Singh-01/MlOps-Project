from monitoring.decision_engine import evaluate_model

from app.prometheus_metrics import (
    data_drift_status,
    model_retraining_total
)


def run_monitoring():

    result = evaluate_model()

    if not isinstance(result, dict):
        return result

    # Update Prometheus Metrics
    data_drift_status.set(
        1 if result["drift_detected"] else 0
    )

    if result["retraining_triggered"]:
        model_retraining_total.inc()

    return result