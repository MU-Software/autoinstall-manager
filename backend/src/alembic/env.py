from asyncio import run
from os import getenv

from alembic import context
from sqlalchemy.engine import Connection
from src.models import default_model_mixin_metadata
from src.settings import ProjectSetting

project_settings = ProjectSetting.from_dotenv(env_file=getenv("ENV_FILE", ".env"))


def run_migrations_offline() -> None:
    context.configure(
        url=project_settings.sqlalchemy.url,
        target_metadata=default_model_mixin_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=default_model_mixin_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = project_settings.sqlalchemy.async_engine

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    run(run_async_migrations())


(run_migrations_offline if context.is_offline_mode() else run_migrations_online)()
