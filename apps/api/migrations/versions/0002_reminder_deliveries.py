"""Persist reminder delivery attempts and suppress duplicate emails.

Revision ID: 0002_reminder_deliveries
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_reminder_deliveries"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "reminder_deliveries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("task_id", sa.String(length=36), sa.ForeignKey("maintenance_tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("recipient", sa.String(length=320), nullable=False),
        sa.Column("subject", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.UniqueConstraint("fingerprint", name="uq_reminder_delivery_fingerprint"),
    )
    op.create_index("ix_reminder_deliveries_task_id", "reminder_deliveries", ["task_id"])


def downgrade():
    op.drop_index("ix_reminder_deliveries_task_id", table_name="reminder_deliveries")
    op.drop_table("reminder_deliveries")
