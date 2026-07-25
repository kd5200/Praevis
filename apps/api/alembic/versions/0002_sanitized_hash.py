"""Add sanitized_content_hash for integrity receipts.

Revision ID: 0002_sanitized_hash
Revises: 0001_initial
Create Date: 2026-07-25
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_sanitized_hash"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "scans",
        sa.Column("sanitized_content_hash", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("scans", "sanitized_content_hash")
