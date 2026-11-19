"""Warehouse interface definitions and factory."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd

from talentflow.config import config, logger

class WarehouseEngine(ABC):
    """Abstract interface for TalentFlow warehouse backends."""

    @abstractmethod
    def execute_query(self, query: str, params: Dict[str, Any] | None = None) -> pd.DataFrame:
        """Execute a SQL query and return results as a Pandas DataFrame."""
        pass

    @abstractmethod
    def load_table(self, df: pd.DataFrame, table_name: str, schema: str, if_exists: str = "replace") -> None:
        """Load a DataFrame into a warehouse table."""
        pass

    @abstractmethod
    def table_exists(self, table_name: str, schema: str) -> bool:
        """Check if a table exists in the target schema."""
        pass

    @abstractmethod
    def get_table_names(self, schema: str) -> List[str]:
        """List tables in a schema."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close any open connections."""
        pass


def get_warehouse_engine() -> WarehouseEngine:
    """Factory function returning the configured warehouse engine (DuckDB or BigQuery)."""
    if config.is_gcp_mode():
        from talentflow.warehouse.bigquery_engine import BigQueryEngine
        return BigQueryEngine()
    else:
        from talentflow.warehouse.duckdb_engine import DuckDBEngine
        return DuckDBEngine()
