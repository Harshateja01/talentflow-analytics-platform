"""Ingestion module for TalentFlow data pipeline."""

from .gcs_uploader import GCSUploader
from .bigquery_loader import BigQueryLoader

__all__ = ["GCSUploader", "BigQueryLoader"]
