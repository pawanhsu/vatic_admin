"""add forget password in uers

Revision ID: 0dca346e2e9d
Revises: d2731ef989cd
Create Date: 2017-07-06 10:34:02.421952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dca346e2e9d'
down_revision = 'd2731ef989cd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('forgetPasswordToken',sa.String(50),default=None))
    op.add_column('users', sa.Column('forgetPasswordTokenExpireTime',sa.DateTime,default=None))
    pass


def downgrade():
    pass
