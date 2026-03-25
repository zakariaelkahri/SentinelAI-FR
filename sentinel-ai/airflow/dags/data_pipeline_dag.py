"""
SentinelAI Data Pipeline DAG

This DAG handles data ingestion and preprocessing:
1. Fetch new data
2. Validate data quality
3. Store processed data
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'sentinelai',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}


def fetch_data(**context):
    """Fetch new data from sources."""
    import logging
    logging.info("Fetching new data...")
    return {"status": "fetched", "count": 500}


def validate_data(**context):
    """Validate data quality."""
    import logging
    logging.info("Validating data quality...")
    return {"status": "validated", "valid_records": 495}


def process_data(**context):
    """Process and transform data."""
    import logging
    logging.info("Processing data...")
    return {"status": "processed"}


def store_data(**context):
    """Store processed data."""
    import logging
    logging.info("Storing processed data...")
    return {"status": "stored"}


with DAG(
    'sentinel_data_pipeline',
    default_args=default_args,
    description='SentinelAI Data Ingestion Pipeline',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data', 'pipeline', 'sentinel'],
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data,
    )

    validate_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    process_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )

    store_task = PythonOperator(
        task_id='store_data',
        python_callable=store_data,
    )

    fetch_task >> validate_task >> process_task >> store_task
