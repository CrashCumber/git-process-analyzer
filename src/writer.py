import csv
from io import TextIOWrapper
from pathlib import Path

from attrs import asdict

from logger import logger


class DataSetWriter(csv.DictWriter):
    def writeheader(self):
        header = dict(zip(self.fieldnames, self.fieldnames))
        return super().writerow(header)

    def writerow(self, row):
        if row is None:
            return
        return super().writerow(asdict(row))


def prepare_file(
    fieldnames: list | tuple, filename: str, repo_name: str, timestamp, dir_dataset=None
) -> tuple[TextIOWrapper, DataSetWriter]:
    if not dir_dataset:
        dir_dataset = Path().absolute() / "datasets" / repo_name / timestamp

    dir_dataset.mkdir(exist_ok=True, parents=True)

    file_path = dir_dataset / f"{filename}.csv"
    logger.warn("Write dataset in file %s", file_path)
    file_dataset = open(file_path, "w", newline="")
    writer = DataSetWriter(file_dataset, fieldnames=fieldnames)
    writer.writeheader()
    return file_dataset, writer
