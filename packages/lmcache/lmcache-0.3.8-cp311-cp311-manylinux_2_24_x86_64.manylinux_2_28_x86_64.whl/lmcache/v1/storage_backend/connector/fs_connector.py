# SPDX-License-Identifier: Apache-2.0
# Standard
from pathlib import Path
from typing import List, Optional, Tuple, no_type_check
import asyncio
import os

# Third Party
import aiofiles
import aiofiles.os

# First Party
from lmcache.logging import init_logger
from lmcache.utils import CacheEngineKey
from lmcache.v1.config import LMCacheEngineConfig
from lmcache.v1.memory_management import MemoryObj
from lmcache.v1.protocol import RemoteMetadata
from lmcache.v1.storage_backend.connector.base_connector import RemoteConnector
from lmcache.v1.storage_backend.local_cpu_backend import LocalCPUBackend

logger = init_logger(__name__)

METADATA_BYTES_LEN = 28


class FSConnector(RemoteConnector):
    """File system based connector that stores data in local files.

    Data is stored in the following format:
    - Each key is stored as a separate file
    - File content: metadata (METADATA_BYTES_LEN bytes) + serialized data
    """

    def __init__(
        self,
        base_paths_str: str,
        loop: asyncio.AbstractEventLoop,
        local_cpu_backend: LocalCPUBackend,
        config: Optional[LMCacheEngineConfig],
    ):
        """
        Args:
            base_paths_str: Comma separated storage paths
            loop: Asyncio event loop
            local_cpu_backend: Memory allocator interface
            config: Lmcache engine config
        """
        # Parse comma separated paths
        self.base_paths = (
            [Path(p.strip()) for p in base_paths_str.split(",")]
            if "," in base_paths_str
            else [Path(base_paths_str)]
        )

        self.loop = loop
        self.local_cpu_backend = local_cpu_backend

        relative_tmp_dir = (
            None
            if config is None
            else config.get_extra_config_value("fs_connector_relative_tmp_dir", None)
        )
        self.relative_tmp_dir = None
        if relative_tmp_dir is not None:
            self.relative_tmp_dir = Path(relative_tmp_dir)
            assert not self.relative_tmp_dir.is_absolute()

        self.read_ahead_size = (
            None
            if config is None
            else config.get_extra_config_value("fs_connector_read_ahead_size", None)
        )

        logger.info(
            f"Initialized FSConnector with base paths {self.base_paths}, "
            f"relative tmp dir: {self.relative_tmp_dir}, "
            f"read ahead size: {self.read_ahead_size}"
        )
        # Create directories for all paths
        for path in self.base_paths:
            path.mkdir(parents=True, exist_ok=True)
            if self.relative_tmp_dir is not None:
                (path / self.relative_tmp_dir).mkdir(parents=False, exist_ok=True)

    def _get_base_path(self, key: CacheEngineKey) -> Path:
        """Get file base path for the given key"""
        if len(self.base_paths) == 1:
            base_path = self.base_paths[0]
        else:
            # Calculate hash value and modulo to select path
            hash_val = abs(key.chunk_hash)
            idx = hash_val % len(self.base_paths)
            base_path = self.base_paths[idx]

        return base_path

    def _get_file_name(self, key: CacheEngineKey) -> str:
        return key.to_string().replace("/", "-") + ".data"

    def _get_file_path(self, key: CacheEngineKey) -> Path:
        """Get file path for the given key"""
        base_path = self._get_base_path(key)
        file_name = self._get_file_name(key)
        return base_path / file_name

    def _get_file_and_tmp_path(self, key: CacheEngineKey) -> Tuple[Path, Path]:
        """Get file and tmp path for the given key"""
        base_path = self._get_base_path(key)
        file_name = self._get_file_name(key)
        file_path = base_path / file_name
        if self.relative_tmp_dir is not None:
            tmp_path = base_path / self.relative_tmp_dir / file_name
        else:
            tmp_path = file_path.with_suffix(".tmp")
        return file_path, tmp_path

    async def exists(self, key: CacheEngineKey) -> bool:
        """Check if key exists in file system"""
        file_path = self._get_file_path(key)
        return await aiofiles.os.path.exists(file_path)

    def exists_sync(self, key: CacheEngineKey) -> bool:
        """Check if key exists in file system synchronized"""
        file_path = self._get_file_path(key)
        return os.path.exists(file_path)

    async def get(self, key: CacheEngineKey) -> Optional[MemoryObj]:
        """Get data from file system"""
        file_path = self._get_file_path(key)

        memory_obj = None
        try:
            async with aiofiles.open(file_path, "rb") as f:
                if self.save_chunk_meta:
                    # Read metadata buffer first to get shape, dtype, fmt
                    # to be able to allocate memory object for the data and read into it
                    md_buffer = bytearray(METADATA_BYTES_LEN)
                    num_read = await f.readinto(md_buffer)
                    if num_read != len(md_buffer):
                        raise RuntimeError(
                            f"Partial read meta {len(md_buffer)} got {num_read}"
                        )

                    # Deserialize metadata and allocate memory
                    metadata = RemoteMetadata.deserialize(md_buffer)
                    memory_obj = self.local_cpu_backend.allocate(
                        metadata.shape, metadata.dtype, metadata.fmt
                    )
                else:
                    memory_obj = self.local_cpu_backend.allocate(
                        self.meta_shape, self.meta_dtype, self.meta_fmt
                    )
                if memory_obj is None:
                    logger.debug("Memory allocation failed during async disk load.")
                    return None

                # Read the actual data into allocated memory
                buffer = memory_obj.byte_array
                if self.save_chunk_meta:
                    # if save chunk meta, read meta will trigger
                    # read ahead if fs supported
                    num_read = await f.readinto(buffer)
                    if num_read != len(buffer):
                        raise RuntimeError(
                            f"Partial read data {len(buffer)} got {num_read}"
                        )
                else:
                    if self.read_ahead_size is None:
                        num_read = await f.readinto(buffer)
                    else:
                        if not isinstance(buffer, memoryview):
                            buffer = memoryview(buffer)

                        # trigger read head if fs supported
                        num_read_ahead = await f.readinto(
                            buffer[: self.read_ahead_size]
                        )
                        assert num_read_ahead <= self.read_ahead_size

                        # if num_read_ahead == self.read_ahead_size,
                        # means there may still be some remaining content
                        if num_read_ahead == self.read_ahead_size:
                            num_read_tail = await f.readinto(
                                buffer[self.read_ahead_size :]
                            )
                            assert num_read_tail is not None
                            num_read = num_read_ahead + num_read_tail
                        else:
                            num_read = num_read_ahead
                    # reshape and check
                    assert num_read is not None
                    memory_obj = self.reshape_partial_chunk(memory_obj, num_read)

            return memory_obj

        except Exception as e:
            if not isinstance(e, FileNotFoundError):
                logger.error(f"Failed to read from file {file_path}: {str(e)}")
            if memory_obj is not None:
                memory_obj.ref_count_down()
            return None

    async def put(self, key: CacheEngineKey, memory_obj: MemoryObj):
        """Store data to file system"""
        final_path, temp_path = self._get_file_and_tmp_path(key)

        try:
            # Prepare metadata
            buffer = memory_obj.byte_array
            metadata = (
                RemoteMetadata(
                    len(buffer),
                    memory_obj.get_shape(),
                    memory_obj.get_dtype(),
                    memory_obj.get_memory_format(),
                )
                if self.save_chunk_meta
                else None
            )

            # Write to file (metadata + data)
            async with aiofiles.open(temp_path, "wb") as f:
                if metadata is not None:
                    await f.write(metadata.serialize())
                await f.write(buffer)

            # Atomically rename temp file to final destination
            await aiofiles.os.replace(temp_path, final_path)

        except Exception as e:
            logger.error(f"Failed to write file {final_path}: {str(e)}")
            if await aiofiles.os.path.exists(temp_path):
                await aiofiles.os.unlink(temp_path)  # Remove corrupted file
            raise

    def remove_sync(self, key: CacheEngineKey) -> bool:
        """
        Remove the file associated with the given key.

        Args:
            key: The key to remove.

        Returns:
            bool: True if the file was successfully removed, False otherwise.
        """
        file_path = self._get_file_path(key)
        try:
            os.remove(file_path)
            return True
        except OSError as e:
            logger.error(f"Failed to remove file {file_path}: {e}")
            return False

    @no_type_check
    async def list(self) -> List[str]:
        """List all keys in file system"""
        keys = []
        for base_path in self.base_paths:
            keys.extend([f.stem for f in base_path.glob("*.data")])
        return keys

    def support_batched_async_contains(self) -> bool:
        return True

    async def batched_async_contains(
        self,
        lookup_id: str,
        keys: List[CacheEngineKey],
        pin: bool = False,
    ) -> int:
        """Check how many keys exist in file system in batch

        Args:
            lookup_id: Identifier for this lookup operation
            keys: List of keys to check
            pin: Whether to pin the keys (not used in FS connector)

        Returns:
            Number of consecutive keys that exist, starting from the first key
        """
        tasks = [self.exists(key) for key in keys]
        results = await asyncio.gather(*tasks)
        try:
            return results.index(False)
        except ValueError:
            return len(results)

    def support_batched_get_non_blocking(self) -> bool:
        return True

    async def batched_get_non_blocking(
        self,
        lookup_id: str,
        keys: List[CacheEngineKey],
    ) -> List[MemoryObj]:
        """Batched get the memory_objs of the corresponding keys (non-blocking)

        Args:
            lookup_id: Identifier for this lookup operation
            keys: List of keys to get

        Returns:
            List of memory objects that exist (excludes None values)
        """
        # Use asyncio.gather to fetch all keys concurrently
        results = await asyncio.gather(
            *(self.get(key) for key in keys), return_exceptions=True
        )

        # Filter out None values and exceptions, return only valid memory objects
        memory_objs = []
        for result in results:
            if isinstance(result, MemoryObj):
                memory_objs.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Exception during batched get: {result}")

        return memory_objs

    async def close(self):
        """Clean up resources"""
        logger.info("Closed the file system connector")
