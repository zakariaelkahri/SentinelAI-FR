# SentinelAI

A complete ML platform with FastAPI backend, React frontend, and integrated MLOps tools.

## Architecture

```
sentinel-ai/
├── backend/          # FastAPI REST API
├── frontend/         # React dashboard
├── airflow/          # DAGs for ML pipelines
├── mlflow/           # Model tracking & registry
├── prometheus/       # Metrics collection
├── grafana/          # Monitoring dashboards
└── docker-compose.yml
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Backend (FastAPI) | 8000 | REST API for predictions |
| Frontend (React) | 3000 | Dashboard UI |
| MLflow | 5000 | Model tracking & registry |
| Airflow | 8080 | Workflow orchestration |
| Grafana | 3001 | Monitoring dashboards |
| Prometheus | 9090 | Metrics collection |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & message broker |

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd sentinel-ai
   ```

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the services:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MLflow: http://localhost:5000
   - Airflow: http://localhost:8080 (admin/admin)
   - Grafana: http://localhost:3001 (admin/admin)
   - Prometheus: http://localhost:9090

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| Airflow | admin | admin |
| Grafana | admin | admin |
| PostgreSQL | postgres | postgres |

## API Endpoints

- `GET /health` - Health check
- `GET /api/v1/models` - List registered models
- `POST /api/v1/predict` - Run prediction on image
- `POST /api/v1/predict/batch` - Batch predictions
- `GET /metrics` - Prometheus metrics

## Airflow DAGs

- `sentinel_model_training` - Daily model training pipeline
- `sentinel_data_pipeline` - Hourly data ingestion pipeline
