"""AI Insights Engine with controlled queries and safe LLM / rule-based fallback."""

from typing import Dict, Any, Tuple
import pandas as pd

from talentflow.config import config, logger
from talentflow.analytics.queries import AnalyticsQueries
from talentflow.ai_insights.prompts import SUPPORTED_QUESTIONS, SYSTEM_INSTRUCTION
from talentflow.ai_insights.fallback import DeterministicInsightsFallback

class AIInsightsEngine:
    """Natural Language Analytics interface for HR leaders and Talent Partners."""

    def __init__(self):
        self.queries = AnalyticsQueries()
        self.has_gemini = bool(config.gemini_api_key and config.gemini_api_key.strip())

    def analyze_question(self, question_key: str) -> Dict[str, Any]:
        """Executes predefined query for the selected analytical intent and synthesizes insights."""
        if question_key not in SUPPORTED_QUESTIONS:
            raise ValueError(f"Unsupported question key: '{question_key}'. Choose from: {list(SUPPORTED_QUESTIONS.keys())}")

        q_info = SUPPORTED_QUESTIONS[question_key]
        query_method_name = f"get_{q_info['query_key']}"
        query_method = getattr(self.queries, query_method_name, None)

        if not query_method:
            raise AttributeError(f"Query method {query_method_name} not found on AnalyticsQueries.")

        # Execute approved query
        df = query_method()

        # Generate Insights (Gemini if key is present, otherwise deterministic fallback)
        llm_used = False
        summary_text = ""

        if self.has_gemini:
            try:
                from google import genai
                client = genai.Client(api_key=config.gemini_api_key)
                prompt = f"""
{SYSTEM_INSTRUCTION}

Question: {q_info['label']}

Data Context (Markdown Table):
{df.to_markdown(index=False)}

Please provide a concise, high-impact executive summary for HR leadership.
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                if response and response.text:
                    summary_text = response.text
                    llm_used = True
            except Exception as e:
                logger.warning(f"Gemini API invocation failed ({e}). Falling back to deterministic rules engine.")

        if not summary_text:
            fallback_method_name = f"summarize_{question_key}"
            fallback_method = getattr(DeterministicInsightsFallback, fallback_method_name, None)
            if fallback_method:
                summary_text = fallback_method(df)
            else:
                summary_text = f"Insights for **{q_info['label']}** generated based on {len(df)} records."

        return {
            "question_key": question_key,
            "question_label": q_info["label"],
            "description": q_info["description"],
            "data": df,
            "summary": summary_text,
            "llm_used": llm_used,
            "engine": "Gemini 2.5 Flash" if llm_used else "Deterministic HR Analytics Engine (Rule-based Fallback)",
        }
