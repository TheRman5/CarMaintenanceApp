# Car Maintenance App | Milestone 1 Setup Guide

This is a working local-development starter for vehicle management, odometer updates, maintenance tasks, recurrence, service history, and a persistent light/dark theme.

**Development only:** This milestone uses a fixed local-development owner and **does not implement authentication**. Do not deploy the backend to the public internet. A later milestone will implement server-side Supabase Auth verification and account isolation.

## Recommended setup: Windows 11 + WSL2 + Ubuntu 24.04

You can run the **FastAPI backend and Next.js frontend entirely inside WSL2**, while using VS Code and your normal Windows browser. No Docker, OpenAI key, Supabase account, Twilio account, or Resend account is needed for this milestone.

### Step 1: Install or confirm WSL2 (Windows PowerShell)

If you already have **Ubuntu running under WSL2**, skip to Step 2.

Open **PowerShell as Administrator** and run:

```powershell
wsl --install -d Ubuntu-24.04
```

Restart Windows if prompted, then open **Ubuntu 24.04** from the Start menu and create your Linux username and password.

Confirm WSL2 from PowerShell:

```powershell
wsl --list --verbose
```

Your Ubuntu distribution should show `VERSION 2`. If it shows `1`, run (in PowerShell):

```powershell
wsl --set-version Ubuntu-24.04 2
```

If the named distribution is not available, check `wsl --list --online` and use the Ubuntu 24.04 distribution name your system offers.

### Step 2: Install development tools (Ubuntu/WSL terminal)

**All commands from this point through Step 7 run in the Ubuntu terminal, not Windows PowerShell**, unless stated otherwise.

```bash
sudo apt update
sudo apt install -y git unzip curl ca-certificates build-essential python3 python3-venv python3-pip
python3 --version
```

You need **Python 3.12 or newer**. Ubuntu 24.04 normally includes Python 3.12. If your distribution has an older Python version, use Ubuntu 24.04 or install a supported Python release before proceeding.

