import yaml
from airflow import DAG
from airflow.providers.google.cloud.operators.dataplex import (
    DataplexCreateLakeOperator, DataplexCreateZoneOperator, DataplexCreateAssetOperator,
)
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models import Variable
import logging

# Define the GCS bucket and file path
gcs_bucket = 'dataplex_demo_env'
gcs_file_path = 'dataplex_env_config.yaml'

# Load configuration from GCS
gcs_hook = GCSHook()
config_file = gcs_hook.download(bucket_name=gcs_bucket, object_name=gcs_file_path)
config = yaml.safe_load(config_file)

# Read the UUID from the Airflow variable
unique_id = Variable.get("dag_1")

# Log the UUID clearly
logging.info(f"UUID for this DAG run: {unique_id}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id=f'dag_1_dataplex_lake_zone_asset_creation',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['dataplex', 'gcp', 'dq', 'demo'],
) as dag:   
    # Lake Creation
    create_lake = DataplexCreateLakeOperator(
        task_id=f'create_lake',
        project_id=config['project_id'],
        region=config['region'],
        lake_id=f"{config['lake']['lake_id']}-{unique_id}",
        body={
            "display_name": f"{config['lake']['display_name']}_{unique_id}",
            "description": f"{config['lake']['description']}_{unique_id}",
            "labels": {
                "env": f"{config['lake']['labels']['env']}_{unique_id}",
            },
        }
    )

    # Zone Creation (Raw Zone)
    create_raw_zone = DataplexCreateZoneOperator(
        task_id=f'create_raw_zone',
        project_id=config['project_id'],
        region=config['region'],
        lake_id=f"{config['lake']['lake_id']}-{unique_id}",
        zone_id=f"{config['raw_zone']['zone_id']}-{unique_id}",
        body={
            "display_name": f"{config['raw_zone']['display_name']}_{unique_id}",
            "description": f"{config['raw_zone']['description']}_{unique_id}",
            "type_": config['raw_zone']['type'],
            "resource_spec": {
                "location_type": config['raw_zone']['resource_spec']['location_type']
            },
            "labels": {
                "env": f"{config['raw_zone']['labels']['env']}_{unique_id}",
            },
        },
    )

    # Zone Creation (Curated Zone)
    create_curated_zone = DataplexCreateZoneOperator(
        task_id=f'create_curated_zone',
        project_id=config['project_id'],
        region=config['region'],
        lake_id=f"{config['lake']['lake_id']}-{unique_id}",
        zone_id=f"{config['curated_zone']['zone_id']}-{unique_id}",
        body={
            "display_name": f"{config['curated_zone']['display_name']}_{unique_id}",
            "description": f"{config['curated_zone']['description']}_{unique_id}",
            "type_": config['curated_zone']['type'],
            "resource_spec": {
                "location_type": config['curated_zone']['resource_spec']['location_type'],
            },
            "labels": {
                "env": f"{config['curated_zone']['labels']['env']}_{unique_id}",
            },
        },
    )

    # BigQuery Asset Creation
    create_bq_asset = DataplexCreateAssetOperator(
        task_id=f'create_bq_asset',
        project_id=config['project_id'],
        region=config['region'],
        lake_id=f"{config['lake']['lake_id']}-{unique_id}",
        zone_id=f"{config['curated_zone']['zone_id']}-{unique_id}",
        asset_id=f"{config['bq_asset']['asset_id']}-{unique_id}",
        body={
            "display_name": f"{config['bq_asset']['display_name']}_{unique_id}",
            "description": f"{config['bq_asset']['description']}_{unique_id}",
            "resource_spec": {
                "type_": config['bq_asset']['resource_spec']['type'],
                "name": f"{config['bq_asset']['resource_spec']['name']}",
            },
            "discovery_spec": {
                "enabled": config['bq_asset']['discovery_spec']['enabled'],
                "include_patterns": config['bq_asset']['discovery_spec']['include_patterns'],
                "exclude_patterns": config['bq_asset']['discovery_spec']['exclude_patterns'],
            },
            "labels": {
                "env": f"{config['bq_asset']['labels']['env']}_{unique_id}",
            },
        },
    )

    # Cloud Storage Asset Creation
    create_gcs_asset = DataplexCreateAssetOperator(
        task_id=f'create_gcs_asset',
        project_id=config['project_id'],
        region=config['region'],
        lake_id=f"{config['lake']['lake_id']}-{unique_id}",
        zone_id=f"{config['raw_zone']['zone_id']}-{unique_id}",
        asset_id=f"{config['gcs_asset']['asset_id']}-{unique_id}",
        body={
            "display_name": f"{config['gcs_asset']['display_name']}_{unique_id}",
            "description": f"{config['gcs_asset']['description']}_{unique_id}",
            "resource_spec": {
                "type_": config['gcs_asset']['resource_spec']['type'],
                "name": f"{config['gcs_asset']['resource_spec']['name']}",
            },
            "discovery_spec": {
                "enabled": config['gcs_asset']['discovery_spec']['enabled'],
                "include_patterns": config['gcs_asset']['discovery_spec']['include_patterns'],
                "exclude_patterns": config['gcs_asset']['discovery_spec']['exclude_patterns'],
            },
            "labels": {
                "env": f"{config['gcs_asset']['labels']['env']}_{unique_id}",
            },
        },
    )

    # Define task dependencies
    create_lake >> create_raw_zone
    create_lake >> create_curated_zone
    create_curated_zone >> create_bq_asset
    create_raw_zone >> create_gcs_asset
