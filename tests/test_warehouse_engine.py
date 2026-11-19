"""Tests for warehouse connection and DuckDB engine."""

import pytest
import pandas as pd
from talentflow.warehouse.duckdb_engine import DuckDBEngine

def test_duckdb_lifecycle(tmp_path):
    test_db = tmp_path / "test.duckdb"
    engine = DuckDBEngine(db_path=test_db)
    
    # Test loading table
    sample_df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "metric": [10.5, 20.0, 30.5],
    })
    engine.load_table(sample_df, table_name="test_table", schema="talentflow_raw")
    
    assert engine.table_exists("test_table", schema="talentflow_raw")
    assert not engine.table_exists("non_existent_table", schema="talentflow_raw")
    
    # Test query execution
    df_out = engine.execute_query("SELECT count(*) as cnt FROM talentflow_raw.test_table")
    assert df_out.iloc[0]["cnt"] == 3
    
    engine.close()
