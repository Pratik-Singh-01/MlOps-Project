import json
import os
import pandas as pd
from sqlalchemy import create_engine

import config

try:
    from evidently import Report
except ImportError:
    from evidently.report import Report

try:
    from evidently.presets import DataDriftPreset
except ImportError:
    from evidently.metric_preset import DataDriftPreset


engine = create_engine(config.DATABASE_URL)


def check_drift():
    try:
        production_df = pd.read_sql("SELECT * FROM predictions", engine)
    except Exception:
        production_df = pd.DataFrame()

    if production_df.empty:
        print("No production data available.")
        return False

    training_df = pd.read_csv(config.DATA_PATH)
    training_features = training_df.drop(columns=["Class"])

    def extract_features(val):
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except Exception:
                val = {}
        if isinstance(val, dict):
            return val.get("features", [])
        return []

    production_features = pd.DataFrame(
        production_df["input_data"].apply(extract_features).tolist()
    )

    if production_features.empty or production_features.shape[1] != training_features.shape[1]:
        print("Invalid feature matrix for drift comparison.")
        return False

    production_features.columns = training_features.columns

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=training_features, current_data=production_features)
    os.makedirs("monitoring", exist_ok=True)
    report.save_html("monitoring/drift_report.html")

    drift_detected = False
    try:
        if hasattr(report, "as_dict"):
            res_dict = report.as_dict()
            drift_detected = res_dict["metrics"][0]["result"]["dataset_drift"]
        elif hasattr(report, "dict"):
            res_dict = report.dict()
            drift_detected = res_dict["metrics"][0]["result"]["dataset_drift"]
    except Exception as exc:
        print(f"Warning: Failed to extract dataset drift flag: {exc}")

    print("\n==============================")
    print("DRIFT DETECTION REPORT")
    print("==============================")
    print(f"Dataset Drift : {drift_detected}")

    return drift_detected


if __name__ == "__main__":
    check_drift()

