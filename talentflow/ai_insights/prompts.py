"""Predefined analytical intent mapping and query definitions."""

from typing import Dict, Any, List

SUPPORTED_QUESTIONS: Dict[str, Dict[str, Any]] = {
    "funnel_bottlenecks": {
        "label": "What are the main recruiting funnel bottlenecks?",
        "description": "Identifies stages with the sharpest candidate drop-off and longest stage transition latencies.",
        "query_key": "recruiting_funnel_summary",
    },
    "highest_conversion_sources": {
        "label": "Which recruiting sources have the highest conversion?",
        "description": "Ranks acquisition channels by application-to-hire conversion and offer acceptance rates.",
        "query_key": "source_performance",
    },
    "high_attrition_departments": {
        "label": "Which departments have higher attrition?",
        "description": "Analyzes turnover rates, average tenure, and departure timing by department.",
        "query_key": "department_metrics",
    },
    "hiring_cycle_factors": {
        "label": "What factors are associated with longer hiring cycles?",
        "description": "Evaluates days to hire by department, interview round durations, and candidate feedback.",
        "query_key": "stage_duration_breakdown",
    },
    "latest_period_changes": {
        "label": "What changed in the latest reporting period?",
        "description": "Compares recent monthly hiring and application velocity with prior quarterly trends.",
        "query_key": "monthly_hiring_trends",
    },
}

SYSTEM_INSTRUCTION = """
You are a Principal HR & People Analytics Intelligence Advisor for TalentFlow Analytics.
Your objective is to provide clear, actionable, executive-ready insights based strictly
on the structured warehouse metric data provided to you.

Rules:
1. Ground every claim directly in the provided metric tables and numbers.
2. Differentiate clearly between correlation and causation (e.g. higher tenure for referrals is an observed correlation, not necessarily direct causation).
3. Be concise: use bullet points, bold key numbers, and highlight 2-3 strategic recommendations.
4. If asked about data outside the provided tables, state clearly that the metrics are not present in the current warehouse extract.
"""
