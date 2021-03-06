"""empty message

Revision ID: d5654f813a1b
Revises: 
Create Date: 2018-06-12 18:48:48.076437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5654f813a1b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image_batch',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dirname', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.Text(), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('password'),
    sa.UniqueConstraint('username')
    )
    op.create_table('video_batch',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dirname', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('image_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.Text(), nullable=False),
    sa.Column('is_labeled', sa.Boolean(), nullable=False),
    sa.Column('batch_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['batch_id'], ['image_batch.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('image_task')
    op.drop_table('video_batch')
    op.drop_table('user')
    op.drop_table('image_batch')
    # ### end Alembic commands ###
