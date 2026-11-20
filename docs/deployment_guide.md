# TalentFlow Deployment Guide

This guide covers deployment instructions for **Local Development**, **Google Cloud BigQuery + GCS**, and **Containerized Cloud Run**.

---

## 1. Local Development Deployment (DuckDB Engine)

Local mode runs out-of-the-box without GCP credentials or internet access.

### Prerequisites
- Python 3.11+
- Git

### Step-by-Step Local Setup

1. **Clone Repository & Create Virtual Environment**:
   ```bash
   git clone https://github.com/your-username/talentflow-analytics-platform.git
   cd talentflow-analytics-platform
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Local Environment**:
   ```bash
   cp .env.example .env
   # Default settings in .env already configure TALENTFLOW_MODE=local
   ```

4. **Execute End-to-End Pipeline**:
   ```bash
   python -m talentflow.pipeline --mode local
   ```
   *This automatically generates ~20k records, runs data quality checks, loads DuckDB, builds 20 dbt models, and runs 59 dbt tests in ~20 seconds.*

5. **Launch Streamlit Dashboard**:
   ```bash
   streamlit run talentflow/dashboards/app.py
   ```
   Open `http://localhost:8501` in your browser.

---

## 2. Google Cloud Platform Deployment (BigQuery & Optional GCS)

TalentFlow supports **direct BigQuery ingestion using Application Default Credentials (ADC)** without requiring a Google Cloud Storage bucket or service account JSON key file.

### Option A: BigQuery-Only Setup using ADC (Recommended Developer Setup)

No service account keys or GCS buckets required. TalentFlow streams Pandas DataFrames directly into BigQuery tables via `client.load_table_from_dataframe()` using idempotent `WRITE_TRUNCATE` operations, and dbt authenticates seamlessly via OAuth (`method: oauth`).

1. **Authenticate via Google Cloud ADC**:
   ```bash
   gcloud auth application-default login
   ```
   *This grants your local developer environment authenticated access to your GCP project.*

2. **Set Active Project**:
   ```bash
   gcloud config set project talentflow-analytics
   ```

3. **Enable BigQuery API**:
   ```bash
   gcloud services enable bigquery.googleapis.com
   ```

4. **Configure `.env`**:
   ```ini
   TALENTFLOW_MODE=gcp
   GCP_PROJECT_ID=talentflow-analytics
   GCP_REGION=us-central1
   # GCS_BUCKET_NAME is omitted — pipeline runs in BigQuery-Only mode!
   # GOOGLE_APPLICATION_CREDENTIALS is omitted — dbt uses ADC OAuth!
   BQ_RAW_DATASET=talentflow_raw
   BQ_STAGING_DATASET=talentflow_staging
   BQ_ANALYTICS_DATASET=talentflow_analytics
   ```

5. **Execute BigQuery Cloud Pipeline**:
   ```bash
   python -m talentflow.pipeline --mode gcp
   ```

---

### Option B: Full Cloud Setup (BigQuery + GCS Landing Zone)

Use this mode if your organization mandates a Cloud Storage landing zone / data lake archive prior to warehouse ingestion:

1. **Create GCS Bucket**:
   ```bash
   gcloud storage buckets create gs://talentflow-data-lake-talentflow-analytics --location=us-central1
   ```

2. **Add `GCS_BUCKET_NAME` to `.env`**:
   ```ini
   GCS_BUCKET_NAME=talentflow-data-lake-talentflow-analytics
   ```
   *(Optional) If using a dedicated Service Account instead of ADC:*
   ```ini
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

3. **Execute Pipeline**:
   ```bash
   python -m talentflow.pipeline --mode gcp
   ```
   *The pipeline will upload all 8 CSV extracts to `gs://${GCS_BUCKET_NAME}/raw/` before loading into BigQuery.*

---

### BigQuery Sandbox, Quotas & Cost Considerations

- **BigQuery Sandbox (No Credit Card Required)**:
  - You can test TalentFlow in BigQuery without enabling billing.
  - Limits: 10 GB active storage, 1 TB query analysis per month.
  - Tables automatically expire after 60 days unless billing is enabled.
- **BigQuery Free Tier (With Billing Enabled)**:
  - First 10 GB of storage and 1 TB of queries per month are 100% free.
  - The TalentFlow dataset contains ~20,640 records (~3 MB total storage), consuming less than 0.03% of the free tier allowance. Cost: **$0.00**.

---

## 3. Docker Containerization & Google Cloud Run

### Build & Run Container Locally
```bash
docker build -t talentflow-app .
docker run -p 8501:8501 talentflow-app
```

### Deploy to Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/talentflow-app
gcloud run deploy talentflow-dashboard \
    --image gcr.io/YOUR_PROJECT_ID/talentflow-app \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8501 \
    --set-env-vars TALENTFLOW_MODE=local
```
