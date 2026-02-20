from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from .schema import EmployeeCreate, EmployeeOut
from .service import create_employee as create_employee_service
from .service import delete_employee as delete_employee_service
from .service import list_employees as list_employees_service

router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    return await create_employee_service(db, payload)


@router.get("", response_model=Page[EmployeeOut])
async def list_employees(
    params: Params = Depends(),
    search: str | None = Query(default=None),
    attendance_date: date | None = Query(default=None, alias="date"),
    db: AsyncSession = Depends(get_db),
):
    return await list_employees_service(db, params, search, attendance_date)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: str, db: AsyncSession = Depends(get_db)):
    await delete_employee_service(db, employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
