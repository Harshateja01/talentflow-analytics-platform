"""Synthetic Data Generator for TalentFlow.

Produces high-fidelity synthetic recruiting, candidate, application,
interview, offer, employee, and engagement survey datasets with
realistic relational integrity and controlled data-quality anomalies.
"""

import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

from talentflow.config import config, logger
from talentflow.data_generation.schemas import (
    DEPARTMENTS,
    RECRUITING_SOURCES,
    LOCATIONS,
    JOB_LEVELS,
    JOB_TITLES,
    EDUCATION_LEVELS,
    OFFER_STATUSES,
    DECLINE_REASONS,
    EMPLOYMENT_STATUSES,
)

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Avery",
    "Michael", "Sarah", "David", "Emily", "James", "Emma", "Daniel", "Olivia", "Matthew", "Sophia",
    "Jessica", "Andrew", "Priya", "Rahul", "Wei", "Mei", "Carlos", "Elena", "Kwame", "Amara",
    "Dmitry", "Fatima", "Tariq", "Hana", "Lucas", "Chloe", "Mateo", "Camila", "Liam", "Mia",
    "Benjamin", "Harper", "Ethan", "Evelyn", "Alexander", "Abigail", "Henry", "Emily", "Sebastian", "Elizabeth"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "proton.me", "hey.com"]

