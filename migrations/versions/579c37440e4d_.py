"""empty message

Revision ID: 579c37440e4d
Revises: a53524410b9f
Create Date: 2019-12-03 14:00:49.195124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '579c37440e4d'
down_revision = 'a53524410b9f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('possible_move')
    op.create_foreign_key(None, 'list_possible_moves', 'chess_game', ['game_id'], ['id'])
    op.create_foreign_key(None, 'list_possible_moves', 'player', ['player_id'], ['id'])
    op.drop_column('move', 'possible_move_id')
    op.drop_column('move', 'possible_moves_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('move', sa.Column('possible_moves_id', sa.VARCHAR(), nullable=True))
    op.add_column('move', sa.Column('possible_move_id', sa.VARCHAR(), nullable=True))
    op.drop_constraint(None, 'list_possible_moves', type_='foreignkey')
    op.drop_constraint(None, 'list_possible_moves', type_='foreignkey')
    op.create_table('possible_move',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('player_id', sa.INTEGER(), nullable=True),
    sa.Column('game_id', sa.VARCHAR(), nullable=True),
    sa.Column('source_position', sa.VARCHAR(), nullable=True),
    sa.Column('target_position', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['chess_game.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['player.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
