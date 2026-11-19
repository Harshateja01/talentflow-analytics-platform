"""Google BigQuery warehouse engine for cloud production mode."""

from typing import Dict, Any, List
import pandas as pd

from talentflow.config import config, logger
from talentflow.warehouse.connection import WarehouseEngine

class BigQueryEngine(WarehouseEngine):
    """Production warehouse backed by Google BigQuery."""

    def __init__(self):
        if not config.gcp_project_id:
            raise ValueError("GCP_PROJECT_ID is not configured. Set GCP_PROJECT_ID or switch to local mode.")
        
        try:
            from google.cloud import bigquery
            self.client = bigquery.Client(project=config.gcp_project_id, location=config.gcp_region)
            logger.info(f"Initialized BigQuery client for project '{config.gcp_project_id}' in region '{config.gcp_region}'")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise

    def execute_query(self, query: str, params: Dict[str, Any] | None = None) -> pd.DataFrame:
        """Execute a SQL query in BigQuery and return DataFrame."""
        try:
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig()
            if params:
                query_params = []
                for k, v in params.items():
                    query_params.append(bigquery.ScalarQueryParameter(k, "STRING", str(v)))
                job_config.query_parameters = query_params

            logger.info("Executing BigQuery job...")
            query_job = self.client.query(query, job_config=job_config)
            df = query_job.to_dataframe()
            logger.info(f"BigQuery job returned {len(df):,} rows.")
            return df
        except Exception as e:
            logger.error(f"Error executing BigQuery query: {e}")
            raise

    def load_table(self, df: pd.DataFrame, table_name: str, schema: str = "talentflow_raw", if_exists: str = "replace") -> None:
        """Load DataFrame into BigQuery table with schema and disposition settings."""
        from google.cloud import bigquery
        
        table_id = f"{config.gcp_project_id}.{schema}.{table_name}"
        logger.info(f"Loading {len(df):,} rows to BigQuery table {table_id}...")
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=(
                bigquery.WriteDisposition.WRITE_TRUNCATE
                if if_exists == "replace"
                else bigquery.WriteDisposition.WRITE_APPEND
            )
        )
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for table load to complete
        logger.info(f"Loaded BigQuery table {table_id} successfully.")

    def table_exists(self, table_name: str, schema: str = "talentflow_raw") -> bool:
        """Check if BigQuery table exists."""
        from google.cloud.exceptions import NotFound
        table_id = f"{config.gcp_project_id}.{schema}.{table_name}"
        try:
            self.client.get_table(table_id)
            return True
        except NotFound:
            return False

    def get_table_names(self, schema: str) -> List[str]:
        """List tables in a BigQuery dataset."""
        dataset_id = f"{config.gcp_project_id}.{schema}"
        tables = self.client.list_tables(dataset_id)
        return [table.table_id for table in tables]

    def close(self) -> None:
        """BigQuery client uses HTTP connections; no persistent socket to close."""
        pass
