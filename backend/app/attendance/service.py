from datetime import date

from fastapi import HTTPException, status
from fastapi_pagination import Page, Params, paginate
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..employees.model import Employee
from .model import Attendance
from .schema import AttendanceAdminOut, AttendanceCreate, AttendanceOut, AttendanceToggleOut


async def toggle_attendance(db: AsyncSession, payload: AttendanceCreate) -> AttendanceToggleOut:
    employee_result = await db.execute(select(Employee).where(Employee.employee_id == payload.employee_id))
    employee = employee_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    existing_result = await db.execute(
        select(Attendance).where(Attendance.employee_id == employee.id, Attendance.date == payload.date)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.commit()
        return AttendanceToggleOut(action="unmarked", attendance=None)

    record = Attendance(employee_id=employee.id, date=payload.date, is_present=payload.is_present)
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return AttendanceToggleOut(
        action="marked",
        attendance=AttendanceOut(employee_id=employee.employee_id, date=record.date, is_present=record.is_present),
    )


async def list_attendance(
    db: AsyncSession,
    employee_id: str,
    params: Params,
    date_filter: date | None = None,
) -> Page[AttendanceOut]:
    employee_result = await db.execute(select(Employee).where(Employee.employee_id == employee_id))
    employee = employee_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    query = select(Attendance).where(Attendance.employee_id == employee.id)
    if date_filter:
        query = query.where(Attendance.date == date_filter)

    result = await db.execute(query.order_by(Attendance.date.desc()))
    records = result.scalars().all()
    items = [
        AttendanceOut(employee_id=employee.employee_id, date=record.date, is_present=record.is_present)
        for record in records
    ]
    return paginate(items, params)


async def list_all_attendance(
    db: AsyncSession,
    params: Params,
    date_filter: date | None = None,
    employee_filter: str | None = None,
    search: str | None = None,
) -> Page[AttendanceAdminOut]:
    if date_filter:
        query = select(Employee, Attendance).outerjoin(
            Attendance,
            and_(Attendance.employee_id == Employee.id, Attendance.date == date_filter),
        )
        if employee_filter and employee_filter.strip():
            query = query.where(Employee.employee_id == employee_filter.strip())
        if search and search.strip():
            query = query.where(Employee.full_name.ilike(f"%{search.strip()}%"))

        result = await db.execute(query.order_by(Employee.full_name.asc()))
        rows = result.all()
        items = [
            AttendanceAdminOut(
                employee_id=employee.employee_id,
                employee_name=employee.full_name,
                date=date_filter,
                is_present=attendance.is_present if attendance else False,
            )
            for employee, attendance in rows
        ]
        return paginate(items, params)

    query = select(Attendance, Employee).join(Employee, Attendance.employee_id == Employee.id)
    if employee_filter and employee_filter.strip():
        query = query.where(Employee.employee_id == employee_filter.strip())
    if search and search.strip():
        query = query.where(Employee.full_name.ilike(f"%{search.strip()}%"))

    result = await db.execute(query.order_by(Attendance.date.desc(), Employee.full_name.asc()))
    rows = result.all()
    items = [
        AttendanceAdminOut(
            employee_id=employee.employee_id,
            employee_name=employee.full_name,
            date=attendance.date,
            is_present=attendance.is_present,
        )
        for attendance, employee in rows
    ]
    return paginate(items, params)
