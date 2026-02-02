from pydantic import BaseModel, Field
from typing import List


class Service(BaseModel):
    service_name: str = Field(description="Name of the service")
    cost_per_unit: float = Field(description="Cost per unit of the service")
    units: int = Field(description="Name of the Number of units for the service")
    tuition: float = Field(description="Total tuition for the service")

class TutoringService(BaseModel):
    service_name: str = Field(description="Description of the program written in the box below the text 'The program will be designed to support the student in achieving the following'")
    cost_per_unit: float = Field(description="NOT written in .pdf docuMent. Just divide tuition by units")
    units: int = Field(description="Number of total sessions purchased")
    tuition: float = Field(description="Dolars for Total amount")