Install **Node.js 22 inside WSL**, using [nvm](https://github.com/nvm-sh/nvm) (do not rely on a separate Windows Node.js installation):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 22
nvm alias default 22
node --version
npm --version
```

If `nvm` is not found after installation, close and reopen the Ubuntu terminal, then try `nvm --version` again.

### Step 3: Place the project in your WSL home directory

**If you already cloned or pushed the code to GitHub:**

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/TheRman5/CarMaintenanceApp.git
cd CarMaintenanceApp
```

If the repository is **already cloned**, do not clone it again. Just `cd` into that existing copy.

**If you have not yet added the starter files to your GitHub repository:**

1. Download `CarMaintenanceApp-Milestone1-WSL.zip` using your Windows browser.
2. In Ubuntu, clone your existing GitHub repository using the commands above.
3. Replace `YOUR_WINDOWS_USER` with your Windows profile folder name, then run:

```bash
cd ~/projects
unzip "/mnt/c/Users/YOUR_WINDOWS_USER/Downloads/CarMaintenanceApp-Milestone1-WSL.zip" -d ~/projects
cp -a ~/projects/CarMaintenanceApp-Starter/. ~/projects/CarMaintenanceApp/
cd ~/projects/CarMaintenanceApp
```

This copies `apps/`, `.gitignore`, and `START_HERE.md` into your repository while retaining your original `README.md` and Git history. If the ZIP is stored elsewhere, adjust the path. To find your Windows home path, run `$env:USERPROFILE` in PowerShell.

**Important:** Work from `~/projects/CarMaintenanceApp` in WSL, not `/mnt/c/...`; Linux filesystem storage typically performs better with Node development tools.

Verify the project folders exist:

```bash
ls apps/api apps/web
```

### Step 4: Start the Python backend (Ubuntu Terminal A)

Open the first Ubuntu terminal and run:

```bash
cd ~/projects/CarMaintenanceApp/apps/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Leave this terminal running. `alembic upgrade head` creates the local SQLite schema and `garage.db` under `apps/api`. The `.env` file contains local-development settings, and the app's built-in defaults match those settings. Do not commit `.env`.

To confirm the API is running, open these addresses in your **Windows browser**:

- Health check: http://localhost:8000/health
- Interactive API documentation: http://localhost:8000/docs

The health endpoint should return JSON indicating that the local development API is running. Modern WSL2 installations generally forward localhost ports to Windows automatically.

### Step 5: Start the Next.js frontend (Ubuntu Terminal B)

Open a **second Ubuntu terminal**, leaving the backend running in Terminal A:

```bash
cd ~/projects/CarMaintenanceApp/apps/web
cp .env.example .env.local
npm install
npm run dev
```

The frontend reads `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` from `apps/web/.env.local`. This points your browser to the backend running on port 8000.

Open **http://localhost:3000** in your Windows browser. You should see the dashboard.

To stop either development server, press `Ctrl+C` in its terminal. To restart later, use the shorter commands in Step 6.

### Step 6: Daily startup (after the first installation)

**Ubuntu Terminal A, API:**

```bash
cd ~/projects/CarMaintenanceApp/apps/api
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Ubuntu Terminal B, web app:**

```bash
cd ~/projects/CarMaintenanceApp/apps/web
npm run dev
```

Open http://localhost:3000 in Windows.

### Step 7: Run backend tests

You can open a third Ubuntu terminal, or stop the backend in Terminal A temporarily:

```bash
cd ~/projects/CarMaintenanceApp/apps/api
source .venv/bin/activate
python -m pytest -q
```

### Step 8: Edit code and push to GitHub

For convenient WSL development in VS Code, install VS Code on Windows and its **WSL extension**, then from Ubuntu:

```bash
cd ~/projects/CarMaintenanceApp
code .
```

Use VS Code's WSL environment so Node, Python, and Git run within Ubuntu.

After copying the starter files, review changes before committing:

```bash
cd ~/projects/CarMaintenanceApp
git status
git add .
git commit -m "Set up initial CarMaintenanceApp and WSL instructions"
git push origin HEAD
```

If only the guide changed, use `git add START_HERE.md` instead of `git add .`. Never commit `.env`, `.env.local`, `.venv`, `node_modules`, or your local SQLite database. The starter `.gitignore` excludes these files.

## Troubleshooting WSL

| Problem | What to check |
| --- | --- |
| `python3 -m venv` fails | Run `sudo apt install python3-venv` and verify `python3 --version` is 3.12+. |
| `nvm: command not found` | Run `source ~/.bashrc`, or reopen Ubuntu. See the [nvm installation instructions](https://github.com/nvm-sh/nvm). |
| `npm: command not found` | Confirm `nvm install 22` finished inside Ubuntu, then open a new terminal. |
| `ModuleNotFoundError` or missing `uvicorn` | Activate the backend environment using `source .venv/bin/activate`, then reinstall `python -m pip install -r requirements.txt`. |
| Browser cannot open the API | Ensure Terminal A is still running. In Ubuntu, try `curl http://127.0.0.1:8000/health`. If that works, review your WSL localhost-forwarding configuration. |
| Frontend says it cannot reach the backend | Confirm `http://localhost:8000/health` works in the **Windows browser**, and `apps/web/.env.local` has `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`. Restart `npm run dev` after any environment changes. |
| Port 3000 or 8000 is already in use | Stop old development servers with `Ctrl+C`, or inspect running processes using `ss -ltnp`. |
| Slow `npm install` or file watching | Keep the repository under `~/projects` in WSL rather than `/mnt/c`. |
| Changes are not appearing in Git | Run `git status` from your repository root. Check that starter contents were copied into the repository, not into a nested folder. |

If you previously installed the app using PowerShell, the WSL `.venv` and `node_modules` are **separate** from the Windows versions. Reinstall dependencies inside Ubuntu rather than copying those folders.

## First hands-on workflow

1. Click **Add a vehicle** and enter its details and current mileage.
2. Click **Add maintenance**. Create a task such as an oil change, due in 5,000 miles and 180 days.
3. Complete the task and enter the service date and odometer reading.
4. Verify the next due date and mileage update automatically.
5. Open **Service history** and confirm the completed work was recorded.
6. Use **Update mileage** to cross a maintenance threshold and confirm the task status changes.
7. Switch between light and dark modes. Refresh and confirm the preference persists.

## Project structure

```text
CarMaintenanceApp/
├── README.md                  existing project README
├── START_HERE.md              this setup guide
├── .gitignore
└── apps/
    ├── api/
    │   ├── app/
    │   │   ├── db.py          database connection
    │   │   ├── models.py      normalized tables with owner_id
    │   │   ├── schemas.py     request and response validation
    │   │   ├── scheduling.py  shared due-date logic
    │   │   └── main.py        REST CRUD endpoints
    │   ├── migrations/        Alembic baseline
    │   ├── tests/             backend tests
    │   ├── alembic.ini
    │   └── requirements.txt
    └── web/
        ├── app/
        │   ├── page.tsx       responsive dashboard
        │   ├── layout.tsx
        │   └── globals.css    theme and mobile styles
        ├── lib/api.ts         typed HTTP client
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

A task is overdue if its due date is past **or** the odometer has exceeded the due mileage. A task is due at the exact date or mileage threshold. It is due soon within 30 days or 500 miles of either threshold.

When you complete a recurring task, the new due values are calculated using the **completion date and recorded mileage**, not the prior thresholds. One-time tasks are marked completed.

## Next milestones

1. Supabase Auth and secure owner checks. Remove the development owner bypass before deployment.
2. Manufacturer/AI suggestions with manual approval and natural-language maintenance logging.
3. Resend email and Twilio SMS reminders with opt-in and retry-safe scheduled jobs.
4. Multiple vehicles, receipt uploads, and production deployment.

**Database note:** Local development uses SQLite by default. The backend also supports a PostgreSQL connection via `DATABASE_URL=postgresql+psycopg://...`; initialize a new database with `alembic upgrade head`. The application currently uses development-safe defaults; loading a non-default environment file into your shell will be needed before connecting to a different database.
