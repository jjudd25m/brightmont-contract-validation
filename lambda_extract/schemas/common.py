from pydantic import BaseModel, Field
from typing import Optional
from .enums import CollegeBound


class Student(BaseModel):
    first_name: str = Field(description="Student's first name")
    last_name: str = Field(description="Student's last name")
    nickname: Optional[str] = Field(description="Student's nickname")

class ParentGuardian(BaseModel):
    full_name: str = Field(description="Full name of the parent or guardian")
    email: str = Field(description="Email address of the parent or guardian")

class SecondParentGuardian(BaseModel):
    full_name: str = Field(description="Full name of the second parent or guardian")
    email: str = Field(description="Email address of the second parent or guardian")

class StudentProgram(BaseModel):
    campus: str = Field(description="Name of the campus")
    courses: Optional[str] = Field(description="List of courses")
    college_bound: Optional[CollegeBound] = Field(description="Student's college bound status")
    current_grade: int = Field(description="Ordinary number of the current grade")
