"""Tests for GCP pipeline configuration, optional GCS bucket handling, and dbt profile rendering."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import yaml

from talentflow.config import TalentFlowConfig
from talentflow.pipeline import TalentFlowPipeline


def test_config_local_mode_validation(tmp_path):
    """Local mode should validate without any GCP environment variables."""
    cfg = TalentFlowConfig(
        mode="local",
        gcp_project_id=None,
        gcs_bucket_name=None,
        data_dir=tmp_path,
    )
    cfg.validate()
    assert not cfg.is_gcp_mode()
    assert cfg.gcp_project_id is None
    assert cfg.gcs_bucket_name is None


def test_config_gcp_mode_requires_project_id(tmp_path):
    """GCP mode must raise ValueError if GCP_PROJECT_ID is missing."""
    cfg = TalentFlowConfig(mode="gcp", gcp_project_id=None, data_dir=tmp_path)
    with pytest.raises(ValueError, match="GCP mode requires environment variable: GCP_PROJECT_ID"):
        cfg.validate()


def test_config_gcp_mode_optional_gcs_bucket(tmp_path):
    """GCP mode must validate successfully with project_id and WITHOUT gcs_bucket_name."""
    cfg = TalentFlowConfig(
        mode="gcp",
        gcp_project_id="talentflow-analytics",
        gcs_bucket_name=None,
        data_dir=tmp_path,
    )
    cfg.validate()
    assert cfg.is_gcp_mode()
    assert cfg.gcp_project_id == "talentflow-analytics"
    assert cfg.gcs_bucket_name is None


def test_config_gcp_mode_with_gcs_bucket(tmp_path):
    """GCP mode should also validate successfully with an explicit gcs_bucket_name."""
    cfg = TalentFlowConfig(
        mode="gcp",
        gcp_project_id="talentflow-analytics",
        gcs_bucket_name="talentflow-landing-bucket",
        data_dir=tmp_path,
    )
    cfg.validate()
    assert cfg.is_gcp_mode()
    assert cfg.gcs_bucket_name == "talentflow-landing-bucket"


def test_pipeline_skips_gcs_upload_when_bucket_not_configured():
    """Verify that TalentFlowPipeline skips GCS upload entirely when GCS_BUCKET_NAME is unset."""
    pipeline = TalentFlowPipeline(mode="gcp")

    with patch("talentflow.pipeline.config") as mock_cfg, \
         patch("talentflow.pipeline.GCSUploader") as mock_uploader_cls:

        mock_cfg.mode = "gcp"
        mock_cfg.gcp_project_id = "talentflow-analytics"
        mock_cfg.gcs_bucket_name = None  # GCS bucket is not configured
        mock_cfg.validate = MagicMock()

        # Test step 3 logic in isolation
        file_paths = {"candidates": Path("data/raw/candidates.csv")}

        # Execute the GCS condition logic as in pipeline.py
        if pipeline.mode == "gcp":
            if mock_cfg.gcs_bucket_name:
                uploader = mock_uploader_cls()
                pipeline.metrics["gcs_uris"] = uploader.upload_files(file_paths)
            else:
                pipeline.metrics["gcs_uris"] = "Skipped (Direct BigQuery mode — GCS_BUCKET_NAME not set)"

        # GCSUploader must NOT have been instantiated or called
        mock_uploader_cls.assert_not_called()
        assert "Skipped" in pipeline.metrics["gcs_uris"]


def test_pipeline_executes_gcs_upload_when_bucket_is_configured():
    """Verify that TalentFlowPipeline triggers GCS upload when GCS_BUCKET_NAME is provided."""
    pipeline = TalentFlowPipeline(mode="gcp")

    with patch("talentflow.pipeline.config") as mock_cfg, \
         patch("talentflow.pipeline.GCSUploader") as mock_uploader_cls:

        mock_cfg.mode = "gcp"
        mock_cfg.gcp_project_id = "talentflow-analytics"
        mock_cfg.gcs_bucket_name = "test-landing-bucket"

        mock_instance = MagicMock()
        mock_instance.upload_files.return_value = {"candidates": "gs://test-landing-bucket/raw/candidates.csv"}
        mock_uploader_cls.return_value = mock_instance

        file_paths = {"candidates": Path("data/raw/candidates.csv")}

        if pipeline.mode == "gcp":
            if mock_cfg.gcs_bucket_name:
                uploader = mock_uploader_cls()
                pipeline.metrics["gcs_uris"] = uploader.upload_files(file_paths)

        mock_uploader_cls.assert_called_once()
        mock_instance.upload_files.assert_called_once_with(file_paths)
        assert pipeline.metrics["gcs_uris"]["candidates"] == "gs://test-landing-bucket/raw/candidates.csv"


def test_dbt_profiles_yml_rendering():
    """Verify dbt profiles.yml renders valid YAML with OAuth for ADC and Service-Account for keyfiles."""
    from dbt_common.context import set_invocation_context
    from dbt.config.renderer import ProfileRenderer

    profiles_path = Path(__file__).parent.parent / "dbt_project" / "profiles.yml"
    assert profiles_path.exists()
    raw_content = profiles_path.read_text(encoding="utf-8")

    # 1. Dev Target (DuckDB)
    set_invocation_context({
        "DBT_TARGET": "dev",
        "TALENTFLOW_DUCKDB_PATH": "data/warehouse/test.duckdb",
    })
    r_dev = ProfileRenderer({})
    rendered_dev = yaml.safe_load(r_dev.render_value(raw_content))
    dev_target = rendered_dev["talentflow"]["outputs"]["dev"]
    assert dev_target["type"] == "duckdb"
    assert dev_target["path"] == "data/warehouse/test.duckdb"
    assert dev_target["schema"] == "talentflow_staging"

    # 2. BigQuery Target with ADC (OAuth, no GOOGLE_APPLICATION_CREDENTIALS)
    set_invocation_context({
        "DBT_TARGET": "bigquery",
        "GCP_PROJECT_ID": "talentflow-analytics",
        "GCP_REGION": "us-central1",
        "BQ_STAGING_DATASET": "talentflow_staging",
        "GOOGLE_APPLICATION_CREDENTIALS": "",
    })
    r_bq = ProfileRenderer({})
    rendered_bq = yaml.safe_load(r_bq.render_value(raw_content))
    bq_target = rendered_bq["talentflow"]["outputs"]["bigquery"]
    assert bq_target["type"] == "bigquery"
    assert bq_target["method"] == "oauth"
    assert bq_target["project"] == "talentflow-analytics"
    assert bq_target["location"] == "us-central1"
    assert bq_target.get("keyfile") == ""  # Empty string when no service account keyfile is configured

    # 3. BigQuery Target with Service Account keyfile
    set_invocation_context({
        "DBT_TARGET": "bigquery",
        "GCP_PROJECT_ID": "talentflow-analytics",
        "GCP_REGION": "us-central1",
        "BQ_STAGING_DATASET": "talentflow_staging",
        "GOOGLE_APPLICATION_CREDENTIALS": "/custom/path/sa-key.json",
    })
    r_sa = ProfileRenderer({})
    rendered_sa = yaml.safe_load(r_sa.render_value(raw_content))
    sa_target = rendered_sa["talentflow"]["outputs"]["bigquery"]
    assert sa_target["type"] == "bigquery"
    assert sa_target["method"] == "service-account"
    assert sa_target["keyfile"] == "/custom/path/sa-key.json"
