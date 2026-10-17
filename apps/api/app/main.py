import os
from datetime import date
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import MaintenanceTask, OdometerReading, ServiceRecord, Vehicle
from .scheduling import next_due, status_for
from .schemas import (
    OdometerUpdate, ServiceCreate, ServiceInput, ServiceOut,
    TaskCreate, TaskOut, TaskUpdate, VehicleCreate, VehicleOut, VehicleUpdate,
)

# Milestone 1 intentionally supports LOCAL DEVELOPMENT ONLY. No internet deployment.
# Supabase Auth + owner identity verification is the next security milestone.
if os.getenv("APP_ENV", "development") != "development":
    raise RuntimeError("Authentication not implemented. API refuses to run outside APP_ENV=development.")

app = FastAPI(title="Garage Maintenance Tracker API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

# Temporary fixed development identity. Replace with verified JWT identity before deploying.
DEV_OWNER_ID = "local-dev-user"


def get_vehicle(vehicle_id: str, db: Session) -> Vehicle:
    vehicle = db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.owner_id == DEV_OWNER_ID))
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


def get_task(vehicle_id: str, task_id: str, db: Session) -> MaintenanceTask:
    task = db.scalar(select(MaintenanceTask).where(
        MaintenanceTask.id == task_id,
        MaintenanceTask.vehicle_id == vehicle_id,
        MaintenanceTask.owner_id == DEV_OWNER_ID,
    ))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def task_response(task: MaintenanceTask, odometer: int) -> TaskOut:
    return TaskOut.model_validate({
        "id": task.id, "vehicle_id": task.vehicle_id, "name": task.name,
        "description": task.description, "interval_days": task.interval_days,
        "interval_miles": task.interval_miles, "next_due_date": task.next_due_date,
        "next_due_mileage": task.next_due_mileage, "last_completed_at": task.last_completed_at,
        "last_completed_mileage": task.last_completed_mileage,
        "status": ("completed" if task.last_completed_at and task.next_due_date is None and task.next_due_mileage is None else status_for(date.today(), odometer, task.next_due_date, task.next_due_mileage)),
        "created_at": task.created_at,
    })


@app.get("/health")
def health():
    return {"status": "ok", "mode": "local-development"}


@app.get("/api/vehicles", response_model=list[VehicleOut])
def list_vehicles(db: Session = Depends(get_db)):
    return db.scalars(select(Vehicle).where(Vehicle.owner_id == DEV_OWNER_ID).order_by(Vehicle.created_at)).all()


