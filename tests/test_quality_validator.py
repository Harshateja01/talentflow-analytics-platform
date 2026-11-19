"""Tests for data quality validation and reporting."""

import pytest
import pandas as pd
from talentflow.data_generation.generator import SyntheticDataGenerator
from talentflow.quality.validator import DataQualityValidator
from talentflow.quality.reporter import QualityReporter

@pytest.fixture
def datasets():
    gen = SyntheticDataGenerator(seed=999)
    return gen.generate_all_datasets(num_candidates=100, num_applications=120, target_employees=30)

def test_validator_detects_controlled_anomalies(datasets):
    validator = DataQualityValidator(datasets)
    results = validator.run_all_checks()
    
    assert len(results) > 0
    # Should identify both passing checks and controlled failures
    pass_results = [r for r in results if r.status == "PASS"]
    fail_results = [r for r in results if r.status == "FAIL"]
    
    assert len(pass_results) > 0
    assert len(fail_results) > 0

def test_reporter_summary_generation(datasets):
    validator = DataQualityValidator(datasets)
    results = validator.run_all_checks()
    summary = QualityReporter.generate_summary(results)
    
    assert "total_checks" in summary
    assert "pass_rate_pct" in summary
    assert summary["total_checks"] == len(results)
    assert 0 <= summary["pass_rate_pct"] <= 100
