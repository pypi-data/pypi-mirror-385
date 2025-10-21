"""
Test script for the metadata scanner.

This creates a small test directory structure to verify the C++ extension works correctly.
"""

import os
import struct
import tempfile
import shutil
from pathlib import Path

def create_test_structure():
    """Create a test directory structure with sample metadata files."""
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="metadata_test_")
    print(f"Creating test structure in: {test_dir}")
    
    # Create two-level directory structure (must be exactly 2 characters)
    level1_dirs = ["ab", "cd"]
    level2_dirs = ["12", "34"]
    
    for level1 in level1_dirs:
        for level2 in level2_dirs:
            path = Path(test_dir) / level1 / level2
            path.mkdir(parents=True, exist_ok=True)
            
            # Create test metadata file
            filename = f"vllm@meta-llama_Llama-3.1-70B-Instruct@4@0@137ef891ec63db12.weka1.metadata"
            filepath = path / filename
            
            # Pack test metadata
            # Format: <QQQQ + shape (2 dimensions)
            version = 1
            dtype_idx = 0  # torch.half
            size = 1024
            ndim = 2
            shape = [128, 256]
            
            metadata_desc = "<QQQQ" + ndim * "Q"
            data = struct.pack(metadata_desc, version, dtype_idx, size, ndim, *shape)
            
            with open(filepath, 'wb') as f:
                f.write(data)
            
            print(f"  Created: {filepath}")
    
    return test_dir


def test_scanner():
    """Test the C++ scanner."""
    
    # Try to import the extension
    try:
        import metadata_scanner
        print("✓ Successfully imported metadata_scanner")
    except ImportError as e:
        print(f"✗ Failed to import metadata_scanner: {e}")
        print("\nPlease build the extension first:")
        print("  cd /home/serapheim/src/purple_bindings")
        print("  pip install .")
        return False
    
    # Create test structure
    test_dir = create_test_structure()
    
    try:
        # Scan directory
        print(f"\nScanning directory: {test_dir}")
        results = metadata_scanner.scan_metadata(test_dir)
        
        print(f"\n✓ Found {len(results)} metadata files")
        
        # Verify results
        if len(results) == 0:
            print("✗ No files found!")
            return False
        
        # Check first result
        entry = results[0]
        print("\nFirst entry:")
        print(f"  fmt: {entry['fmt']}")
        print(f"  model_name: {entry['model_name']}")
        print(f"  world_size: {entry['world_size']}")
        print(f"  worker_id: {entry['worker_id']}")
        print(f"  chunk_hash: {entry['chunk_hash']:x}")
        print(f"  size: {entry['size']}")
        print(f"  dtype_idx: {entry['dtype_idx']}")
        print(f"  shape: {entry['shape']}")
        print(f"  path: {entry['path']}")
        
        # Verify expected values (underscores converted to slashes)
        assert entry['fmt'] == 'vllm'
        assert entry['model_name'] == 'meta-llama/Llama-3.1-70B-Instruct'
        assert entry['world_size'] == 4
        assert entry['worker_id'] == 0
        assert entry['chunk_hash'] == 0x137ef891ec63db12
        assert entry['size'] == 1024
        assert entry['dtype_idx'] == 0
        assert entry['shape'] == (128, 256)
        
        print("\n✓ All tests passed!")
        return True
        
    finally:
        # Cleanup
        print(f"\nCleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    success = test_scanner()
    exit(0 if success else 1)

