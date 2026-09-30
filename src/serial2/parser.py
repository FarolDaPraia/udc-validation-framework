#!/usr/bin/env python3
"""
Serial2 Log Parser & Validator
Reads Serial2 .s2db database and filters for UDC-related entries.
Supports flexible, configurable filter patterns.
"""

import sqlite3
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re
import os

from .filter import FilterConfig


class Serial2LogParser:
    """Parse and filter Serial2 log database."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def get_total_entries(self) -> int:
        """Get total number of log entries."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM LogEntry;")
        return cursor.fetchone()[0]

    def filter_logs(self, pattern: str = "udc*", case_insensitive: bool = True) -> List[Dict]:
        """
        Filter logs by pattern (module or message).

        Args:
            pattern: Wildcard pattern to search (e.g., 'udc*', '*UDC*')
            case_insensitive: Whether to ignore case

        Returns:
            List of matching log entries
        """
        # Convert wildcard pattern to SQL LIKE pattern
        sql_pattern = pattern.replace('*', '%')
        if case_insensitive:
            sql_pattern = sql_pattern.upper()

        cursor = self.conn.cursor()

        if case_insensitive:
            query = """
                SELECT id, pcDateTime, targetDateTime, channel, logLevel,
                       module, message, utcDateTime, lineNumber
                FROM LogEntry
                WHERE UPPER(module) LIKE ? OR UPPER(message) LIKE ?
                ORDER BY utcDateTime
            """
            cursor.execute(query, (sql_pattern, sql_pattern))
        else:
            query = """
                SELECT id, pcDateTime, targetDateTime, channel, logLevel,
                       module, message, utcDateTime, lineNumber
                FROM LogEntry
                WHERE module LIKE ? OR message LIKE ?
                ORDER BY utcDateTime
            """
            cursor.execute(query, (sql_pattern, sql_pattern))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'pc_datetime': row['pcDateTime'],
                'target_datetime': row['targetDateTime'],
                'channel': row['channel'],
                'level': row['logLevel'],
                'module': row['module'],
                'message': row['message'],
                'utc_datetime': row['utcDateTime'],
                'line_number': row['lineNumber']
            })

        return results

    def filter_by_config(self, filter_config: Dict) -> List[Dict]:
        """
        Filter logs using a configuration object.

        Args:
            filter_config: Dict with 'modules', 'keywords', 'log_levels'

        Returns:
            List of matching log entries
        """
        modules = filter_config.get('modules', [])
        keywords = filter_config.get('keywords', [])
        levels = filter_config.get('log_levels', [])

        cursor = self.conn.cursor()

        # Build WHERE clause
        where_parts = []

        if modules:
            module_placeholders = ','.join('?' * len(modules))
            where_parts.append(f"module IN ({module_placeholders})")

        if keywords:
            keyword_conditions = []
            for kw in keywords:
                sql_kw = kw.replace('*', '%').upper()
                keyword_conditions.append(f"UPPER(message) LIKE '{sql_kw}'")
            where_parts.append(f"({' OR '.join(keyword_conditions)})")

        if levels:
            level_placeholders = ','.join('?' * len(levels))
            where_parts.append(f"logLevel IN ({level_placeholders})")

        if not where_parts:
            return []

        where_clause = ' AND '.join(where_parts)
        query = f"""
            SELECT id, pcDateTime, targetDateTime, channel, logLevel,
                   module, message, utcDateTime, lineNumber
            FROM LogEntry
            WHERE {where_clause}
            ORDER BY utcDateTime
        """

        # Build parameter list
        params = []
        if modules:
            params.extend(modules)
        if levels:
            params.extend(levels)

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'pc_datetime': row['pcDateTime'],
                'target_datetime': row['targetDateTime'],
                'channel': row['channel'],
                'level': row['logLevel'],
                'module': row['module'],
                'message': row['message'],
                'utc_datetime': row['utcDateTime'],
                'line_number': row['lineNumber']
            })

        return results

    def get_module_stats(self) -> Dict[str, int]:
        """Get count of log entries per module."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT module, COUNT(*) as count FROM LogEntry GROUP BY module ORDER BY count DESC;")

        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_log_levels(self) -> Dict[str, int]:
        """Get count of log entries per level."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT logLevel, COUNT(*) as count FROM LogEntry GROUP BY logLevel ORDER BY logLevel;")

        return {row[0]: row[1] for row in cursor.fetchall()}

    def validate_entries(self, entries: List[Dict]) -> Dict:
        """
        Validate log entries.

        Returns:
            Dictionary with validation statistics
        """
        if not entries:
            return {'total': 0, 'by_level': {}, 'by_module': {}}

        validation = {
            'total': len(entries),
            'by_level': {},
            'by_module': {},
            'date_range': {
                'first': min((e['utc_datetime'] for e in entries if e['utc_datetime']), default=None),
                'last': max((e['utc_datetime'] for e in entries if e['utc_datetime']), default=None)
            }
        }

        for entry in entries:
            level = entry.get('level', 'UNKNOWN')
            module = entry.get('module', 'UNKNOWN')

            validation['by_level'][level] = validation['by_level'].get(level, 0) + 1
            validation['by_module'][module] = validation['by_module'].get(module, 0) + 1

        return validation


