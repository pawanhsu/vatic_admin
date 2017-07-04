"""update video tables:foreign key to user table

Revision ID: d2731ef989cd
Revises: ac426beb0df8
Create Date: 2017-06-27 10:29:15.433742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2731ef989cd'
down_revision = 'ac426beb0df8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('videos',
        sa.Column('user_id',sa.String(50),sa.ForeignKey('users.id'),default = 'max.hsu@ironyun.com')

    )


def downgrade():
    pass
