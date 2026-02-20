from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from .schema import AttendanceAdminOut, AttendanceCreate, AttendanceOut, AttendanceToggleOut
from .service import list_all_attendance as list_all_attendance_service
from .service import list_attendance as list_attendance_service
from .service import toggle_attendance as toggle_attendance_service

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance"])


@router.post("", response_model=AttendanceToggleOut, status_code=status.HTTP_200_OK)
async def toggle_attendance(payload: AttendanceCreate, db: AsyncSession = Depends(get_db)):
    return await toggle_attendance_service(db, payload)


@router.get("", response_model=Page[AttendanceAdminOut])
async def list_all_attendance(
    params: Params = Depends(),
    date_filter: date | None = Query(default=None, alias="date"),
    employee_filter: str | None = Query(default=None, alias="employee_id"),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await list_all_attendance_service(db, params, date_filter, employee_filter, search)


@router.get("/{employee_id}", response_model=Page[AttendanceOut])
async def list_attendance(
    employee_id: str,
    params: Params = Depends(),
    date_filter: date | None = Query(default=None, alias="date"),
    db: AsyncSession = Depends(get_db),
):
    return await list_attendance_service(db, employee_id, params, date_filter)
