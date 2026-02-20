from datetime import date

from pydantic import BaseModel, EmailStr, Field


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    department: str = Field(min_length=2, max_length=100)


class EmployeeOut(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    is_present: bool = False
    attendance_date: date | None = None

    model_config = {"from_attributes": True}
