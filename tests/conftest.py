"""Pytest configuration and global fixtures for TalentFlow."""

import os
import pytest
from talentflow.config import config


@pytest.fixture(autouse=True)
def default_local_test_mode(monkeypatch):
    """Ensure unit tests execute against the local DuckDB warehouse by default,

    even when the developer has TALENTFLOW_MODE=gcp set in their active .env file.
    """
    original_mode = config.mode
    config.mode = "local"
    monkeypatch.setenv("TALENTFLOW_MODE", "local")
    yield
    config.mode = original_mode
