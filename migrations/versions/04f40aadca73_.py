"""empty message

Revision ID: 04f40aadca73
Revises: 
Create Date: 2019-11-20 20:15:55.105444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04f40aadca73'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('password', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'password')
    # ### end Alembic commands ###
