import csv
import logging
from typing import AsyncGenerator

from docsloader import utils
from docsloader.base import BaseLoader, DocsData

logger = logging.getLogger(__name__)


class CsvLoader(BaseLoader):
    """
    csv loader

    params:
        - path_or_url: str
        - suffix: str = None
        - encoding: str = None
        - load_type: str = "basic"
        - load_options: dict = None
        - metadata: dict = None
        - rm_tmpfile: bool = False
    """

    async def load_by_basic(self) -> AsyncGenerator[DocsData, None]:
        csv_sep = self.load_options.get("csv_sep")
        table_fmt = self.load_options.get("table_fmt")
        with open(self.tmpfile, "r", encoding=self.encoding, newline="") as f:  # header
            reader = csv.reader(f, delimiter=csv_sep)
            try:
                header = [col.strip() or None for col in next(reader)]
            except StopIteration:
                return
            header_len = len(header)
            for row in reader:
                if len(row) > header_len:
                    header_len = len(row)
            if len(header) < header_len:
                header.extend([None] * (header_len - len(header)))  # noqa
        with open(self.tmpfile, "r", encoding=self.encoding, newline="") as f:  # body
            reader = csv.reader(f, delimiter=csv_sep)
            try:
                next(reader)
            except StopIteration:
                return
            self.metadata.update({
                "header": header,
            })
            has_value = False
            for row in reader:
                has_value = True
                row = [r if r else None for r in row]
                row = (row + [None] * (header_len - len(row)))[:header_len]
                yield DocsData(
                    type="text",
                    text=utils.format_table(row, fmt=table_fmt),
                    data=row,
                    metadata=self.metadata,
                )
            if not has_value:
                yield DocsData(
                    type="text",
                    text="",
                    data=[],
                    metadata=self.metadata,
                )
