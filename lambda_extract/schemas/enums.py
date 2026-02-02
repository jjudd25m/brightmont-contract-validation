from enum import Enum

class DocumentTitle(str, Enum):
    ADDITIONAL_SESSION = "Additional Sessions Agreement"
    ESA_ENROLLMENT = "ESA Enrollment & Tuition Agreement"
    ENROLLMENT_TUITION_AGREEMENT = "Enrollment & Tuition Agreement"
    RECURRING_TUTORING = "Recurring Tutoring Agreement"
    SKILL_BUILDING = "Skill Building Agreement"

class CollegeBound(str, Enum):
    FOUR_YEAR = "4-Year College"
    COMMUNITY_COLLEGE = "Community College/Vocational"
    CAREER_MILITARY = "Career/Military"
    NCAA = "NCAA"
