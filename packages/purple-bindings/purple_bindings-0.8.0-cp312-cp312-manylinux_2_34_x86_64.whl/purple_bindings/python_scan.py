"""
Python implementation of metadata scanning (from original repo).
This is used for benchmarking against the C++ implementation.
"""

import os
import struct
import asyncio
import time
from dataclasses import dataclass
from typing import Optional
from collections import OrderedDict

# Constants (adjust these to match your actual constants)
_DATA_FILE_SUFFIX = ".weka1"
_METADATA_FILE_SUFFIX = ".metadata"
_METADATA_MAX_SIZE = 4096
_METADATA_VERSION = 1

# Torch dtypes mapping
torch_dtypes_names = [
    "torch.half",
    "torch.float16",
    "torch.bfloat16",
    "torch.float",
    "torch.float32",
    "torch.float64",
    "torch.double",
    "torch.uint8",
    "torch.float8_e4m3fn",
    "torch.float8_e5m2",
]


class UnsupportedMetadataVersion(Exception):
    pass


@dataclass(order=True, frozen=True)
class CacheEngineKey:
    fmt: str
    model_name: str
    world_size: int
    worker_id: int
    chunk_hash: int
    request_configs: Optional[dict] = None

    @classmethod
    def from_string(cls, key_str):
        """Parse key from string format."""
        parts = key_str.split("@")
        if len(parts) != 5:
            raise ValueError(f"Invalid key string format: {key_str}")
        return cls(
            fmt=parts[0],
            model_name=parts[1],
            world_size=int(parts[2]),
            worker_id=int(parts[3]),
            chunk_hash=int(parts[4], 16),  # Hex
        )


@dataclass
class DiskCacheMetadata:
    path: str
    size: int  # in bytes
    shape: Optional[tuple] = None
    dtype: Optional[str] = None
    fmt: Optional[str] = None
    pin_count: int = 0


def unpack_metadata(buffer):
    """Unpack binary metadata."""
    version, dt_idx, size, ndim = struct.unpack_from("<QQQQ", buffer)
    shape_offset = struct.calcsize("<QQQQ")
    if version != _METADATA_VERSION:
        raise UnsupportedMetadataVersion(f"Unsupported metadata version: {version}")
    shape = struct.unpack_from("<" + ndim * "Q", buffer, offset=shape_offset)
    return tuple(shape), torch_dtypes_names[dt_idx], size


class MetadataScanner:
    """Python implementation of metadata scanner."""

    def __init__(self, weka_path, layerwise=False):
        self.weka_path = weka_path
        self.layerwise = layerwise
        self.hot_cache: OrderedDict[CacheEngineKey, DiskCacheMetadata] = OrderedDict()
        self.metadata_dirs = set()

    async def _scan_metadata(self):
        """Async scan of metadata (original implementation)."""
        tasks = []
        start = time.perf_counter()
        with os.scandir(self.weka_path) as it:
            for entry in it:
                if not entry.is_dir():
                    continue
                l1_dir = os.path.basename(entry.name)
                if len(l1_dir) != 2:
                    continue
                tasks.append(
                    asyncio.to_thread(
                        self._scan_metadata_subdir,
                        os.path.join(self.weka_path, l1_dir),
                        l1_dir,
                    )
                )
        await asyncio.gather(*tasks)
        end = time.perf_counter()
        return end - start

    def _scan_metadata_subdir(self, path, l1_dir):
        """Scan a subdirectory for metadata files."""
        target_suffix = _DATA_FILE_SUFFIX + _METADATA_FILE_SUFFIX
        with os.scandir(path) as it:
            for entry in it:
                if not entry.is_dir():
                    continue
                l2_dir = os.path.basename(entry.name)
                if len(l2_dir) != 2:
                    continue
                with os.scandir(os.path.join(path, l2_dir)) as it2:
                    for fentry in it2:
                        if not fentry.is_file():
                            continue
                        if not fentry.name.endswith(target_suffix):
                            continue
                        filename = os.path.basename(fentry.name)
                        key_str = filename[: -len(target_suffix)].replace("_", "/")
                        try:
                            key = CacheEngineKey.from_string(key_str)
                        except ValueError as e:
                            # Silently skip invalid files for benchmarking
                            continue
                        try:
                            self._read_metadata(key, fentry.path, l1_dir + l2_dir)
                        except UnsupportedMetadataVersion:
                            # Silently skip for benchmarking
                            pass

    def _read_metadata(self, key, filename, subdir_key):
        """Read metadata from a file."""
        with open(filename, "rb") as f:
            buf = f.read(_METADATA_MAX_SIZE)
        shape, dtype, size = unpack_metadata(buf)
        
        fmt = "KV_2LTD"  # Default format
        
        metadata = DiskCacheMetadata(
            filename.removesuffix(_METADATA_FILE_SUFFIX), size, shape, dtype, fmt
        )
        self.metadata_dirs.add(subdir_key)
        self.hot_cache[key] = metadata
        return metadata

    def scan_sync(self):
        """Synchronous wrapper for async scan."""
        return asyncio.run(self._scan_metadata())


def scan_python(root_path):
    """Main entry point for Python scanning."""
    scanner = MetadataScanner(root_path)
    elapsed = scanner.scan_sync()
    return scanner.hot_cache, elapsed

