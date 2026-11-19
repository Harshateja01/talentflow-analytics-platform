"""Predefined analytics queries against the marts layer supporting global filtering."""

from typing import Dict, Any, List, Optional
import pandas as pd

from talentflow.config import config, logger
from talentflow.warehouse import get_warehouse_engine

class AnalyticsQueries:
    """Provides controlled, curated analytical queries against the analytics warehouse."""

    def __init__(self):
        self.engine = get_warehouse_engine()
        self.schema = config.bq_analytics_dataset if config.is_gcp_mode() else "talentflow_analytics"

    def _build_where_clause(
        self,
        departments: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        job_levels: Optional[List[str]] = None,
        dept_col: str = "department_name",
        source_col: str = "recruiting_source",
        level_col: str = "job_level",
    ) -> str:
        """Constructs sanitized SQL WHERE conditions for active filters."""
        conditions = []
        if departments:
            escaped = [d.replace("'", "''") for d in departments]
            conditions.append(f"{dept_col} in ({', '.join(f"'{d}'" for d in escaped)})")
        if sources:
            escaped = [s.replace("'", "''") for s in sources]
            conditions.append(f"{source_col} in ({', '.join(f"'{s}'" for s in escaped)})")
        if job_levels:
            escaped = [j.replace("'", "''") for j in job_levels]
            conditions.append(f"{level_col} in ({', '.join(f"'{j}'" for j in escaped)})")

        return f"where {' and '.join(conditions)}" if conditions else ""

    def get_filter_options(self) -> Dict[str, List[str]]:
        """Returns distinct filter values available in the analytics warehouse."""
        try:
            depts_df = self.engine.execute_query(f"select department_name from {self.schema}.dim_department order by department_name")
            sources_df = self.engine.execute_query(f"select source_name from {self.schema}.dim_recruiting_source order by source_name")
            levels_df = self.engine.execute_query(f"select distinct job_level from {self.schema}.fct_employee_lifecycle order by job_level")
            
            return {
                "departments": depts_df["department_name"].tolist() if not depts_df.empty else [],
                "sources": sources_df["source_name"].tolist() if not sources_df.empty else [],
                "job_levels": levels_df["job_level"].dropna().tolist() if not levels_df.empty else [],
            }
        except Exception as e:
            logger.warning(f"Unable to fetch filter options from warehouse: {e}")
            return {"departments": [], "sources": [], "job_levels": []}

    def get_executive_kpis(
        self,
        departments: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Aggregate high-level executive KPIs with optional filtering."""
        pipe_where = self._build_where_clause(departments=departments, sources=sources)
        emp_where = self._build_where_clause(departments=departments, sources=sources)
        
        query = f"""
        with apps as (
            select
                count(application_id) as total_applications,
                sum(stage_offer) as total_offers,
                sum(stage_hired) as total_hires,
                avg(total_time_to_hire_days) as avg_time_to_hire_days
            from {self.schema}.fct_recruiting_pipeline
            {pipe_where}
        ),
        workforce as (
            select
                count(employee_id) as total_employees,
                sum(is_active) as active_headcount,
                sum(is_attrition) as total_attrition
            from {self.schema}.fct_employee_lifecycle
            {emp_where}
        )
        select
            coalesce(a.total_applications, 0) as total_applications,
            coalesce(a.total_offers, 0) as total_offers,
            coalesce(a.total_hires, 0) as total_hires,
            round(coalesce(a.avg_time_to_hire_days, 0), 1) as avg_time_to_hire_days,
            round(coalesce(a.total_hires, 0) * 100.0 / nullif(a.total_offers, 0), 1) as offer_acceptance_rate_pct,
            coalesce(w.active_headcount, 0) as active_headcount,
            coalesce(w.total_attrition, 0) as total_attrition,
            round(coalesce(w.total_attrition, 0) * 100.0 / nullif(w.total_employees, 0), 1) as attrition_rate_pct
        from apps a cross join workforce w
        """
        df = self.engine.execute_query(query)
        if df.empty:
            return {}
        return df.iloc[0].to_dict()

    def get_monthly_hiring_trends(
        self,
        departments: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Monthly hiring and application volume trends."""
        where_clause = self._build_where_clause(departments=departments, sources=sources)
        query = f"""
        select
            application_month,
            sum(total_applications) as applications,
            sum(total_screens) as screens,
            sum(total_tech_interviews) as tech_interviews,
            sum(total_onsites) as onsites,
            sum(total_offers_extended) as offers_extended,
            sum(total_hires) as hires,
            round(avg(avg_time_to_hire_days), 1) as avg_time_to_hire_days
        from {self.schema}.mart_recruiting_kpis
        {where_clause}
        group by application_month
        order by application_month asc
        """
        return self.engine.execute_query(query)

    def get_recruiting_funnel_summary(
        self,
        departments: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Overall candidate conversion through the recruiting funnel."""
        where_clause = self._build_where_clause(departments=departments, sources=sources)
        query = f"""
        select
            sum(stage_applied) as applied,
            sum(stage_screen) as screen,
            sum(stage_tech) as technical_interview,
            sum(stage_onsite) as onsite_interview,
            sum(stage_offer) as offer_extended,
            sum(stage_hired) as hired
        from {self.schema}.fct_recruiting_pipeline
        {where_clause}
        """
        return self.engine.execute_query(query)

    def get_stage_duration_breakdown(
        self,
        departments: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Average duration spent in each recruitment phase."""
        cond = ["stage_hired = 1"]
        if departments:
            escaped = [d.replace("'", "''") for d in departments]
            cond.append(f"department_name in ({', '.join(f"'{d}'" for d in escaped)})")
        if sources:
            escaped = [s.replace("'", "''") for s in sources]
            cond.append(f"recruiting_source in ({', '.join(f"'{s}'" for s in escaped)})")
        
        where_clause = f"where {' and '.join(cond)}"
        query = f"""
        select
            department_name,
            round(avg(days_app_to_screen), 1) as avg_app_to_screen_days,
            round(avg(days_screen_to_tech), 1) as avg_screen_to_tech_days,
            round(avg(days_tech_to_onsite), 1) as avg_tech_to_onsite_days,
            round(avg(days_onsite_to_offer), 1) as avg_onsite_to_offer_days,
            round(avg(total_time_to_hire_days), 1) as avg_total_time_to_hire_days
        from {self.schema}.fct_recruiting_pipeline
        {where_clause}
        group by department_name
        order by avg_total_time_to_hire_days desc
        """
        return self.engine.execute_query(query)

    def get_source_performance(
        self,
        departments: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Performance breakdown by recruiting channel with live filtering across pipeline & workforce."""
        if not departments and not sources:
            # Fast path against dim mart
            query = f"""
            select
                source_name,
                source_channel,
                cost_per_posting,
                total_applications,
                total_offers_extended,
                total_hires,
                app_to_hire_conversion_pct,
                offer_acceptance_rate_pct,
                avg_time_to_hire_days,
                avg_candidate_experience_rating,
                employees_churned,
                employee_churn_rate_pct,
                avg_employee_tenure_months,
                avg_employee_engagement
            from {self.schema}.dim_recruiting_source
            order by total_hires desc
            """
            return self.engine.execute_query(query)
        
        # Filtered dynamically from fact tables
        p_where = self._build_where_clause(departments=departments, sources=sources)
        e_where = self._build_where_clause(departments=departments, sources=sources)

        query = f"""
        with p as (
            select
                recruiting_source,
                count(application_id) as total_applications,
                sum(stage_offer) as total_offers_extended,
                sum(stage_hired) as total_hires,
                avg(total_time_to_hire_days) as avg_time_to_hire_days,
                avg(avg_candidate_experience_score) as avg_candidate_experience_rating
            from {self.schema}.fct_recruiting_pipeline
            {p_where}
            group by recruiting_source
        ),
        e as (
            select
                recruiting_source,
                count(employee_id) as employees_hired,
                sum(is_attrition) as employees_churned,
                avg(tenure_months) as avg_employee_tenure_months,
                avg(avg_engagement_score) as avg_employee_engagement
            from {self.schema}.fct_employee_lifecycle
            {e_where}
            group by recruiting_source
        )
        select
            s.source_name,
            s.source_channel,
            s.cost_per_posting,
            coalesce(p.total_applications, 0) as total_applications,
            coalesce(p.total_offers_extended, 0) as total_offers_extended,
            coalesce(p.total_hires, 0) as total_hires,
            round(coalesce(p.total_hires, 0) * 100.0 / nullif(p.total_applications, 0), 2) as app_to_hire_conversion_pct,
            round(coalesce(p.total_hires, 0) * 100.0 / nullif(p.total_offers_extended, 0), 1) as offer_acceptance_rate_pct,
            round(coalesce(p.avg_time_to_hire_days, 0), 1) as avg_time_to_hire_days,
            round(coalesce(p.avg_candidate_experience_rating, 0), 2) as avg_candidate_experience_rating,
            coalesce(e.employees_churned, 0) as employees_churned,
            round(coalesce(e.employees_churned, 0) * 100.0 / nullif(e.employees_hired, 0), 1) as employee_churn_rate_pct,
            round(coalesce(e.avg_employee_tenure_months, 0), 1) as avg_employee_tenure_months,
            round(coalesce(e.avg_employee_engagement, 0), 2) as avg_employee_engagement
        from {self.schema}.dim_recruiting_source s
        left join p on s.source_name = p.recruiting_source
        left join e on s.source_name = e.recruiting_source
        where coalesce(p.total_applications, 0) > 0 or coalesce(e.employees_hired, 0) > 0
        order by total_hires desc
        """
        return self.engine.execute_query(query)

    def get_department_metrics(self, departments: Optional[List[str]] = None) -> pd.DataFrame:
        """Department dimension and workforce summary."""
        where_clause = ""
        if departments:
            escaped = [d.replace("'", "''") for d in departments]
            where_clause = f"where department_name in ({', '.join(f"'{d}'" for d in escaped)})"

        query = f"""
        select
            department_id,
            department_name,
            department_lead,
            cost_center,
            active_headcount,
            total_historic_hires,
            total_attrition,
            historic_attrition_rate_pct,
            avg_tenure_months,
            avg_performance_rating,
            avg_department_engagement
        from {self.schema}.dim_department
        {where_clause}
        order by active_headcount desc
        """
        return self.engine.execute_query(query)

    def get_workforce_demographics(
        self,
        departments: Optional[List[str]] = None,
        job_levels: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Workforce distribution by location, job level, and tenure band."""
        where_clause = self._build_where_clause(departments=departments, job_levels=job_levels)
        query = f"""
        select
            location,
            job_level,
            tenure_band,
            count(employee_id) as employee_count,
            sum(is_active) as active_count,
            sum(is_attrition) as attrition_count,
            round(avg(base_salary), 0) as avg_salary,
            round(avg(avg_engagement_score), 2) as avg_engagement
        from {self.schema}.fct_employee_lifecycle
        {where_clause}
        group by location, job_level, tenure_band
        order by employee_count desc
        """
        return self.engine.execute_query(query)

    def get_attrition_analysis(
        self,
        departments: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        job_levels: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Attrition segment analysis."""
        where_clause = self._build_where_clause(departments=departments, sources=sources, job_levels=job_levels)
        query = f"""
        select
            department_name,
            recruiting_source,
            job_level,
            attrition_type,
            attrition_risk_segment,
            count(employee_id) as departures,
            round(avg(tenure_months), 1) as avg_tenure_months,
            round(avg(avg_engagement_score), 2) as avg_engagement_before_exit
        from {self.schema}.fct_employee_attrition
        {where_clause}
        group by department_name, recruiting_source, job_level, attrition_type, attrition_risk_segment
        order by departures desc
        """
        return self.engine.execute_query(query)

    def get_engagement_by_tenure(
        self,
        departments: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Average employee engagement and sentiment across tenure bands."""
        cond = ["avg_engagement_score is not null"]
        if departments:
            escaped = [d.replace("'", "''") for d in departments]
            cond.append(f"department_name in ({', '.join(f"'{d}'" for d in escaped)})")
        
        where_clause = f"where {' and '.join(cond)}"
        query = f"""
        select
            tenure_band,
            count(employee_id) as sample_size,
            round(avg(avg_engagement_score), 2) as avg_engagement,
            round(avg(avg_satisfaction_score), 2) as avg_satisfaction,
            round(avg(avg_wlb_score), 2) as avg_work_life_balance,
            round(avg(avg_career_growth_score), 2) as avg_career_growth,
            round(avg(avg_manager_effectiveness_score), 2) as avg_manager_effectiveness
        from {self.schema}.fct_employee_lifecycle
        {where_clause}
        group by tenure_band
        order by sample_size desc
        """
        return self.engine.execute_query(query)

    def get_retention_cohorts(self, departments: Optional[List[str]] = None) -> pd.DataFrame:
        """Cohort retention rates by department and hire cohort month."""
        where_clause = ""
        if departments:
            escaped = [d.replace("'", "''") for d in departments]
            where_clause = f"where department_id in (select department_id from {self.schema}.dim_department where department_name in ({', '.join(f"'{d}'" for d in escaped)}))"

        query = f"""
        select
            cohort_month,
            department_id,
            sum(cohort_size) as cohort_size,
            sum(retained_90_days_count) as retained_90d,
            sum(retained_180_days_count) as retained_180d,
            sum(retained_365_days_count) as retained_365d,
            round(sum(retained_90_days_count) * 100.0 / nullif(sum(cohort_size), 0), 1) as retention_rate_90d_pct,
            round(sum(retained_180_days_count) * 100.0 / nullif(sum(cohort_size), 0), 1) as retention_rate_180d_pct,
            round(sum(retained_365_days_count) * 100.0 / nullif(sum(cohort_size), 0), 1) as retention_rate_365d_pct
        from talentflow_staging.int_employee_retention
        {where_clause}
        group by cohort_month, department_id
        order by cohort_month desc
        """
        try:
            return self.engine.execute_query(query)
        except Exception:
            # Fallback if int_employee_retention is queried in analytics schema
            return pd.DataFrame()
