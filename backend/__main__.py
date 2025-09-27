from os import getenv
from pathlib import Path
from sys import path

from uvicorn.server import Server

app_dir = Path(__file__).parent
path.insert(0, app_dir.as_posix())

from src.settings import ProjectSetting  # noqa: E402

if __name__ == "__main__":
    uvicorn_config = ProjectSetting.from_dotenv(env_file=getenv("ENV_FILE", ".env")).to_uvicorn_config()
    Server(config=uvicorn_config).run()
