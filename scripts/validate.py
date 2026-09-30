#!/usr/bin/env python3
"""
Main Validation Script
Orchestrates Serial2 log parsing and validation

Usage:
    python scripts/validate.py <db_path> [--filter <filter_name>] [--output <output.json>]
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.serial2 import Serial2LogParser, FilterConfig
from src.validators import Serial2Validator


def main():
    parser = argparse.ArgumentParser(
        description='UDC Validation Framework - Serial2 Log Validator'
    )
    parser.add_argument('db_path', help='Path to Serial2 .s2db database')
    parser.add_argument('--filter', help='Filter name from config')
    parser.add_argument('--output', help='Output file (JSON)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--list-filters', action='store_true', help='List available filters')

    args = parser.parse_args()

    try:
        # Load filter config
        config_path = Path(__file__).parent.parent / 'config' / 'filters.json'
        filter_config = FilterConfig(str(config_path))

        if args.list_filters:
            print("\n=== AVAILABLE FILTERS ===")
            for name, cfg in filter_config.list_filters().items():
                status = "[ON]" if cfg.get('enabled') else "[OFF]"
                print(f"\n{status} {name}")
                print(f"    {cfg.get('description', 'N/A')}")
            return 0

        # Parse logs
        log_parser = Serial2LogParser(args.db_path)
        print(f"[OK] Connected to {args.db_path}")
        print(f"[OK] Total entries: {log_parser.get_total_entries():,}")

        if args.stats:
            print("\n=== LOG STATISTICS ===")
            levels = log_parser.get_log_levels()
            for level, count in sorted(levels.items(), key=lambda x: -x[1]):
                print(f"  {level}: {count:,}")

        # Filter logs
        if args.filter:
            cfg = filter_config.get_filter(args.filter)
            entries = log_parser.filter_by_config(cfg)
            print(f"\n[FILTER] {args.filter}")
        else:
            enabled = filter_config.get_enabled_filters()
            if enabled:
                print(f"\n[FILTER] Using {len(enabled)} enabled filter(s)")
                all_entries = []
                for fname, cfg in enabled.items():
                    all_entries.extend(log_parser.filter_by_config(cfg))
                entries = all_entries
            else:
                print("[ERROR] No filters specified or enabled")
                return 1

        print(f"[OK] Found {len(entries)} matching entries")

        # Validate
        validator = Serial2Validator()
        validation = validator.validate_entries(entries)
        print(f"\n=== VALIDATION RESULTS ===")
        print(f"Valid: {validation['valid_entries']}")
        print(f"Invalid: {validation['invalid_entries']}")
        print(f"With errors: {validation['with_errors']}")

        # Export if requested
        if args.output:
            output = {
                'source': args.db_path,
                'filter': args.filter or 'enabled_filters',
                'total_entries': len(entries),
                'validation': validation,
                'entries': entries[:100]  # First 100 for preview
            }

            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            import json
            with open(output_path, 'w') as f:
                json.dump(output, f, indent=2, default=str)

            print(f"[OK] Exported to {output_path}")

        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
