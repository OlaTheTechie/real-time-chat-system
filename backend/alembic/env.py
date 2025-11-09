from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# add the app directory to the python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database.database import Base
from app.models import User, ChatRoom, Message, PasswordResetToken  # import all models
from app.core.config import settings

# this is the alembic config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with the one from settings (which reads from env vars)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# interpret the config file for python logging.
# this line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's metadata object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """run migrations in 'offline' mode.

    this configures the context with just a url
    and not an engine, though an engine is acceptable
    here as well.  by skipping the engine creation
    we don't even need a dbapi to be available.

    calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """run migrations in 'online' mode.

    in this scenario we need to create an engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()