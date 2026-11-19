"""Data Quality Validator executing comprehensive rules across datasets."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from talentflow.config import logger
from talentflow.data_generation.schemas import (
    STAGES_ORDER,
    OFFER_STATUSES,
    EMPLOYMENT_STATUSES,
    DEPARTMENTS,
)

@dataclass
class QualityCheckResult:
    check_name: str
    dataset: str
    column: Optional[str]
    check_type: str  # uniqueness, not_null, referential_integrity, accepted_values, date_sequence
    severity: str    # ERROR, WARNING
    status: str      # PASS, FAIL
    records_checked: int
    failed_records: int
    failure_percentage: float
    details: str

class DataQualityValidator:
    """Performs deep validation on raw and processed HR datasets."""

    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        self.datasets = datasets
        self.results: List[QualityCheckResult] = []

    def run_all_checks(self) -> List[QualityCheckResult]:
        """Execute the full suite of data quality validation checks."""
        self.results = []
        logger.info("Executing comprehensive Data Quality test suite...")

        self._check_uniqueness()
        self._check_not_null()
        self._check_accepted_values()
        self._check_date_sequences()
        self._check_referential_integrity()

        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        logger.info(f"Data Quality Suite Finished: {pass_count} Passed, {fail_count} Failed out of {len(self.results)} checks.")
        return self.results

    def _add_result(
        self,
        check_name: str,
        dataset: str,
        column: Optional[str],
        check_type: str,
        severity: str,
        records_checked: int,
        failed_records: int,
        details: str,
    ) -> None:
        fail_pct = round((failed_records / records_checked * 100.0), 2) if records_checked > 0 else 0.0
        status = "FAIL" if failed_records > 0 else "PASS"
        self.results.append(
            QualityCheckResult(
                check_name=check_name,
                dataset=dataset,
                column=column,
                check_type=check_type,
                severity=severity,
                status=status,
                records_checked=records_checked,
                failed_records=failed_records,
                failure_percentage=fail_pct,
                details=details,
            )
        )

    def _check_uniqueness(self) -> None:
        """Validate primary key uniqueness."""
        pk_map = {
            "candidates": "candidate_id",
            "applications": "application_id",
            "interviews": "interview_id",
            "offers": "offer_id",
            "employees": "employee_id",
            "engagement_surveys": "survey_id",
            "departments": "department_id",
            "recruiting_sources": "source_id",
        }
        for ds_name, pk_col in pk_map.items():
            if ds_name in self.datasets:
                df = self.datasets[ds_name]
                if pk_col in df.columns:
                    total = len(df)
                    dupes = df.duplicated(subset=[pk_col], keep=False).sum()
                    self._add_result(
                        check_name=f"PK Uniqueness on {ds_name}.{pk_col}",
                        dataset=ds_name,
                        column=pk_col,
                        check_type="uniqueness",
                        severity="ERROR",
                        records_checked=total,
                        failed_records=int(dupes),
                        details=f"Found {dupes} duplicate rows with non-unique {pk_col}" if dupes else "All primary keys are unique.",
                    )

    def _check_not_null(self) -> None:
        """Validate required non-null attributes."""
        not_null_map = {
            "candidates": ["candidate_id", "email", "created_at"],
            "applications": ["application_id", "candidate_id", "application_date", "department_id"],
            "interviews": ["interview_id", "application_id", "interview_date", "interview_round"],
            "offers": ["offer_id", "application_id", "offer_date", "offer_status"],
            "employees": ["employee_id", "candidate_id", "department_id", "hire_date", "employment_status"],
        }
        for ds_name, cols in not_null_map.items():
            if ds_name in self.datasets:
                df = self.datasets[ds_name]
                total = len(df)
                for col in cols:
                    if col in df.columns:
                        nulls = df[col].isnull().sum()
                        self._add_result(
                            check_name=f"Not-Null Check on {ds_name}.{col}",
                            dataset=ds_name,
                            column=col,
                            check_type="not_null",
                            severity="ERROR",
                            records_checked=total,
                            failed_records=int(nulls),
                            details=f"Detected {nulls} null or empty values in mandatory column {col}" if nulls else f"Column {col} has 0 null values.",
                        )

    def _check_accepted_values(self) -> None:
        """Validate categorical domains."""
        if "applications" in self.datasets:
            df = self.datasets["applications"]
            if "candidate_stage" in df.columns:
                invalid = (~df["candidate_stage"].isin(STAGES_ORDER)).sum()
                self._add_result(
                    check_name="Accepted Values: application candidate_stage",
                    dataset="applications",
                    column="candidate_stage",
                    check_type="accepted_values",
                    severity="ERROR",
                    records_checked=len(df),
                    failed_records=int(invalid),
                    details=f"Found {invalid} stages outside standard pipeline stages: {STAGES_ORDER}",
                )

        if "offers" in self.datasets:
            df = self.datasets["offers"]
            if "offer_status" in df.columns:
                invalid = (~df["offer_status"].isin(OFFER_STATUSES)).sum()
                self._add_result(
                    check_name="Accepted Values: offer offer_status",
                    dataset="offers",
                    column="offer_status",
                    check_type="accepted_values",
                    severity="ERROR",
                    records_checked=len(df),
                    failed_records=int(invalid),
                    details=f"Found {invalid} statuses outside valid domain: {OFFER_STATUSES}",
                )

        if "employees" in self.datasets:
            df = self.datasets["employees"]
            if "employment_status" in df.columns:
                invalid = (~df["employment_status"].isin(EMPLOYMENT_STATUSES)).sum()
                self._add_result(
                    check_name="Accepted Values: employee employment_status",
                    dataset="employees",
                    column="employment_status",
                    check_type="accepted_values",
                    severity="ERROR",
                    records_checked=len(df),
                    failed_records=int(invalid),
                    details=f"Found {invalid} employment statuses outside valid domain: {EMPLOYMENT_STATUSES}",
                )

    def _check_date_sequences(self) -> None:
        """Validate temporal chronological logic."""
        # 1. Interview Date must be >= Application Date
        if "applications" in self.datasets and "interviews" in self.datasets:
            app_df = self.datasets["applications"][["application_id", "application_date"]].dropna()
            int_df = self.datasets["interviews"][["interview_id", "application_id", "interview_date"]].dropna()
            merged = int_df.merge(app_df, on="application_id", how="inner")
            
            # Compare dates
            invalid_seq = (pd.to_datetime(merged["interview_date"]) < pd.to_datetime(merged["application_date"])).sum()
            self._add_result(
                check_name="Chronological Order: interview_date >= application_date",
                dataset="interviews",
                column="interview_date",
                check_type="date_sequence",
                severity="ERROR",
                records_checked=len(merged),
                failed_records=int(invalid_seq),
                details=f"Identified {invalid_seq} interviews scheduled prior to application date",
            )

        # 2. Termination Date must be >= Hire Date for employees
        if "employees" in self.datasets:
            emp_df = self.datasets["employees"].dropna(subset=["hire_date", "termination_date"])
            if len(emp_df) > 0:
                invalid_term = (pd.to_datetime(emp_df["termination_date"]) < pd.to_datetime(emp_df["hire_date"])).sum()
                self._add_result(
                    check_name="Chronological Order: termination_date >= hire_date",
                    dataset="employees",
                    column="termination_date",
                    check_type="date_sequence",
                    severity="ERROR",
                    records_checked=len(emp_df),
                    failed_records=int(invalid_term),
                    details=f"Identified {invalid_term} employees with termination date before hire date",
                )

    def _check_referential_integrity(self) -> None:
        """Validate foreign key relationships across datasets."""
        # 1. applications.candidate_id -> candidates.candidate_id
        if "applications" in self.datasets and "candidates" in self.datasets:
            app_df = self.datasets["applications"]
            cand_df = self.datasets["candidates"]
            valid_cands = set(cand_df["candidate_id"].dropna().unique())
            orphans = (~app_df["candidate_id"].isin(valid_cands)).sum()
            self._add_result(
                check_name="FK Integrity: applications.candidate_id in candidates",
                dataset="applications",
                column="candidate_id",
                check_type="referential_integrity",
                severity="ERROR",
                records_checked=len(app_df),
                failed_records=int(orphans),
                details=f"Identified {orphans} orphaned applications with unresolvable candidate_id",
            )

        # 2. applications.department_id -> departments.department_id
        if "applications" in self.datasets and "departments" in self.datasets:
            app_df = self.datasets["applications"]
            dept_df = self.datasets["departments"]
            valid_depts = set(dept_df["department_id"].dropna().unique())
            invalid_depts = (~app_df["department_id"].isin(valid_depts)).sum()
            self._add_result(
                check_name="FK Integrity: applications.department_id in departments",
                dataset="applications",
                column="department_id",
                check_type="referential_integrity",
                severity="WARNING",
                records_checked=len(app_df),
                failed_records=int(invalid_depts),
                details=f"Identified {invalid_depts} applications with inconsistent or missing department_id",
            )
