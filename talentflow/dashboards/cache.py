"""Dashboard caching and resource management for Streamlit.

Phase 1: Shared AnalyticsQueries factory and cached filter options.
Phase 2: Param-aware read-only analytical query caching with tuple hashing
         and mutation-safe copy semantics.
"""

from typing import Dict, Any, List, Optional, Tuple, Sequence
import streamlit as st
import pandas as pd
from talentflow.analytics.queries import AnalyticsQueries

CACHE_TTL_SECONDS = 300  # 5 minutes


# -----------------------------------------------------------------------------
# Parameter Normalization Helpers
# -----------------------------------------------------------------------------

def _normalize_filter(val: Optional[Sequence[str]]) -> Optional[Tuple[str, ...]]:
    """Convert sequence of filter values into a sorted, immutable tuple for hashing."""
    if not val:
        return None
    return tuple(sorted(val))


def _to_list(val: Optional[Tuple[str, ...]]) -> Optional[List[str]]:
    """Convert immutable tuple back to list for warehouse query engines."""
    return list(val) if val else None


# -----------------------------------------------------------------------------
# Phase 1: Shared AnalyticsQueries Instance & Sidebar Filters
# -----------------------------------------------------------------------------

@st.cache_resource
def _get_raw_analytics_queries() -> AnalyticsQueries:
    """Internal factory creating one reusable AnalyticsQueries instance with persistent engine."""
    return AnalyticsQueries()


@st.cache_data(ttl=600)
def get_cached_filter_options() -> Dict[str, List[str]]:
    """Returns distinct filter options cached for 10 minutes to minimize warehouse roundtrips."""
    queries = _get_raw_analytics_queries()
    return queries.get_filter_options()


