"""update vatic user table

Revision ID: 366f3f37132e
Revises: 
Create Date: 2017-05-19 14:41:14.622687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '366f3f37132e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('verification',sa.Boolean,nullable=False,default = False))


def downgrade():
    pass
