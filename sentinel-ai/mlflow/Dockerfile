# MLflow Dockerfile
FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir \
    mlflow==2.10.0 \
    psycopg2-binary==2.9.9 \
    boto3==1.34.0

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "postgresql://postgres:postgres@db:5432/mlflow", \
     "--default-artifact-root", "/mlflow/artifacts"]
