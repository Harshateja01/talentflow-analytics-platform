# TalentFlow Data Dictionary

This document details the source datasets, column types, descriptions, nullability, and domain constraints for the TalentFlow platform.

---

## 1. Raw Source Datasets (`talentflow_raw`)

### `candidates`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `candidate_id` | STRING | No (PK) | Unique synthetic identifier for candidate | `CAN-00042` |
| `first_name` | STRING | No | Candidate given name | `Alex` |
| `last_name` | STRING | No | Candidate family name | `Chen` |
| `email` | STRING | No | Standardized contact email | `alex.chen42@gmail.com` |
| `phone` | STRING | Yes (Anomaly) | Candidate phone number | `+1-415-555-1234` |
| `location` | STRING | No | Candidate primary metro location | `San Francisco, CA` |
| `highest_education` | STRING | No | Highest attained education credential | `Master's Degree` |
| `years_of_experience` | INTEGER | No | Self-reported professional experience | `7` |
| `created_at` | TIMESTAMP | No | Candidate profile record creation timestamp | `2023-04-12 10:15:00` |

---

### `applications`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `application_id` | STRING | No (PK) | Unique job application identifier | `APP-001042` |
| `candidate_id` | STRING | No (FK) | Reference to `candidates.candidate_id` | `CAN-00042` |
| `job_id` | STRING | No | Requisition / open position identifier | `JOB-DEP-001-44` |
| `department_id` | STRING | Yes (Anomaly) | Department code (cleaned in staging) | `DEP-001` |
| `recruiting_source` | STRING | No | Sourcing channel attribution | `Employee Referral` |
| `application_date` | DATE | No | Date candidate submitted application | `2023-04-15` |
| `candidate_stage` | STRING | No | Progression stage (`Applied`, `Screen`, `Technical Interview`, `Manager & Onsite`, `Offer`, `Hired`) | `Technical Interview` |
| `current_status` | STRING | No | Current disposition status (`Applied`, `Screen`, `Interview`, `Hired`, `Rejected`) | `Interview` |
| `rejection_reason` | STRING | Yes | Feedback reason if candidate was rejected | `Technical Assessment Failed` |
| `created_at` | TIMESTAMP | No | Application record timestamp | `2023-04-15 11:20:00` |
| `updated_at` | TIMESTAMP | No | Last update timestamp | `2023-04-22 16:40:00` |

---

### `interviews`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `interview_id` | STRING | No (PK) | Unique interview round identifier | `INT-003421` |
| `application_id` | STRING | No (FK) | Reference to `applications.application_id` | `APP-001042` |
| `interview_round` | STRING | No | Interview type (`Screen`, `Technical`, `Hiring Manager & Onsite`) | `Technical` |
| `interview_date` | DATE | No | Scheduled date of interview round | `2023-04-20` |
| `interviewer_id` | STRING | No | Employee identifier of interviewer | `EMP-00142` |
| `interview_result` | STRING | No | Interview outcome decision (`Pass`, `Fail`) | `Pass` |
| `score` | INTEGER | No | Competency evaluation rating (1 to 5 scale) | `4` |
| `candidate_feedback_score` | INTEGER | No | Candidate experience satisfaction rating (1 to 5) | `5` |
| `duration_minutes` | INTEGER | No | Scheduled length of interview round | `60` |

---

### `offers`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `offer_id` | STRING | No (PK) | Unique compensation package offer ID | `OFF-000842` |
| `application_id` | STRING | No (FK) | Reference to `applications.application_id` | `APP-001042` |
| `offer_date` | DATE | No | Date offer was extended to candidate | `2023-05-02` |
| `offer_status` | STRING | No | Offer disposition (`Accepted`, `Declined`, `Pending`, `Rescinded`) | `Accepted` |
| `base_salary` | NUMERIC | No | Annual base compensation (USD) | `165000` |
| `bonus_pct` | NUMERIC | No | Annual bonus target percentage | `0.15` |
| `stock_units` | INTEGER | No | Equity incentive grant (RSUs) | `2500` |
| `offer_response_date` | DATE | Yes | Date candidate provided formal response | `2023-05-06` |
| `decline_reason` | STRING | Yes | Explanation if offer declined | `Compensation Below Expectations` |

---

### `employees`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `employee_id` | STRING | No (PK) | Unique employee identifier | `EMP-000452` |
| `candidate_id` | STRING | No (FK) | Reference to `candidates.candidate_id` | `CAN-00042` |
| `application_id` | STRING | No (FK) | Reference to `applications.application_id` | `APP-001042` |
| `department_id` | STRING | No (FK) | Reference to `departments.department_id` | `DEP-001` |
| `job_title` | STRING | No | Professional title | `Analytics Engineer` |
| `job_level` | STRING | No | Career ladder tier (`L1` to `M2`) | `L3 - Senior` |
| `location` | STRING | No | Office hub / remote location | `San Francisco, CA` |
| `hire_date` | DATE | No | Official employee start date | `2023-06-01` |
| `employment_status` | STRING | No | Current workforce status (`Active`, `Terminated`, `Resigned`, `On Leave`) | `Active` |
| `termination_date` | DATE | Yes | Departure date if churned | `2024-08-15` |
| `manager_id` | STRING | Yes | Manager's employee ID | `EMP-000015` |
| `performance_rating` | INTEGER | No | Annual performance assessment (1 to 5) | `4` |

---

### `engagement_surveys`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `survey_id` | STRING | No (PK) | Unique survey submission ID | `SRV-001204` |
| `employee_id` | STRING | No (FK) | Reference to `employees.employee_id` | `EMP-000452` |
| `survey_date` | DATE | No | Date survey completed | `2023-11-15` |
| `engagement_score` | NUMERIC | No | Overall workplace engagement score (1.0 to 5.0) | `4.4` |
| `satisfaction_score` | NUMERIC | No | Job satisfaction rating (1.0 to 5.0) | `4.2` |
| `work_life_balance_score` | NUMERIC | No | Work-life flexibility rating (1.0 to 5.0) | `4.0` |
| `career_growth_score` | NUMERIC | No | Growth opportunities rating (1.0 to 5.0) | `4.3` |
| `manager_effectiveness_score` | NUMERIC | No | Leadership effectiveness rating (1.0 to 5.0) | `4.6` |

---

### `departments`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `department_id` | STRING | No (PK) | Department code (`DEP-001` to `DEP-008`) | `DEP-001` |
| `department_name` | STRING | No | Department title | `Engineering` |
| `department_lead` | STRING | No | Executive department sponsor | `Sarah Chen` |
| `cost_center` | STRING | No | Financial cost center reference | `CC-101` |

---

### `recruiting_sources`
| Column | Type | Nullable | Description | Sample Value |
|---|---|---|---|---|
| `source_id` | STRING | No (PK) | Channel identifier (`SRC-001` to `SRC-007`) | `SRC-002` |
| `source_name` | STRING | No | Sourcing channel name | `Employee Referral` |
| `source_channel` | STRING | No | Sourcing classification | `Internal Referral` |
| `cost_per_posting` | NUMERIC | No | Baseline cost per campaign / listing (USD) | `0` |
