from pydantic import BaseModel, Field
from typing import Optional, List


class ScholarshipPayment(BaseModel):
    scholarship_type: str = Field(description="Type of Step Up Scholarship to be applied")
    scholarship_payment: float = Field(description="Amount in dolars of scholarship payment")

class SinglePayment(BaseModel):
    amount: float = Field(description="Amount in dolars of single playment")
    due_date: str = Field(description="Due date for the single payment (MM/DD/YY)")

class Payment(BaseModel):
    scholarship_payment: Optional[ScholarshipPayment] = Field(default=None, description="Scholarship data if exists")
    single_payment: Optional[SinglePayment] = Field(description="Single payment data if selected")
    multiple_payment: Optional[List[SinglePayment]] = Field(description="Multiple payment data if selected. Sometimes written as 'Quarterly Payment'")
