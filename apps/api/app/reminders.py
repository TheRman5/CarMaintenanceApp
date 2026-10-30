"""Email service reminders. Runs independently of FastAPI and the web app.

For this development milestone, only the fixed local-dev owner is notified.
"""
import argparse
import hashlib
import os
from datetime import date, datetime, timedelta, timezone
from typing import Callable

import httpx
from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import MaintenanceTask, ReminderDelivery, Vehicle
from .scheduling import status_for

DEV_OWNER_ID = "local-dev-user"
ALERT_STATUSES = {"due_soon", "due", "overdue"}


def reminder_key(task: MaintenanceTask, status: str) -> str:
    """One email per status and due schedule, including after service resets the schedule."""
    value = f"{task.id}|{task.next_due_date}|{task.next_due_mileage}|{status}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def message_for(task: MaintenanceTask, vehicle: Vehicle, status: str, today: date) -> tuple[str, str]:
    name = f"{vehicle.year} {vehicle.make} {vehicle.model}"
    status_label = {"due_soon": "Due soon", "due": "Due now", "overdue": "Overdue"}[status]
    subject = f"{status_label}: {task.name} for {name}"
    lines = [
        f"Maintenance alert: {status_label.lower()}",
        f"Vehicle: {name}",
        f"Service: {task.name}",
        f"Current odometer: {vehicle.odometer:,} miles",
    ]
    if task.next_due_date is not None:
        lines.append(f"Due date: {task.next_due_date.isoformat()} ({(task.next_due_date - today).days:+d} days)")
    if task.next_due_mileage is not None:
        lines.append(
            f"Due mileage: {task.next_due_mileage:,} miles "
            f"({task.next_due_mileage - vehicle.odometer:+,} miles remaining)"
        )
    lines.append("\nOpen your Car Maintenance App when convenient to record completed work.")
    return subject, "\n".join(lines)


def _claim(db: Session, task: MaintenanceTask, vehicle: Vehicle, status: str, today: date, recipient: str):
    """Reserve delivery in the database, or retry a failed/stale claim atomically."""
    key = reminder_key(task, status)
    now = datetime.now(timezone.utc)
    delivery = ReminderDelivery(
        fingerprint=key, task_id=task.id, recipient=recipient,
        subject=message_for(task, vehicle, status, today)[0],
        body=message_for(task, vehicle, status, today)[1],
        state="sending", attempts=1, claimed_at=now,
    )
    db.add(delivery)
    try:
        db.commit()
        db.refresh(delivery)
        return delivery
    except IntegrityError:
        db.rollback()

    # A successful send is never repeated. A failed send can retry immediately.
    # A worker interrupted during sending can retry after the claim lease expires.
    result = db.execute(
        update(ReminderDelivery)
        .where(
            ReminderDelivery.fingerprint == key,
            ReminderDelivery.state != "sent",
            or_(
                ReminderDelivery.state == "failed",
                ReminderDelivery.claimed_at < now - timedelta(hours=1),
            ),
        )
        .values(
            state="sending",
            attempts=ReminderDelivery.attempts + 1,
            claimed_at=now,
            last_error=None,
        )
    )
    db.commit()
    if result.rowcount != 1:
        return None
    return db.scalar(select(ReminderDelivery).where(ReminderDelivery.fingerprint == key))


def send_with_resend(delivery: ReminderDelivery) -> None:
    api_key = os.getenv("RESEND_API_KEY")
    sender = os.getenv("REMINDER_EMAIL_FROM")
    if not api_key or not sender:
        raise RuntimeError("RESEND_API_KEY and REMINDER_EMAIL_FROM must be configured")
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Idempotency-Key": delivery.fingerprint,
        },
        json={
            "from": sender,
            "to": [delivery.recipient],
            "subject": delivery.subject,
            "text": delivery.body,
        },
        timeout=25.0,
    )
    response.raise_for_status()
    if not response.json().get("id"):
        raise RuntimeError("Resend did not return an email id")


def run_reminders(
    db: Session,
    *,
    today: date | None = None,
    recipient: str,
    sender: Callable[[ReminderDelivery], None] = send_with_resend,
    dry_run: bool = False,
    warning_days: int = 30,
    warning_miles: int = 500,
) -> dict[str, int]:
    if warning_days < 0 or warning_miles < 0:
        raise ValueError("Warning thresholds cannot be negative")
    if not dry_run and not recipient.strip():
        raise ValueError("A reminder recipient email is required")
    today = today or date.today()
    counts = {"eligible": 0, "sent": 0, "skipped": 0, "failed": 0}
    pairs = db.execute(
        select(MaintenanceTask, Vehicle)
        .join(Vehicle, MaintenanceTask.vehicle_id == Vehicle.id)
        .where(MaintenanceTask.owner_id == DEV_OWNER_ID, Vehicle.owner_id == DEV_OWNER_ID)
    ).all()
    for task, vehicle in pairs:
        status = status_for(
            today, vehicle.odometer, task.next_due_date, task.next_due_mileage,
            warning_days=warning_days, warning_miles=warning_miles,
        )
        if status not in ALERT_STATUSES:
            continue
        counts["eligible"] += 1
        if dry_run:
            print(f"[DRY RUN] {vehicle.year} {vehicle.make} {vehicle.model}: {task.name} ({status})")
            continue
        claim = _claim(db, task, vehicle, status, today, recipient)
        if claim is None:
            counts["skipped"] += 1
            continue
        try:
            sender(claim)
        except Exception as exc:
            claim.state = "failed"
            claim.last_error = str(exc)[:500]
            db.commit()
            print(f"Email failed for task {task.id}: {type(exc).__name__}")
            counts["failed"] += 1
        else:
            claim.state = "sent"
            claim.sent_at = datetime.now(timezone.utc)
            db.commit()
            counts["sent"] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Check service deadlines and email reminders")
    parser.add_argument("--dry-run", action="store_true", help="Preview eligible tasks without emailing or writing records")
    args = parser.parse_args()
    if not os.getenv("DATABASE_URL"):
        parser.error("Set DATABASE_URL explicitly to the database containing your maintenance records")
    if not args.dry_run and not os.getenv("DATABASE_URL", "").startswith("postgresql+psycopg://"):
        parser.error("Automated email delivery requires hosted PostgreSQL; SQLite is supported for previews only")
    recipient = os.getenv("REMINDER_EMAIL_TO", "")
    if not args.dry_run and (not recipient or not os.getenv("RESEND_API_KEY") or not os.getenv("REMINDER_EMAIL_FROM")):
        parser.error("Set REMINDER_EMAIL_TO, REMINDER_EMAIL_FROM, and RESEND_API_KEY")
    days = int(os.getenv("REMINDER_WARNING_DAYS", "30"))
    miles = int(os.getenv("REMINDER_WARNING_MILES", "500"))
    with SessionLocal() as db:
        results = run_reminders(
            db, recipient=recipient, dry_run=args.dry_run,
            warning_days=days, warning_miles=miles,
        )
    print(f"Reminders: {results}")
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
