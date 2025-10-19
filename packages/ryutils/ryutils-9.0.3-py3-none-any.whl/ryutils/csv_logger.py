"""
Utility script that helps write transactions to a spreadsheet
"""

import csv
import json
import os
import typing as T

from ryutils import log


class CsvLogger:
    def __init__(self, csv_file: str, header: T.List[str], dry_run=False, verbose=False) -> None:
        self.csv_file = csv_file
        self.header = header
        self.col_map = {col.lower(): i for i, col in enumerate(header)}
        self.dry_run = dry_run
        self._write_header_if_needed()
        self.verbose = verbose

    def write(self, data: T.Dict[str, T.Any]) -> None:
        if self.dry_run:
            return

        if self.verbose:
            log.print_bold(
                f"Writing stats to {self.csv_file}:\nStats:\n{json.dumps(data, indent=4)}"
            )
        with open(self.csv_file, "a", encoding="utf-8") as appendfile:
            csv_writer = csv.writer(appendfile)

            row = [""] * len(self.header)
            for key, value in data.items():
                try:
                    row[self.col_map[key.lower()]] = value
                except KeyError:
                    pass
            csv_writer.writerow(row)

    def read(self) -> T.List[T.List[T.Any]]:
        if not os.path.isfile(self.csv_file):
            return []

        with open(self.csv_file, encoding="utf-8") as infile:
            reader = list(csv.reader(infile))
        return reader[1:]

    def get_col_map(self) -> T.Dict[str, int]:
        return self.col_map

    def _write_header_if_needed(self) -> None:
        if self.dry_run:
            return

        if not os.path.isfile(self.csv_file):
            with open(self.csv_file, "w", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(self.header)
            return

        with open(self.csv_file, "r+", encoding="utf-8") as file:
            reader = list(csv.reader(file))

            if len(reader) == 0 or len(self.header) != len(
                [i for i in reader[0] if i in self.header]
            ):
                file.seek(0)
                file.truncate()
                writer = csv.writer(file)
                writer.writerow(self.header)
