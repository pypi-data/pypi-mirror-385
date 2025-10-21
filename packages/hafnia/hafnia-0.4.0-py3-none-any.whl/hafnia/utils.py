import hashlib
import os
import time
import zipfile
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional
from zipfile import ZipFile

import more_itertools
import pathspec
import rich
import seedir
from rich import print as rprint

from hafnia.log import sys_logger, user_logger

PATH_DATA = Path("./.data")
PATH_DATASETS = PATH_DATA / "datasets"
PATH_DATASET_RECIPES = PATH_DATA / "dataset_recipes"
PATH_TRAINER_PACKAGES = PATH_DATA / "trainers"
FILENAME_HAFNIAIGNORE = ".hafniaignore"
DEFAULT_IGNORE_SPECIFICATION = [
    "*.jpg",
    "*.png",
    "*.py[cod]",
    "*_cache/",
    "**.egg-info/",
    ".data",
    ".git",
    ".venv",
    ".vscode",
    "__pycache__",
    "trainer.zip",
    "tests",
    "wandb",
]


def timed(label: str):
    """
    Decorator factory that allows custom labels for timing.
    Usage: @timed("Custom Operation")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            operation_label = label or func.__name__
            tik = time.perf_counter()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                sys_logger.error(f"{operation_label} failed: {e}")
                raise  # Re-raise the exception after logging
            finally:
                elapsed = time.perf_counter() - tik
                sys_logger.debug(f"{operation_label} took {elapsed:.2f} seconds.")

        return wrapper

    return decorator


def get_path_hafnia_cache() -> Path:
    return Path.home() / "hafnia"


def get_path_torchvision_downloads() -> Path:
    return get_path_hafnia_cache() / "torchvision_downloads"


def get_path_hafnia_conversions() -> Path:
    return get_path_hafnia_cache() / "hafnia_conversions"


def now_as_str() -> str:
    """Get the current date and time as a string."""
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def get_trainer_package_path(trainer_name: str) -> Path:
    now = now_as_str()
    path_trainer = PATH_TRAINER_PACKAGES / f"{trainer_name}_{now}.zip"
    return path_trainer


def filter_trainer_package_files(trainer_path: Path, path_ignore_file: Optional[Path] = None) -> Iterator:
    path_ignore_file = path_ignore_file or trainer_path / FILENAME_HAFNIAIGNORE
    if not path_ignore_file.exists():
        ignore_specification_lines = DEFAULT_IGNORE_SPECIFICATION
        user_logger.info(
            f"No '{FILENAME_HAFNIAIGNORE}' was file found. Files are excluded using the default ignore patterns.\n"
            f"\tDefault ignore patterns: {DEFAULT_IGNORE_SPECIFICATION}\n"
            f"Add a '{FILENAME_HAFNIAIGNORE}' file to the root folder to make custom ignore patterns."
        )
    else:
        ignore_specification_lines = Path(path_ignore_file).read_text().splitlines()
    ignore_specification = pathspec.GitIgnoreSpec.from_lines(ignore_specification_lines)
    include_files = ignore_specification.match_tree(trainer_path, negate=True)
    return include_files


@timed("Wrapping recipe.")
def archive_dir(
    recipe_path: Path,
    output_path: Optional[Path] = None,
    path_ignore_file: Optional[Path] = None,
) -> Path:
    recipe_zip_path = output_path or recipe_path / "trainer.zip"
    assert recipe_zip_path.suffix == ".zip", "Output path must be a zip file"
    recipe_zip_path.parent.mkdir(parents=True, exist_ok=True)

    user_logger.info(f" Creating zip archive of '{recipe_path}'")
    include_files = filter_trainer_package_files(recipe_path, path_ignore_file)
    with ZipFile(recipe_zip_path, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zip_ref:
        for str_filepath in include_files:
            full_path = recipe_path / str_filepath
            zip_ref.write(full_path, str_filepath)
    show_trainer_package_content(recipe_zip_path)

    return recipe_zip_path


def size_human_readable(size_bytes: int, suffix="B") -> str:
    size_value = float(size_bytes)
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(size_value) < 1024.0:
            return f"{size_value:3.1f} {unit}{suffix}"
        size_value /= 1024.0
    return f"{size_value:.1f}Yi{suffix}"


def show_trainer_package_content(recipe_path: Path, style: str = "emoji", depth_limit: int = 3) -> None:
    def scan(parent: seedir.FakeDir, path: zipfile.Path, depth: int = 0) -> None:
        if depth >= depth_limit:
            return
        for child in path.iterdir():
            if child.is_dir():
                folder = seedir.FakeDir(child.name)
                scan(folder, child, depth + 1)
                folder.parent = parent
            else:
                parent.create_file(child.name)

    recipe = seedir.FakeDir("recipe")
    scan(recipe, zipfile.Path(recipe_path))
    rprint(recipe.seedir(sort=True, first="folders", style=style, printout=False))
    user_logger.info(f"Recipe size: {size_human_readable(os.path.getsize(recipe_path))}. Max size 800 MiB")


def get_dataset_path_in_hafnia_cloud() -> Path:
    if not is_hafnia_cloud_job():
        user_logger.error(
            f"The function '{get_dataset_path_in_hafnia_cloud.__name__}' should only be called, when "
            "running in HAFNIA cloud environment (HAFNIA_CLOUD-environment variable have been defined)"
        )

    return Path(os.getenv("MDI_DATASET_DIR", "/opt/ml/input/data/training"))


def is_hafnia_cloud_job() -> bool:
    """Check if the current job is running in HAFNIA cloud environment."""
    return os.getenv("HAFNIA_CLOUD", "false").lower() == "true"


def pascal_to_snake_case(name: str) -> str:
    """
    Convert PascalCase to snake_case.
    """
    return "".join(["_" + char.lower() if char.isupper() else char for char in name]).lstrip("_")


def snake_to_pascal_case(name: str) -> str:
    """
    Convert snake_case to PascalCase.
    """
    return "".join(word.capitalize() for word in name.split("_"))


def hash_from_string(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def pretty_print_list_as_table(
    table_title: str,
    dict_items: List[Dict],
    column_name_to_key_mapping: Dict,
) -> None:
    """
    Pretty print a list of dictionary elements as a table.
    """

    table = rich.table.Table(title=table_title)
    for i_dict, dictionary in enumerate(dict_items):
        if i_dict == 0:
            for column_name, _ in column_name_to_key_mapping.items():
                table.add_column(column_name, justify="left", style="cyan", no_wrap=True)
        row = [str(dictionary.get(field, "")) for field in column_name_to_key_mapping.values()]
        table.add_row(*row)

    rich.print(table)


def is_hafnia_configured() -> bool:
    """
    Check if Hafnia is configured by verifying if the API key is set.
    """
    from cli.config import Config

    return Config().is_configured()


def remove_duplicates_preserve_order(seq: Iterable) -> List:
    """
    Remove duplicates from a list while preserving the order of elements.
    """
    return list(more_itertools.unique_everseen(seq))


def is_image_file(file_path: Path) -> bool:
    image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif")
    return file_path.suffix.lower() in image_extensions
