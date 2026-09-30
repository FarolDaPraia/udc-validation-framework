#!/usr/bin/env python3
"""
Real-Time Log Streaming Demo
Shows live streaming of Serial2 logs with pre-filtering

Usage:
    python scripts/stream_logs.py <db_path> [--filter <filter_name>] [--batch]
"""

import sys
import argparse
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.streaming import LogStreamReader, PreFilter
from src.serial2 import FilterConfig


def print_entry(entry) -> None:
    """Pretty print a log entry."""
    timestamp = entry.pc_datetime.split('T')[1][:8] if 'T' in entry.pc_datetime else "??:??:??"
    msg_short = entry.message[:60] + "..." if len(entry.message) > 60 else entry.message

    level_colors = {
        'Error': '❌ ',
        'Fatal': '🔴 ',
        'Warn': '⚠️  ',
        'Info': 'ℹ️  ',
        'Trace': '📍 ',
    }

    symbol = level_colors.get(entry.level, '  ')
    print(f"{symbol} [{timestamp}] {entry.level:6} | {entry.module:20} | {msg_short}")


def main():
    parser = argparse.ArgumentParser(
        description='Real-time Serial2 log streaming with pre-filtering'
    )
    parser.add_argument('db_path', help='Path to Serial2 .s2db database')
    parser.add_argument('--filter', help='Filter name to apply')
    parser.add_argument('--batch', action='store_true', help='Use batch mode')
    parser.add_argument('--limit', type=int, help='Limit number of entries')
    parser.add_argument('--interval', type=float, default=0.1, help='Poll interval (seconds)')

    args = parser.parse_args()

    try:
        # Initialize reader
        print("[*] Initializing Real-Time Log Stream Reader...")
        reader = LogStreamReader(
            args.db_path,
            poll_interval=args.interval,
            batch_size=10
        )

        # Initialize pre-filter
        print("[*] Loading pre-filter...")
        pre_filter = PreFilter()

        # Load filter config
        config_path = Path(__file__).parent.parent / 'config' / 'filters.json'
        if config_path.exists():
            import json
            with open(config_path) as f:
                config = json.load(f)
            pre_filter.add_rules_from_config(config)

        # Override with specific filter if provided
        if args.filter:
            print(f"[*] Using filter: {args.filter}")
        else:
            print("[*] Using enabled filters from config")

        print("\n" + "=" * 100)
        print("REAL-TIME LOG STREAM (Press Ctrl+C to stop)")
        print("=" * 100 + "\n")

        count = 0
        start_time = time.time()

        if args.batch:
            # Batch mode
            for batch in reader.stream_batch():
                print(f"\n[Batch {count // 10 + 1}] {len(batch)} entries")

                for entry in batch:
                    if pre_filter.should_pass(entry):
                        print_entry(entry)
                        count += 1

                        if args.limit and count >= args.limit:
                            raise KeyboardInterrupt

        else:
            # Individual entry mode
            for entry in reader.stream():
                if pre_filter.should_pass(entry):
                    print_entry(entry)
                    count += 1

                    if args.limit and count >= args.limit:
                        raise KeyboardInterrupt

    except KeyboardInterrupt:
        elapsed = time.time() - start_time

        print("\n\n" + "=" * 100)
        print("STREAMING STOPPED")
        print("=" * 100)

        # Print statistics
        reader_stats = reader.get_stats()
        filter_stats = pre_filter.get_stats()

        print("\n=== READER STATISTICS ===")
        print(f"Total read: {reader_stats['total_read']:,}")
        print(f"Total events: {reader_stats['total_events']:,}")
        print(f"Errors: {reader_stats['errors']}")
        print(f"Elapsed: {elapsed:.1f}s")

        if elapsed > 0:
            print(f"Read throughput: {reader_stats['total_read'] / elapsed:.1f} reads/sec")
            print(f"Event throughput: {reader_stats['total_events'] / elapsed:.1f} events/sec")

        print("\n=== PRE-FILTER STATISTICS ===")
        print(f"Total checked: {filter_stats['total_checked']:,}")
        print(f"Passed: {filter_stats['total_passed']:,} ({filter_stats['pass_rate_percent']:.2f}%)")
        print(f"Dropped: {filter_stats['total_dropped']:,} ({filter_stats['drop_rate_percent']:.2f}%)")

        print("\n=== RESULTS ===")
        print(f"Streamed entries: {count:,}")
        print(f"Throughput: {count / elapsed:.1f} entries/sec" if elapsed > 0 else "")

        return 0

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        return 1

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
