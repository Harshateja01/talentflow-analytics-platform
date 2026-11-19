"""Helper service computing derived metrics and formatting indicators."""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

class KPIService:
    """Computes high-level talent acquisition and workforce health indicators."""

    @staticmethod
    def calculate_funnel_dropoff(funnel_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculates stage-by-stage drop-off percentages."""
        if funnel_df.empty:
            return []
        
        row = funnel_df.iloc[0]
        stages = [
            ("Applied", int(row.get("applied", 0))),
            ("Screen", int(row.get("screen", 0))),
            ("Technical Interview", int(row.get("technical_interview", 0))),
            ("Manager & Onsite", int(row.get("onsite_interview", 0))),
            ("Offer Extended", int(row.get("offer_extended", 0))),
            ("Hired", int(row.get("hired", 0))),
        ]

        result = []
        for i, (stage_name, count) in enumerate(stages):
            prev_count = stages[i - 1][1] if i > 0 else count
            conversion_pct = round((count / prev_count * 100.0), 1) if prev_count > 0 else 0.0
            dropoff_pct = round(100.0 - conversion_pct, 1) if i > 0 else 0.0
            overall_pct = round((count / stages[0][1] * 100.0), 1) if stages[0][1] > 0 else 0.0
            
            result.append({
                "stage": stage_name,
                "candidates": count,
                "stage_conversion_pct": conversion_pct,
                "stage_dropoff_pct": dropoff_pct,
                "cumulative_funnel_pct": overall_pct,
            })
        return result

    @staticmethod
    def calculate_source_roi(source_df: pd.DataFrame) -> pd.DataFrame:
        """Calculates estimated cost-per-hire and retention scores by channel."""
        if source_df.empty:
            return source_df
        
        df = source_df.copy()
        # Cost per hire estimation = (cost_per_posting * total_applications / 20) / hires
        df["cost_per_hire_estimate"] = (
            (df["cost_per_posting"] * (df["total_applications"] / 50.0)) / df["total_hires"].replace(0, np.nan)
        ).round(0).fillna(0)
        
        # 1-year retention score = 100 - churn_rate
        df["retention_rate_pct"] = (100.0 - df["employee_churn_rate_pct"]).round(1)
        return df
