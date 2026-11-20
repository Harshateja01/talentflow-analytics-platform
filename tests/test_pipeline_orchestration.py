"""Unit tests for TalentFlow pipeline orchestration and error handling."""

from unittest.mock import MagicMock, patch
import pytest

from talentflow.pipeline import TalentFlowPipeline


@pytest.fixture
def mock_pipeline_dependencies():
    """Mocks expensive data generation and validation steps for fast pipeline testing."""
    with patch("talentflow.pipeline.SyntheticDataGenerator") as mock_gen_cls, \
         patch("talentflow.pipeline.DataQualityValidator") as mock_val_cls, \
         patch("talentflow.pipeline.QualityReporter") as mock_rep_cls, \
         patch("talentflow.pipeline.BigQueryLoader") as mock_loader_cls:

        # Mock generator
        mock_gen = MagicMock()
        mock_gen.generate_all_datasets.return_value = {"candidates": MagicMock()}
        mock_gen.save_to_csv.return_value = {"candidates": "dummy_path.csv"}
        mock_gen_cls.return_value = mock_gen

        # Mock validator & reporter
        mock_val = MagicMock()
        mock_val.run_all_checks.return_value = []
        mock_val_cls.return_value = mock_val

        mock_rep_cls.save_report.return_value = "dummy_report.json"
        mock_rep_cls.generate_summary.return_value = {"pass_rate_pct": 100.0, "total": 10, "passed": 10, "failed": 0}

        # Mock loader
        mock_loader = MagicMock()
        mock_loader.load_raw_csv_files.return_value = {"candidates": 100}
        mock_loader.engine = MagicMock()
        mock_loader_cls.return_value = mock_loader

        yield {
            "generator": mock_gen,
            "validator": mock_val,
            "reporter": mock_rep_cls,
            "loader": mock_loader,
            "loader_cls": mock_loader_cls,
        }


def test_failed_dbt_run_skips_dbt_test_and_fails_pipeline(mock_pipeline_dependencies):
    """When dbt run fails, dbt test must be skipped, test success set to False, and status FAILED."""
    pipeline = TalentFlowPipeline(mode="local")

    with patch.object(pipeline, "run_dbt_command") as mock_dbt:
        # dbt run returns False (failure)
        mock_dbt.side_effect = lambda args: False if args == ["run"] else True

        result = pipeline.execute()

        # Check dbt invocations
        assert mock_dbt.call_count == 1
        mock_dbt.assert_called_once_with(["run"])

        # Check returned metrics
        assert result["dbt_run_success"] is False
        assert result["dbt_test_success"] is False
        assert result["status"] == "FAILED"
        assert "duration_seconds" in result
        assert result["duration_seconds"] >= 0


def test_successful_dbt_run_proceeds_to_dbt_test(mock_pipeline_dependencies):
    """When dbt run succeeds, dbt test must execute and result in SUCCESS if tests pass."""
    pipeline = TalentFlowPipeline(mode="local")

    with patch.object(pipeline, "run_dbt_command") as mock_dbt:
        # Both dbt run and dbt test return True (success)
        mock_dbt.return_value = True

        result = pipeline.execute()

        # Both dbt run and dbt test should have been called in sequence
        assert mock_dbt.call_count == 2
        mock_dbt.assert_any_call(["run"])
        mock_dbt.assert_any_call(["test"])

        assert result["dbt_run_success"] is True
        assert result["dbt_test_success"] is True
        assert result["status"] == "SUCCESS"
        assert result["duration_seconds"] >= 0


def test_failed_dbt_test_produces_failed_status(mock_pipeline_dependencies):
    """When dbt run succeeds but dbt test fails, pipeline status must be FAILED."""
    pipeline = TalentFlowPipeline(mode="local")

    with patch.object(pipeline, "run_dbt_command") as mock_dbt:
        # dbt run succeeds, but dbt test fails
        def dbt_side_effect(args):
            if args == ["run"]:
                return True
            if args == ["test"]:
                return False
            return False

        mock_dbt.side_effect = dbt_side_effect

        result = pipeline.execute()

        assert mock_dbt.call_count == 2
        mock_dbt.assert_any_call(["run"])
        mock_dbt.assert_any_call(["test"])

        assert result["dbt_run_success"] is True
        assert result["dbt_test_success"] is False
        assert result["status"] == "FAILED"


def test_warehouse_cleanup_on_ingestion_exception(mock_pipeline_dependencies):
    """Warehouse engine resources must be closed even when ingestion raises an exception."""
    mock_loader = mock_pipeline_dependencies["loader"]
    mock_loader.load_raw_csv_files.side_effect = RuntimeError("Database connection lost during ingestion")

    pipeline = TalentFlowPipeline(mode="local")

    with pytest.raises(RuntimeError, match="Database connection lost during ingestion"):
        pipeline.execute()

    # Verify that loader.engine.close() was called in the finally block
    mock_loader.engine.close.assert_called_once()


def test_warehouse_cleanup_without_engine(mock_pipeline_dependencies):
    """Warehouse cleanup should not fail if loader has no engine or engine is None."""
    mock_loader = mock_pipeline_dependencies["loader"]
    mock_loader.engine = None
    mock_loader.load_raw_csv_files.side_effect = RuntimeError("Immediate connection failure")

    pipeline = TalentFlowPipeline(mode="local")

    with pytest.raises(RuntimeError, match="Immediate connection failure"):
        pipeline.execute()
