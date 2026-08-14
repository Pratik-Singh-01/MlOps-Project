import pandas as pd
from sqlalchemy import create_engine

import config


engine = create_engine(config.DATABASE_URL)


def compute_metrics() -> dict:
    try:
        df = pd.read_sql("SELECT * FROM predictions", engine)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        return {
            "total_predictions": 0,
            "avg_confidence": 0.0,
            "avg_latency_ms": 0.0,
            "prediction_distribution": {},
            "fraud_rate": 0.0,
        }

    prediction_counts = df["prediction"].value_counts().to_dict()
    fraud_rate = float((df["prediction"].astype(str) == "1").mean() * 100)

    return {
        "total_predictions": len(df),
        "avg_confidence": round(float(df["confidence"].mean()), 4),
        "avg_latency_ms": round(float(df["latency_ms"].mean()), 2),
        "prediction_distribution": prediction_counts,
        "fraud_rate": round(fraud_rate, 2),
    }


if __name__ == "__main__":
    print(compute_metrics())

