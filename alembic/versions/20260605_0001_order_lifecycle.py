"""add order lifecycle fields

Revision ID: 20260605_0001
Revises:
Create Date: 2026-06-05
"""
from alembic import op
import sqlalchemy as sa

revision = "20260605_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("orders", sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"))
    op.add_column("orders", sa.Column("payment_status", sa.String(length=30), nullable=False, server_default="unpaid"))
    op.add_column("orders", sa.Column("total_amount", sa.Numeric(10, 2), nullable=False, server_default="0"))


def downgrade():
    op.drop_column("orders", "total_amount")
    op.drop_column("orders", "payment_status")
    op.drop_column("orders", "status")
