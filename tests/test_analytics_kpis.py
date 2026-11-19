"""Tests for analytics queries and derived KPI calculations."""

import pytest
import pandas as pd
from talentflow.analytics.queries import AnalyticsQueries
from talentflow.analytics.kpis import KPIService

def test_kpi_service_funnel_dropoff():
    mock_funnel = pd.DataFrame([{
        "applied": 1000,
        "screen": 700,
        "technical_interview": 400,
        "onsite_interview": 200,
        "offer_extended": 100,
        "hired": 80,
    }])
    
    steps = KPIService.calculate_funnel_dropoff(mock_funnel)
    assert len(steps) == 6
    assert steps[0]["stage"] == "Applied"
    assert steps[0]["candidates"] == 1000
    assert steps[1]["stage_conversion_pct"] == 70.0
    assert steps[5]["stage"] == "Hired"
    assert steps[5]["stage_conversion_pct"] == 80.0

def test_kpi_service_source_roi():
    mock_sources = pd.DataFrame([{
        "source_name": "LinkedIn",
        "cost_per_posting": 500,
        "total_applications": 200,
        "total_hires": 10,
        "employee_churn_rate_pct": 15.0,
    }])
    
    res = KPIService.calculate_source_roi(mock_sources)
    assert "cost_per_hire_estimate" in res.columns
    assert "retention_rate_pct" in res.columns
    assert res.iloc[0]["retention_rate_pct"] == 85.0

def test_analytics_queries_execution():
    queries = AnalyticsQueries()
    kpis = queries.get_executive_kpis()
    assert isinstance(kpis, dict)
    assert "total_applications" in kpis
    assert "total_hires" in kpis
    assert "active_headcount" in kpis
