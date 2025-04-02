# Dataplex Data Quality Setup

Welcome to the Dataplex Data Quality Setup guide! This document provides detailed instructions on setting up Dataplex data quality scans using `gcloud` commands. Follow these steps to ensure your data quality processes are up and running smoothly.

## Prerequisites

Before you begin, make sure you have the Google Cloud SDK installed and configured. You can verify your current project with the following command:
```bash
gcloud config get project
```

## Environment Variables

Set the following environment variables:
```bash
export TENANT_PROJECT_ID=playpen-6dae04
export CENTRAL_PROJECT_ID=playpen-0b66a6
export LOCATION=europe-west1
export DATASET=tenant_dataset
export TABLE=cycle_hire
```

## Step-by-Step Instructions

### 1. Create a Dataplex Lake

**Generic Command:**
```bash
gcloud dataplex lakes create [LAKE_NAME] \
    --project=[PROJECT_ID] \
    --location=[LOCATION] \
    --display-name="[DISPLAY_NAME]" \
    --description="[DESCRIPTION]"
```

**Example:**
```bash
gcloud dataplex lakes create demo-lake \
    --project=$CENTRAL_PROJECT_ID \
    --location=$LOCATION \
    --display-name="demo-lake" \
    --description="demo-lake-description"
```

#### Verify Lake Creation

**Generic Command:**
```bash
gcloud dataplex lakes list \
    --project=[PROJECT_ID] \
    --location=[LOCATION]
```

**Example:**
```bash
gcloud dataplex lakes list \
    --project=$CENTRAL_PROJECT_ID \
    --location=$LOCATION
```

### 2. Create a Curated Zone

**Generic Command:**
```bash
gcloud dataplex zones create [ZONE_NAME] \
    --project=[PROJECT_ID] \
    --lake="[LAKE_NAME]" \
    --resource-location-type="[RESOURCE_LOCATION_TYPE]" \
    --location=[LOCATION] \
    --type=[ZONE_TYPE] \
    --discovery-enabled \
    --discovery-include-patterns="[INCLUDE_PATTERNS]" \
    --discovery-exclude-patterns="[EXCLUDE_PATTERNS]" \
    --discovery-schedule="[SCHEDULE]" \
    --display-name="[DISPLAY_NAME]" \
    --description="[DESCRIPTION]"
```

**Example:**
```bash
gcloud dataplex zones create demo-curated-zone \
    --project=$CENTRAL_PROJECT_ID \
    --lake="demo-lake" \
    --resource-location-type="MULTI_REGION" \
    --location=$LOCATION \
    --type=CURATED \
    --discovery-enabled \
    --discovery-include-patterns="*" \
    --discovery-exclude-patterns="temp_*" \
    --discovery-schedule="0 * * * *" \
    --display-name="demo-curated-zone" \
    --description="demo-curated-zone-description"
```

#### Verify Zone Creation

**Generic Command:**
```bash
gcloud dataplex zones list \
    --project=[PROJECT_ID] \
    --lake="[LAKE_NAME]" \
    --location=[LOCATION]
```

**Example:**
```bash
gcloud dataplex zones list \
    --project=$CENTRAL_PROJECT_ID \
    --lake="demo-lake" \
    --location=$LOCATION
```

### 3. Create a Curated Asset

**Generic Command:**
```bash
gcloud dataplex assets create [ASSET_NAME] \
    --project=[PROJECT_ID] \
    --lake="[LAKE_NAME]" \
    --zone="[ZONE_NAME]" \
    --location=[LOCATION] \
    --resource-type=[RESOURCE_TYPE] \
    --resource-name="[RESOURCE_NAME]" \
    --display-name="[DISPLAY_NAME]" \
    --description="[DESCRIPTION]"
```

**Example:**
```bash
gcloud dataplex assets create demo-curated-asset \
    --project=$CENTRAL_PROJECT_ID \
    --lake="demo-lake" \
    --zone="demo-curated-zone" \
    --location=$LOCATION \
    --resource-type=BIGQUERY_DATASET \
    --resource-name="projects/$TENANT_PROJECT_ID/datasets/$DATASET" \
    --display-name="demo-curated-asset" \
    --description="demo-curated-asset-description"
```

#### Verify Asset Creation

**Generic Command:**
```bash
gcloud dataplex assets list \
    --project=[PROJECT_ID] \
    --lake="[LAKE_NAME]" \
    --zone="[ZONE_NAME]" \
    --location=[LOCATION]
```

**Example:**
```bash
gcloud dataplex assets list \
    --project=$CENTRAL_PROJECT_ID \
    --lake="demo-lake" \
    --zone="demo-curated-zone" \
    --location=$LOCATION
```

### 4. Create a Data Quality Scan

**Generic Command:**
```bash
gcloud dataplex datascans create data-quality [SCAN_NAME] \
  --project=[PROJECT_ID] \
  --location=[LOCATION] \
  --data-source-entity=projects/[PROJECT_ID]/locations/[LOCATION]/lakes/[LAKE_NAME]/zones/[ZONE_NAME]/entities/[TABLE_NAME] \
  --data-quality-spec-file="[SPEC_FILE_PATH]"
```

**Example:**
```bash
gcloud dataplex datascans create data-quality demo-data-quality-scan \
  --project=$CENTRAL_PROJECT_ID \
  --location=$LOCATION \
  --data-source-entity=projects/$CENTRAL_PROJECT_ID/locations/$LOCATION/lakes/demo-lake/zones/demo-curated-zone/entities/$TABLE \
  --data-quality-spec-file="Tenant_project/Excel_configs/test_project_id__test_dataset_id__test_table__star_star_star_1_2_3.yaml"
```

#### Verify Data Quality Scan Creation

**Generic Command:**
```bash
gcloud dataplex datascans list \
    --project=[PROJECT_ID] \
    --location=[LOCATION]
```

**Example:**
```bash
gcloud dataplex datascans list \
    --project=$CENTRAL_PROJECT_ID \
    --location=$LOCATION
```

### 5. Run the Data Quality Scan

**Generic Command:**
```bash
gcloud dataplex datascans run [SCAN_NAME] \
    --project=[PROJECT_ID] \
    --location=[LOCATION]
```

**Example:**
```bash
gcloud dataplex datascans run demo-data-quality-scan \
    --project=$CENTRAL_PROJECT_ID \
    --location=$LOCATION
```

#### Verify Data Quality Scan Execution

**Generic Command:**
```bash
gcloud dataplex datascans describe [SCAN_NAME] \
    --project=[PROJECT_ID] \
    --location=[LOCATION]
```

**Example:**
```bash
gcloud dataplex datascans describe demo-data-quality-scan \
    --project=$CENTRAL_PROJECT_ID \
    --location=$LOCATION
```
## Conclusion

By following the steps outlined in this guide, you have successfully set up Dataplex data quality scans using `gcloud` commands. This setup ensures that your data within Dataplex lakes, zones, and assets is regularly monitored and maintained for quality. Regular data quality scans help in identifying and addressing issues promptly, thereby maintaining the integrity and reliability of your data.

Remember to periodically review and update your configurations and environment variables to adapt to any changes in your data infrastructure. If you encounter any issues or need further assistance, refer to the Google Cloud documentation or reach out to your support team.

Thank you for using Dataplex for your data quality needs!
```