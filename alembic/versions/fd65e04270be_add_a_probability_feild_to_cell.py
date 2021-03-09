"""add a probability feild to Cell

Revision ID: fd65e04270be
Revises: 597872ae37c5
Create Date: 2021-03-08 08:09:17.209515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd65e04270be'
down_revision = '597872ae37c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notificationlist', sa.Column('probability', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notificationlist', 'probability')
    # ### end Alembic commands ###