def main():
    parser = argparse.ArgumentParser(description='Parse and filter Serial2 logs with configurable filters')
    parser.add_argument('db_path', help='Path to .s2db database file')
    parser.add_argument('--filter', help='Use named filter from config (e.g., udc_logs, audio_logs)')
    parser.add_argument('--list-filters', action='store_true', help='List all available filters')
    parser.add_argument('--config', default='filter_config.json', help='Path to filter config (default: filter_config.json)')
    parser.add_argument('--pattern', help='Direct pattern search (overrides --filter)')
    parser.add_argument('--case-sensitive', action='store_true', help='Case sensitive search')
    parser.add_argument('--output', help='Output file (JSON format)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--limit', type=int, help='Limit number of results')

    args = parser.parse_args()

    try:
        # Load filter configuration
        try:
            filter_config = FilterConfig(args.config)
        except FileNotFoundError:
            print(f"[WARN] Config not found: {args.config}, using CLI args only")
            filter_config = None

        # List filters if requested
        if args.list_filters:
            if filter_config:
                print("\n=== AVAILABLE FILTERS ===")
                for name, cfg in filter_config.list_filters().items():
                    status = "[ON]" if cfg.get('enabled') else "[OFF]"
                    print(f"\n{status} {name}")
                    print(f"    Description: {cfg.get('description', 'N/A')}")
                    print(f"    Modules: {', '.join(cfg.get('modules', []))}")
                    print(f"    Keywords: {', '.join(cfg.get('keywords', []))}")
                    print(f"    Levels: {', '.join(cfg.get('log_levels', []))}")
            else:
                print("[ERROR] No filter config available")
            return 0

        # Initialize parser
        log_parser = Serial2LogParser(args.db_path)
        print(f"[OK] Connected to {args.db_path}")
        print(f"[OK] Total log entries: {log_parser.get_total_entries():,}")

        # Show statistics if requested
        if args.stats:
            print("\n=== LOG LEVEL DISTRIBUTION ===")
            levels = log_parser.get_log_levels()
            for level, count in sorted(levels.items(), key=lambda x: -x[1]):
                print(f"  {level}: {count:,}")

            print("\n=== TOP 10 MODULES ===")
            modules = log_parser.get_module_stats()
            for module, count in list(modules.items())[:10]:
                print(f"  {module}: {count:,}")

        # Filter logs
        entries = []

        if args.pattern:
            # Use pattern override
            print(f"\n[FILTER] Pattern: '{args.pattern}'")
            entries = log_parser.filter_logs(args.pattern, not args.case_sensitive)

        elif args.filter and filter_config:
            # Use named filter from config
            cfg = filter_config.get_filter(args.filter)
            print(f"\n[FILTER] Using config: '{args.filter}'")
            print(f"         Modules: {', '.join(cfg.get('modules', []))}")
            print(f"         Keywords: {', '.join(cfg.get('keywords', []))}")
            entries = log_parser.filter_by_config(cfg)

        elif filter_config:
            # Use enabled filters from config
            enabled = filter_config.get_enabled_filters()
            if enabled:
                print(f"\n[FILTER] Using {len(enabled)} enabled filter(s) from config")
                all_entries = []
                for filter_name, cfg in enabled.items():
                    print(f"         - {filter_name}")
                    all_entries.extend(log_parser.filter_by_config(cfg))
                entries = all_entries
            else:
                print("\n[WARN] No filters enabled in config. Use --list-filters to see available options")
                print("[HINT] Use --pattern or --filter to specify what to search")
                return 1
        else:
            print("\n[ERROR] No filter specified. Use --pattern, --filter, or enable filters in config")
            return 1

        if args.limit:
            entries = entries[:args.limit]

        print(f"[OK] Found {len(entries)} matching entries")

        # Validate
        validation = log_parser.validate_entries(entries)
        print("\n=== VALIDATION RESULTS ===")
        print(f"Total entries: {validation['total']}")
        if validation['by_level']:
            print("By log level:")
            for level, count in sorted(validation['by_level'].items()):
                print(f"  {level}: {count}")
        if validation['by_module']:
            print(f"Unique modules: {len(validation['by_module'])}")

        # Show sample
        if entries:
            print("\n=== SAMPLE ENTRIES (First 3) ===")
            for i, entry in enumerate(entries[:3], 1):
                print(f"\n{i}. [{entry['level']}] {entry['module']} - {entry['utc_datetime']}")
                print(f"   {entry['message'][:100]}...")

        # Export if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            export_data = {
                'timestamp': datetime.now().isoformat(),
                'source': str(args.db_path),
                'filter_pattern': args.pattern,
                'total_found': len(entries),
                'validation': validation,
                'entries': entries
            }

            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            print(f"\n[OK] Exported {len(entries)} entries to {output_path}")

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
