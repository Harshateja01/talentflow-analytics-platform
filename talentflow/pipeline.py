"""TalentFlow End-to-End Analytics Pipeline Orchestrator."""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from talentflow.config import config, logger
from talentflow.data_generation.generator import SyntheticDataGenerator
from talentflow.quality.validator import DataQualityValidator
from talentflow.quality.reporter import QualityReporter
from talentflow.warehouse import get_warehouse_engine
from talentflow.ingestion.bigquery_loader import BigQueryLoader
from talentflow.ingestion.gcs_uploader import GCSUploader

class TalentFlowPipeline:
    """Orchestrates end-to-end data generation, ingestion, dbt models, and validation."""

    def __init__(self, mode: str | None = None):
        if mode:
            config.mode = mode.lower()
        self.mode = config.mode
        self.dbt_dir = Path(__file__).parent.parent / "dbt_project"
        self.start_time = None
        self.metrics: Dict[str, Any] = {}

    def run_dbt_command(self, args: list[str]) -> bool:
        """Executes a dbt CLI command targeting dev (DuckDB) or bigquery."""
        target = "bigquery" if self.mode == "gcp" else "dev"
        cmd = [
            "dbt",
            *args,
            "--profiles-dir", ".",
            "--target", target,
            "--no-version-check",
            "--no-send-anonymous-usage-stats",
        ]
        
        env = os.environ.copy()
        env["TALENTFLOW_DUCKDB_PATH"] = str(config.duckdb_path.resolve())
        env["DBT_TARGET"] = target
        if config.gcp_project_id:
            env["GCP_PROJECT_ID"] = config.gcp_project_id
        if config.gcp_region:
            env["GCP_REGION"] = config.gcp_region

        logger.info(f"Running dbt command in {self.dbt_dir}: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(self.dbt_dir), env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"dbt command failed (code {result.returncode}):\n{result.stderr}\n{result.stdout}")
            return False
        else:
            logger.info(f"dbt output:\n{result.stdout}")
            return True

    def execute(
        self,
        num_candidates: int = 5000,
        num_applications: int = 6000,
        target_employees: int = 1500,
    ) -> Dict[str, Any]:
        """Runs the complete 10-step pipeline."""
        self.start_time = time.time()
        logger.info("=" * 80)
        logger.info(f"STARTING TALENTFLOW PIPELINE RUN (Mode: {self.mode.upper()})")
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 80)

        config.validate()

        # Step 1: Generate synthetic source datasets
        logger.info("\n--- Step 1: Generating Realistic Synthetic Datasets ---")
        generator = SyntheticDataGenerator(seed=42)
        datasets = generator.generate_all_datasets(
            num_candidates=num_candidates,
            num_applications=num_applications,
            target_employees=target_employees,
        )
        file_paths = generator.save_to_csv(datasets, config.raw_data_dir)
        self.metrics["generated_files"] = {k: str(v) for k, v in file_paths.items()}

        # Step 2: Run pre-ingestion data quality checks
        logger.info("\n--- Step 2: Executing Pre-Ingestion Data Quality Validation ---")
        validator = DataQualityValidator(datasets)
        quality_results = validator.run_all_checks()
        report_path = QualityReporter.save_report(quality_results, config.reports_dir)
        self.metrics["quality_summary"] = QualityReporter.generate_summary(quality_results)

        # Step 3: Upload to GCS (GCP mode only)
        if self.mode == "gcp":
            logger.info("\n--- Step 3: Uploading Datasets to Google Cloud Storage Landing Zone ---")
            uploader = GCSUploader()
            gcs_uris = uploader.upload_files(file_paths)
            self.metrics["gcs_uris"] = gcs_uris
        else:
            logger.info("\n--- Step 3: Skipping GCS Upload (Local Development Mode active) ---")
            self.metrics["gcs_uris"] = "Local mode - GCS upload skipped"

        # Step 4: Ingest raw datasets into warehouse raw schema
        logger.info(f"\n--- Step 4: Loading Raw Datasets into Warehouse ({'BigQuery' if self.mode == 'gcp' else 'DuckDB'}) ---")
        loader = BigQueryLoader()
        loaded_counts = loader.load_raw_csv_files(file_paths)
        loader.engine.close()
        self.metrics["loaded_raw_tables"] = loaded_counts

        # Step 5, 6, 7: Run dbt transformations (staging, intermediate, marts)
        logger.info("\n--- Step 5-7: Executing dbt Staging, Intermediate, and Mart Transformations ---")
        dbt_run_success = self.run_dbt_command(["run"])
        self.metrics["dbt_run_success"] = dbt_run_success
        if not dbt_run_success:
            logger.error("dbt transformation failed. Review logs above.")

        # Step 8: Execute dbt data quality & singular tests
        logger.info("\n--- Step 8: Executing dbt Schema and Custom Date Sequence Tests ---")
        dbt_test_success = self.run_dbt_command(["test"])
        self.metrics["dbt_test_success"] = dbt_test_success

        # Step 9 & 10: Refresh and generate execution summary
        duration = round(time.time() - self.start_time, 2)
        self.metrics["duration_seconds"] = duration
        self.metrics["status"] = "SUCCESS" if (dbt_run_success and dbt_test_success) else "FAILED"

        logger.info("\n" + "=" * 80)
        logger.info(f"TALENTFLOW PIPELINE EXECUTION FINISHED: {self.metrics['status']}")
        logger.info(f"Total Duration: {duration} seconds")
        logger.info(f"Data Quality Pass Rate: {self.metrics['quality_summary']['pass_rate_pct']}%")
        logger.info(f"Raw Tables Ingested: {sum(loaded_counts.values()):,} rows across {len(loaded_counts)} tables")
        logger.info("=" * 80)

        return self.metrics

def main():
    parser = argparse.ArgumentParser(description="TalentFlow Analytics Pipeline Runner")
    parser.add_argument(
        "--mode",
        choices=["local", "gcp"],
        default=os.getenv("TALENTFLOW_MODE", "local"),
        help="Pipeline execution mode (local: DuckDB, gcp: BigQuery + GCS)",
    )
    parser.add_argument("--candidates", type=int, default=5000, help="Number of candidates to generate")
    parser.add_argument("--applications", type=int, default=6000, help="Number of applications to generate")
    parser.add_argument("--employees", type=int, default=1500, help="Target number of employees")
    
    args = parser.parse_args()
    pipeline = TalentFlowPipeline(mode=args.mode)
    results = pipeline.execute(
        num_candidates=args.candidates,
        num_applications=args.applications,
        target_employees=args.employees,
    )
    if results["status"] != "SUCCESS":
        sys.exit(1)

if __name__ == "__main__":
    main()
