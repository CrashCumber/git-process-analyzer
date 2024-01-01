import csv
import logging
import time
from pathlib import Path


# enum to do
def write_dataset(
    data_raw: dict | list, fieldnames: list, filename: str, repo_name: str
):
    dir_dataset = Path().absolute() / "datasets" / repo_name
    dir_dataset.mkdir(exist_ok=True, parents=True)

    file_path = dir_dataset / f"{filename}_{int(time.time())}.csv"
    logging.info("Write dataset in file %s", file_path)

    if isinstance(data_raw, dict):
        data = data_raw.values()
    else:
        data = data_raw

    with open(file_path, "w", newline="") as file_dataset:
        writer = csv.DictWriter(file_dataset, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
