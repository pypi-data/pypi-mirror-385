"""
Benchmark script to compare C++ vs Python metadata scanning performance.
"""

import time
import sys
import os
import argparse
from pathlib import Path

# Try to import the C++ extension
try:
    import metadata_scanner
    cpp_available = True
except ImportError:
    print("Warning: C++ extension not available. Run 'pip install .' first.")
    cpp_available = False

# Import Python implementation
from .python_scan import scan_python, CacheEngineKey, DiskCacheMetadata
from collections import OrderedDict


def format_time(seconds):
    """Format time in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"


def convert_cpp_to_python_objects(cpp_results):
    """
    Convert C++ results (list of dicts) to the same format as Python implementation:
    OrderedDict[CacheEngineKey, DiskCacheMetadata]
    
    This allows for a fair comparison by doing the same object creation work.
    """
    cache = OrderedDict()
    
    # Torch dtypes mapping (same as in python_scan.py)
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
    
    for entry in cpp_results:
        # Create CacheEngineKey from the parsed fields
        key = CacheEngineKey(
            fmt=entry["fmt"],
            model_name=entry["model_name"],
            world_size=entry["world_size"],
            worker_id=entry["worker_id"],
            chunk_hash=entry["chunk_hash"],
        )
        
        # Create DiskCacheMetadata
        # Note: C++ returns dtype_idx, we need to convert to dtype string
        dtype_str = torch_dtypes_names[entry["dtype_idx"]]
        
        metadata = DiskCacheMetadata(
            path=entry["path"],
            size=entry["size"],
            shape=entry["shape"],
            dtype=dtype_str,
            fmt=entry["fmt"],
        )
        
        cache[key] = metadata
    
    return cache


def benchmark_python(cache_path, num_runs=3):
    """Benchmark Python implementation."""
    print(f"\n{'='*60}")
    print("🐍 Python Implementation (with asyncio)")
    print(f"{'='*60}")
    
    times = []
    for run in range(num_runs):
        print(f"\nRun {run + 1}/{num_runs}...", end=" ", flush=True)
        start = time.perf_counter()
        cache, _ = scan_python(cache_path)
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        print(f"✓ {format_time(elapsed)} ({len(cache)} entries)")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n{'─'*60}")
    print(f"Results:")
    print(f"  Average: {format_time(avg_time)}")
    print(f"  Min:     {format_time(min_time)}")
    print(f"  Max:     {format_time(max_time)}")
    print(f"  Entries: {len(cache)}")
    
    return avg_time, len(cache)


def benchmark_cpp(cache_path, num_runs=3, show_timing=False, fair_comparison=True, max_threads=32):
    """Benchmark C++ implementation.
    
    Args:
        cache_path: Path to scan
        num_runs: Number of benchmark runs
        show_timing: Show detailed C++ internal timing
        fair_comparison: If True, also time conversion to Python objects (OrderedDict)
                        to match what Python implementation does
        max_threads: Maximum number of threads to use
    """
    if not cpp_available:
        print("\n❌ C++ extension not available")
        return None, 0
    
    thread_desc = "auto" if max_threads == 0 else f"{max_threads} threads"
    print(f"\n{'='*60}")
    print(f"⚡ C++ Implementation [Direct C API, {thread_desc}]")
    print(f"{'='*60}")
    
    scan_times = []
    conversion_times = []
    total_times = []
    
    for run in range(num_runs):
        print(f"\nRun {run + 1}/{num_runs}...", end=" ", flush=True)
        
        # Time C++ scanning
        scan_start = time.perf_counter()
        # Use verbose mode only on the last run if requested
        verbose = show_timing and (run == num_runs - 1)
        results = metadata_scanner.scan_metadata(cache_path, verbose=verbose, max_threads=max_threads)
        scan_end = time.perf_counter()
        scan_elapsed = scan_end - scan_start
        scan_times.append(scan_elapsed)
        
        # Time conversion to Python objects (for fair comparison)
        if fair_comparison:
            convert_start = time.perf_counter()
            cache = convert_cpp_to_python_objects(results)
            convert_end = time.perf_counter()
            convert_elapsed = convert_end - convert_start
            conversion_times.append(convert_elapsed)
            total_elapsed = scan_elapsed + convert_elapsed
            total_times.append(total_elapsed)
            entry_count = len(cache)
        else:
            total_elapsed = scan_elapsed
            total_times.append(total_elapsed)
            entry_count = len(results)
        
        if not verbose:
            print(f"✓ {format_time(total_elapsed)} ({entry_count} entries)")
    
    avg_scan = sum(scan_times) / len(scan_times) if scan_times else 0
    avg_conversion = sum(conversion_times) / len(conversion_times) if conversion_times else 0
    avg_total = sum(total_times) / len(total_times)
    min_total = min(total_times)
    max_total = max(total_times)
    
    print(f"\n{'─'*60}")
    print(f"Results:")
    if fair_comparison:
        print(f"  C++ Scan:      {format_time(avg_scan)}")
        print(f"  Obj Creation:  {format_time(avg_conversion)}")
        print(f"  {'─'*56}")
    print(f"  Average Total: {format_time(avg_total)}")
    print(f"  Min:           {format_time(min_total)}")
    print(f"  Max:           {format_time(max_total)}")
    print(f"  Entries:       {entry_count}")
    
    if fair_comparison and avg_total > 0:
        scan_pct = (avg_scan / avg_total) * 100
        conv_pct = (avg_conversion / avg_total) * 100
        print(f"\n  Breakdown: {scan_pct:.1f}% scan, {conv_pct:.1f}% object creation")
    
    return avg_total, entry_count


def main():
    """Main benchmark function."""
    parser = argparse.ArgumentParser(
        description='Benchmark C++ vs Python metadata scanning performance'
    )
    parser.add_argument(
        'cache_path',
        nargs='?',
        default='/mnt/weka/cache/',
        help='Path to cache directory (default: /mnt/weka/cache/)'
    )
    parser.add_argument(
        '--timing',
        action='store_true',
        help='Show detailed timing breakdown (C++ scan vs Python conversion)'
    )
    parser.add_argument(
        '--runs',
        type=int,
        default=3,
        help='Number of runs per implementation (default: 3)'
    )
    parser.add_argument(
        '--no-fair-comparison',
        action='store_true',
        help='Skip object creation for C++ (faster but unfair comparison with Python)'
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=32,
        help='Maximum number of threads for C++ scanner (default: 32, 0=hardware_concurrency, 1=single-threaded)'
    )
    
    args = parser.parse_args()
    cache_path = args.cache_path
    num_runs = args.runs
    fair_comparison = not args.no_fair_comparison
    max_threads = args.threads
    
    print(f"\n{'='*60}")
    print(f"🏁 Metadata Scanner Benchmark")
    print(f"{'='*60}")
    print(f"Cache path: {cache_path}")
    
    if not os.path.exists(cache_path):
        print(f"\n❌ Error: Cache path does not exist: {cache_path}")
        sys.exit(1)
    
    if not os.path.isdir(cache_path):
        print(f"\n❌ Error: Cache path is not a directory: {cache_path}")
        sys.exit(1)
    
    print(f"Runs per implementation: {num_runs}")
    print(f"C++ threads: {max_threads}")
    if args.timing:
        print("Timing breakdown: Enabled (shown on last C++ run)")
    if fair_comparison:
        print("Fair comparison: Enabled (C++ will create OrderedDict with Python objects)")
    else:
        print("Fair comparison: Disabled (C++ returns raw list of dicts - faster but unfair)")
    
    # Run Python benchmark
    py_time, py_entries = benchmark_python(cache_path, num_runs)
    
    # Run C++ benchmark
    cpp_time, cpp_entries = benchmark_cpp(
        cache_path, num_runs, show_timing=args.timing,
        fair_comparison=fair_comparison, max_threads=max_threads
    )
    
    # Compare results
    if cpp_available and cpp_time is not None:
        print(f"\n{'='*60}")
        print("📊 Comparison")
        print(f"{'='*60}")
        
        speedup = py_time / cpp_time
        
        print(f"\nSpeedup: {speedup:.2f}x faster with C++")
        print(f"Time saved: {format_time(py_time - cpp_time)} per scan")
        
        if py_entries != cpp_entries:
            print(f"\n⚠️  Warning: Entry counts differ!")
            print(f"   Python: {py_entries}")
            print(f"   C++:    {cpp_entries}")
        else:
            print(f"\n✓ Both implementations found {py_entries} entries")
        
        # Performance breakdown
        print(f"\n{'─'*60}")
        print("Performance Breakdown:")
        print(f"  Python: {format_time(py_time)}")
        print(f"  C++:    {format_time(cpp_time)}")
        print(f"  Speedup: {speedup:.2f}x")
        
        # Visual bar chart
        max_len = 50
        py_bar_len = max_len
        cpp_bar_len = int(max_len * (cpp_time / py_time))
        
        print(f"\n  Python: {'█' * py_bar_len}")
        print(f"  C++:    {'█' * cpp_bar_len}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()

