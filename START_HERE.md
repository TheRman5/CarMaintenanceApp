# Car Maintenance App | Milestone 1

This is **real local-development code**, not a mockup. It implements vehicle management, odometer updates, maintenance tasks, recurrence, completion, service history, and persistent light/dark theme.

**Important: development only. Do not deploy to the public internet yet.** Milestone 1 intentionally has a fixed local development owner and no authentication. In a later milestone we will verify Supabase Auth tokens server-side and derive the owner from the verified JWT.

## Prerequisites

- Node.js 20 or newer (Node 22 LTS recommended)
- Python 3.12 or newer
- Two terminal windows
- You do **not** need OpenAI, Supabase, Twilio, Resend, or Docker accounts to complete Milestone 1.

## First installation

Unzip the starter into your existing `CarMaintenanceApp` repository. Keep your current README.md. The files in this archive live in `apps/api` and `apps/web`.

### Terminal A: Backend

On Windows PowerShell, from your repository root:

```powershell
cd apps/api
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

If `py -3.12` is unavailable, use `py -m venv .venv` or `python -m venv .venv` with your installed Python 3.12+.

Backend: http://127.0.0.1:8000/health
Interactive API docs: http://127.0.0.1:8000/docs

### Terminal B: Frontend

```powershell
cd apps/web
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open **http://127.0.0.1:3000** in a browser.

### Tests

```powershell
cd apps/api
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

## First hands-on workflow

1. Click **Add a vehicle** and enter your vehicle details and current mileage.
2. Click **Add maintenance**, create a task such as oil change, due in 5,000 miles and 180 days.
3. Click the completion checkmark on a task, enter the service date and odometer, and save.
4. See the task's next due date and mileage update automatically.
5. Go to **Service history** and verify that the completed work is recorded.
6. Use **Update mileage** to push the odometer past a task's mileage threshold and confirm the task becomes overdue.
7. Toggle between light and dark themes. Refresh the page and verify the preference is remembered.

## Project structure

```text
CarMaintenanceApp/
├── README.md                  (keep your original)
├── START_HERE.md              setup and first-use instructions
├── .gitignore
└── apps/
    ├── api/
    │   ├── app/
    │   │   ├── db.py          SQLAlchemy database connection
    │   │   ├── models.py      normalized tables with owner_id
    │   │   ├── schemas.py     request and response validation
    │   │   ├── scheduling.py  shared, tested due-date logic
    │   │   └── main.py        REST CRUD endpoints
    │   ├── migrations/        Alembic baseline
    │   ├── tests/             backend tests
    │   ├── alembic.ini
    │   └── requirements.txt
    └── web/
        ├── app/
        │   ├── page.tsx       responsive interactive dashboard
        │   ├── layout.tsx
        │   └── globals.css    theme and mobile styles
        ├── lib/api.ts        typed HTTP client
        └── package.json
```

## API routes

- `GET /health`
- `GET/POST /api/vehicles`
- `PATCH /api/vehicles/{vehicle_id}`
- `POST /api/vehicles/{vehicle_id}/odometer`
- `GET/POST /api/vehicles/{vehicle_id}/tasks`
- `PATCH/DELETE /api/vehicles/{vehicle_id}/tasks/{task_id}`
- `POST /api/vehicles/{vehicle_id}/tasks/{task_id}/complete`
- `GET/POST /api/vehicles/{vehicle_id}/service-records`

## Scheduling behavior

The task is overdue if the due date is in the past **or** the current odometer exceeds the due mileage. It is due on the exact due date or mileage, and "due soon" within 30 days or 500 miles of either threshold.

When you mark a repeating task complete, the next due values are based on **the completion date and recorded mileage**, not the old due values. One-time tasks become completed rather than recurring.

Important edge cases for future iterations: adjusting service history, odometer correction (e.g. dashboard replacement), maintenance forecasts from driving patterns, time zone preferences, and user-configurable reminder lead times.

## Next milestones

1. Supabase Auth and secure multi-account ownership checks. Remove local owner bypass before public deployment.
2. Manufacturer/AI maintenance suggestions with manual review; natural-language service entry.
3. Email and SMS reminders using Resend and Twilio, configurable leads, opt-in, retry-safe scheduled worker, delivery logs.
4. Additional vehicles, receipt uploads, and production deployment.

**Architecture choice:** SQLite is the default only to make local development immediate. Set `DATABASE_URL=postgresql+psycopg://...` to move to PostgreSQL and run `alembic upgrade head`. Do not commit `.env` or production secrets.
