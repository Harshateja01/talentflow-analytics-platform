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

## 2. Google Cloud Platform Deployment (BigQuery & GCS)

### Prerequisites
- Active Google Cloud Platform account with billing enabled.
- `gcloud` CLI installed and authenticated.

### Step-by-Step GCP Infrastructure Provisioning

1. **Set Active Project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable Required APIs**:
   ```bash
   gcloud services enable storage.googleapis.com bigquery.googleapis.com datacatalog.googleapis.com
   ```

3. **Create Google Cloud Storage Bucket**:
   ```bash
   gcloud storage buckets create gs://talentflow-data-lake-YOUR_PROJECT_ID --location=us-central1
   ```

4. **Create Service Account & Grant Permissions**:
   ```bash
   gcloud iam service-accounts create sa-talentflow-pipeline \
       --display-name="TalentFlow Pipeline Runner"

   # Grant Storage Admin & BigQuery Roles
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:sa-talentflow-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/storage.objectAdmin"

   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:sa-talentflow-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/bigquery.dataEditor"

   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:sa-talentflow-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/bigquery.jobUser"

   # Generate Service Account Key
   gcloud iam service-accounts keys create ./gcp-key.json \
       --iam-account="sa-talentflow-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com"
   ```

5. **Update `.env` Configuration**:
   ```ini
   TALENTFLOW_MODE=gcp
   GCP_PROJECT_ID=YOUR_PROJECT_ID
   GCP_REGION=us-central1
   GCS_BUCKET_NAME=talentflow-data-lake-YOUR_PROJECT_ID
   GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
   BQ_RAW_DATASET=talentflow_raw
   BQ_STAGING_DATASET=talentflow_staging
   BQ_ANALYTICS_DATASET=talentflow_analytics
   GEMINI_API_KEY=YOUR_GEMINI_KEY
   ```

6. **Execute GCP Pipeline**:
   ```bash
   python -m talentflow.pipeline --mode gcp
   ```

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
