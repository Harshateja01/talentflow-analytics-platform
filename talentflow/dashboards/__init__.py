"""Streamlit dashboard package for TalentFlow."""

from .cache import (
    get_shared_analytics_queries,
    get_cached_filter_options,
    get_cached_executive_kpis,
    get_cached_monthly_hiring_trends,
    get_cached_recruiting_funnel_summary,
    get_cached_funnel_metrics,
    get_cached_stage_duration_breakdown,
    get_cached_source_performance,
    get_cached_department_metrics,
    get_cached_workforce_demographics,
    get_cached_attrition_analysis,
    get_cached_engagement_by_tenure,
    get_cached_retention_cohorts,
    clear_dashboard_cache,
)

__all__ = [
    "get_shared_analytics_queries",
    "get_cached_filter_options",
    "get_cached_executive_kpis",
    "get_cached_monthly_hiring_trends",
    "get_cached_recruiting_funnel_summary",
    "get_cached_funnel_metrics",
    "get_cached_stage_duration_breakdown",
    "get_cached_source_performance",
    "get_cached_department_metrics",
    "get_cached_workforce_demographics",
    "get_cached_attrition_analysis",
    "get_cached_engagement_by_tenure",
    "get_cached_retention_cohorts",
    "clear_dashboard_cache",
]
