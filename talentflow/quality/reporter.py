"""Generates structured Data Quality summary reports."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from talentflow.config import config, logger
from talentflow.quality.validator import QualityCheckResult

class QualityReporter:
    """Formats, summarizes, and exports data quality check outcomes."""

    @staticmethod
    def to_dataframe(results: List[QualityCheckResult]) -> pd.DataFrame:
        """Converts results into an analysis-ready DataFrame."""
        return pd.DataFrame([r.__dict__ for r in results])

    @staticmethod
    def generate_summary(results: List[QualityCheckResult]) -> Dict[str, Any]:
        """Calculates aggregate quality metrics."""
        total = len(results)
        passed = sum(1 for r in results if r.status == "PASS")
        failed = sum(1 for r in results if r.status == "FAIL")
        pass_rate = round((passed / total * 100.0), 1) if total > 0 else 0.0
        
        checks_by_type = {}
        for r in results:
            checks_by_type[r.check_type] = checks_by_type.get(r.check_type, 0) + 1

        failed_checks = [
            {
                "check_name": r.check_name,
                "dataset": r.dataset,
                "column": r.column,
                "check_type": r.check_type,
                "failed_records": r.failed_records,
                "failure_percentage": r.failure_percentage,
                "details": r.details,
            }
            for r in results if r.status == "FAIL"
        ]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "pass_rate_pct": pass_rate,
            "checks_by_type": checks_by_type,
            "failed_checks_detail": failed_checks,
        }

    @classmethod
    def save_report(cls, results: List[QualityCheckResult], output_dir: Path | None = None) -> Path:
        """Writes both JSON and Markdown reports to disk."""
        target_dir = output_dir or config.reports_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        summary = cls.generate_summary(results)

        # 1. JSON Export
        json_path = target_dir / "data_quality_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # 2. Markdown Export
        md_path = target_dir / "data_quality_report.md"
        df = cls.to_dataframe(results)
        
        md_content = f"""# TalentFlow Data Quality & Governance Audit Report

**Generated:** {summary['timestamp']} UTC  
**Overall Status:** {"🟢 HEALTHY" if summary['pass_rate_pct'] > 90 else "🔴 ATTENTION REQUIRED"}  
**Summary:** {summary['passed_checks']}/{summary['total_checks']} checks passed ({summary['pass_rate_pct']}%)

---

## 1. Executive Summary

| Metric | Value |
|---|---|
| Total Quality Assertions | {summary['total_checks']} |
| Successful Checks | {summary['passed_checks']} |
| Failed Assertions | {summary['failed_checks']} |
| Pass Rate | **{summary['pass_rate_pct']}%** |

### Checks by Category
"""
        for ctype, count in summary["checks_by_type"].items():
            md_content += f"- **{ctype}**: {count} tests\n"

        md_content += "\n## 2. Failed Checks & Controlled Data Quality Scenarios\n\n"
        if summary["failed_checks_detail"]:
            md_content += "| Dataset | Check Name | Check Type | Failed Records | Failure % | Remediation / Finding |\n"
            md_content += "|---|---|---|---|---|---|\n"
            for f in summary["failed_checks_detail"]:
                md_content += f"| `{f['dataset']}` | {f['check_name']} | `{f['check_type']}` | {f['failed_records']:,} | {f['failure_percentage']}% | {f['details']} |\n"
        else:
            md_content += "No quality failures detected. All checks passed.\n"

        md_content += "\n## 3. Full Test Results Matrix\n\n"
        md_content += df[["dataset", "check_name", "check_type", "status", "failed_records", "failure_percentage"]].to_markdown(index=False)
        md_content += "\n"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Saved Data Quality reports to {json_path} and {md_path}")
        return md_path
