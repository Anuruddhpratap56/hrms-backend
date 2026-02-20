# HRMS Lite (Full Stack)

HRMS Lite is a full-stack admin tool to manage employee records and daily attendance from a single admin panel.

## 1. Tech Stack
- Frontend: React + Vite
- Backend: FastAPI (async)
- Database: PostgreSQL
- ORM: SQLAlchemy (async)
- Migrations: Alembic
- Pagination: fastapi-pagination

## 2. Project Structure
- `backend/` FastAPI APIs, business logic, models, migrations
- `frontend/` React admin panel, API integration, reusable UI modules

## 3. Setup and Run

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

### Environment
- Backend `.env`:
```env
DATABASE_URL=postgresql+psycopg2://postgres:<password>@localhost:5432/hrms_lite
```

- Frontend `.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 4. API Summary

### Health
- `GET /health`

### Employee APIs
- `POST /api/v1/employees`
- `GET /api/v1/employees?page=1&size=10&search=<name>&date=YYYY-MM-DD`
- `DELETE /api/v1/employees/{employee_id}`

### Attendance APIs
- `POST /api/v1/attendance` (toggle: mark/unmark)
- `GET /api/v1/attendance?page=1&size=10&date=YYYY-MM-DD&employee_id=<id>&search=<name>`
- `GET /api/v1/attendance/{employee_id}?page=1&size=10&date=YYYY-MM-DD`

## 5. Core Business Rules

### Employee Creation
- Frontend sends: `full_name`, `email`, `department`
- Backend generates `employee_id` automatically in format: `emp00<sequence>`
- Duplicate email returns `409`

### Attendance Toggle
- Endpoint: `POST /api/v1/attendance`
- Input: `employee_id`, `date`, `is_present`
- Behavior:
  - If record for `employee_id + date` exists: it is deleted (unmark)
  - If not exists: record is created (mark)
- Frontend sends `is_present: true` for toggle actions

## 6. Attendance Listing Flow 


### Case A: Date is selected in attendance filters
- API: `GET /api/v1/attendance?date=YYYY-MM-DD...`
- Result includes **all employees** for that date:
  - Employees with attendance record -> `is_present=true` (Present)
  - Employees without attendance record -> `is_present=false` (Absent)
- This is used to show full day attendance sheet (present + absent)

### Case B: Date is not selected
- API returns existing attendance rows from attendance table only
- Sorted by date (latest first)
- This view is history-driven (not full roster)

## 7. Employee Section Flow (Frontend)

### List Employees
- Uses `GET /api/v1/employees`
- Supports pagination and name search
- Also sends attendance date (selected date or current day)
- Each employee row includes day-wise `is_present` for that date

### Mark/Unmark from Employee Table
- Each row has toggle icon button
- Uses selected date from employee section; if no date selected, uses current day
- Calls attendance toggle API
- Refreshes employee table after action
- Shows toast with employee name and action result

### Create Employee
- Open create modal
- Submit form to employee create API
- On success: toast + list refresh
- On validation/duplicate error: error toast with backend message

### Delete Employee
- Confirmation modal
- On confirm, delete API called
- List refreshes

### View Employee Attendance
- Eye icon opens popup modal
- Popup calls `GET /api/v1/attendance/{employee_id}` with pagination and optional date filter

## 8. Attendance Section Flow (Frontend)

### Attendance Table
- Uses `GET /api/v1/attendance`
- Filters:
  - Date
  - Employee ID
  - Employee name search
- Supports pagination

### Row Toggle Button
- Each row shows status badge and mark/unmark icon
- Button toggles attendance for that row's employee/date
- Toast message uses employee **name**
- Table refreshes after toggle

## 9. Sorting, Pagination, and UI States
- Pagination is enabled on all tables
- Attendance records are sorted by date descending in backend queries
- UI states handled:
  - Loading
  - Empty
  - Error
  - Success toasts

## 10. Validation and Error Handling
- Required field validation (`422`)
- Invalid email validation (`422`)
- Duplicate email (`409`)
- Employee not found (`404`)
- Validation handler returns specific message in `detail`

## 11. Reusable UI Modules
Used reusable modules in frontend where meaningful:
- `DataTable`
- `Modal`
- `PaginationControls`
- `StatusBadge`
- `ConfirmDialog`

## 12. Final Notes
- Single-admin system (no authentication)
- Attendance is intentionally toggle-based for quick operations
- Present/Absent mapping:
  - `is_present=true` -> Present``
  - `is_present=false` -> Absent
- In date-selected attendance view, absent rows are generated for employees without records to provide complete daily visibility