# -----------------------------------------------------------------------------
# Phase 2: Cached Analytical Query Implementations (Tuple Keys, TTL=300s)
# -----------------------------------------------------------------------------

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_executive_kpis(
    departments: Optional[Tuple[str, ...]] = None,
    sources: Optional[Tuple[str, ...]] = None,
) -> Dict[str, Any]:
    queries = _get_raw_analytics_queries()
    return queries.get_executive_kpis(
        departments=_to_list(departments),
        sources=_to_list(sources),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_monthly_hiring_trends(
    departments: Optional[Tuple[str, ...]] = None,
    sources: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_monthly_hiring_trends(
        departments=_to_list(departments),
        sources=_to_list(sources),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_recruiting_funnel_summary(
    departments: Optional[Tuple[str, ...]] = None,
    sources: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_recruiting_funnel_summary(
        departments=_to_list(departments),
        sources=_to_list(sources),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_stage_duration_breakdown(
    departments: Optional[Tuple[str, ...]] = None,
    sources: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_stage_duration_breakdown(
        departments=_to_list(departments),
        sources=_to_list(sources),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_source_performance(
    departments: Optional[Tuple[str, ...]] = None,
    sources: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_source_performance(
        departments=_to_list(departments),
        sources=_to_list(sources),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_department_metrics(
    departments: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_department_metrics(
        departments=_to_list(departments),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_workforce_demographics(
    departments: Optional[Tuple[str, ...]] = None,
    job_levels: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_workforce_demographics(
        departments=_to_list(departments),
        job_levels=_to_list(job_levels),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_attrition_analysis(
    departments: Optional[Tuple[str, ...]] = None,
    sources: Optional[Tuple[str, ...]] = None,
    job_levels: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_attrition_analysis(
        departments=_to_list(departments),
        sources=_to_list(sources),
        job_levels=_to_list(job_levels),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_engagement_by_tenure(
    departments: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_engagement_by_tenure(
        departments=_to_list(departments),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def _cached_retention_cohorts(
    departments: Optional[Tuple[str, ...]] = None,
) -> pd.DataFrame:
    queries = _get_raw_analytics_queries()
    return queries.get_retention_cohorts(
        departments=_to_list(departments),
    )


# -----------------------------------------------------------------------------
# Public Safe Wrappers (Copy Semantics for Caller Mutation Safety)
# -----------------------------------------------------------------------------

def get_cached_executive_kpis(
    departments: Optional[Sequence[str]] = None,
    sources: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    res = _cached_executive_kpis(_normalize_filter(departments), _normalize_filter(sources))
    return res.copy() if isinstance(res, dict) else res


def get_cached_monthly_hiring_trends(
    departments: Optional[Sequence[str]] = None,
    sources: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_monthly_hiring_trends(_normalize_filter(departments), _normalize_filter(sources)).copy()


def get_cached_recruiting_funnel_summary(
    departments: Optional[Sequence[str]] = None,
    sources: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_recruiting_funnel_summary(_normalize_filter(departments), _normalize_filter(sources)).copy()


# Alias requested in specifications
get_cached_funnel_metrics = get_cached_recruiting_funnel_summary


def get_cached_stage_duration_breakdown(
    departments: Optional[Sequence[str]] = None,
    sources: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_stage_duration_breakdown(_normalize_filter(departments), _normalize_filter(sources)).copy()


def get_cached_source_performance(
    departments: Optional[Sequence[str]] = None,
    sources: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_source_performance(_normalize_filter(departments), _normalize_filter(sources)).copy()


def get_cached_department_metrics(
    departments: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_department_metrics(_normalize_filter(departments)).copy()


def get_cached_workforce_demographics(
    departments: Optional[Sequence[str]] = None,
    job_levels: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_workforce_demographics(_normalize_filter(departments), _normalize_filter(job_levels)).copy()


def get_cached_attrition_analysis(
    departments: Optional[Sequence[str]] = None,
    sources: Optional[Sequence[str]] = None,
    job_levels: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_attrition_analysis(
        _normalize_filter(departments),
        _normalize_filter(sources),
        _normalize_filter(job_levels),
    ).copy()


def get_cached_engagement_by_tenure(
    departments: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_engagement_by_tenure(_normalize_filter(departments)).copy()


def get_cached_retention_cohorts(
    departments: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    return _cached_retention_cohorts(_normalize_filter(departments)).copy()


def clear_dashboard_cache() -> None:
    """Clears all cached analytical query data and filter options in Streamlit."""
    st.cache_data.clear()


# -----------------------------------------------------------------------------
# Cached Proxy Class Reused by Shared AnalyticsQueries Factory
# -----------------------------------------------------------------------------

class CachedAnalyticsQueries:
    """Transparent proxy delegating query calls to cached wrappers."""

    def __init__(self, raw: AnalyticsQueries):
        self._raw = raw

    @property
    def engine(self):
        return self._raw.engine

    @property
    def schema(self):
        return self._raw.schema

    def get_filter_options(self) -> Dict[str, List[str]]:
        return get_cached_filter_options()

    def get_executive_kpis(self, departments=None, sources=None) -> Dict[str, Any]:
        return get_cached_executive_kpis(departments=departments, sources=sources)

    def get_monthly_hiring_trends(self, departments=None, sources=None) -> pd.DataFrame:
        return get_cached_monthly_hiring_trends(departments=departments, sources=sources)

    def get_recruiting_funnel_summary(self, departments=None, sources=None) -> pd.DataFrame:
        return get_cached_recruiting_funnel_summary(departments=departments, sources=sources)

    def get_funnel_metrics(self, departments=None, sources=None) -> pd.DataFrame:
        return get_cached_funnel_metrics(departments=departments, sources=sources)

    def get_stage_duration_breakdown(self, departments=None, sources=None) -> pd.DataFrame:
        return get_cached_stage_duration_breakdown(departments=departments, sources=sources)

    def get_source_performance(self, departments=None, sources=None) -> pd.DataFrame:
        return get_cached_source_performance(departments=departments, sources=sources)

    def get_department_metrics(self, departments=None) -> pd.DataFrame:
        return get_cached_department_metrics(departments=departments)

    def get_workforce_demographics(self, departments=None, job_levels=None) -> pd.DataFrame:
        return get_cached_workforce_demographics(departments=departments, job_levels=job_levels)

    def get_attrition_analysis(self, departments=None, sources=None, job_levels=None) -> pd.DataFrame:
        return get_cached_attrition_analysis(departments=departments, sources=sources, job_levels=job_levels)

    def get_engagement_by_tenure(self, departments=None) -> pd.DataFrame:
        return get_cached_engagement_by_tenure(departments=departments)

    def get_retention_cohorts(self, departments=None) -> pd.DataFrame:
        return get_cached_retention_cohorts(departments=departments)


@st.cache_resource
def get_shared_analytics_queries() -> CachedAnalyticsQueries:
    """Returns a shared, cached AnalyticsQueries service with reusable warehouse engine."""
    raw = _get_raw_analytics_queries()
    return CachedAnalyticsQueries(raw)
