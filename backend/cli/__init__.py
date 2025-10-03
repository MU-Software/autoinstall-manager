from collections.abc import Callable
from pathlib import Path
from sys import path

from typer import Typer

app_dir = Path(__file__).parent.parent
path.insert(0, app_dir.as_posix())

from src.utils.importlib import load_module  # noqa: E402
from src.utils.stdlib import isiterable  # noqa: E402

typer_app = Typer()

current_dir = Path(__file__).parent
for module_path in current_dir.glob("*.py"):
    if module_path.stem.startswith("__"):
        continue
    module = load_module(module_path)

    cli_patterns: list[Callable] | None = getattr(module, "cli_patterns", None)
    if not (cli_patterns and isiterable(cli_patterns)):
        continue

    for cli_func in cli_patterns:
        typer_app.command()(cli_func)
