"""Configuration management for TalentFlow."""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

@dataclass
class TalentFlowConfig:
    """Central configuration class supporting both local development and GCP deployment."""
    mode: str = field(default_factory=lambda: os.getenv("TALENTFLOW_MODE", "local").lower())
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("TALENTFLOW_DATA_DIR", "./data")).resolve())
    
    # GCP Configuration
    gcp_project_id: str | None = field(default_factory=lambda: os.getenv("GCP_PROJECT_ID"))
    gcp_region: str = field(default_factory=lambda: os.getenv("GCP_REGION", "us-central1"))
    gcs_bucket_name: str | None = field(default_factory=lambda: os.getenv("GCS_BUCKET_NAME"))
    google_application_credentials: str | None = field(default_factory=lambda: os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    
    # BigQuery Datasets
    bq_raw_dataset: str = field(default_factory=lambda: os.getenv("BQ_RAW_DATASET", "talentflow_raw"))
    bq_staging_dataset: str = field(default_factory=lambda: os.getenv("BQ_STAGING_DATASET", "talentflow_staging"))
    bq_analytics_dataset: str = field(default_factory=lambda: os.getenv("BQ_ANALYTICS_DATASET", "talentflow_analytics"))
    
    # AI / LLM Configuration
    gemini_api_key: str | None = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    
    @property
    def duckdb_path(self) -> Path:
        """Path to the local DuckDB warehouse file."""
        return self.data_dir / "warehouse" / "talentflow.duckdb"
    
    @property
    def raw_data_dir(self) -> Path:
        """Directory where generated raw CSV files reside."""
        return self.data_dir / "raw"

    @property
    def reports_dir(self) -> Path:
        """Directory where validation and quality reports are saved."""
        return self.data_dir / "reports"

    def is_gcp_mode(self) -> bool:
        return self.mode == "gcp"

    def validate(self) -> None:
        """Validate configuration settings based on active mode."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "warehouse").mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        if self.is_gcp_mode():
            missing = []
            if not self.gcp_project_id:
                missing.append("GCP_PROJECT_ID")
            if not self.gcs_bucket_name:
                missing.append("GCS_BUCKET_NAME")
            if missing:
                raise ValueError(
                    f"GCP mode requires environment variables: {', '.join(missing)}. "
                    "Set them in your .env file or switch TALENTFLOW_MODE to 'local'."
                )

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures structured application logging."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("talentflow")

# Global default config instance
config = TalentFlowConfig()
logger = setup_logging()
