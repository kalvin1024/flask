"""empty message

Revision ID: a00b9af4e16a
Revises: 9b9d8865b8a1
Create Date: 2023-09-20 03:59:41.654961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a00b9af4e16a'
down_revision = '9b9d8865b8a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
         # Step 1: Add the new column, allowing NULL values
        batch_op.add_column(sa.Column('email', sa.String(), nullable=True))
        
    # Step 2: Populate the column with default values
    op.execute("UPDATE users SET email = 'a@b.com' WHERE email IS NULL")

    # Alter users table: Update email column properties
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Step 3: Set the column to NOT NULL
        batch_op.alter_column('email', existing_type=sa.String(), nullable=False)

        # Step 4: Add unique constraint
        batch_op.create_unique_constraint(None, ['email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('email')

    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=False)

    # ### end Alembic commands ###