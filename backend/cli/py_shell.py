from collections.abc import Callable
from os import getenv

import sqlalchemy as sa
from IPython import start_ipython
from src.models import MODELS
from src.settings import ProjectSetting


def py_shell() -> None:
    config = ProjectSetting.from_dotenv(env_file=getenv("ENV_FILE", ".env"))

    with config.sqlalchemy.sync_session_maker() as session:
        try:
            ipy_namespace = {
                "sa": sa,
                "config": config,
                "session": session,
                **MODELS,
            }
            start_ipython(argv=[], user_ns=ipy_namespace)

            session.commit()
        except Exception as se:
            session.rollback()
            raise se
        finally:
            session.close()

    config.sqlalchemy.sync_cleanup()


cli_patterns: list[Callable] = [py_shell]
