# Persistent database and background email reminders

This milestone adds a **standalone Python reminder worker** and a GitHub Actions schedule. The frontend and FastAPI process do not need to be running for the scheduled job to send email. No AI API is required for this feature.

## How storage works

- Existing SQLite file `apps/api/garage.db` already persists across local application restarts, but GitHub-hosted jobs cannot read a local WSL database.
- To allow both your WSL app and the GitHub Actions job to see the same vehicles, tasks, and mileage, use **one hosted PostgreSQL database**, for example a Supabase project.
- This repository's existing SQLAlchemy and Alembic support PostgreSQL using the `postgresql+psycopg://` URL.
- **Development-only security:** the API still uses a fixed `local-dev-user` identity and has no real authentication. Bind the API only to `127.0.0.1`, never expose it publicly, and do not treat this as a production deployment.

## 1. Supabase: create and initialize the database

1. Create a project at https://supabase.com and copy its Postgres connection string from the project dashboard. Prefer a transaction or session pooler connection compatible with your network, and use the SQLAlchemy driver prefix `postgresql+psycopg://`. Use SSL as required by your provider.
2. Set the URL as `DATABASE_URL` in your WSL shell. **Do not commit the URL** (it contains database credentials).
3. If you previously entered data into local SQLite, note that creating a new Postgres database does **not** automatically move that data. You must migrate the existing records separately.
4. Run the migrations from `apps/api`:

```bash
cd apps/api
source .venv/bin/activate
export DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:PORT/postgres?sslmode=require'
alembic upgrade head
```

5. Start your existing local FastAPI process from the **same shell** with `DATABASE_URL` exported. The Next.js frontend requires no changes. Stop both local servers to verify the database remains accessible from the next startup.

## 2. Resend: configure email delivery

1. Create a Resend account at https://resend.com, verify a domain for the From address, and create a restricted email-sending API key.
2. Test/verification recipients and sending domains depend on your Resend account configuration. For normal delivery, use your own verified sending domain.
3. Add these **repository secrets** under GitHub Settings > Secrets and variables > Actions:
   - `DATABASE_URL`: the same hosted database URL your local API uses, with appropriate database permissions.
   - `RESEND_API_KEY`: your private Resend key.
   - `REMINDER_EMAIL_FROM`: a sender from your verified domain.
   - `REMINDER_EMAIL_TO`: the destination email.
4. Do not put secrets in `NEXT_PUBLIC_*`, application source, or screenshots.

## 3. Test before enabling delivery

Preview reminders locally without sending emails:

```bash
cd apps/api
source .venv/bin/activate
export DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:PORT/postgres?sslmode=require'
python -m app.reminders --dry-run
```

The existing rules treat tasks as due soon **30 days or 500 miles** before their next threshold. A task is `due` on the exact date/mileage and `overdue` once past either value. The daily worker sends one email for each task/due-schedule/status combination and stores records in `reminder_deliveries`. Repeated runs for the same status skip sending. A changed due schedule (for example after completion) can notify again, as can a later transition from due soon to due or overdue.

Run backend tests using `cd apps/api && python -m pytest -q`.

## 4. GitHub Actions scheduling

The workflow at `.github/workflows/maintenance-reminders.yml` supports **Run workflow** for manual testing and a cron schedule of **13:17 UTC daily**.

**Important GitHub limitation:** GitHub's `schedule` trigger only runs workflows from the repository's **default branch** (currently `main`). You can manually trigger the workflow from the feature/Dev branch to test, but automated daily runs require merging the workflow into `main`. GitHub may delay scheduled workflow execution.

The worker must have outbound connectivity to the database and Resend, even though the local app can be stopped. GitHub-hosted runners have ephemeral filesystems, so SQLite data stored only in a runner is not persistent.

## Safety and reliability

- An existing successful notification is suppressed by a unique database fingerprint.
- Failed notifications can retry, and interrupted claims can retry after one hour.
- Resend requests include an idempotency key to reduce duplicate sends caused by network errors; this is still not a strict exactly-once guarantee in all outage scenarios.
- No message is sent during dry runs.
- The development owner ID maps to a **single email**. This is not a multi-user notification system.
- Mileage-based reminders only reflect the **last entered odometer reading**. This worker does not estimate mileage while you are away.
- For production, implement Supabase Auth, actual user notification preferences, recipient verification/opt-in, secrets rotation and restricted worker DB credentials, and proper delivery observability.

## Next steps

When ready, extend reminders with a `notification_preferences` table for per-user destination and lead times, SMS through Twilio, and an OpenAI-based maintenance suggestion assistant that asks for approval before changing schedules.
