"""Google Cloud Storage uploader for raw data landing zone."""

from pathlib import Path
from typing import Dict, List
from talentflow.config import config, logger

class GCSUploader:
    """Uploads raw CSV extracts to Google Cloud Storage bucket landing zone."""

    def __init__(self, bucket_name: str | None = None, project_id: str | None = None):
        self.bucket_name = bucket_name or config.gcs_bucket_name
        self.project_id = project_id or config.gcp_project_id

    def upload_files(self, file_paths: Dict[str, Path], destination_prefix: str = "raw") -> Dict[str, str]:
        """Uploads files to GCS and returns their gs:// URI."""
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME is not configured.")

        try:
            from google.cloud import storage
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.bucket_name)

            uploaded_uris = {}
            for table_name, file_path in file_paths.items():
                blob_name = f"{destination_prefix}/{file_path.name}"
                blob = bucket.blob(blob_name)
                
                logger.info(f"Uploading {file_path} to gs://{self.bucket_name}/{blob_name}...")
                blob.upload_from_filename(str(file_path))
                uri = f"gs://{self.bucket_name}/{blob_name}"
                uploaded_uris[table_name] = uri
                logger.info(f"Uploaded successfully: {uri}")

            return uploaded_uris
        except Exception as e:
            logger.error(f"GCS upload failed: {e}")
            raise
