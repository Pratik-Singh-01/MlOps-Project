from prometheus_client import Counter, Gauge, Info

# Total fraud predictions made
fraud_predictions_total = Counter(
    "fraud_predictions_total",
    "Total number of fraud predictions"
)

# Average confidence of the latest prediction
prediction_confidence = Gauge(
    "prediction_confidence",
    "Confidence score of the latest prediction"
)

# Whether drift is currently detected
data_drift_status = Gauge(
    "data_drift_status",
    "1 if drift detected, otherwise 0"
)

# Number of retraining events
model_retraining_total = Counter(
    "model_retraining_total",
    "Total number of model retraining events"
)

# Active model version
model_info = Info(
    "model",
    "Current deployed model"
)