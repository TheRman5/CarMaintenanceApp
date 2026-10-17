from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class VehicleCreate(BaseModel):
    year: int = Field(ge=1886, le=2100)
    make: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    trim: str | None = Field(default=None, max_length=80)
    engine: str | None = Field(default=None, max_length=100)
    vin: str | None = Field(default=None, min_length=17, max_length=17)
    odometer: int = Field(default=0, ge=0)

    @field_validator("vin")
    @classmethod
    def clean_vin(cls, value: str | None) -> str | None:
        return value.upper() if value else None


class VehicleUpdate(BaseModel):
    year: int | None = Field(default=None, ge=1886, le=2100)
    make: str | None = Field(default=None, min_length=1, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=80)
    trim: str | None = Field(default=None, max_length=80)
    engine: str | None = Field(default=None, max_length=100)
    vin: str | None = Field(default=None, min_length=17, max_length=17)
    # Odometer changes are recorded via the dedicated endpoint.


class VehicleOut(VehicleCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class OdometerUpdate(BaseModel):
    mileage: int = Field(ge=0)


class TaskBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    interval_days: int | None = Field(default=None, gt=0)
    interval_miles: int | None = Field(default=None, gt=0)
    next_due_date: date | None = None
    next_due_mileage: int | None = Field(default=None, ge=0)



class TaskCreate(TaskBase):
    @model_validator(mode="after")
    def has_schedule(self):
        if self.next_due_date is None and self.next_due_mileage is None:
            raise ValueError("Provide a next due date or mileage.")
        return self


class TaskUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    interval_days: int | None = Field(default=None, gt=0)
    interval_miles: int | None = Field(default=None, gt=0)
    next_due_date: date | None = None
    next_due_mileage: int | None = Field(default=None, ge=0)


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vehicle_id: str
    last_completed_at: date | None
    last_completed_mileage: int | None
    status: str
    created_at: datetime


class ServiceInput(BaseModel):
    performed_at: date
    mileage: int = Field(ge=0)
    cost: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    notes: str | None = Field(default=None, max_length=4000)
    parts: str | None = Field(default=None, max_length=4000)


class ServiceCreate(ServiceInput):
    service_type: str = Field(min_length=1, max_length=120)


class ServiceOut(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vehicle_id: str
    task_id: str | None
    created_at: datetime
