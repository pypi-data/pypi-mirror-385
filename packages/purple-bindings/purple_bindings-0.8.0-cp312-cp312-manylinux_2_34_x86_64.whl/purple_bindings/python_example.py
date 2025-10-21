"""
Example Python code showing how to use the metadata_scanner C++ extension.

This integrates with your existing Python code structure.
"""

import torch
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

# Import the C++ extension
import metadata_scanner

# Your existing torch dtypes
torch_dtypes = [
    torch.half,
    torch.float16,
    torch.bfloat16,
    torch.float,
    torch.float32,
    torch.float64,
    torch.double,
    torch.uint8,
    torch.float8_e4m3fn,
    torch.float8_e5m2,
]

@dataclass(order=True)
class CacheEngineKey:
    fmt: str
    model_name: str
    world_size: int
    worker_id: int
    chunk_hash: int
    request_configs: Optional[dict] = None

@dataclass
class DiskCacheMetadata:
    path: str
    size: int  # in bytes
    shape: Optional[torch.Size] = None
    dtype: Optional[torch.dtype] = None
    fmt: Optional[str] = None  # Assuming MemoryFormat is a string
    pin_count: int = 0


def load_cache_from_cpp(root_path: str) -> OrderedDict:
    """
    Load cache metadata using the C++ scanner.
    
    Args:
        root_path: Root directory containing the two-level cache structure
        
    Returns:
        OrderedDict mapping CacheEngineKey to DiskCacheMetadata
    """
    hot_cache: OrderedDict[CacheEngineKey, DiskCacheMetadata] = OrderedDict()
    
    # Call C++ scanner
    results = metadata_scanner.scan_metadata(root_path)
    
    # Convert results to Python objects
    for entry in results:
        # Create CacheEngineKey from parsed filename
        cache_key = CacheEngineKey(
            fmt=entry["fmt"],
            model_name=entry["model_name"],
            world_size=entry["world_size"],
            worker_id=entry["worker_id"],
            chunk_hash=entry["chunk_hash"],
            request_configs=None
        )
        
        # Create DiskCacheMetadata from file data
        shape_tuple = entry["shape"]
        dtype = torch_dtypes[entry["dtype_idx"]]
        
        cache_metadata = DiskCacheMetadata(
            path=entry["path"],
            size=entry["size"],
            shape=torch.Size(shape_tuple),
            dtype=dtype,
            fmt=entry["fmt"],
            pin_count=0
        )
        
        hot_cache[cache_key] = cache_metadata
    
    return hot_cache


# Example usage
if __name__ == "__main__":
    # Replace with your actual cache directory
    cache_dir = "/path/to/your/cache/directory"
    
    # Load cache using C++ extension
    hot_cache = load_cache_from_cpp(cache_dir)
    
    print(f"Loaded {len(hot_cache)} cache entries")
    
    # Example: iterate through cache
    for key, metadata in hot_cache.items():
        print(f"Key: {key.model_name}, Worker: {key.worker_id}")
        print(f"  Shape: {metadata.shape}, Dtype: {metadata.dtype}")
        print(f"  Path: {metadata.path}")

