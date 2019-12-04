"""empty message

Revision ID: 1c0fb088501c
Revises: 2c61e4b0299b
Create Date: 2019-12-04 06:50:50.422001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c0fb088501c'
down_revision = '2c61e4b0299b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chess_game', sa.Column('votes', sa.Integer(), nullable=True))
    op.add_column('possible_moves', sa.Column('votes', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('possible_moves', 'votes')
    op.drop_column('chess_game', 'votes')
    # ### end Alembic commands ###