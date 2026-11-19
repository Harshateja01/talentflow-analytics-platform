"""Tests for AI insights module and deterministic fallback."""

import pytest
from talentflow.ai_insights.engine import AIInsightsEngine
from talentflow.ai_insights.prompts import SUPPORTED_QUESTIONS

def test_ai_insights_supported_questions():
    engine = AIInsightsEngine()
    
    for q_key in SUPPORTED_QUESTIONS.keys():
        result = engine.analyze_question(q_key)
        assert "question_key" in result
        assert "question_label" in result
        assert "summary" in result
        assert len(result["summary"]) > 20
        assert "engine" in result

def test_ai_insights_invalid_question():
    engine = AIInsightsEngine()
    with pytest.raises(ValueError):
        engine.analyze_question("unknown_unsupported_question_123")
