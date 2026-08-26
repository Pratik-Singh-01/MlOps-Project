import subprocess
import sys

import pandas as pd

import config
from app.database import engine
from monitoring.drift_check import check_drift


def evaluate_model():
    try:
        df = pd.read_sql("SELECT * FROM predictions", engine)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        print("No prediction logs available.")
        return {
            "drift_detected": False,
            "retraining_triggered": False,
            "avg_confidence": 0,
            "fraud_rate": 0,
        }

    df["prediction"] = pd.to_numeric(df["prediction"])
    avg_confidence = df["confidence"].mean()
    fraud_rate = ((df["prediction"] == 1).sum() / len(df)) * 100
    drift_detected = check_drift()

    retrain_required = False
    reasons = []

    if avg_confidence < config.CONFIDENCE_THRESHOLD:
        retrain_required = True
        reasons.append("Low Confidence")
    if fraud_rate > config.FRAUD_RATE_THRESHOLD:
        retrain_required = True
        reasons.append("High Fraud Rate")
    if drift_detected:
        retrain_required = True
        reasons.append("Data Drift Detected")

    print("\n=========================")
    print("MODEL HEALTH REPORT")
    print("=========================\n")
    print(f"Drift Detected     : {drift_detected}")
    print(f"Average Confidence : {avg_confidence:.4f}")
    print(f"Fraud Rate         : {fraud_rate:.2f}%")
    print("\nDecision:")

    if retrain_required:
        print("RETRAIN REQUIRED")
        print("\nReasons:")
        for reason in reasons:
            print(f" - {reason}")
        print("\nStarting Retraining Pipeline...\n")

        result = subprocess.run(
            [sys.executable, "training/retrain_model.py"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise RuntimeError(result.stderr)

        print("\nRetraining Finished Successfully.")
        return {
            "drift_detected": drift_detected,
            "retraining_triggered": True,
            "avg_confidence": round(avg_confidence, 4),
            "fraud_rate": round(fraud_rate, 2),
        }

    print("MODEL HEALTHY")
    return {
        "drift_detected": drift_detected,
        "retraining_triggered": False,
        "avg_confidence": round(avg_confidence, 4),
        "fraud_rate": round(fraud_rate, 2),
    }


if __name__ == "__main__":
    print(evaluate_model())
