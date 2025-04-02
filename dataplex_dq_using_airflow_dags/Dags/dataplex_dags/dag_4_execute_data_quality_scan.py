from airflow import DAG
from airflow.providers.google.cloud.operators.dataplex import DataplexRunDataQualityScanOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable  # Import Variable class

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    dag_id='dag_4_execute_existing_data_quality_scan',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['dataplex', 'gcp', 'dq', 'demo'],
) as dag:

    # Fetch the data_scan_id from Airflow variables
    data_scan_id = Variable.get("data_scan_id", default_var="playpen-0b66a6-demo-dataplex-cycle-hire12-dq-scan")

    execute_data_quality_scan = DataplexRunDataQualityScanOperator(
        task_id='execute_data_quality_scan',
        project_id='playpen-0b66a6',
        region='europe-west1',
        data_scan_id=data_scan_id,  # Use the variable here
        asynchronous=False,  # Optional, set to True if you want to run asynchronously
    )

    execute_data_quality_scan