class SyntheticDataGenerator:
    """Generates synthetic HR and recruiting datasets with controlled anomalies."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.base_date = datetime(2023, 1, 1)
        self.end_date = datetime(2025, 12, 31)

    def _random_date(self, start: datetime, end: datetime) -> datetime:
        delta = end - start
        random_days = random.randint(0, max(0, int(delta.total_seconds() // 86400)))
        return start + timedelta(days=random_days)

    def generate_departments(self) -> pd.DataFrame:
        """Generate departments dimension dataset."""
        return pd.DataFrame(DEPARTMENTS)

    def generate_recruiting_sources(self) -> pd.DataFrame:
        """Generate recruiting sources dimension dataset."""
        return pd.DataFrame(RECRUITING_SOURCES)

    def generate_candidates(self, num_records: int = 5000) -> pd.DataFrame:
        """Generate candidate pool."""
        logger.info(f"Generating {num_records} candidates...")
        records = []
        for i in range(1, num_records + 1):
            cand_id = f"CAN-{i:05d}"
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            domain = random.choice(EMAIL_DOMAINS)
            email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 999)}@{domain}"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            loc = random.choice(LOCATIONS)
            edu = random.choices(
                EDUCATION_LEVELS, weights=[0.55, 0.25, 0.05, 0.08, 0.07], k=1
            )[0]
            yoe = int(np.clip(np.random.gamma(shape=3.0, scale=2.0), 0, 30))
            created_at = self._random_date(self.base_date, self.end_date - timedelta(days=90))

            records.append({
                "candidate_id": cand_id,
                "first_name": fn,
                "last_name": ln,
                "email": email,
                "phone": phone,
                "location": loc,
                "highest_education": edu,
                "years_of_experience": yoe,
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        df = pd.DataFrame(records)
        
        # Inject controlled data quality anomalies
        # 1. Null / missing phone numbers (~1.5%)
        null_phone_idx = df.sample(frac=0.015, random_state=self.seed).index
        df.loc[null_phone_idx, "phone"] = None

        # 2. Duplicate candidate entries (~0.5%)
        dupe_rows = df.sample(n=int(num_records * 0.005), random_state=self.seed).copy()
        df = pd.concat([df, dupe_rows], ignore_index=True)

        return df

    def generate_all_datasets(
        self,
        num_candidates: int = 5000,
        num_applications: int = 6000,
        target_employees: int = 1500,
    ) -> Dict[str, pd.DataFrame]:
        """Generates all 8 related datasets maintaining relational and temporal integrity."""
        dept_df = self.generate_departments()
        source_df = self.generate_recruiting_sources()
        cand_df = self.generate_candidates(num_candidates)

        clean_cands = cand_df.drop_duplicates(subset=["candidate_id"]).to_dict("records")
        dept_ids = [d["department_id"] for d in DEPARTMENTS]
        source_names = [s["source_name"] for s in RECRUITING_SOURCES]

        logger.info(f"Generating applications and downstream lifecycle data for target ~{num_applications} apps...")

        applications = []
        interviews = []
        offers = []
        employees = []
        surveys = []

        app_counter = 1
        interview_counter = 1
        offer_counter = 1
        employee_counter = 1
        survey_counter = 1

        cand_idx = 0
        while app_counter <= num_applications and cand_idx < len(clean_cands):
            cand = clean_cands[cand_idx]
            cand_idx += 1
            cand_id = cand["candidate_id"]
            cand_created = datetime.strptime(cand["created_at"], "%Y-%m-%d %H:%M:%S")

            # A candidate may have 1 or 2 applications
            num_apps_for_cand = 2 if random.random() < 0.18 and app_counter < num_applications else 1

            for _ in range(num_apps_for_cand):
                if app_counter > num_applications:
                    break
                app_id = f"APP-{app_counter:06d}"
                dept_id = random.choice(dept_ids)
                job_title = random.choice(JOB_TITLES[dept_id])
                job_id = f"JOB-{dept_id}-{random.randint(10, 99)}"
                recruiting_source = random.choices(
                    source_names,
                    weights=[0.35, 0.20, 0.18, 0.10, 0.10, 0.05, 0.02],
                    k=1
                )[0]
                
                app_date = self._random_date(cand_created, cand_created + timedelta(days=45))
                if app_date > self.end_date:
                    app_date = self.end_date - timedelta(days=random.randint(10, 60))

                # Recruiting Funnel Progression Simulation
                # Stages: Applied -> Screen -> Technical -> Manager/Onsite -> Offer -> Hired
                reached_screen = random.random() < 0.70
                reached_tech = reached_screen and (random.random() < 0.58)
                reached_onsite = reached_tech and (random.random() < 0.55)
                reached_offer = reached_onsite and (random.random() < 0.52)

                app_status = "Applied"
                candidate_stage = "Applied"
                rejection_reason = None
                updated_at = app_date

                # Interview generation
                if reached_screen:
                    candidate_stage = "Screen"
                    screen_date = app_date + timedelta(days=random.randint(2, 6))
                    interviewer = f"EMP-{random.randint(100, 500):04d}"
                    screen_result = "Pass" if reached_tech else "Fail"
                    screen_score = random.randint(3, 5) if reached_tech else random.randint(1, 2)
                    candidate_exp_score = random.choices([3, 4, 5], weights=[0.2, 0.4, 0.4])[0]
                    
                    interviews.append({
                        "interview_id": f"INT-{interview_counter:06d}",
                        "application_id": app_id,
                        "interview_round": "Screen",
                        "interview_date": screen_date.strftime("%Y-%m-%d"),
                        "interviewer_id": interviewer,
                        "interview_result": screen_result,
                        "score": screen_score,
                        "candidate_feedback_score": candidate_exp_score,
                        "duration_minutes": 30,
                    })
                    interview_counter += 1
                    updated_at = screen_date

                if reached_tech:
                    candidate_stage = "Technical Interview"
                    tech_date = screen_date + timedelta(days=random.randint(4, 10))
                    tech_result = "Pass" if reached_onsite else "Fail"
                    tech_score = random.randint(3, 5) if reached_onsite else random.randint(1, 2)
                    candidate_exp_score = random.choices([3, 4, 5], weights=[0.15, 0.45, 0.40])[0]

                    interviews.append({
                        "interview_id": f"INT-{interview_counter:06d}",
                        "application_id": app_id,
                        "interview_round": "Technical",
                        "interview_date": tech_date.strftime("%Y-%m-%d"),
                        "interviewer_id": f"EMP-{random.randint(100, 500):04d}",
                        "interview_result": tech_result,
                        "score": tech_score,
                        "candidate_feedback_score": candidate_exp_score,
                        "duration_minutes": 60,
                    })
                    interview_counter += 1
                    updated_at = tech_date

                if reached_onsite:
                    candidate_stage = "Manager & Onsite"
                    onsite_date = tech_date + timedelta(days=random.randint(5, 14))
                    onsite_result = "Pass" if reached_offer else "Fail"
                    onsite_score = random.randint(4, 5) if reached_offer else random.randint(2, 3)
                    candidate_exp_score = random.choices([3, 4, 5], weights=[0.1, 0.4, 0.5])[0]

                    interviews.append({
                        "interview_id": f"INT-{interview_counter:06d}",
                        "application_id": app_id,
                        "interview_round": "Hiring Manager & Onsite",
                        "interview_date": onsite_date.strftime("%Y-%m-%d"),
                        "interviewer_id": f"EMP-{random.randint(10, 99):04d}",
                        "interview_result": onsite_result,
                        "score": onsite_score,
                        "candidate_feedback_score": candidate_exp_score,
                        "duration_minutes": 90,
                    })
                    interview_counter += 1
                    updated_at = onsite_date

                # Offer generation
                if reached_offer:
                    candidate_stage = "Offer"
                    offer_date = onsite_date + timedelta(days=random.randint(2, 7))
                    
                    # Acceptance probability varies by recruiting source (Referral > Direct > LinkedIn > Agency)
                    accept_prob = {
                        "Employee Referral": 0.88,
                        "Direct / Careers Site": 0.82,
                        "LinkedIn": 0.76,
                        "University Campus": 0.80,
                        "GitHub / Technical Community": 0.84,
                        "External Agency": 0.68,
                        "Job Boards (Indeed/Glassdoor)": 0.70,
                    }.get(recruiting_source, 0.75)

                    is_accepted = random.random() < accept_prob
                    offer_status = "Accepted" if is_accepted else "Declined"
                    
                    # 3% pending if recent
                    if (self.end_date - offer_date).days < 20 and random.random() < 0.25:
                        offer_status = "Pending"
                        is_accepted = False

                    resp_date = offer_date + timedelta(days=random.randint(2, 7))
                    base_salary = random.randint(95, 230) * 1000
                    bonus_pct = random.choice([0.10, 0.15, 0.20])
                    stock_units = random.randint(500, 6000)
                    decline_reason = random.choice(DECLINE_REASONS) if offer_status == "Declined" else None

                    offers.append({
                        "offer_id": f"OFF-{offer_counter:06d}",
                        "application_id": app_id,
                        "offer_date": offer_date.strftime("%Y-%m-%d"),
                        "offer_status": offer_status,
                        "base_salary": base_salary,
                        "bonus_pct": bonus_pct,
                        "stock_units": stock_units,
                        "offer_response_date": resp_date.strftime("%Y-%m-%d") if offer_status != "Pending" else None,
                        "decline_reason": decline_reason,
                    })
                    offer_counter += 1
                    updated_at = resp_date

                    if is_accepted:
                        app_status = "Hired"
                        candidate_stage = "Hired"
                        
                        # Employee record
                        hire_date = resp_date + timedelta(days=random.randint(14, 35))
                        job_level = random.choices(
                            JOB_LEVELS, weights=[0.20, 0.35, 0.25, 0.10, 0.04, 0.04, 0.02]
                        )[0]

                        # Employee status simulation based on tenure
                        tenure_days = (self.end_date - hire_date).days
                        # Annualized attrition ~ 12-15%, higher in Sales and CS, lower in Eng and Product
                        dept_attrition_factor = {
                            "DEP-001": 0.10, # Engineering
                            "DEP-002": 0.11, # Product
                            "DEP-003": 0.22, # Sales
                            "DEP-004": 0.16, # Marketing
                            "DEP-005": 0.19, # CS
                            "DEP-006": 0.09, # G&A
                            "DEP-007": 0.12, # HR
                            "DEP-008": 0.08, # Finance
                        }.get(dept_id, 0.14)

                        # Referrals stay longer!
                        if recruiting_source == "Employee Referral":
                            dept_attrition_factor *= 0.65
                        elif recruiting_source == "External Agency":
                            dept_attrition_factor *= 1.35

                        prob_terminated = min(0.40, (tenure_days / 365.0) * dept_attrition_factor)
                        
                        emp_id = f"EMP-{employee_counter:05d}"
                        emp_status = "Active"
                        term_date = None

                        if random.random() < prob_terminated and tenure_days > 60:
                            emp_status = random.choice(["Resigned", "Terminated"])
                            term_days_after_hire = random.randint(60, max(61, tenure_days))
                            term_date = (hire_date + timedelta(days=term_days_after_hire)).strftime("%Y-%m-%d")

                        perf_rating = random.choices(
                            [1, 2, 3, 4, 5],
                            weights=[0.05, 0.12, 0.55, 0.20, 0.08] if emp_status == "Active" else [0.20, 0.35, 0.35, 0.08, 0.02]
                        )[0]

                        employees.append({
                            "employee_id": emp_id,
                            "candidate_id": cand_id,
                            "application_id": app_id,
                            "department_id": dept_id,
                            "job_title": job_title,
                            "job_level": job_level,
                            "location": cand["location"],
                            "hire_date": hire_date.strftime("%Y-%m-%d"),
                            "employment_status": emp_status,
                            "termination_date": term_date,
                            "manager_id": f"EMP-{random.randint(1, 50):05d}" if employee_counter > 50 else None,
                            "performance_rating": perf_rating,
                        })

                        # Engagement survey for employees with at least 90 days tenure
                        if tenure_days >= 90:
                            survey_date = hire_date + timedelta(days=random.randint(80, min(tenure_days, 360)))
                            # Engagement is higher for active and high performers
                            base_eng = 4.2 if emp_status == "Active" else 2.6
                            if recruiting_source == "Employee Referral":
                                base_eng += 0.3
                            
                            eng_score = round(float(np.clip(np.random.normal(base_eng, 0.5), 1.0, 5.0)), 1)
                            sat_score = round(float(np.clip(np.random.normal(base_eng - 0.1, 0.6), 1.0, 5.0)), 1)
                            wlb_score = round(float(np.clip(np.random.normal(3.8, 0.7), 1.0, 5.0)), 1)
                            growth_score = round(float(np.clip(np.random.normal(base_eng - 0.2, 0.6), 1.0, 5.0)), 1)
                            mgr_score = round(float(np.clip(np.random.normal(4.0, 0.5), 1.0, 5.0)), 1)

                            surveys.append({
                                "survey_id": f"SRV-{survey_counter:06d}",
                                "employee_id": emp_id,
                                "survey_date": survey_date.strftime("%Y-%m-%d"),
                                "engagement_score": eng_score,
                                "satisfaction_score": sat_score,
                                "work_life_balance_score": wlb_score,
                                "career_growth_score": growth_score,
                                "manager_effectiveness_score": mgr_score,
                            })
                            survey_counter += 1

                        employee_counter += 1

                    elif offer_status == "Declined":
                        app_status = "Rejected"
                        rejection_reason = "Candidate Declined Offer"
                    else:
                        app_status = "Offer Extended"
                else:
                    # Dropped out at an earlier stage
                    if not reached_screen:
                        app_status = "Rejected"
                        rejection_reason = "Resume Screening Failed"
                    elif not reached_tech:
                        app_status = "Rejected"
                        rejection_reason = "Screen Interview Failed"
                    elif not reached_onsite:
                        app_status = "Rejected"
                        rejection_reason = "Technical Assessment Failed"
                    else:
                        app_status = "Rejected"
                        rejection_reason = "Hiring Team Consensus Not Reached"

                applications.append({
                    "application_id": app_id,
                    "candidate_id": cand_id,
                    "job_id": job_id,
                    "department_id": dept_id,
                    "recruiting_source": recruiting_source,
                    "application_date": app_date.strftime("%Y-%m-%d"),
                    "candidate_stage": candidate_stage,
                    "current_status": app_status,
                    "rejection_reason": rejection_reason,
                    "created_at": app_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                })
                app_counter += 1

        app_df = pd.DataFrame(applications)
        int_df = pd.DataFrame(interviews)
        off_df = pd.DataFrame(offers)
        emp_df = pd.DataFrame(employees)
        srv_df = pd.DataFrame(surveys)

        # Inject controlled anomalies into datasets for data quality demonstration
        logger.info("Injecting controlled data quality scenarios (missing values, invalid dates, inconsistent departments)...")
        
        # 1. Inconsistent department casing / typos in applications (~1%)
        if len(app_df) > 100:
            dirty_idx = app_df.sample(frac=0.01, random_state=self.seed).index
            typos = ["Eng", "ENGINEERING", "Sales ", "cs", "HR Dept", "Unknown"]
            for idx in dirty_idx:
                app_df.loc[idx, "department_id"] = random.choice(typos)

        # 2. Missing department_id in applications (~0.5%)
        if len(app_df) > 100:
            null_dept_idx = app_df.sample(frac=0.005, random_state=self.seed + 1).index
            app_df.loc[null_dept_idx, "department_id"] = None

        # 3. Duplicate application records (~0.3%)
        if len(app_df) > 100:
            dupe_apps = app_df.sample(n=int(len(app_df) * 0.003), random_state=self.seed).copy()
            app_df = pd.concat([app_df, dupe_apps], ignore_index=True)

        # 4. Invalid date anomaly: a tiny handful of interviews with date before application date
        if len(int_df) > 50:
            dirty_int_idx = int_df.sample(n=4, random_state=self.seed).index
            int_df.loc[dirty_int_idx, "interview_date"] = "2022-01-01"

        # 5. Missing decline_reason on some declined offers (~2%)
        if len(off_df) > 20:
            declined_idx = off_df[off_df["offer_status"] == "Declined"].sample(frac=0.05, random_state=self.seed).index
            off_df.loc[declined_idx, "decline_reason"] = None

        logger.info(
            f"Dataset Generation Complete:\n"
            f" - Candidates: {len(cand_df):,}\n"
            f" - Applications: {len(app_df):,}\n"
            f" - Interviews: {len(int_df):,}\n"
            f" - Offers: {len(off_df):,}\n"
            f" - Employees: {len(emp_df):,}\n"
            f" - Engagement Surveys: {len(srv_df):,}\n"
            f" - Departments: {len(dept_df):,}\n"
            f" - Recruiting Sources: {len(source_df):,}"
        )

        return {
            "candidates": cand_df,
            "applications": app_df,
            "interviews": int_df,
            "offers": off_df,
            "employees": emp_df,
            "engagement_surveys": srv_df,
            "departments": dept_df,
            "recruiting_sources": source_df,
        }

    def save_to_csv(self, datasets: Dict[str, pd.DataFrame], output_dir: Path) -> Dict[str, Path]:
        """Saves generated DataFrames to CSV files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        file_paths = {}
        for name, df in datasets.items():
            path = output_dir / f"{name}.csv"
            df.to_csv(path, index=False)
            file_paths[name] = path
            logger.info(f"Saved {name}.csv ({len(df):,} rows) -> {path}")
        return file_paths
