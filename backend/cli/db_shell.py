from collections.abc import Callable
from itertools import chain
from os import environ, getenv
from subprocess import run  # nosec B404

from src.settings import ProjectSetting
from src.utils.dockerlib import build_docker_cmd
from src.utils.networklib import islocalhost


def db_shell(use_docker: bool = True) -> None:
    config = ProjectSetting.from_dotenv(env_file=getenv("ENV_FILE", ".env"))

    exec_environ: dict[str, str] = {
        "TZ": "Asia/Seoul",
        "PGPASSWORD": config.sqlalchemy.password,
    }
    kwargs: dict[str, str] = {
        "-U": config.sqlalchemy.username,
        "-h": config.sqlalchemy.host,
        "-p": str(config.sqlalchemy.port),
        "-d": config.sqlalchemy.name,
    }
    if use_docker and islocalhost(kwargs["-h"]):
        kwargs["-h"] = "host.docker.internal"

    psql_cli: list[str] = ["psql"]
    psql_args: list[str] = list(chain.from_iterable([k, v] for k, v in kwargs.items() if v))
    psql_exec: list[str] = psql_cli + psql_args
    if use_docker:
        psql_exec = build_docker_cmd(repository="postgres", cmd=psql_exec, env=exec_environ)

    run(args=psql_exec, env=environ | exec_environ)  # nosec B603


cli_patterns: list[Callable] = [db_shell]
