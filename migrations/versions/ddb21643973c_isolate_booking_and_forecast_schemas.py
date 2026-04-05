"""Isolate booking and forecast schemas

Revision ID: ddb21643973c
Revises: b6e2d3497c23
Create Date: 2026-03-02 17:57:33.628535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddb21643973c'
down_revision: Union[str, Sequence[str], None] = 'b6e2d3497c23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # create schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS booking")
    op.execute("CREATE SCHEMA IF NOT EXISTS forecast")

    # drop foreign keys in public
    op.drop_constraint("booking_hotel_id_fkey", "booking", schema="public", type_="foreignkey")
    op.drop_constraint("hotel_city_id_fkey", "hotel", schema="public", type_="foreignkey")
    op.drop_constraint("prediction_hotel_id_fkey", "prediction", schema="public", type_="foreignkey")
    op.drop_constraint("weather_city_id_fkey", "weather", schema="public", type_="foreignkey")

    # move tables
    op.execute("ALTER TABLE public.city SET SCHEMA booking")
    op.execute("ALTER TABLE public.hotel SET SCHEMA booking")
    op.execute("ALTER TABLE public.booking SET SCHEMA booking")

    op.execute("ALTER TABLE public.weather SET SCHEMA forecast")
    op.execute("ALTER TABLE public.holiday SET SCHEMA forecast")
    op.execute("ALTER TABLE public.prediction SET SCHEMA forecast")

    # recreate booking-internal foreign keys
    op.create_foreign_key(
        "hotel_city_id_fkey",
        source_table="hotel",
        referent_table="city",
        local_cols=["city_id"],
        remote_cols=["id"],
        source_schema="booking",
        referent_schema="booking",
    )
    op.create_foreign_key(
        "booking_hotel_id_fkey",
        source_table="booking",
        referent_table="hotel",
        local_cols=["hotel_id"],
        remote_cols=["id"],
        source_schema="booking",
        referent_schema="booking",
    )

    # move sequences
    op.execute("ALTER SEQUENCE IF EXISTS public.city_id_seq SET SCHEMA booking")
    op.execute("ALTER SEQUENCE IF EXISTS public.hotel_id_seq SET SCHEMA booking")
    op.execute("ALTER SEQUENCE IF EXISTS public.booking_id_seq SET SCHEMA booking")

    op.execute("ALTER SEQUENCE IF EXISTS public.weather_id_seq SET SCHEMA forecast")
    op.execute("ALTER SEQUENCE IF EXISTS public.holiday_id_seq SET SCHEMA forecast")
    op.execute("ALTER SEQUENCE IF EXISTS public.prediction_id_seq SET SCHEMA forecast")

    # update defaults
    op.execute("ALTER TABLE booking.city ALTER COLUMN id SET DEFAULT nextval('booking.city_id_seq')")
    op.execute("ALTER TABLE booking.hotel ALTER COLUMN id SET DEFAULT nextval('booking.hotel_id_seq')")
    op.execute("ALTER TABLE booking.booking ALTER COLUMN id SET DEFAULT nextval('booking.booking_id_seq')")

    op.execute("ALTER TABLE forecast.weather ALTER COLUMN id SET DEFAULT nextval('forecast.weather_id_seq')")
    op.execute("ALTER TABLE forecast.holiday ALTER COLUMN id SET DEFAULT nextval('forecast.holiday_id_seq')")
    op.execute("ALTER TABLE forecast.prediction ALTER COLUMN id SET DEFAULT nextval('forecast.prediction_id_seq')")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("SET search_path TO public, booking, forecast")

    # drop booking foreign keys
    op.drop_constraint("booking_hotel_id_fkey", "booking", schema="booking", type_="foreignkey")
    op.drop_constraint("hotel_city_id_fkey", "hotel", schema="booking", type_="foreignkey")

    # move tables back
    op.execute("ALTER TABLE forecast.prediction SET SCHEMA public")
    op.execute("ALTER TABLE forecast.holiday SET SCHEMA public")
    op.execute("ALTER TABLE forecast.weather SET SCHEMA public")

    op.execute("ALTER TABLE booking.booking SET SCHEMA public")
    op.execute("ALTER TABLE booking.hotel SET SCHEMA public")
    op.execute("ALTER TABLE booking.city SET SCHEMA public")

    # move sequences back
    op.execute("ALTER SEQUENCE IF EXISTS city_id_seq SET SCHEMA public")
    op.execute("ALTER SEQUENCE IF EXISTS hotel_id_seq SET SCHEMA public")
    op.execute("ALTER SEQUENCE IF EXISTS booking_id_seq SET SCHEMA public")

    op.execute("ALTER SEQUENCE IF EXISTS weather_id_seq SET SCHEMA public")
    op.execute("ALTER SEQUENCE IF EXISTS holiday_id_seq SET SCHEMA public")
    op.execute("ALTER SEQUENCE IF EXISTS prediction_id_seq SET SCHEMA public")

    # restore defaults
    op.execute("ALTER TABLE public.city ALTER COLUMN id SET DEFAULT nextval('public.city_id_seq')")
    op.execute("ALTER TABLE public.hotel ALTER COLUMN id SET DEFAULT nextval('public.hotel_id_seq')")
    op.execute("ALTER TABLE public.booking ALTER COLUMN id SET DEFAULT nextval('public.booking_id_seq')")

    op.execute("ALTER TABLE public.weather ALTER COLUMN id SET DEFAULT nextval('public.weather_id_seq')")
    op.execute("ALTER TABLE public.holiday ALTER COLUMN id SET DEFAULT nextval('public.holiday_id_seq')")
    op.execute("ALTER TABLE public.prediction ALTER COLUMN id SET DEFAULT nextval('public.prediction_id_seq')")

    # recreate original foreign keys
    op.create_foreign_key(
        "hotel_city_id_fkey",
        source_table="hotel",
        referent_table="city",
        local_cols=["city_id"],
        remote_cols=["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        "booking_hotel_id_fkey",
        source_table="booking",
        referent_table="hotel",
        local_cols=["hotel_id"],
        remote_cols=["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        "weather_city_id_fkey",
        source_table="weather",
        referent_table="city",
        local_cols=["city_id"],
        remote_cols=["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        "prediction_hotel_id_fkey",
        source_table="prediction",
        referent_table="hotel",
        local_cols=["hotel_id"],
        remote_cols=["id"],
        source_schema="public",
        referent_schema="public",
    )