@app.post("/api/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = Vehicle(owner_id=DEV_OWNER_ID, **payload.model_dump())
    db.add(vehicle)
    db.flush()
    db.add(OdometerReading(owner_id=DEV_OWNER_ID, vehicle_id=vehicle.id, mileage=vehicle.odometer))
    db.commit()
    db.refresh(vehicle)
    return vehicle


@app.patch("/api/vehicles/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: str, payload: VehicleUpdate, db: Session = Depends(get_db)):
    vehicle = get_vehicle(vehicle_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@app.post("/api/vehicles/{vehicle_id}/odometer", response_model=VehicleOut)
def update_odometer(vehicle_id: str, payload: OdometerUpdate, db: Session = Depends(get_db)):
    vehicle = get_vehicle(vehicle_id, db)
    if payload.mileage < vehicle.odometer:
        raise HTTPException(status_code=422, detail="New odometer reading cannot be less than current reading")
    if payload.mileage > vehicle.odometer:
        vehicle.odometer = payload.mileage
        db.add(OdometerReading(owner_id=DEV_OWNER_ID, vehicle_id=vehicle.id, mileage=payload.mileage))
    db.commit()
    db.refresh(vehicle)
    return vehicle


@app.get("/api/vehicles/{vehicle_id}/tasks", response_model=list[TaskOut])
def list_tasks(vehicle_id: str, db: Session = Depends(get_db)):
    vehicle = get_vehicle(vehicle_id, db)
    tasks = db.scalars(select(MaintenanceTask).where(
        MaintenanceTask.owner_id == DEV_OWNER_ID,
        MaintenanceTask.vehicle_id == vehicle_id,
    ).order_by(MaintenanceTask.created_at)).all()
    return [task_response(task, vehicle.odometer) for task in tasks]


@app.post("/api/vehicles/{vehicle_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(vehicle_id: str, payload: TaskCreate, db: Session = Depends(get_db)):
    vehicle = get_vehicle(vehicle_id, db)
    task = MaintenanceTask(owner_id=DEV_OWNER_ID, vehicle_id=vehicle_id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task_response(task, vehicle.odometer)


@app.patch("/api/vehicles/{vehicle_id}/tasks/{task_id}", response_model=TaskOut)
def update_task(vehicle_id: str, task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    vehicle = get_vehicle(vehicle_id, db)
    task = get_task(vehicle_id, task_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    if task.next_due_date is None and task.next_due_mileage is None:
        raise HTTPException(status_code=422, detail="Task requires at least one next due date or mileage")
    db.commit()
    db.refresh(task)
    return task_response(task, vehicle.odometer)


@app.delete("/api/vehicles/{vehicle_id}/tasks/{task_id}", status_code=204)
def delete_task(vehicle_id: str, task_id: str, db: Session = Depends(get_db)):
    get_vehicle(vehicle_id, db)
    task = get_task(vehicle_id, task_id, db)
    db.delete(task)
    db.commit()


@app.post("/api/vehicles/{vehicle_id}/tasks/{task_id}/complete", response_model=ServiceOut, status_code=201)
def complete_task(vehicle_id: str, task_id: str, payload: ServiceInput, db: Session = Depends(get_db)):
    vehicle = get_vehicle(vehicle_id, db)
    task = get_task(vehicle_id, task_id, db)
    if payload.performed_at > date.today():
        raise HTTPException(status_code=422, detail="Completion date cannot be in the future")
    # Historical work can be logged, but must not roll a newer recurring schedule backwards.
    if task.last_completed_at and payload.performed_at < task.last_completed_at:
        raise HTTPException(status_code=422, detail="Completion predates most recent recorded completion")
    record = ServiceRecord(
        owner_id=DEV_OWNER_ID, vehicle_id=vehicle_id, task_id=task.id,
        service_type=task.name, **payload.model_dump(),
    )
    task.last_completed_at = payload.performed_at
    task.last_completed_mileage = payload.mileage
    task.next_due_date, task.next_due_mileage = next_due(
        payload.performed_at, payload.mileage, task.interval_days, task.interval_miles,
    )
    # One-off tasks disappear from the active schedule after completion, but the service stays in history.
    db.add(record)
    if payload.mileage > vehicle.odometer:
        vehicle.odometer = payload.mileage
        db.add(OdometerReading(owner_id=DEV_OWNER_ID, vehicle_id=vehicle.id, mileage=payload.mileage))
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/vehicles/{vehicle_id}/service-records", response_model=list[ServiceOut])
def list_service_records(vehicle_id: str, db: Session = Depends(get_db)):
    get_vehicle(vehicle_id, db)
    return db.scalars(select(ServiceRecord).where(
        ServiceRecord.owner_id == DEV_OWNER_ID, ServiceRecord.vehicle_id == vehicle_id,
    ).order_by(ServiceRecord.performed_at.desc(), ServiceRecord.created_at.desc())).all()


@app.post("/api/vehicles/{vehicle_id}/service-records", response_model=ServiceOut, status_code=201)
def create_service_record(vehicle_id: str, payload: ServiceCreate, db: Session = Depends(get_db)):
    vehicle = get_vehicle(vehicle_id, db)
    if payload.performed_at > date.today():
        raise HTTPException(status_code=422, detail="Service date cannot be in the future")
    record = ServiceRecord(owner_id=DEV_OWNER_ID, vehicle_id=vehicle_id, **payload.model_dump())
    db.add(record)
    if payload.mileage > vehicle.odometer:
        vehicle.odometer = payload.mileage
        db.add(OdometerReading(owner_id=DEV_OWNER_ID, vehicle_id=vehicle.id, mileage=payload.mileage))
    db.commit()
    db.refresh(record)
    return record
