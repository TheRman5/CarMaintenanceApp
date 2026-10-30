from datetime import date, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models import MaintenanceTask, ReminderDelivery, Vehicle
from app.reminders import message_for, run_reminders


def test_reminders_send_once_and_send_again_after_due_schedule_changes():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    today = date(2026, 10, 30)
    sent = []

    def fake_sender(delivery):
        sent.append(delivery.fingerprint)

    try:
        with Session(engine, expire_on_commit=False) as db:
            vehicle = Vehicle(owner_id="local-dev-user", year=2012, make="Jeep", model="Wrangler", odometer=99500)
            db.add(vehicle)
            db.flush()
            task = MaintenanceTask(
                owner_id="local-dev-user", vehicle_id=vehicle.id, name="Oil change",
                next_due_mileage=100000, next_due_date=today + timedelta(days=14),
            )
            db.add(task)
            db.commit()
            a = run_reminders(db, today=today, recipient="dev@example.com", sender=fake_sender)
            assert a["sent"] == 1
            assert a["eligible"] == 1
            b = run_reminders(db, today=today, recipient="dev@example.com", sender=fake_sender)
            assert b["skipped"] == 1
            assert len(sent) == 1

            task.next_due_mileage = 105000
            task.next_due_date = today + timedelta(days=365)
            db.commit()
            assert run_reminders(db, today=today, recipient="dev@example.com", sender=fake_sender)["eligible"] == 0
            vehicle.odometer = 104600
            db.commit()
            assert run_reminders(db, today=today, recipient="dev@example.com", sender=fake_sender)["sent"] == 1
            assert len(sent) == 2
            assert len(db.scalars(select(ReminderDelivery)).all()) == 2
    finally:
        engine.dispose()


def test_failed_reminder_can_retry_and_dry_run_does_not_write():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    today = date(2026, 10, 30)
    try:
        with Session(engine, expire_on_commit=False) as db:
            v = Vehicle(owner_id="local-dev-user", year=2012, make="Jeep", model="Wrangler", odometer=100000)
            db.add(v)
            db.flush()
            t = MaintenanceTask(owner_id="local-dev-user", vehicle_id=v.id, name="Brake fluid", next_due_date=today)
            db.add(t)
            db.commit()
            assert run_reminders(db, today=today, recipient="", dry_run=True)["eligible"] == 1
            assert db.scalars(select(ReminderDelivery)).first() is None
            def fail(_):
                raise ValueError("testing")
            assert run_reminders(db, today=today, recipient="dev@example.com", sender=fail)["failed"] == 1
            delivered = []
            assert run_reminders(db, today=today, recipient="dev@example.com", sender=lambda d: delivered.append(d.id))["sent"] == 1
            assert delivered
            assert run_reminders(db, today=today, recipient="dev@example.com", sender=lambda d: delivered.append(d.id))["skipped"] == 1
            assert len(delivered) == 1
    finally:
        engine.dispose()
