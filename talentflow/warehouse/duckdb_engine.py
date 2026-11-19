"""DuckDB warehouse engine implementation for local development."""

from pathlib import Path
from typing import Dict, Any, List
import duckdb
import pandas as pd

from talentflow.config import config, logger
from talentflow.warehouse.connection import WarehouseEngine

class DuckDBEngine(WarehouseEngine):
    """Local warehouse powered by DuckDB."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or config.duckdb_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(str(self.db_path))
        self._init_schemas()

    def _init_schemas(self) -> None:
        """Create raw, staging, and analytics schemas."""
        for schema in ["talentflow_raw", "talentflow_staging", "talentflow_analytics"]:
            self._conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

    def execute_query(self, query: str, params: Dict[str, Any] | None = None) -> pd.DataFrame:
        """Execute SQL query against DuckDB and return DataFrame."""
        try:
            if params:
                return self._conn.execute(query, params).fetchdf()
            return self._conn.execute(query).fetchdf()
        except Exception as e:
            logger.error(f"Error executing DuckDB query: {e}\nQuery: {query}")
            raise

    def load_table(self, df: pd.DataFrame, table_name: str, schema: str = "talentflow_raw", if_exists: str = "replace") -> None:
        """Load a DataFrame into a DuckDB table."""
        qualified_name = f"{schema}.{table_name}"
        logger.info(f"Loading {len(df):,} rows into DuckDB table {qualified_name}...")
        
        self._conn.register("temp_df", df)
        if if_exists == "replace":
            self._conn.execute(f"CREATE OR REPLACE TABLE {qualified_name} AS SELECT * FROM temp_df;")
        elif if_exists == "append":
            if self.table_exists(table_name, schema):
                self._conn.execute(f"INSERT INTO {qualified_name} SELECT * FROM temp_df;")
            else:
                self._conn.execute(f"CREATE TABLE {qualified_name} AS SELECT * FROM temp_df;")
        self._conn.unregister("temp_df")
        logger.info(f"Loaded {qualified_name} successfully.")

    def table_exists(self, table_name: str, schema: str = "talentflow_raw") -> bool:
        """Check if table exists in DuckDB."""
        res = self._conn.execute(
            """
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = ? AND table_name = ?
            """,
            [schema, table_name],
        ).fetchone()
        return bool(res and res[0] > 0)

    def get_table_names(self, schema: str) -> List[str]:
        """List tables in a DuckDB schema."""
        res = self._conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = ?",
            [schema],
        ).fetchall()
        return [r[0] for r in res]

    def close(self) -> None:
        """Close connection to DuckDB."""
        try:
            self._conn.close()
        except Exception:
            pass
