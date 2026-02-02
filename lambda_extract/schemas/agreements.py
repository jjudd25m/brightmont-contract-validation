from pydantic import BaseModel, Field
from typing import Optional, List

from .enums import DocumentTitle
from .common import Student, ParentGuardian, StudentProgram
from .services import Service, TutoringService
from .payments import Payment, SinglePayment


class TuitionSchemaFirstPage(BaseModel):
    document_title: DocumentTitle = Field(description="Title of document")
    student: Student = Field(description="Information about the student")
    parent_guardian: ParentGuardian = Field(description="Information about the student's parent or guardian")
    second_parent_guardian: Optional[ParentGuardian]= Field(description="Information about the student's second parent or guardian")
    student_program: StudentProgram = Field(description="Information about student program")
    services: List[Service] = Field(description="Services details for different services")
    total_tuition: float = Field(description="Number in dolars of total tuition")
    one_to_one_sessions: int = Field(description="Number of one to one sessions. Can be found below Services")
    homework_studio_sessions: int = Field(description="Number of homework sessions. Write 0 if nothing is written. Can be found below Services")
    scheduled_start_date: str = Field(description="Scheduled start date of the program (MM/DD/YY). Can be found in Program Schedule block")
    doc_id: str = Field(description="Document ID")

class TuitionSchemaSecondPage(BaseModel):
    payment: Payment

class SkillBuildingSchema(BaseModel):
    document_title: DocumentTitle = Field(description="Title of document")
    student: Student = Field(description="Information about the student")
    parent_guardian: ParentGuardian = Field(description="Information about the student's parent or guardian")
    second_parent_guardian: Optional[ParentGuardian]= Field(description="Information about the student's second parent or guardian")
    student_program: StudentProgram = Field(description="Information about student program")
    services: List[Service] = Field(description="Service details for different services")
    total_tuition: float = Field(description="Number in dolars of total tuition")
    scheduled_start_date: str = Field(description="Scheduled start date of the program (MM/DD/YY)")
    doc_id: str = Field(description="Document ID")

class AdditionalSchema(BaseModel):
    document_title: DocumentTitle = Field(description="Title of document")
    student: Student = Field(description="Information about the student")
    parent_guardian: ParentGuardian = Field(description="Information about the student's parent or guardian")
    second_parent_guardian: Optional[ParentGuardian]= Field(description="Information about the student's second parent or guardian")
    student_program: StudentProgram = Field(description="Information about student program")
    services: Service = Field(description="")
    payment: SinglePayment = Field(description="Information about payment")
    doc_id: str = Field(description="Document ID")

class TutoringSchema(BaseModel): # Use the same for recurring tutoring
    document_title: DocumentTitle = Field(description="Title of document")
    student: Student = Field(description="Information about the student")
    parent_guardian: ParentGuardian = Field(description="Information about the student's parent or guardian")
    second_parent_guardian: Optional[ParentGuardian]= Field(description="Information about the student's second parent or guardian")
    student_program: StudentProgram = Field(description="Information about student program")
    services: TutoringService = Field(description="Information about service")
    automatic_renewal_authorization: bool = Field(description="Indicates whether the parent/guardian authorizes automatic renewal of charges") # TODO: This doesn't work properly
    scheduled_start_date: str = Field(description="Scheduled start date of the program (MM/DD/YY)")
    doc_id: str = Field(description="Document ID")

titles = {
    "ESA Enrollment & Tuition Agreement": [TuitionSchemaFirstPage, TuitionSchemaSecondPage],
    "Enrollment & Tuition Agreement": [TuitionSchemaFirstPage, TuitionSchemaSecondPage],
    "Skill Building Agreement": SkillBuildingSchema,
    "Tutoring Agreement": TutoringSchema,
    "Recurring Tutoring Agreement": TutoringSchema,
    "Additional Sessions Agreement": AdditionalSchema
}
