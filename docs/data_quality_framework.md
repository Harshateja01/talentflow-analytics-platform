# TalentFlow Data Quality & Governance Framework

TalentFlow implements an active multi-tiered data quality architecture combining **Python pre-ingestion validation**, **controlled anomaly testing**, and **dbt schema & singular assertions**.

---

## 1. Multi-Tiered Quality Gates

```
[Raw Generation] ──> [Gate 1: Python DQ Suite] ──> [Gate 2: dbt Deduplication] ──> [Gate 3: dbt Tests]
```

### Gate 1: Python Pre-Ingestion Data Quality Suite
Executes before warehouse ingestion to identify:
- Missing mandatory fields (`candidate_id`, `email`, `hire_date`).
- Uniqueness violations on primary keys.
- Referential integrity breaks (applications referencing missing candidates).
- Chronological anomalies (`interview_date < application_date` or `termination_date < hire_date`).
- Categorical domain breaches (unknown pipeline stages or statuses).

### Gate 2: dbt Cleaning & Deduplication Models
Staging SQL models actively cleanse anomalies:
- Standardizes dirty department strings (`'Eng'`, `'Sales '`, `'CS'`) into valid keys (`DEP-001`, `DEP-003`, `DEP-005`).
- Deduplicates duplicate records using `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ... DESC)`.
- Replaces missing optional strings with standardized labels (`'Not Specified'`, `'Not Applicable'`).

### Gate 3: dbt Schema & Singular Tests
59 automated assertions verify:
- Primary key uniqueness across staging and marts.
- Non-null constraints on mandatory dimensions.
- Foreign key referential integrity across all relationships.
- `accepted_values` enforcement on pipeline stages and employment statuses.
- Singular custom test `assert_valid_hiring_date_sequence.sql`.

---

## 2. Controlled Anomaly Scenarios

To prove that validation gates function in production without relying on happy-path data, synthetic generation deliberately injects controlled anomalies:

| Anomaly Scenario | Target Dataset | Injected Volume | Detection Gate | Remediation |
|---|---|---|---|---|
| Inconsistent Department Casing | `applications` | ~1.0% | Pre-ingestion Warn + dbt FK Test | Standardized to canonical keys in `stg_applications` |
| Missing Department Values | `applications` | ~0.5% | Pre-ingestion Fail + dbt Not-Null | Imputed to default department in `stg_applications` |
| Duplicate Applications | `applications` | ~0.3% | Pre-ingestion Fail + dbt PK Test | Deduplicated via window function in `stg_applications` |
| Negative Date Sequence | `interviews` | 4 records | Pre-ingestion Fail + dbt Test | Filtered/flagged in data quality reporting |
| Missing Phone Numbers | `candidates` | ~1.5% | Pre-ingestion Warning | Handled as optional field with default `'Unknown'` |
