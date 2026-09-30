#!/usr/bin/env python3
"""
Test Streaming Reader with sample database
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.streaming import LogStreamReader, PreFilter
import json
import threading
import time


def read_stream(reader, pre_filter, limit=50):
    """Read from stream and apply filter."""
    count = 0
    for entry in reader.stream():
        if pre_filter.should_pass(entry):
            timestamp = entry.pc_datetime.split('T')[1][:8] if 'T' in entry.pc_datetime else "??:??:??"
            msg_short = entry.message[:70] + "..." if len(entry.message) > 70 else entry.message
            print(f"[{timestamp}] {entry.level:6} | {entry.module:20} | {msg_short}")
            count += 1

            if count >= limit:
                break

    return count


def main():
    print("=" * 100)
    print("REAL-TIME STREAMING READER - TEST")
    print("=" * 100 + "\n")

    db_path = "2026-09-30-09_55_37/2026-09-30-09_55_37/2026-09-30-09_55_37.s2db"

    # Initialize reader
    print("[*] Initializing reader...")
    reader = LogStreamReader(db_path, poll_interval=0.01)

    # Initialize filter
    print("[*] Loading filter config...")
    pre_filter = PreFilter()
    with open("config/filters.json") as f:
        config = json.load(f)
    pre_filter.add_rules_from_config(config)

    print(f"[*] Active filters: {len(pre_filter.rules)}\n")
    print("[*] Streaming entries (first 30):\n")

    # Run in separate thread with timeout
    thread = threading.Thread(target=read_stream, args=(reader, pre_filter, 30))
    thread.daemon = True
    thread.start()

    # Wait max 5 seconds
    thread.join(timeout=5)

    print("\n" + "=" * 100)
    print("RESULTS")
    print("=" * 100)

    reader_stats = reader.get_stats()
    filter_stats = pre_filter.get_stats()

    print(f"\n[Reader]")
    print(f"  Total read: {reader_stats['total_read']:,}")
    print(f"  Total events: {reader_stats['total_events']:,}")
    print(f"  Current ID: {reader.last_id}")
    print(f"  Errors: {reader_stats['errors']}")

    print(f"\n[Pre-Filter]")
    print(f"  Checked: {filter_stats['total_checked']:,}")
    print(f"  Passed: {filter_stats['total_passed']:,} ({filter_stats['pass_rate_percent']:.2f}%)")
    print(f"  Dropped: {filter_stats['total_dropped']:,}")

    print(f"\n[Performance]")
    if reader_stats.get('elapsed_seconds', 0) > 0:
        elapsed = reader_stats['elapsed_seconds']
        print(f"  Elapsed: {elapsed:.2f}s")
        print(f"  Throughput: {reader_stats['total_read'] / elapsed:.0f} reads/sec")

    return 0


if __name__ == '__main__':
    sys.exit(main())
