from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
from pyspark.sql import SparkSession

# Add the project root directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.api_client import fetch_weather_data
from scripts.data_transformer import transform_weather_data
from scripts.data_loader import load_data, create_spark_session

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_etl_pipeline',
    default_args=default_args,
    description='A DAG for weather data ETL process using Spark',
    schedule_interval=timedelta(days=1),
)

def etl_process():
    # Create Spark session
    spark = create_spark_session()

    # Extract
    raw_data = fetch_weather_data()
    
    # Transform
    fact_df, dim_df = transform_weather_data(spark, raw_data)
    
    # Load
    load_data(fact_df, dim_df)

    # Stop Spark session
    spark.stop()

with dag:
    etl_task = PythonOperator(
        task_id='weather_etl_process',
        python_callable=etl_process,
    )

etl_task
