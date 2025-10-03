from collections.abc import Callable
from logging import getLogger
from os import getenv

from src.models import DefaultModelMixin
from src.settings import ProjectSetting

logger = getLogger(__name__)


def db_reset(create_tables: bool = False) -> None:
    config = ProjectSetting.from_dotenv(env_file=getenv("ENV_FILE", ".env"))

    if not config.server.debug:
        raise Exception("This command can only be used in debug mode.")

    with config.sqlalchemy.sync_session_maker() as session:
        DefaultModelMixin.metadata.drop_all(bind=session.get_bind(), checkfirst=True)
        logger.warning("All tables dropped.")

        if create_tables:
            DefaultModelMixin.metadata.create_all(bind=session.get_bind(), checkfirst=True)
            logger.warning("All tables created.")

        session.commit()


cli_patterns: list[Callable] = [db_reset]
