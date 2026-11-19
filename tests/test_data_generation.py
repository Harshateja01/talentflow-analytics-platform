"""Tests for synthetic data generation module."""

import pytest
import pandas as pd
from talentflow.data_generation.generator import SyntheticDataGenerator
from talentflow.data_generation.schemas import DEPARTMENTS, RECRUITING_SOURCES

@pytest.fixture
def generator():
    return SyntheticDataGenerator(seed=123)

def test_generate_departments(generator):
    df = generator.generate_departments()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(DEPARTMENTS)
    assert "department_id" in df.columns
    assert "department_name" in df.columns

def test_generate_recruiting_sources(generator):
    df = generator.generate_recruiting_sources()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(RECRUITING_SOURCES)
    assert "source_id" in df.columns
    assert "cost_per_posting" in df.columns

def test_generate_candidates(generator):
    df = generator.generate_candidates(num_records=200)
    assert len(df) >= 200
    assert "candidate_id" in df.columns
    assert "email" in df.columns
    assert "years_of_experience" in df.columns

def test_generate_all_datasets_relational_integrity(generator):
    datasets = generator.generate_all_datasets(
        num_candidates=100,
        num_applications=120,
        target_employees=30,
    )
    
    expected_keys = [
        "candidates", "applications", "interviews", "offers",
        "employees", "engagement_surveys", "departments", "recruiting_sources"
    ]
    for key in expected_keys:
        assert key in datasets
        assert isinstance(datasets[key], pd.DataFrame)
        assert len(datasets[key]) > 0

    # Ensure application candidate IDs point to candidates
    cand_ids = set(datasets["candidates"]["candidate_id"])
    app_cand_ids = set(datasets["applications"]["candidate_id"].dropna())
    assert app_cand_ids.issubset(cand_ids)
