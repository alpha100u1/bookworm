"""empty message

Revision ID: ece4f169367e
Revises: 88b2e9addb5a
Create Date: 2023-09-20 13:23:24.051307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ece4f169367e'
down_revision = '88b2e9addb5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contactus',
    sa.Column('contact_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('contact_email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('contact_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contactus')
    # ### end Alembic commands ###