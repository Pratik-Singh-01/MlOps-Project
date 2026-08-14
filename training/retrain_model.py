import os
import sys

import joblib
import mlflow
import pandas as pd
from mlflow.sklearn import log_model
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def main():
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)

    print("\n========== RETRAINING PIPELINE ==========\n")

    df = pd.read_csv(config.DATA_PATH)
    X = df.drop("Class", axis=1)
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    with mlflow.start_run():
        model = LogisticRegression(max_iter=5000)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print("\nClassification Report:\n")
        print(classification_report(y_test, y_pred))

        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("max_iter", 5000)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("random_state", 42)

        mlflow.log_metric("accuracy", float(accuracy))
        mlflow.log_metric("precision", float(precision))
        mlflow.log_metric("recall", float(recall))
        mlflow.log_metric("f1_score", float(f1))

        log_model(
            sk_model=model,
            artifact_path="fraud_model",
            registered_model_name="FraudDetectionModel",
        )

        os.makedirs("saved_models", exist_ok=True)
        joblib.dump(model, "saved_models/model_v2.pkl")
        joblib.dump(model, config.MODEL_PATH)

    print("\n========================================")
    print("Retraining Completed Successfully")
    print("========================================")
    print("Model saved locally : saved_models/model_v2.pkl")
    print("Model logged to MLflow")
    print(f"Experiment : {config.MLFLOW_EXPERIMENT_NAME}")


if __name__ == "__main__":
    main()
