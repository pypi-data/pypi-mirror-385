import io
import logging
import time
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Union, NamedTuple,
)

import numpy as np

import ray
from ray.data._internal.util import (
    RetryingContextManager,
    RetryingPyFileSystem,
    _check_pyarrow_version,
    _is_local_scheme,
    iterate_with_retry,
    make_async_gen, infer_line_separator,
)
from ray.data.block import Block, BlockAccessor
from ray.data.context import DataContext
from ray.data.datasource.datasource import Datasource, ReadTask
from ray.data.datasource.file_meta_provider import (
    BaseFileMetadataProvider,
    DefaultFileMetadataProvider,
)
from ray.data.datasource.partitioning import (
    Partitioning,
    PathPartitionFilter,
    PathPartitionParser,
)
from ray.data.datasource.path_util import (
    _has_file_extension,
    _resolve_paths_and_filesystem,
)
from ray.util.annotations import DeveloperAPI

if TYPE_CHECKING:
    import pandas as pd
    import pyarrow


logger = logging.getLogger(__name__)


# We should parallelize file size fetch operations beyond this threshold.
FILE_SIZE_FETCH_PARALLELIZATION_THRESHOLD = 16

# 16 file size fetches from S3 takes ~1.5 seconds with Arrow's S3FileSystem.
PATHS_PER_FILE_SIZE_FETCH_TASK = 16


@DeveloperAPI
@dataclass
class FileShuffleConfig:
    """Configuration for file shuffling.

    This configuration object controls how files are shuffled while reading file-based
    datasets.

    .. note::
        Even if you provided a seed, you might still observe a non-deterministic row
        order. This is because tasks are executed in parallel and their completion
        order might vary. If you need to preserve the order of rows, set
        `DataContext.get_current().execution_options.preserve_order`.

    Args:
        seed: An optional integer seed for the file shuffler. If provided, Ray Data
            shuffles files deterministically based on this seed.

    Example:
        >>> import ray
        >>> from ray.data import FileShuffleConfig
        >>> shuffle = FileShuffleConfig(seed=42)
        >>> ds = ray.data.read_images("s3://anonymous@ray-example-data/batoidea", shuffle=shuffle)
    """  # noqa: E501

    seed: Optional[int] = None

    def __post_init__(self):
        """Ensure that the seed is either None or an integer."""
        if self.seed is not None and not isinstance(self.seed, int):
            raise ValueError("Seed must be an integer or None.")

class FileChunkInfo(NamedTuple):
    file_path: str
    offset: int
    size: int
    chunk_index: int

