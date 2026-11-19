"""Schema definitions, lookup constants, and domain choices for TalentFlow."""

from typing import List, Dict

DEPARTMENTS: List[Dict[str, str]] = [
    {"department_id": "DEP-001", "department_name": "Engineering", "department_lead": "Sarah Chen", "cost_center": "CC-101"},
    {"department_id": "DEP-002", "department_name": "Product", "department_lead": "Marcus Brody", "cost_center": "CC-102"},
    {"department_id": "DEP-003", "department_name": "Sales", "department_lead": "Elena Rostova", "cost_center": "CC-201"},
    {"department_id": "DEP-004", "department_name": "Marketing", "department_lead": "David Kim", "cost_center": "CC-202"},
    {"department_id": "DEP-005", "department_name": "Customer Success", "department_lead": "Amara Diallo", "cost_center": "CC-301"},
    {"department_id": "DEP-006", "department_name": "G&A", "department_lead": "Robert Vance", "cost_center": "CC-401"},
    {"department_id": "DEP-007", "department_name": "People / HR", "department_lead": "Priya Patel", "cost_center": "CC-402"},
    {"department_id": "DEP-008", "department_name": "Finance", "department_lead": "Thomas Sterling", "cost_center": "CC-403"},
]

RECRUITING_SOURCES: List[Dict[str, str | int]] = [
    {"source_id": "SRC-001", "source_name": "LinkedIn", "source_channel": "Paid Sourcing / InMail", "cost_per_posting": 500},
    {"source_id": "SRC-002", "source_name": "Employee Referral", "source_channel": "Internal Referral", "cost_per_posting": 0},
    {"source_id": "SRC-003", "source_name": "Direct / Careers Site", "source_channel": "Organic Inbound", "cost_per_posting": 0},
    {"source_id": "SRC-004", "source_name": "External Agency", "source_channel": "Agency Placement", "cost_per_posting": 8000},
    {"source_id": "SRC-005", "source_name": "Job Boards (Indeed/Glassdoor)", "source_channel": "Job Board Aggregators", "cost_per_posting": 350},
    {"source_id": "SRC-006", "source_name": "University Campus", "source_channel": "Campus Outreach", "cost_per_posting": 1200},
    {"source_id": "SRC-007", "source_name": "GitHub / Technical Community", "source_channel": "Organic Community", "cost_per_posting": 100},
]

LOCATIONS: List[str] = [
    "San Francisco, CA",
    "Mountain View, CA",
    "Austin, TX",
    "New York, NY",
    "Chicago, IL",
    "Seattle, WA",
    "Remote - US",
    "London, UK",
    "Amsterdam, NL",
]

JOB_LEVELS: List[str] = [
    "L1 - Associate",
    "L2 - Mid",
    "L3 - Senior",
    "L4 - Staff",
    "L5 - Principal",
    "M1 - Manager",
    "M2 - Director",
]

JOB_TITLES: Dict[str, List[str]] = {
    "DEP-001": [
        "Software Engineer",
        "Senior Software Engineer",
        "Staff Software Engineer",
        "Data Engineer",
        "Analytics Engineer",
        "Site Reliability Engineer",
        "Engineering Manager",
    ],
    "DEP-002": [
        "Associate Product Manager",
        "Product Manager",
        "Senior Product Manager",
        "Director of Product",
        "Product Designer",
    ],
    "DEP-003": [
        "Account Executive",
        "Enterprise Account Executive",
        "Sales Development Rep",
        "Solutions Architect",
        "Sales Director",
    ],
    "DEP-004": [
        "Marketing Specialist",
        "Content Marketing Manager",
        "Growth Marketing Lead",
        "Product Marketing Manager",
    ],
    "DEP-005": [
        "Customer Success Manager",
        "Implementation Consultant",
        "Technical Support Specialist",
    ],
    "DEP-006": ["Legal Counsel", "Operations Specialist", "Executive Assistant"],
    "DEP-007": ["Technical Recruiter", "People Business Partner", "Talent Operations Lead"],
    "DEP-008": ["Financial Analyst", "Senior Accountant", "FP&A Manager"],
}

EDUCATION_LEVELS: List[str] = [
    "Bachelor's Degree",
    "Master's Degree",
    "Ph.D.",
    "Associate Degree",
    "High School / BootCamp",
]

STAGES_ORDER: List[str] = [
    "Applied",
    "Screen",
    "Technical Interview",
    "Manager & Onsite",
    "Offer",
    "Hired",
]

OFFER_STATUSES: List[str] = ["Accepted", "Declined", "Pending", "Rescinded"]
DECLINE_REASONS: List[str] = [
    "Accepted Competing Offer",
    "Compensation Below Expectations",
    "Location / Relocation Constraints",
    "Role Mismatch",
    "Counter-offer from Current Employer",
]

EMPLOYMENT_STATUSES: List[str] = ["Active", "Terminated", "Resigned", "On Leave"]
