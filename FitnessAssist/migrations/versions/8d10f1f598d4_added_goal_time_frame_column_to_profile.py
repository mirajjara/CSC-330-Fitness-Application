"""Added goal_time_frame column to profile

Revision ID: 8d10f1f598d4
Revises: 20bdf68c93e4
Create Date: 2024-04-18 16:42:53.234848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d10f1f598d4'
down_revision = '20bdf68c93e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profile', schema=None) as batch_op:
        batch_op.add_column(sa.Column('goal_time_frame', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profile', schema=None) as batch_op:
        batch_op.drop_column('goal_time_frame')

    # ### end Alembic commands ###