@DeveloperAPI
class FileBasedDatasource(Datasource):
    """File-based datasource for reading files.

    Don't use this class directly. Instead, subclass it and implement `_read_stream()`.
    """

    # If `_WRITE_FILE_PER_ROW` is `True`, this datasource calls `_write_row` and writes
    # each row to a file. Otherwise, this datasource calls `_write_block` and writes
    # each block to a file.
    _WRITE_FILE_PER_ROW = False
    _FILE_EXTENSIONS: Optional[Union[str, List[str]]] = None
    # Number of threads for concurrent reading within each read task.
    # If zero or negative, reading will be performed in the main thread.
    _NUM_THREADS_PER_TASK = 0
    # File split chunk size for reading.
    _DEFAULT_FILE_SPLIT_CHUNK_SIZE = 0
    # Only split file into chunk when file size large than 64MB
    _MIN_FILE_SPLIT_CHUNK_SIZE = 64 * 1024 * 1024

    def __init__(
        self,
        paths: Union[str, List[str]],
        *,
        filesystem: Optional["pyarrow.fs.FileSystem"] = None,
        schema: Optional[Union[type, "pyarrow.lib.Schema"]] = None,
        open_stream_args: Optional[Dict[str, Any]] = None,
        meta_provider: BaseFileMetadataProvider = DefaultFileMetadataProvider(),
        partition_filter: PathPartitionFilter = None,
        partitioning: Partitioning = None,
        ignore_missing_paths: bool = False,
        shuffle: Optional[Union[Literal["files"], FileShuffleConfig]] = None,
        group_files_by_size: bool = False,
        file_split_chunk_size: int = 0,
        include_paths: bool = False,
        file_extensions: Optional[List[str]] = None,
    ):
        _check_pyarrow_version()

        self._supports_distributed_reads = not _is_local_scheme(paths)
        if not self._supports_distributed_reads and ray.util.client.ray.is_connected():
            raise ValueError(
                "Because you're using Ray Client, read tasks scheduled on the Ray "
                "cluster can't access your local files. To fix this issue, store "
                "files in cloud storage or a distributed filesystem like NFS."
            )

        self._schema = schema
        self._data_context = DataContext.get_current()
        self._open_stream_args = open_stream_args
        self._meta_provider = meta_provider
        self._partition_filter = partition_filter
        self._partitioning = partitioning
        self._ignore_missing_paths = ignore_missing_paths
        self._group_files_by_size = group_files_by_size
        self._chunk_size = file_split_chunk_size
        self._include_paths = include_paths
        self._unresolved_paths = paths
        paths, self._filesystem = _resolve_paths_and_filesystem(paths, filesystem)
        self._filesystem = RetryingPyFileSystem.wrap(
            self._filesystem, retryable_errors=self._data_context.retried_io_errors
        )
        paths, file_sizes = map(
            list,
            zip(
                *meta_provider.expand_paths(
                    paths,
                    self._filesystem,
                    partitioning,
                    ignore_missing_paths=ignore_missing_paths,
                )
            ),
        )

        if ignore_missing_paths and len(paths) == 0:
            raise ValueError(
                "None of the provided paths exist. "
                "The 'ignore_missing_paths' field is set to True."
            )

        if self._partition_filter is not None:
            # Use partition filter to skip files which are not needed.
            path_to_size = dict(zip(paths, file_sizes))
            paths = self._partition_filter(paths)
            file_sizes = [path_to_size[p] for p in paths]
            if len(paths) == 0:
                raise ValueError(
                    "No input files found to read. Please double check that "
                    "'partition_filter' field is set properly."
                )

        if file_extensions is not None:
            path_to_size = dict(zip(paths, file_sizes))
            paths = [p for p in paths if _has_file_extension(p, file_extensions)]
            file_sizes = [path_to_size[p] for p in paths]
            if len(paths) == 0:
                raise ValueError(
                    "No input files found to read with the following file extensions: "
                    f"{file_extensions}. Please double check that "
                    "'file_extensions' field is set properly."
                )

        _validate_shuffle_arg(shuffle)
        self._file_metadata_shuffler = None
        if shuffle == "files":
            self._file_metadata_shuffler = np.random.default_rng()
        elif isinstance(shuffle, FileShuffleConfig):
            # Create a NumPy random generator with a fixed seed if provided
            self._file_metadata_shuffler = np.random.default_rng(shuffle.seed)

        # Read tasks serialize `FileBasedDatasource` instances, and the list of paths
        # can be large. To avoid slow serialization speeds, we store a reference to
        # the paths rather than the paths themselves.
        self._paths_ref = ray.put(paths)
        self._file_sizes_ref = ray.put(file_sizes)

    def _paths(self) -> List[str]:
        return ray.get(self._paths_ref)

    def _file_sizes(self) -> List[float]:
        return ray.get(self._file_sizes_ref)

    def estimate_inmemory_data_size(self) -> Optional[int]:
        total_size = 0
        for sz in self._file_sizes():
            if sz is not None:
                total_size += sz
        return total_size

    def get_read_tasks(self, parallelism: int) -> List[ReadTask]:

        open_stream_args = self._open_stream_args
        partitioning = self._partitioning

        paths = self._paths()
        file_sizes = self._file_sizes()

        if self._file_metadata_shuffler is not None:
            files_metadata = list(zip(paths, file_sizes))
            shuffled_files_metadata = [
                files_metadata[i]
                for i in self._file_metadata_shuffler.permutation(len(files_metadata))
            ]
            paths, file_sizes = list(map(list, zip(*shuffled_files_metadata)))

        filesystem = _wrap_s3_serialization_workaround(self._filesystem)

        if open_stream_args is None:
            open_stream_args = {}

        def read_file_chunks(
            file_chunks: Iterable[FileChunkInfo],
        ) -> Iterable[Block]:
            nonlocal filesystem, open_stream_args, partitioning
            fs = _unwrap_s3_serialization_workaround(filesystem)

            for read_path, offset, size, chunk_id in file_chunks:
                partitions: Dict[str, str] = {}
                if partitioning is not None:
                    parse = PathPartitionParser(partitioning)
                    partitions = parse(read_path)
                compression = self.detect_compression(open_stream_args, read_path)
                with RetryingContextManager(
                    self._open_input_source(fs,
                                            read_path,
                                            mode="random" if self._chunk_size > 0 and compression is None
                                            else "stream",
                                            **open_stream_args),
                    context=self._data_context,
                ) as f:
                    for block in iterate_with_retry(
                        lambda: self._read_chunk_stream(f, read_path, offset, size, chunk_id)
                        if self._chunk_size > 0 and f.seekable() else self._read_stream(f, read_path),
                        description="read stream iteratively",
                        match=self._data_context.retried_io_errors,
                    ):
                        if partitions:
                            block = _add_partitions(block, partitions)
                        if self._include_paths:
                            block_accessor = BlockAccessor.for_block(block)
                            block = block_accessor.fill_column("path", read_path)
                        yield block

        def create_read_task_fn(chunks, num_threads):
            def read_task_fn():
                nonlocal num_threads, chunks

                # TODO: We should refactor the code so that we can get the results in
                # order even when using multiple threads.
                if self._data_context.execution_options.preserve_order:
                    num_threads = 0

                if num_threads > 0:
                    if len(chunks) < num_threads:
                        num_threads = len(chunks)

                    logger.debug(
                        f"Reading {len(read_paths)} files with {num_threads} threads."
                    )

                    yield from make_async_gen(
                        iter(chunks),
                        read_file_chunks,
                        num_workers=num_threads,
                        preserve_ordering=True,
                        buffer_size=max(len(chunks) // num_threads, 1),
                    )
                else:
                    logger.debug(f"Reading {len(read_paths)} files.")
                    yield from read_file_chunks(chunks)

            return read_task_fn

        # fix https://github.com/ray-project/ray/issues/24296

        def generate_chunks(file_sizes, read_paths):
            logger.debug(f"generate_chunks file_sizes: {file_sizes}, read_paths: {read_paths}")
            # split file into chunks with argument `file_split_chunk_size`
            nonlocal filesystem, open_stream_args, partitioning
            fs = _unwrap_s3_serialization_workaround(filesystem)
            files_chunks = []
            if self._chunk_size > 0:
                for path, file_size in zip(read_paths, file_sizes):
                    file_chunks = []

                    compression = self.detect_compression(open_stream_args, path)
                    if compression is not None:
                        files_chunks.extend([FileChunkInfo(path, 0, file_size, 0)])
                        continue

                    if (file_size is None
                            or file_size < self._chunk_size
                            or file_size < self._MIN_FILE_SPLIT_CHUNK_SIZE):
                        files_chunks.extend([FileChunkInfo(path, 0, file_size, 0)])
                        continue

                    with RetryingContextManager(
                            self._open_input_source(fs,
                                                    path,
                                                    mode="random",
                                                    **open_stream_args),
                            context=self._data_context,
                    ) as f:
                        if not f.seekable():
                            files_chunks.extend([FileChunkInfo(path, 0, file_size, 0)])
                            continue

                        start_time = time.time()
                        line_separator = infer_line_separator(f)
                        logger.debug(f"line_separator: {line_separator}, time: {time.time() - start_time}")
                        if line_separator is None:
                            files_chunks.extend([FileChunkInfo(path, 0, file_size, 0)])
                            continue

                        current_offset = 0
                        chunk_id = 0
                        while current_offset < file_size:
                            end_pos = min(current_offset + self._chunk_size, file_size)

                            if end_pos < file_size:
                                # Only read 64 units of data after the boundary
                                # (without exceeding the file boundary)
                                buffer_size = min(file_size, end_pos + 64*1024) - end_pos

                                if buffer_size > 0:  # Ensure there is data to read
                                    f.seek(end_pos)
                                    buffer = f.read(buffer_size)

                                    # Search for the newline character from the start position of the buffer
                                    next_newline = buffer.find(line_separator, 0)
                                    if next_newline != -1:
                                        end_pos += next_newline + len(line_separator)
                                    else:
                                        # TODO
                                        file_chunks = [FileChunkInfo(path, 0, file_size, chunk_id)]
                                        break


                            chunk_size = end_pos - current_offset
                            file_chunks.append(FileChunkInfo(path, current_offset, chunk_size, chunk_id))
                            chunk_id += 1
                            current_offset = end_pos

                    # Retain the original logic for merging small blocks
                    if len(file_chunks) >= 2:
                        last_chunk = file_chunks[-1]
                        prev_chunk = file_chunks[-2]
                        if last_chunk.size <= self._chunk_size * 0.3 and prev_chunk.file_path == path:
                            merged = FileChunkInfo(path, prev_chunk.offset, prev_chunk.size + last_chunk.size, prev_chunk.chunk_index)
                            file_chunks[-2:] = [merged]
                    files_chunks.extend(file_chunks)
            else:
                for path, file_size in zip(read_paths, file_sizes):
                    files_chunks.append(FileChunkInfo(path, 0, file_size, 0))
            return files_chunks

        start_time = time.time()
        files_chunks = generate_chunks(file_sizes, paths)
        logger.debug(f"generate_chunks time: {time.time() - start_time}")
        parallelism = min(parallelism, len(files_chunks))
        if self._group_files_by_size:
            split_files_chunks_array = self._group_files_by_size_greedy(files_chunks, parallelism)
        else:
            split_files_chunks_array = []
            group_size = max(1, len(files_chunks) // parallelism)
            for i in range(parallelism):
                start = i * group_size
                end = start + group_size if i < parallelism - 1 else len(files_chunks)
                split_files_chunks = files_chunks[start:end]
                split_files_chunks_array.append(split_files_chunks)

        read_tasks = []
        for split_files_chunks in split_files_chunks_array:
            if len(split_files_chunks) <= 0:
                continue

            read_paths = [chunk[0] for chunk in split_files_chunks]
            file_sizes = [chunk[2] for chunk in split_files_chunks]

            meta = self._meta_provider(
                read_paths,
                self._schema,
                rows_per_file=self._rows_per_file(),
                file_sizes=file_sizes,
            )

            read_task_fn = create_read_task_fn(split_files_chunks, self._NUM_THREADS_PER_TASK)

            read_task = ReadTask(read_task_fn, meta)

            read_tasks.append(read_task)

        return read_tasks

    def _group_files_by_size_greedy(self, file_chunks: List[FileChunkInfo], parallelism: int) -> List[List[FileChunkInfo]]:
        """Greedy algorithm: After sorting chunks in descending order of size, assign chunks to the group with the smallest current total size to balance group sizes.

        Args:
            file_chunks: List of chunk tuples generated by generate_chunks, where each tuple has the format (path, offset, size, chunk_id)
            parallelism: Target number of groups

        Returns:
            List of grouped chunk tuples, where each sublist is the chunk collection of a group
        """
        # Sorted in descending order of chunk size (the 3rd element of the tuple is the chunk size)
        sorted_chunks = sorted(file_chunks, key=lambda chunk: -chunk.size)

        # Initialize group containers (each element is a list of chunks)
        groups = [[] for _ in range(parallelism)]
        group_totals = [0.0] * parallelism  # Track the total chunk size of each group

        # Greedy assignment: Place each chunk into the group with the smallest current total size
        for chunk in sorted_chunks:
            chunk_size = chunk.size
            min_group_idx = np.argmin(group_totals)
            groups[min_group_idx].append(chunk)
            group_totals[min_group_idx] += chunk_size

        return groups

    def _open_input_source(
        self,
        filesystem: "RetryingPyFileSystem",
        path: str,
        mode: str = "stream",
        **open_args,
    ) -> "pyarrow.NativeFile":
        """Opens a source path for reading and returns the associated Arrow NativeFile.

        The default implementation opens the source path as a sequential input stream,
        using self._data_context.streaming_read_buffer_size as the buffer size if none
        is given by the caller.

        Implementations that do not support streaming reads (e.g. that require random
        access) should override this method.
        """
        import pyarrow as pa

        compression = self.detect_compression(open_args, path)

        if mode == "random":
            file = filesystem.open_input_file(path)
        else:
            buffer_size = open_args.pop("buffer_size", None)
            if buffer_size is None:
                buffer_size = self._data_context.streaming_read_buffer_size

            if compression == "snappy":
                # Arrow doesn't support streaming Snappy decompression since the canonical
                # C++ Snappy library doesn't natively support streaming decompression. We
                # works around this by manually decompressing the file with python-snappy.
                open_args["compression"] = None
            else:
                open_args["compression"] = compression

            file = filesystem.open_input_stream(path, buffer_size=buffer_size, **open_args)

            if compression == "snappy":
                from pyarrow.fs import HadoopFileSystem
                import snappy

                stream = io.BytesIO()
                if isinstance(filesystem.unwrap(), HadoopFileSystem):
                    snappy.hadoop_snappy.stream_decompress(src=file, dst=stream)
                else:
                    snappy.stream_decompress(src=file, dst=stream)
                stream.seek(0)

                file = pa.PythonFile(stream, mode="r")

        return file

    def detect_compression(self, open_args, path):
        compression = open_args.get("compression", None)
        if compression is None:
            try:
                # If no compression manually given, try to detect
                # compression codec from path.
                import pyarrow as pa
                compression = pa.Codec.detect(path).name
            except (ValueError, TypeError):
                # Arrow's compression inference on the file path
                # doesn't work for Snappy, so we double-check ourselves.
                import pathlib

                suffix = pathlib.Path(path).suffix
                if suffix and suffix[1:] == "snappy":
                    compression = "snappy"
                else:
                    compression = None
        return compression

    def _rows_per_file(self):
        """Returns the number of rows per file, or None if unknown."""
        return None

    def _infer_schema(self, f: "pyarrow.NativeFile", path: str, line_terminator: bytes = b'\n'):
        return True, None

    def _read_stream(self, f: "pyarrow.NativeFile", path: str) -> Iterator[Block]:
        """Streaming read a single file.

        This method should be implemented by subclasses.
        """
        raise NotImplementedError(
            "Subclasses of FileBasedDatasource must implement _read_stream()."
        )

    def _read_chunk_stream(self,
                           f: "pyarrow.NativeFile",
                           path: str,
                           offset: int,
                           size: int,
                           chunk_id: int) -> Iterator[Block]:
        """Streaming read a file chunk.

        This method should be implemented by subclasses.
        """
        raise NotImplementedError(
            "Subclasses of FileBasedDatasource must implement _read_chunk_stream()."
        )

    @property
    def supports_distributed_reads(self) -> bool:
        return self._supports_distributed_reads


def _add_partitions(
    data: Union["pyarrow.Table", "pd.DataFrame"], partitions: Dict[str, Any]
) -> Union["pyarrow.Table", "pd.DataFrame"]:
    import pandas as pd
    import pyarrow as pa

    assert isinstance(data, (pa.Table, pd.DataFrame))
    if isinstance(data, pa.Table):
        return _add_partitions_to_table(data, partitions)
    if isinstance(data, pd.DataFrame):
        return _add_partitions_to_dataframe(data, partitions)


def _add_partitions_to_table(
    table: "pyarrow.Table", partitions: Dict[str, Any]
) -> "pyarrow.Table":
    import pyarrow as pa
    import pyarrow.compute as pc

    column_names = set(table.column_names)
    for field, value in partitions.items():
        column = pa.array([value] * len(table))
        if field in column_names:
            # TODO: Handle cast error.
            column_type = table.schema.field(field).type
            column = column.cast(column_type)

            values_are_equal = pc.all(pc.equal(column, table[field]))
            values_are_equal = values_are_equal.as_py()

            if not values_are_equal:
                raise ValueError(
                    f"Partition column {field} exists in table data, but partition "
                    f"value '{value}' is different from in-data values: "
                    f"{table[field].unique().to_pylist()}."
                )

            i = table.schema.get_field_index(field)
            table = table.set_column(i, field, column)
        else:
            table = table.append_column(field, column)

    return table


def _add_partitions_to_dataframe(
    df: "pd.DataFrame", partitions: Dict[str, Any]
) -> "pd.DataFrame":
    import pandas as pd

    for field, value in partitions.items():
        column = pd.Series(data=[value] * len(df), name=field)

        if field in df:
            column = column.astype(df[field].dtype)
            mask = df[field].notna()
            if not df[field][mask].equals(column[mask]):
                raise ValueError(
                    f"Partition column {field} exists in table data, but partition "
                    f"value '{value}' is different from in-data values: "
                    f"{list(df[field].unique())}."
                )

        df[field] = column

    return df


def _wrap_s3_serialization_workaround(filesystem: "pyarrow.fs.FileSystem"):
    # This is needed because pa.fs.S3FileSystem assumes pa.fs is already
    # imported before deserialization. See #17085.
    import pyarrow as pa
    import pyarrow.fs

    base_fs = filesystem
    if isinstance(filesystem, RetryingPyFileSystem):
        base_fs = filesystem.unwrap()

    if isinstance(base_fs, pa.fs.S3FileSystem):
        return _S3FileSystemWrapper(filesystem)

    return filesystem


def _unwrap_s3_serialization_workaround(
    filesystem: Union["pyarrow.fs.FileSystem", "_S3FileSystemWrapper"],
):
    if isinstance(filesystem, _S3FileSystemWrapper):
        filesystem = filesystem.unwrap()
    return filesystem


class _S3FileSystemWrapper:
    """pyarrow.fs.S3FileSystem wrapper that can be deserialized safely.

    Importing pyarrow.fs during reconstruction triggers the pyarrow
    S3 subsystem initialization.

    NOTE: This is only needed for pyarrow<14.0.0 and should be removed
        once the minimum supported pyarrow version exceeds that.
        See https://github.com/apache/arrow/pull/38375 for context.
    """

    def __init__(self, fs: "pyarrow.fs.FileSystem"):
        self._fs = fs

    def unwrap(self):
        return self._fs

    @classmethod
    def _reconstruct(cls, fs_reconstruct, fs_args):
        # Implicitly trigger S3 subsystem initialization by importing
        # pyarrow.fs.
        import pyarrow.fs  # noqa: F401

        return cls(fs_reconstruct(*fs_args))

    def __reduce__(self):
        return _S3FileSystemWrapper._reconstruct, self._fs.__reduce__()


def _resolve_kwargs(
    kwargs_fn: Callable[[], Dict[str, Any]], **kwargs
) -> Dict[str, Any]:
    if kwargs_fn:
        kwarg_overrides = kwargs_fn()
        kwargs.update(kwarg_overrides)
    return kwargs


def _validate_shuffle_arg(
    shuffle: Union[Literal["files"], FileShuffleConfig, None],
) -> None:
    if not (
        shuffle is None or shuffle == "files" or isinstance(shuffle, FileShuffleConfig)
    ):
        raise ValueError(
            f"Invalid value for 'shuffle': {shuffle}. "
            "Valid values are None, 'files', `FileShuffleConfig`."
        )
