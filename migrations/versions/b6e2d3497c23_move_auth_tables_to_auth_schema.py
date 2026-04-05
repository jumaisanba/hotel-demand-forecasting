"""Move auth tables to auth schema

Revision ID: b6e2d3497c23
Revises: a9924596f2fc
Create Date: 2026-02-28 20:38:03.962031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6e2d3497c23'
down_revision: Union[str, Sequence[str], None] = 'a9924596f2fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create auth schema and move auth tables from public -> auth
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute('ALTER TABLE public."user" SET SCHEMA auth')
    op.execute("ALTER TABLE public.user_hotel SET SCHEMA auth")

    # Drop cross-context FK: auth.user_hotel.hotel_id -> booking/public.hotel.id
    op.drop_constraint(
        "user_hotel_hotel_id_fkey",
        "user_hotel",
        schema="auth",
        type_="foreignkey",
    )

    # Recreate FK: auth.user_hotel.user_id -> auth.user.id
    op.drop_constraint(
        "user_hotel_user_id_fkey",
        "user_hotel",
        schema="auth",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "user_hotel_user_id_fkey",
        source_table="user_hotel",
        referent_table="user",
        local_cols=["user_id"],
        remote_cols=["id"],
        source_schema="auth",
        referent_schema="auth",
        ondelete="CASCADE",
    )

    # Move sequences and fix id defaults to point to auth.*
    op.execute("ALTER SEQUENCE IF EXISTS public.user_id_seq SET SCHEMA auth")
    op.execute("ALTER SEQUENCE IF EXISTS public.user_hotel_id_seq SET SCHEMA auth")
    op.execute("""ALTER TABLE auth."user" ALTER COLUMN id SET DEFAULT nextval('auth.user_id_seq')""")
    op.execute("""ALTER TABLE auth.user_hotel ALTER COLUMN id SET DEFAULT nextval('auth.user_hotel_id_seq')""")


def downgrade() -> None:
    """Downgrade schema."""
    # Move sequences back and restore id defaults to public.*
    op.execute("""ALTER TABLE auth.user_hotel ALTER COLUMN id SET DEFAULT nextval('public.user_hotel_id_seq')""")
    op.execute("""ALTER TABLE auth."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq')""")
    op.execute("ALTER SEQUENCE IF EXISTS auth.user_hotel_id_seq SET SCHEMA public")
    op.execute("ALTER SEQUENCE IF EXISTS auth.user_id_seq SET SCHEMA public")

    # Move tables back auth -> public and restore FK: public.user_hotel.user_id -> public.user.id
    op.drop_constraint("user_hotel_user_id_fkey", "user_hotel", schema="auth", type_="foreignkey")
    op.execute("ALTER TABLE auth.user_hotel SET SCHEMA public")
    op.execute('ALTER TABLE auth."user" SET SCHEMA public')
    op.create_foreign_key(
        "user_hotel_user_id_fkey",
        source_table="user_hotel",
        referent_table="user",
        local_cols=["user_id"],
        remote_cols=["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )

    # FK to hotel is intentionally not restored.