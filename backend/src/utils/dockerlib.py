from datetime import datetime
from itertools import chain
from json import loads
from logging import getLogger
from pathlib import Path
from subprocess import run  # nosec B404

logger = getLogger(__name__)


def is_container() -> bool:
    cgroup = Path("/proc/self/cgroup")
    return Path("/.dockerenv").is_file() or cgroup.is_file() and "docker" in cgroup.read_text()


def get_local_image_list(repository: str) -> list[dict]:
    proc = run(  # nosec B603
        args=["docker", "image", "ls", "--format", "{{json .}}", repository],
        check=True,
        capture_output=True,
    )
    return sorted(
        [loads(line) for line in proc.stdout.decode().splitlines()],
        key=lambda x: datetime.strptime(x["CreatedAt"], "%Y-%m-%d %H:%M:%S %z %Z"),
        reverse=True,
    )


def build_docker_cmd(
    *,
    repository: str,
    cmd: list[str],
    env: dict[str, str] | None = None,
    tag: str | None = None,
    use_local_image_if_possible: bool = True,
) -> list[str]:
    docker_cmd = ["docker", "run", "-it", "--rm"]
    docker_env = list(chain.from_iterable(["--env", f"{k}={v}"] for k, v in (env or {}).items() if v))

    if use_local_image_if_possible and (local_repo_img := get_local_image_list(repository)):
        docker_img = [local_repo_img[0]["ID"]]
    else:
        docker_img = [repository + f":{tag}" if tag else ":latest"]

    return docker_cmd + docker_env + docker_img + cmd


def get_secret_file(secret_name: str) -> Path | None:
    return secret_file if (secret_file := (Path("/run/secrets") / secret_name)).exists() else None
