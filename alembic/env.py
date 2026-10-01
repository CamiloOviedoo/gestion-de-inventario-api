from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context

from app.config import DATABASE_URL
from app.database import Base
from app.models.category import Category
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
    