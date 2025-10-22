import copy
import logging
import time
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from ray.data._internal.util import infer_line_separator, find_head_n_line
from ray.data.block import Block
from ray.data.datasource.file_based_datasource import FileBasedDatasource
from ray.scripts.scripts import none_to_empty

if TYPE_CHECKING:
    import pyarrow

logger = logging.getLogger(__name__)

class CSVDatasource(FileBasedDatasource):
    """CSV datasource, for reading and writing CSV files."""

    _FILE_EXTENSIONS = [
        "csv",
        "csv.gz",  # gzip-compressed files
        "csv.br",  # Brotli-compressed files
        "csv.zst",  # Zstandard-compressed files
        "csv.lz4",  # lz4-compressed files
    ]

    def __init__(
        self,
        paths: Union[str, List[str]],
        arrow_csv_args: Optional[Dict[str, Any]] = None,
        **file_based_datasource_kwargs,
    ):
        from pyarrow import csv

        if arrow_csv_args is None:
            arrow_csv_args = {}

        file_split_chunk_size = arrow_csv_args.pop("file_split_chunk_size", self._DEFAULT_FILE_SPLIT_CHUNK_SIZE)

        super().__init__(paths, **file_based_datasource_kwargs | {
            "file_split_chunk_size": file_split_chunk_size,
        })

        self.read_options = arrow_csv_args.pop(
            "read_options", csv.ReadOptions(use_threads=False)
        )
        self.parse_options = arrow_csv_args.pop("parse_options", csv.ParseOptions())
        self.arrow_csv_args = arrow_csv_args

    def _read_stream(self, f: "pyarrow.NativeFile", path: str) -> Iterator[Block]:
        import pyarrow as pa
        from pyarrow import csv

        # Re-init invalid row handler: https://issues.apache.org/jira/browse/ARROW-17641
        if hasattr(self.parse_options, "invalid_row_handler"):
            self.parse_options.invalid_row_handler = (
                self.parse_options.invalid_row_handler
            )

        try:
            reader = csv.open_csv(
                f,
                read_options=self.read_options,
                parse_options=self.parse_options,
                **self.arrow_csv_args,
            )
            schema = None
            while True:
                try:
                    batch = reader.read_next_batch()
                    table = pa.Table.from_batches([batch], schema=schema)
                    if schema is None:
                        schema = table.schema
                    yield table
                except StopIteration:
                    return
        except pa.lib.ArrowInvalid as e:
            raise ValueError(
                f"Failed to read CSV file: {path}. "
                "Please check the CSV file has correct format, or filter out non-CSV "
                "file with 'partition_filter' field. See read_csv() documentation for "
                "more details."
            ) from e



    def _read_chunk_stream(self,
                           f: "pyarrow.NativeFile",
                           path: str,
                           offset: int,
                           size: int,
                           chunk_id: int) -> Iterator[Block]:
        import pyarrow as pa
        from pyarrow import csv

        # Re-init invalid row handler: https://issues.apache.org/jira/browse/ARROW-17641
        if hasattr(self.parse_options, "invalid_row_handler"):
            self.parse_options.invalid_row_handler = (
                self.parse_options.invalid_row_handler
            )

        try:
            schema = None
            read_options = copy.deepcopy(self.read_options)
            if chunk_id > 0:
                line_separator = infer_line_separator(f)
                suc, schema = self._infer_schema(f, path, line_separator)
                if suc:
                    read_options.column_names = schema.names
                else:
                    raise ValueError(
                        f"Failed to infer schema for CSV file: {path}. "
                        "Please check the CSV file has correct format, or filter out non-CSV "
                        "file with 'partition_filter' field. See read_csv() documentation for "
                        "more details."
                    )

            start_time = time.time()
            f = f.get_stream(offset, size)
            reader = csv.open_csv(
                f,
                read_options=read_options,
                parse_options=self.parse_options,
                **self.arrow_csv_args,
            )
            end_time = time.time()

            total_time = 0
            while True:
                try:
                    read_start_time = time.time()
                    batch = reader.read_next_batch()
                    read_end_time =  time.time()
                    total_time += (read_end_time - read_start_time)
                    table = pa.Table.from_batches([batch], schema=schema)
                    if schema is None:
                        schema = table.schema
                    yield table
                except StopIteration:
                    logger.debug(f"Reading chunk from {path}, "
                                 f"schema: {schema}, "
                                 f"offset: {offset}, "
                                 f"size: {size}, "
                                 f"chunk_id: {chunk_id}, "
                                 f"open_time: {end_time - start_time}, "
                                 f"read_time: {total_time}")
                    return
        except pa.lib.ArrowInvalid as e:
            raise ValueError(
                f"Failed to read CSV file: {path}. "
                "Please check the CSV file has correct format, or filter out non-CSV "
                "file with 'partition_filter' field. See read_csv() documentation for "
                "more details."
            ) from e

    def _infer_schema(self, f: "pyarrow.NativeFile", path: str, line_terminator: bytes = b'\n'):
        import pyarrow as pa
        from pyarrow import csv
        import io

        try:
            head_lines = find_head_n_line(f, line_terminator=line_terminator)
            if not head_lines:
                return False, None

            # Construct virtual CSV data containing header lines
            virtual_csv = io.BytesIO(
                line_terminator.join(head_lines) +  # 前3行内容
                line_terminator  # 补充最后一行的行分隔符
            )

            # Parse the header using current configurations
            reader = csv.read_csv(
                virtual_csv,
                read_options=self.read_options,
                parse_options=self.parse_options,
                **self.arrow_csv_args
            )
            return True, reader.schema
        except pa.lib.ArrowInvalid as e:
            logger.warning(f"Header parsing failed for {path}: {str(e)}")
            return False, None