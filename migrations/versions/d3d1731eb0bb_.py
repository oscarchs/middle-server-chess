"""empty message

Revision ID: d3d1731eb0bb
Revises: 1d214bacc4c7
Create Date: 2019-12-03 08:57:45.527804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3d1731eb0bb'
down_revision = '1d214bacc4c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'move', 'possible_moves', ['possible_move_id'], ['id'])
    op.drop_column('move', 'possible_moves_id')
    op.add_column('possible_moves', sa.Column('game_id', sa.Unicode(), nullable=True))
    op.create_foreign_key(None, 'possible_moves', 'chess_game', ['game_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'possible_moves', type_='foreignkey')
    op.drop_column('possible_moves', 'game_id')
    op.add_column('move', sa.Column('possible_moves_id', sa.VARCHAR(), nullable=True))
    op.drop_constraint(None, 'move', type_='foreignkey')
    # ### end Alembic commands ###
