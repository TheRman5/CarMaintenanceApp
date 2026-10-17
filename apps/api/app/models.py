import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def new_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    make: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    trim: Mapped[str | None] = mapped_column(String(80))
    engine: Mapped[str | None] = mapped_column(String(100))
    vin: Mapped[str | None] = mapped_column(String(17))
    odometer: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    vehicle_id: Mapped[str] = mapped_column(String(36), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    interval_days: Mapped[int | None] = mapped_column(Integer)
    interval_miles: Mapped[int | None] = mapped_column(Integer)
    next_due_date: Mapped[date | None] = mapped_column(Date)
    next_due_mileage: Mapped[int | None] = mapped_column(Integer)
    last_completed_at: Mapped[date | None] = mapped_column(Date)
    last_completed_mileage: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    vehicle_id: Mapped[str] = mapped_column(String(36), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("maintenance_tasks.id", ondelete="SET NULL"))
    performed_at: Mapped[date] = mapped_column(Date, nullable=False)
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    service_type: Mapped[str] = mapped_column(String(120), nullable=False)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    parts: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class OdometerReading(Base):
    __tablename__ = "odometer_readings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    vehicle_id: Mapped[str] = mapped_column(String(36), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
