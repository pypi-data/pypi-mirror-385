from pathlib import Path
from typing import Optional

import click

from cli import consts
from cli.config import Config
from hafnia import utils


@click.group()
def dataset():
    """Manage dataset interaction"""
    pass


@dataset.command("ls")
@click.pass_obj
def cmd_list_datasets(cfg: Config) -> None:
    """List available datasets on Hafnia platform"""
    from hafnia.platform.datasets import get_datasets, pretty_print_datasets

    datasets = get_datasets(cfg=cfg)
    pretty_print_datasets(datasets)


@dataset.command("download")
@click.argument("dataset_name")
@click.option(
    "--destination",
    "-d",
    default=None,
    required=False,
    help=f"Destination folder to save the dataset. Defaults to '{utils.PATH_DATASETS}/<dataset_name>'",
)
@click.option("--force", "-f", is_flag=True, default=False, help="Flag to enable force redownload")
@click.pass_obj
def cmd_dataset_download(cfg: Config, dataset_name: str, destination: Optional[click.Path], force: bool) -> Path:
    """Download dataset from Hafnia platform"""

    from hafnia.platform import datasets

    try:
        path_dataset = datasets.download_or_get_dataset_path(
            dataset_name=dataset_name,
            cfg=cfg,
            path_datasets_folder=destination,
            force_redownload=force,
        )
    except Exception:
        raise click.ClickException(consts.ERROR_GET_RESOURCE)
    return path_dataset
