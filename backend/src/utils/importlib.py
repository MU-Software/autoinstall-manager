from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import TypeVar, cast

from src.utils.stdlib import isiterable

T = TypeVar("T")


def load_module(module_path: Path) -> ModuleType:
    if not module_path.is_file():
        raise ValueError(f"module_path must be file path: {module_path}")

    module_path = module_path.resolve()
    if not ((module_spec := spec_from_file_location(module_path.stem, module_path)) and module_spec.loader):
        raise ValueError(f"Failed to load module: {module_path}")

    module = module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def auto_import_objs(pattern_name: str, file_prefix: str, dir: Path) -> list[T]:
    collected_objs: list[T] = []
    for module_path in dir.glob(f"**/{file_prefix}*.py"):
        if module_path.stem.startswith("__"):
            continue

        if obj := cast(T, getattr(load_module(module_path), pattern_name, None)):
            collected_objs.append(obj)
    return collected_objs


def auto_import_patterns(pattern_name: str, file_prefix: str, dir: Path) -> list[T]:
    return list(filter(isiterable, auto_import_objs(pattern_name, file_prefix, dir)))
