"""Add profile_img and introduce to User model

Revision ID: fb7867b656ef
Revises: b1c71a88acbb
Create Date: 2024-07-17 04:34:18.612223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb7867b656ef'
down_revision: Union[str, None] = 'b1c71a88acbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_img', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('introduce', sa.Text(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_nickname'), 'users', ['nickname'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_nickname'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'introduce')
    op.drop_column('users', 'profile_img')
    # ### end Alembic commands ###
