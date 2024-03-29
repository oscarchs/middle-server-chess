"""empty message

Revision ID: 2c61e4b0299b
Revises: d9a091d1ce2b
Create Date: 2019-12-03 15:33:43.511496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c61e4b0299b'
down_revision = 'd9a091d1ce2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'move', 'possible_moves', ['list_id'], ['id'])
    op.drop_column('move', 'possible_moves_id')
    op.drop_column('move', 'possible_move_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('move', sa.Column('possible_move_id', sa.VARCHAR(), nullable=True))
    op.add_column('move', sa.Column('possible_moves_id', sa.VARCHAR(), nullable=True))
    op.drop_constraint(None, 'move', type_='foreignkey')
    # ### end Alembic commands ###
