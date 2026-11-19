# TalentFlow Security, IAM, and HR Governance Architecture

In enterprise human resources analytics, candidate personally identifiable information (PII) and employee compensation data require strict least-privilege security controls and data access restrictions.

---

## 1. Principle of Least Privilege & GCP IAM Roles

| Role Name | Target Scope | Assigned GCP Roles | Permitted Operations |
|---|---|---|---|
| **Pipeline Service Account** (`sa-talentflow-pipeline`) | GCS Bucket & BigQuery Datasets | `roles/storage.objectAdmin`<br>`roles/bigquery.dataEditor`<br>`roles/bigquery.jobUser` | Read/write raw GCS files, load raw tables, execute dbt builds. |
| **Analytics Engineer** | `talentflow_staging`, `talentflow_analytics` | `roles/bigquery.dataEditor`<br>`roles/bigquery.jobUser` | Develop dbt models and schema tests. No access to production PII columns. |
| **HR Business Partner / BI Analyst** | `talentflow_analytics` | `roles/bigquery.dataViewer`<br>`roles/bigquery.jobUser` | Query curated marts and build dashboards via Streamlit. |
| **Compensation Specialist** | `fct_employee_lifecycle` (Authorized View) | `roles/datacatalog.maskedReader` | View unmasked salary bands for compensation parity audits. |

---

## 2. BigQuery Column-Level Security & Policy Tags

For real GCP deployments, TalentFlow defines Google Cloud Data Catalog Taxonomy Policy Tags:

```
Taxonomy: HR_Data_Governance
 ├── Tag: PII_Confidential (Candidate Email, Phone, Home Location)
 └── Tag: Compensation_Restricted (Base Salary, Bonus Pct, Stock Grants)
```

1. **Policy Tag Enforcement**:
   - `candidates.email` and `candidates.phone` are protected under `PII_Confidential`.
   - `offers.base_salary` and `employees.base_salary` are protected under `Compensation_Restricted`.
2. **Dynamic Data Masking**:
   Users without the `roles/datacatalog.maskedReader` role receive SHA-256 hashed or null-masked values for protected columns when querying BigQuery directly.

---

## 3. Synthetic Data & Log Protection Guarantees

- **No Real Personal Data**: 100% of names, contact records, compensation amounts, and survey responses are algorithmically generated using synthetic pseudorandom seeds.
- **Log Hygiene**: Logging frameworks in `talentflow/config.py` sanitize logs. Candidate names, phone numbers, and compensation values are never printed to stdout or written to application logs.
- **Credential Safety**: No credentials, tokens, or service account JSON files are ever hardcoded or tracked in Git. Environment variables and Secret Manager are enforced.
