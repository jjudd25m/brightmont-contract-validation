from dataclasses import dataclass
from typing import Any
from .agreements import (
    TuitionSchemaFirstPage,
    TuitionSchemaSecondPage,
    SkillBuildingSchema,
    TutoringSchema,
    AdditionalSchema,
)
from .post_processing import (
    post_additional_sessions,
    post_skill_building,
    post_tutoring
)

titles = {
    "ESA Enrollment & Tuition Agreement": [TuitionSchemaFirstPage, TuitionSchemaSecondPage],
    "Enrollment & Tuition Agreement": [TuitionSchemaFirstPage, TuitionSchemaSecondPage],
    "Skill Building Agreement": SkillBuildingSchema,
    "Tutoring Agreement": TutoringSchema,
    "Recurring Tutoring Agreement": TutoringSchema,
    "Additional Sessions Agreement": AdditionalSchema
}

@dataclass(frozen=True)
class ExtractionStep:
    schema: Any
    page_range: str

EXTRACTION_PLANS = {
    "ESA Enrollment & Tuition Agreement": [
        ExtractionStep(TuitionSchemaFirstPage, "1-1"),
        ExtractionStep(TuitionSchemaSecondPage, "2-2"),
    ],
    "Enrollment & Tuition Agreement": [
        ExtractionStep(TuitionSchemaFirstPage, "1-1"),
        ExtractionStep(TuitionSchemaSecondPage, "2-2"),
    ],
    "Skill Building Agreement": [
        ExtractionStep(SkillBuildingSchema, "1-1"),
    ],
    "Tutoring Agreement": [
        ExtractionStep(TutoringSchema, "1-1"),
    ],
    "Recurring Tutoring Agreement": [
        ExtractionStep(TutoringSchema, "1-1"),
    ],
    "Additional Sessions Agreement": [
        ExtractionStep(AdditionalSchema, "1-1"),
    ],
}

POST_PROCESSING_PLAN = {
    "Skill Building Agreement": post_skill_building,
    "Tutoring Agreement": post_tutoring,
    "Recurring Tutoring Agreement": post_tutoring,
    "Additional Sessions Agreement": post_additional_sessions,
}
