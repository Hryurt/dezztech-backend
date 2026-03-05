"""add company_roles and refactor users_companies role

Revision ID: 5d1ce1fee886
Revises: fde4df0b6f54
Create Date: 2026-03-02 21:48:48.734804

"""
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5d1ce1fee886'
down_revision: str | Sequence[str] | None = 'fde4df0b6f54'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'company_roles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name=op.f('uq_company_roles_name')),
    )
    op.create_index(op.f('ix_company_roles_id'), 'company_roles', ['id'], unique=False)

    op.add_column(
        'users_companies',
        sa.Column('role_id', sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        'fk_users_companies_role_id',
        'users_companies',
        'company_roles',
        ['role_id'],
        ['id'],
        ondelete='RESTRICT',
    )

    owner_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    op.bulk_insert(
        sa.table(
            'company_roles',
            sa.column('id', sa.Uuid()),
            sa.column('name', sa.String()),
            sa.column('permissions', postgresql.JSON()),
            sa.column('is_active', sa.Boolean()),
        ),
        [
            {'id': owner_id, 'name': 'owner', 'permissions': [], 'is_active': True},
            {'id': admin_id, 'name': 'admin', 'permissions': [], 'is_active': True},
        ],
    )

    op.execute(
        sa.text("""
            UPDATE users_companies uc
            SET role_id = cr.id
            FROM company_roles cr
            WHERE cr.name = uc.role AND uc.role_id IS NULL
        """)
    )
    op.alter_column(
        'users_companies',
        'role_id',
        existing_type=sa.Uuid(),
        nullable=False,
    )
    op.drop_column('users_companies', 'role')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'users_companies',
        sa.Column('role', sa.String(length=50), nullable=True),
    )
    op.drop_constraint('fk_users_companies_role_id', 'users_companies', type_='foreignkey')
    op.drop_column('users_companies', 'role_id')
    op.drop_index(op.f('ix_company_roles_id'), table_name='company_roles')
    op.drop_table('company_roles')
