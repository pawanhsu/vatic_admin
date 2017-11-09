"""modify users

Revision ID: 33a9ad55c6f8
Revises: d2731ef989cd
Create Date: 2017-07-06 14:25:49.232941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33a9ad55c6f8'
down_revision = 'd2731ef989cd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('forgetPasswordToken',sa.String(50),default=None))
    op.add_column('users', sa.Column('forgetPasswordTokenExpireTime',sa.DateTime,default=None))
    pass

def downgrade():
    pass
