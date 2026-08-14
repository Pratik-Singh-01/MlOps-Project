# ML Observability Platform

FastAPI-based fraud detection service with prediction logging, model monitoring,
drift detection, retraining hooks, Prometheus/Grafana observability, and MLflow
experiment tracking.

## Public Repo Setup

1. Copy `.env.example` to `.env`.
2. Replace every placeholder secret and password in `.env`.
3. Review whether large local artifacts such as `mlruns/`, `mlflow.db`, and
   `saved_models/*.pkl` should stay out of source control for your workflow.
4. Start the stack with `docker compose --env-file .env up --build`.

## Security Notes

- The repository no longer ships usable default secrets.
- Runtime secrets must be provided through environment variables.
- Do not commit `.env`, generated model artifacts, or local experiment data.

## Local Demo Login

- In local `development` mode, the dashboard can use:
- Username: `pratiksingh`
- Password: `pratik123`
- Override these with environment variables before any real deployment.
