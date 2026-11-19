"""Predefined analytics queries against the marts layer."""

from typing import Dict, Any, List
import pandas as pd

from talentflow.config import config, logger
from talentflow.warehouse import get_warehouse_engine

class AnalyticsQueries:
    """Provides controlled, curated analytical queries against the analytics warehouse."""

    def __init__(self):
        self.engine = get_warehouse_engine()
        self.schema = config.bq_analytics_dataset if config.is_gcp_mode() else "talentflow_analytics"

    def get_executive_kpis(self) -> Dict[str, Any]:
        """Aggregate high-level executive KPIs."""
        query = f"""
        with apps as (
            select
                count(application_id) as total_applications,
                sum(stage_offer) as total_offers,
                sum(stage_hired) as total_hires,
                avg(total_time_to_hire_days) as avg_time_to_hire_days
            from {self.schema}.fct_recruiting_pipeline
        ),
        workforce as (
            select
                count(employee_id) as total_employees,
                sum(is_active) as active_headcount,
                sum(is_attrition) as total_attrition
            from {self.schema}.fct_employee_lifecycle
        )
        select
            a.total_applications,
            a.total_offers,
            a.total_hires,
            round(a.avg_time_to_hire_days, 1) as avg_time_to_hire_days,
            round(a.total_hires * 100.0 / nullif(a.total_offers, 0), 1) as offer_acceptance_rate_pct,
            w.active_headcount,
            w.total_attrition,
            round(w.total_attrition * 100.0 / nullif(w.total_employees, 0), 1) as attrition_rate_pct
        from apps a cross join workforce w
        """
        df = self.engine.execute_query(query)
        if df.empty:
            return {}
        return df.iloc[0].to_dict()

    def get_monthly_hiring_trends(self) -> pd.DataFrame:
        """Monthly hiring and application volume trends."""
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
        group by application_month
        order by application_month asc
        """
        return self.engine.execute_query(query)

    def get_recruiting_funnel_summary(self) -> pd.DataFrame:
        """Overall candidate conversion through the recruiting funnel."""
        query = f"""
        select
            sum(stage_applied) as applied,
            sum(stage_screen) as screen,
            sum(stage_tech) as technical_interview,
            sum(stage_onsite) as onsite_interview,
            sum(stage_offer) as offer_extended,
            sum(stage_hired) as hired
        from {self.schema}.fct_recruiting_pipeline
        """
        return self.engine.execute_query(query)

    def get_stage_duration_breakdown(self) -> pd.DataFrame:
        """Average duration spent in each recruitment phase."""
        query = f"""
        select
            department_name,
            round(avg(days_app_to_screen), 1) as avg_app_to_screen_days,
            round(avg(days_screen_to_tech), 1) as avg_screen_to_tech_days,
            round(avg(days_tech_to_onsite), 1) as avg_tech_to_onsite_days,
            round(avg(days_onsite_to_offer), 1) as avg_onsite_to_offer_days,
            round(avg(total_time_to_hire_days), 1) as avg_total_time_to_hire_days
        from {self.schema}.fct_recruiting_pipeline
        where stage_hired = 1
        group by department_name
        order by avg_total_time_to_hire_days desc
        """
        return self.engine.execute_query(query)

    def get_source_performance(self) -> pd.DataFrame:
        """Performance breakdown by recruiting channel."""
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

    def get_department_metrics(self) -> pd.DataFrame:
        """Department dimension and workforce summary."""
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
        order by active_headcount desc
        """
        return self.engine.execute_query(query)

    def get_workforce_demographics(self) -> pd.DataFrame:
        """Workforce distribution by location, job level, and tenure band."""
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
        group by location, job_level, tenure_band
        order by employee_count desc
        """
        return self.engine.execute_query(query)

    def get_attrition_analysis(self) -> pd.DataFrame:
        """Attrition segment analysis."""
        query = f"""
        select
            department_name,
            recruiting_source,
            attrition_type,
            attrition_risk_segment,
            count(employee_id) as departures,
            round(avg(tenure_months), 1) as avg_tenure_months,
            round(avg(avg_engagement_score), 2) as avg_engagement_before_exit
        from {self.schema}.fct_employee_attrition
        group by department_name, recruiting_source, attrition_type, attrition_risk_segment
        order by departures desc
        """
        return self.engine.execute_query(query)

    def get_engagement_by_tenure(self) -> pd.DataFrame:
        """Average employee engagement and sentiment across tenure bands."""
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
        where avg_engagement_score is not null
        group by tenure_band
        order by sample_size desc
        """
        return self.engine.execute_query(query)
