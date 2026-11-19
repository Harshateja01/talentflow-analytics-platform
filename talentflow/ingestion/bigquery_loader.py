"""Loads raw files from GCS or local disk into warehouse raw tables."""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from talentflow.config import config, logger
from talentflow.warehouse import get_warehouse_engine

class BigQueryLoader:
    """Manages repeatable raw ingestion into BigQuery or local warehouse."""

    def __init__(self):
        self.engine = get_warehouse_engine()

    def create_datasets_if_needed(self) -> None:
        """Ensure destination schemas/datasets exist."""
        if config.is_gcp_mode():
            from google.cloud import bigquery
            client = self.engine.client
            for dataset_name in [config.bq_raw_dataset, config.bq_staging_dataset, config.bq_analytics_dataset]:
                dataset_ref = f"{config.gcp_project_id}.{dataset_name}"
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = config.gcp_region
                try:
                    client.create_dataset(dataset, exists_ok=True)
                    logger.info(f"Verified BigQuery dataset {dataset_ref}")
                except Exception as e:
                    logger.error(f"Failed to create BigQuery dataset {dataset_ref}: {e}")
                    raise
        else:
            logger.info("Local mode: DuckDB schemas verified.")

    def load_raw_csv_files(self, file_paths: Dict[str, Path]) -> Dict[str, int]:
        """Loads all raw CSV files into the raw warehouse schema."""
        self.create_datasets_if_needed()
        loaded_counts = {}

        for table_name, file_path in file_paths.items():
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}. Skipping.")
                continue

            df = pd.read_csv(file_path)
            raw_schema = config.bq_raw_dataset if config.is_gcp_mode() else "talentflow_raw"
            
            logger.info(f"Ingesting {table_name} ({len(df):,} rows) into {raw_schema}.{table_name}...")
            self.engine.load_table(
                df=df,
                table_name=table_name,
                schema=raw_schema,
                if_exists="replace"
            )
            loaded_counts[table_name] = len(df)

        return loaded_counts
