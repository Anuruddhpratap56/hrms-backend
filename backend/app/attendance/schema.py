from datetime import date

from pydantic import BaseModel, Field


class AttendanceCreate(BaseModel):
    employee_id: str = Field(min_length=1, max_length=50)
    date: date
    is_present: bool


class AttendanceOut(BaseModel):
    employee_id: str
    date: date
    is_present: bool

    model_config = {"from_attributes": True}


class AttendanceToggleOut(BaseModel):
    action: str
    attendance: AttendanceOut | None = None


class AttendanceAdminOut(BaseModel):
    employee_id: str
    employee_name: str
    date: date
    is_present: bool
