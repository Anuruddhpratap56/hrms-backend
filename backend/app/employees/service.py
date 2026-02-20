from datetime import date

from fastapi import HTTPException, status
from fastapi_pagination import Page, Params, paginate
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..attendance.model import Attendance
from .model import Employee
from .schema import EmployeeCreate, EmployeeOut


async def create_employee(db: AsyncSession, payload: EmployeeCreate) -> Employee:
    email_result = await db.execute(select(Employee).where(Employee.email == payload.email))
    existing_email = email_result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    max_id_result = await db.execute(select(func.max(Employee.id)))
    max_id = max_id_result.scalar_one()
    next_id = (max_id or 0) + 1
    generated_employee_id = f"EMP00{next_id}"

    employee = Employee(
        employee_id=generated_employee_id,
        full_name=payload.full_name.strip(),
        email=payload.email.strip().lower(),
        department=payload.department.strip(),
    )
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee


async def list_employees(
    db: AsyncSession,
    params: Params,
    search: str | None = None,
    attendance_date: date | None = None,
) -> Page[EmployeeOut]:
    target_date = attendance_date or date.today()
    query = select(Employee, Attendance).outerjoin(
        Attendance,
        and_(Attendance.employee_id == Employee.id, Attendance.date == target_date),
    )
    if search and search.strip():
        query = query.where(Employee.full_name.ilike(f"%{search.strip()}%"))
    result = await db.execute(query.order_by(Employee.id.desc()))
    records = result.all()
    items = [
        EmployeeOut(
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            email=employee.email,
            department=employee.department,
            is_present=attendance.is_present if attendance else False,
            attendance_date=target_date,
        )
        for employee, attendance in records
    ]
    return paginate(items, params)


async def delete_employee(db: AsyncSession, employee_id: str) -> None:
    result = await db.execute(select(Employee).where(Employee.employee_id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    await db.delete(employee)
    await db.commit()
