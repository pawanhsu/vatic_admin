"""create users table

Revision ID: ac426beb0df8
Revises:
Create Date: 2017-06-27 10:06:54.155878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac426beb0df8'
down_revision = None
branch_labels = None
depends_on = None



def upgrade():
    op.create_table('users',
        sa.Column('id',sa.String(50),nullable = False,primary_key = True),
        sa.Column('token',sa.String(30)),
        sa.Column('username',sa.String(50)),
        sa.Column('password',sa.String(50)),
        sa.Column('priority',sa.Integer),
        sa.Column('token',sa.String(50),unique = True, default = None),
        sa.Column('verification',sa.Boolean(),nullable = False,default = False)
    )


def downgrade():
    pass
