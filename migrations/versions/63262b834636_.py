"""empty message

Revision ID: 63262b834636
Revises: 6f5302295ee0
Create Date: 2019-12-03 08:55:33.384696

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63262b834636'
down_revision = '6f5302295ee0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('move', 'possible_move_id')
    op.add_column('possible_moves', sa.Column('game_id', sa.Unicode(), nullable=True))
    op.create_foreign_key(None, 'possible_moves', 'chess_game', ['game_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'possible_moves', type_='foreignkey')
    op.drop_column('possible_moves', 'game_id')
    op.add_column('move', sa.Column('possible_move_id', sa.VARCHAR(), nullable=True))
    # ### end Alembic commands ###
