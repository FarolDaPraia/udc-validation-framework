#!/usr/bin/env python3
"""
UDC Validation Framework - Quick Start Example
Shows basic usage of the validation framework
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.serial2 import Serial2LogParser, FilterConfig
from src.validators import Serial2Validator


def main():
    print("=" * 60)
    print("UDC Validation Framework - Quick Start")
    print("=" * 60)

    # Configuration paths
    db_path = "2026-09-30-09_55_37/2026-09-30-09_55_37/2026-09-30-09_55_37.s2db"
    config_path = "config/filters.json"

    try:
        # Step 1: Load filter configuration
        print("\n[Step 1] Loading filter configuration...")
        filter_config = FilterConfig(config_path)
        print(f"✓ Loaded {len(filter_config.list_filters())} filters")

        # Step 2: Connect to Serial2 database
        print("\n[Step 2] Connecting to Serial2 database...")
        parser = Serial2LogParser(db_path)
        total = parser.get_total_entries()
        print(f"✓ Connected to database with {total:,} entries")

        # Step 3: Get filter definition
        print("\n[Step 3] Getting filter definition...")
        udc_filter = filter_config.get_filter("udc_logs")
        print(f"✓ Filter 'udc_logs':")
        print(f"  - Modules: {', '.join(udc_filter['modules'])}")
        print(f"  - Keywords: {', '.join(udc_filter['keywords'])}")
        print(f"  - Levels: {', '.join(udc_filter['log_levels'])}")

        # Step 4: Apply filter
        print("\n[Step 4] Applying filter...")
        entries = parser.filter_by_config(udc_filter)
        print(f"✓ Found {len(entries)} matching entries")

        # Step 5: Show statistics
        print("\n[Step 5] Database statistics...")
        levels = parser.get_log_levels()
        print("  Log levels in database:")
        for level, count in sorted(levels.items(), key=lambda x: -x[1]):
            print(f"    - {level}: {count:,}")

        modules = parser.get_module_stats()
        print("\n  Top 5 modules:")
        for module, count in list(modules.items())[:5]:
            print(f"    - {module}: {count:,}")

        # Step 6: Validate entries
        print("\n[Step 6] Validating entries...")
        validator = Serial2Validator()
        validation = validator.validate_entries(entries)
        print(f"✓ Validation complete:")
        print(f"  - Valid entries: {validation['valid_entries']}")
        print(f"  - Invalid entries: {validation['invalid_entries']}")
        print(f"  - With errors: {validation['with_errors']}")

        # Step 7: Show sample entries
        print("\n[Step 7] Sample entries (first 3):")
        for i, entry in enumerate(entries[:3], 1):
            print(f"\n  [{i}] {entry['level']} - {entry['module']}")
            msg = entry['message'][:70] + "..." if len(entry['message']) > 70 else entry['message']
            print(f"      {msg}")

        # Step 8: Compare filters
        print("\n[Step 8] Comparing different filters...")
        filters_to_test = ["udc_logs", "udc_errors", "all_udc"]
        print("  Filter comparison:")
        for fname in filters_to_test:
            try:
                fdef = filter_config.get_filter(fname)
                count = len(parser.filter_by_config(fdef))
                status = "[ENABLED]" if fdef.get('enabled') else "[DISABLED]"
                print(f"    - {fname} {status}: {count} entries")
            except ValueError:
                pass

        print("\n" + "=" * 60)
        print("✓ Quick start complete! See docs/ for more examples.")
        print("=" * 60)

        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure you're in the project root directory!")
        print("Update db_path and config_path if needed.")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
