import csv
import time
from io import TextIOWrapper
from pathlib import Path

from logger import logger


def write_dataset(
    data_raw: dict | list, fieldnames: list, filename: str, repo_name: str
):
    dir_dataset = Path().absolute() / "datasets" / repo_name
    dir_dataset.mkdir(exist_ok=True, parents=True)

    file_path = dir_dataset / f"{filename}_{int(time.time())}.csv"
    logger.info("Write dataset in file %s", file_path)

    if isinstance(data_raw, dict):
        data = data_raw.values()
    else:
        data = data_raw

    with open(file_path, "w", newline="") as file_dataset:
        writer = csv.DictWriter(file_dataset, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def prepare_file(
    fieldnames: list, filename: str, repo_name: str
) -> tuple[TextIOWrapper, csv.DictWriter]:
    dir_dataset = Path().absolute() / "datasets" / repo_name
    dir_dataset.mkdir(exist_ok=True, parents=True)

    file_path = dir_dataset / f"{filename}_{int(time.time())}.csv"
    logger.info("Write dataset in file %s", file_path)
    file_dataset = open(file_path, "w", newline="")
    writer = csv.DictWriter(file_dataset, fieldnames=fieldnames)
    writer.writeheader()
    return file_dataset, writer
