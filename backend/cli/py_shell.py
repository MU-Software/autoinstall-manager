from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from functools import partial
from os import getenv

import sqlalchemy as sa
from anyio import to_thread
from asyncer import syncify
from IPython.terminal.ipapp import TerminalIPythonApp
from src.models import MODELS
from src.settings import ProjectSetting
from traitlets.config import Config


@partial(syncify, raise_sync_error=False)
async def py_shell() -> None:  # type: ignore[misc]
    config = ProjectSetting.from_dotenv(env_file=getenv("ENV_FILE", ".env"))

    async with config.sqlalchemy.async_session_maker() as session:
        ipy_namespace = {
            # SQLAlchemy
            "sa": sa,
            # Datetime utilities
            "datetime": datetime,
            "date": date,
            "time": time,
            "timedelta": timedelta,
            "now": datetime.now,
            "today": date.today,
            "yesterday": lambda: date.today() - timedelta(days=1),
            "tomorrow": lambda: date.today() + timedelta(days=1),
            # App config
            "config": config,
            # Database models
            **MODELS,
            # Async SQLModel Session
            "session": session,
        }

        c = Config()
        c.TerminalInteractiveShell.autoawait = True
        c.TerminalInteractiveShell.loop_runner = "asyncio"
        instance = TerminalIPythonApp.instance(config=c, user_ns=ipy_namespace)
        instance.initialize(argv=[])

        try:
            await to_thread.run_sync(instance.start)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.aclose()
            await config.sqlalchemy.async_cleanup()


cli_patterns: list[Callable] = [py_shell]
