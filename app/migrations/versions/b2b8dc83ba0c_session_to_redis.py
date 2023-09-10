"""session_to_redis

Revision ID: b2b8dc83ba0c
Revises: 6c633631c35a
Create Date: 2023-09-10 12:11:02.576639

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2b8dc83ba0c'
down_revision = '6c633631c35a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('refresh_session')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('refresh_session',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_agent', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('expires_in', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='refresh_session_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='refresh_session_pkey')
    )
    # ### end Alembic commands ###