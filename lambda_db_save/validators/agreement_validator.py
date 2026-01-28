from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator, field_validator # pip install email-validator
from typing import Optional, List

class Service(BaseModel):
    service_name: str
    cost_per_unit: float
    units: float # Sometimes it's 0,5
    tuition: float

class AgreementData(BaseModel):
    document_title: str
    student_first_name: str
    student_last_name: str
    student_nickname: Optional[str] = None
    parent_guardian_full_name: str
    parent_guardian_email: EmailStr
    second_parent_guardian_full_name: Optional[str] = None
    second_parent_guardian_email: Optional[EmailStr] = None
    student_courses: Optional[str] = None
    student_campus: str
    student_college_bound: Optional[str] = None # TODO: Make an enum
    current_grade: int
    total_tuition: Optional[float] = None # TODO: Check this. For some reason it's not extracted from a lot of documents
    one_to_one_sessions: Optional[int] = None
    homework_studio_sessions: Optional[int] = None
    scheduled_start_date: Optional[str] = None
    scholarship_type: Optional[str] = None
    scholarship_payment: Optional[float] = None
    is_single_payment: bool
    # payment_amount: float
    payment_amount: float | None = None
    s3_path: str
    document_id: str
    services_list: List[Service]
    is_valid: bool = Field(default=True)
    is_human_approved: bool = Field(default=True)
    input_format: str

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        fmt = data.get("input_format")
        if fmt == "user save":
            return cls._normalize_user_save_data(data)
        elif fmt == "extracted from model":
            return cls._normalize_model_extracted_data(data)
        else:
            raise ValueError("input_format must be provided")

    # TODO: Set is_valid to false if something is wrong in a method below
    def is_valid_service(service: dict) -> bool:
        if not isinstance(service, dict):
            return False
        meaningful_keys = ("service_name", "cost_per_unit", "units", "tuition")
        for key in meaningful_keys:
            value = service.get(key)
            if value not in ("", None):
                return True
        return False


    @classmethod
    def _normalize_model_extracted_data(cls, data: dict) -> dict:
        student = data.get("student") or {}
        parent = data.get("parent_guardian") or {}
        second_parent = data.get("second_parent_guardian") or {}
        program = data.get("student_program") or {}
        payment = data.get("payment") or {}

        scholarship_payment_obj = payment.get("scholarship_payment")
        scholarship_type = None
        scholarship_payment = None
        if scholarship_payment_obj:
            scholarship_type = scholarship_payment_obj.get("scholarship_type")
            scholarship_payment = scholarship_payment_obj.get("scholarship_payment")

        is_single_payment = True
        payment_amount = None

        single_payment = payment.get("single_payment")
        if single_payment:
            payment_amount = single_payment.get("amount")

        multiple_payments = payment.get("multiple_payment")
        if multiple_payments:
            is_single_payment = False
            payment_amount = sum(p.get("amount", 0) for p in multiple_payments if isinstance(p, dict))

        services = data.get("services_list") or data.get("services") or []

        services_list = [
            s for s in services
            if cls.is_valid_service(s)
        ]

        return {
            "document_title": data["document_title"],
            "student_first_name": student.get("first_name", ""),
            "student_last_name": student.get("last_name", ""),
            "student_nickname": student.get("nickname", "") or "",
            "parent_guardian_full_name": parent.get("full_name", ""),
            "parent_guardian_email": parent.get("email", ""),
            "second_parent_guardian_full_name": second_parent.get("full_name") or second_parent.get("second_parent_guardian_full_name") or "",
            "second_parent_guardian_email": second_parent.get("email") or second_parent.get("second_parent_guardian_email") or "",

            "student_campus": program.get("campus", ""),
            "student_courses": program.get("courses") or "",
            "student_college_bound": program.get("college_bound") or "",
            "current_grade": program.get("current_grade", ""),

            "services_list": services_list,
            "total_tuition": data.get("total_tuition"),
            "one_to_one_sessions": data.get("one_to_one_sessions"),
            "homework_studio_sessions": data.get("homework_studio_sessions"),
            "scheduled_start_date": data.get("scheduled_start_date"),

            "s3_path": data["s3_path"],
            "document_id": data.get("document_id") or data.get("doc_id"),

            "scholarship_type": scholarship_type,
            "scholarship_payment": scholarship_payment,
            "is_single_payment": is_single_payment,
            "payment_amount": payment_amount,

            "is_valid": data.get("is_valid", True),
            "is_human_approved": data.get("is_human_approved", False),
            "input_format": data.get("input_format") or "",
        }

    @classmethod
    def _normalize_user_save_data(cls, data: dict) -> dict:
        print("RETURNING USER SAVE DATA")
        services_list = data.get("services_list") or data.get("services"),
        print(f"Services list: {services_list}")
        services = data.get("services_list") or data.get("services") or []

        services_list = [
            s for s in services
            if cls.is_valid_service(s)
        ]

        return {
            "document_title": data["document_title"],
            "student_first_name": data["student_first_name"],
            "student_last_name": data["student_last_name"],
            "student_nickname": data.get("student_nickname") or "",

            "parent_guardian_full_name": data["parent_guardian_full_name"],
            "parent_guardian_email": data["parent_guardian_email"],

            "second_parent_guardian_full_name": data.get("second_parent_guardian_full_name") or "",
            "second_parent_guardian_email": data.get("second_parent_guardian_email") or "",

            "student_campus": data["student_campus"],
            "student_courses": data.get("courses") or data.get("student_courses") or "",
            "student_college_bound": data.get("student_college_bound") or "",
            "current_grade": data["current_grade"],

            "services_list": services_list,

            "total_tuition": data.get("total_tuition"),
            "one_to_one_sessions": data.get("one_to_one_sessions"),
            "homework_studio_sessions": data.get("homework_studio_sessions"),
            "scheduled_start_date": data.get("scheduled_start_date"),

            "s3_path": data["s3_path"],
            "document_id": data["document_id"],

            "scholarship_type": data.get("scholarship_type"),
            "scholarship_payment": data.get("scholarship_payment"),
            "is_single_payment": data.get("is_single_payment", True),
            "payment_amount": data.get("payment_amount"),

            "is_valid": data.get("is_valid", True),
            "is_human_approved": data.get("is_human_approved", False),
            "input_format": data.get("input_format") or "",
        }

    @field_validator(
        "student_nickname",
        "second_parent_guardian_full_name",
        "second_parent_guardian_email",
        "student_courses",
        "student_college_bound",
        "scheduled_start_date",
        "scholarship_type",
        "document_id",
        mode="before")
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator(
        "scholarship_payment",
        "payment_amount",
        mode="before")
    def empty_string_to_none_for_floats(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
            try:
                return float(v)
            except ValueError:
                cls.is_valid = False
                return None
        return v

    @field_validator("one_to_one_sessions", "homework_studio_sessions", mode="before")
    def empty_string_to_none_for_ints(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
            try:
                return int(v)
            except ValueError:
                cls.is_valid = False
                return None
        return v

    @model_validator(mode="after")
    def check_total_matches_services(self):
        try:
            print(f"SERVICES validator: {self.services_list}")
            total_from_services = sum(s.tuition for s in self.services_list)
            allowed_diff = self.payment_amount * 0.10  # 10% of total
            diff = abs(total_from_services - self.payment_amount)

            if diff > allowed_diff:
                cls.is_valid = False
            return self
        except Exception as e:
            self.is_valid = False
            return self


def check_agreement_data(**kwargs):
    print(f"Check start: {kwargs}")
    try:
        obj = AgreementData(**kwargs)
        return True, obj
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return False, e.errors()
