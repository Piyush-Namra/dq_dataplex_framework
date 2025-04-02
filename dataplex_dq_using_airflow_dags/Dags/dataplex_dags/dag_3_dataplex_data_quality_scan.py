import os
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
from google.cloud import storage
from airflow.providers.google.cloud.operators.dataplex import DataplexCreateOrUpdateDataQualityScanOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from google.cloud import dataplex_v1
from google.cloud.dataplex_v1.types import DataQualitySpec, Trigger
import json
import yaml

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Function to list YAML files in the GCS bucket
def list_yaml_files(bucket_path, **kwargs):
    # Initialize the GCS client
    client = storage.Client()
    
    # Extract bucket name and prefix from the bucket_path
    bucket_name, prefix = bucket_path.replace("gs://", "").split("/", 1)
    
    # Get the bucket object
    bucket = client.get_bucket(bucket_name)
    
    # List all blobs (files) in the specified prefix
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    # Initialize an empty list to store valid YAML files
    valid_yaml_list = []
    
    # Create a list of blob names
    file_list = [blob.name for blob in blobs]
    
    # Filter the list to include only YAML files
    for file in file_list:
        if file.endswith('.json'):
            valid_yaml_list.append(file)
    
    # Push the list of valid YAML files to XCom
    print(f'Pushing to XCom: {valid_yaml_list}')
    kwargs['ti'].xcom_push(key='yaml_files', value=valid_yaml_list)
    kwargs['ti'].xcom_push(key='lake_id', value=lake_id)
    kwargs['ti'].xcom_push(key='zone_id', value=zone_id)
    kwargs['ti'].xcom_push(key='region', value=region)
    print(f'valid_yaml_list_onkar {valid_yaml_list}')
    
def create_dq_scans(**kwargs):
    # Retrieve the list of YAML files from XCom
    file_names = kwargs['ti'].xcom_pull(task_ids='list_yaml_files_task', key='yaml_files', include_prior_dates=True)
    print(f"onkar inside dq_scan- {file_names}")
    
    lake_id = kwargs['ti'].xcom_pull(task_ids='list_yaml_files_task', key='lake_id', include_prior_dates=True)
    zone_id = kwargs['ti'].xcom_pull(task_ids='list_yaml_files_task', key='zone_id', include_prior_dates=True)
    region = kwargs['ti'].xcom_pull(task_ids='list_yaml_files_task', key='region', include_prior_dates=True)
    print(f'Pulled from XCom: {file_names}, {lake_id}, {zone_id}, {region}')
    
    if file_names is None:
        raise ValueError("No YAML files found in XCom.")
    
    # Initialize GCS client
    storage_client = storage.Client()
    bucket_name = gcs_location.replace('gs://', '').split('/')[0]
    bucket = storage_client.bucket(bucket_name)
    
    processed_files = []
    for file_name in file_names:
        print(f"Onkar-reading {file_name}")
        # Skip if file doesn't end with .yaml
        if not file_name.endswith('.json'):
            continue

        # Check if the file exists in the bucket
        blob = bucket.blob(file_name)
        if not blob.exists():
            print(f"File not found in GCS: {file_name}")
            continue

        # Parse filename
        filename_parts = os.path.splitext(os.path.basename(file_name))[0].split('__')
        
        # Determine if it's a star_ file
        is_star_file = 'star_' in file_name

        # Ensure we have enough parts
        if len(filename_parts) < 3:
            print(f"Skipping invalid filename: {file_name}")
            continue

        # Extract details
        project_id = filename_parts[0]
        dataset = filename_parts[1]
        table_name = filename_parts[2]

        rev_project_id = filename_parts[0].replace("_","-")
        rev_dataset = filename_parts[1].replace("_","-")
        rev_table_name = filename_parts[2].replace("_","-")

        
        l_schedule = ""
        
        # Get schedule from filename if it's a star file
        schedule = filename_parts[3] if is_star_file and len(filename_parts) > 3 else None

        # Optional: Print schedule if present
        if schedule:
            print(f"Schedule for {file_name}: {schedule}")
            l_schedule = schedule.replace("star","*").replace("_"," ")
            print(f"Formatted Schedule for {file_name}: {l_schedule}")

        # Download YAML file content
        yaml_content = blob.download_as_text()
        
        # Converting YAML content to dictionary and then to JSON string
        #yaml_dict = yaml.safe_load(yaml_content)
        yaml_dict = json.loads(yaml_content)
        #json_content = json.dumps(yaml_dict)
        
        print(f"Onkar json content -> {yaml_dict}")

        # Retrofitting 
        EXAMPLE_DATA_SCAN = dataplex_v1.DataScan()
        EXAMPLE_DATA_SCAN.data.entity = (f"projects/{project_id}/locations/{region}/lakes/{lake_id}/zones/{zone_id}/entities/{table_name}")
        EXAMPLE_DATA_SCAN.data.resource = (f"//bigquery.googleapis.com/projects/{project_id}/datasets/{dataset}/tables/{table_name}")
        
        EXAMPLE_DATA_SCAN.data_quality_spec = DataQualitySpec(
         yaml_dict
        )
        
        if schedule:
            # Create an instance of Schedule with the cron parameter
            schedule = Trigger.Schedule(cron=l_schedule)
            # Create an instance of Trigger with the schedule
            trigger = Trigger(schedule=schedule)
            # Assign the trigger to the execution_spec
            EXAMPLE_DATA_SCAN.execution_spec = dataplex_v1.DataScan.ExecutionSpec(trigger=trigger)
        
        print(f"onkar check {project_id} {region} {dataset} {table_name}")
        print(f"onkar -> create_dq_scan_{os.path.splitext(os.path.basename(file_name))[0]}")
        print(f"{project_id}-{dataset}-{table_name}-dq-scan")
        DataplexCreateOrUpdateDataQualityScanOperator(
            task_id=f'create_dq_scan_{os.path.splitext(os.path.basename(file_name))[0]}',
            project_id=project_id,
            region=region,  
            body=EXAMPLE_DATA_SCAN,
            data_scan_id=f"{rev_project_id}-{rev_dataset}-{rev_table_name}-dq-scan",
            #data_scan_id=f"{project_id}_{dataset}_{table_name}_dq-scan",
            dag = kwargs['dag']
            ).execute(context=kwargs)
# DAG definition
with DAG(
    'dag_3_dataplex_data_quality_scan',
    default_args=default_args,
    schedule_interval=None,  # Manually triggered or set as needed
    catchup=False,
    tags=['dataplex', 'gcp', 'dq', 'demo'],
) as dag:
    # Retrieve Airflow variables
    gcs_location = "gs://dataplex_demo_env/dq_excel/"  # You can also use Variable.get() to fetch from Airflow variables
    lake_id = Variable.get("demo-lake")
    zone_id = Variable.get("demo-zone")
    region = 'europe-west1'

    list_yaml_files_task = PythonOperator(
        task_id='list_yaml_files_task',
        python_callable=list_yaml_files,
        op_args=[gcs_location],
        provide_context=True,
    )
    
    # Create a PythonOperator to process the YAML files
    process_dq_scans = PythonOperator(
        task_id='create_dq_scans',
        python_callable=create_dq_scans,
        provide_context=True,
        dag=dag,
    )

    # Set task dependencies
    list_yaml_files_task >> process_dq_scans