# Monitoring Stack

This project ships with Prometheus + Grafana + MLflow preconfigured.

## Access URLs

- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- MLflow: http://localhost:5000
- Backend metrics endpoint: http://localhost:8000/metrics

## Grafana Login

- Username: `admin`
- Password: `admin`

## What Is Preconfigured

- Prometheus scrapes:
  - `prometheus:9090`
  - `backend:8000/metrics`
- Prometheus alert rules:
  - `monitoring/prometheus/rules/rag-alerts.yml`
  - Alerts for RAG p95 latency and RAG error rate (warning + critical)
- Grafana datasource:
  - Prometheus (`uid=prometheus`)
- Grafana dashboard:
  - `SentinelAI RAG Overview` in folder `SentinelAI`
- MLflow:
  - Tracking server with SQLite backend (`/mlflow/mlflow.db`)
  - Artifacts stored under `/mlflow/artifacts`
