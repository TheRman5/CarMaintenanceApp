"""Initial garage schema (without tables added by later migrations).

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=100), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("make", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("trim", sa.String(length=80), nullable=True),
        sa.Column("engine", sa.String(length=100), nullable=True),
        sa.Column("vin", sa.String(length=17), nullable=True),
        sa.Column("odometer", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_vehicles_owner_id", "vehicles", ["owner_id"])

    op.create_table(
        "maintenance_tasks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=100), nullable=False),
        sa.Column("vehicle_id", sa.String(length=36), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("interval_days", sa.Integer(), nullable=True),
        sa.Column("interval_miles", sa.Integer(), nullable=True),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("next_due_mileage", sa.Integer(), nullable=True),
        sa.Column("last_completed_at", sa.Date(), nullable=True),
        sa.Column("last_completed_mileage", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_maintenance_tasks_owner_id", "maintenance_tasks", ["owner_id"])
    op.create_index("ix_maintenance_tasks_vehicle_id", "maintenance_tasks", ["vehicle_id"])

    op.create_table(
        "service_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=100), nullable=False),
        sa.Column("vehicle_id", sa.String(length=36), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_id", sa.String(length=36), sa.ForeignKey("maintenance_tasks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("performed_at", sa.Date(), nullable=False),
        sa.Column("mileage", sa.Integer(), nullable=False),
        sa.Column("service_type", sa.String(length=120), nullable=False),
        sa.Column("cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("parts", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_service_records_owner_id", "service_records", ["owner_id"])
    op.create_index("ix_service_records_vehicle_id", "service_records", ["vehicle_id"])

    op.create_table(
        "odometer_readings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=100), nullable=False),
        sa.Column("vehicle_id", sa.String(length=36), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mileage", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_odometer_readings_owner_id", "odometer_readings", ["owner_id"])
    op.create_index("ix_odometer_readings_vehicle_id", "odometer_readings", ["vehicle_id"])


def downgrade():
    op.drop_index("ix_odometer_readings_vehicle_id", table_name="odometer_readings")
    op.drop_index("ix_odometer_readings_owner_id", table_name="odometer_readings")
    op.drop_table("odometer_readings")

    op.drop_index("ix_service_records_vehicle_id", table_name="service_records")
    op.drop_index("ix_service_records_owner_id", table_name="service_records")
    op.drop_table("service_records")

    op.drop_index("ix_maintenance_tasks_vehicle_id", table_name="maintenance_tasks")
    op.drop_index("ix_maintenance_tasks_owner_id", table_name="maintenance_tasks")
    op.drop_table("maintenance_tasks")

    op.drop_index("ix_vehicles_owner_id", table_name="vehicles")
    op.drop_table("vehicles")
