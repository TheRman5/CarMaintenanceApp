"""Deterministic maintenance scheduling shared by API and future reminders."""
from calendar import monthrange
from datetime import date, timedelta


def status_for(
    today: date,
    odometer: int,
    due_date: date | None,
    due_mileage: int | None,
    *,
    warning_days: int = 30,
    warning_miles: int = 500,
) -> str:
    # If either interval is exceeded, the task is overdue (whichever comes first).
    if (due_date is not None and due_date < today) or (due_mileage is not None and due_mileage < odometer):
        return "overdue"
    if (due_date is not None and due_date == today) or (due_mileage is not None and due_mileage == odometer):
        return "due"
    if (due_date is not None and due_date <= today + timedelta(days=warning_days)) or (
        due_mileage is not None and due_mileage <= odometer + warning_miles
    ):
        return "due_soon"
    return "upcoming" if due_date is not None or due_mileage is not None else "unscheduled"


def next_due(performed_at: date, mileage: int, interval_days: int | None, interval_miles: int | None):
    return (
        performed_at + timedelta(days=interval_days) if interval_days is not None else None,
        mileage + interval_miles if interval_miles is not None else None,
    )
