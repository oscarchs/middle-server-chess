"""empty message

Revision ID: 5829c273b4df
Revises: 3c88eeb2efd9
Create Date: 2019-12-03 14:21:16.407037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5829c273b4df'
down_revision = '3c88eeb2efd9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'list_possible_moves', 'player', ['player_id'], ['id'])
    op.create_foreign_key(None, 'list_possible_moves', 'chess_game', ['game_id'], ['id'])
    op.add_column('move', sa.Column('list_id', sa.Unicode(), nullable=True))
    op.create_foreign_key(None, 'move', 'list_possible_moves', ['list_id'], ['id'])
    op.drop_column('move', 'possible_moves_id')
    op.drop_column('move', 'possible_move_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('move', sa.Column('possible_move_id', sa.VARCHAR(), nullable=True))
    op.add_column('move', sa.Column('possible_moves_id', sa.VARCHAR(), nullable=True))
    op.drop_constraint(None, 'move', type_='foreignkey')
    op.drop_column('move', 'list_id')
    op.drop_constraint(None, 'list_possible_moves', type_='foreignkey')
    op.drop_constraint(None, 'list_possible_moves', type_='foreignkey')
    # ### end Alembic commands ###
