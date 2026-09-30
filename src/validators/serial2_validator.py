"""
Serial2 Log Validator
Validates Serial2 logs against test cases and rules
"""

from typing import List, Dict, Optional
from datetime import datetime


class Serial2Validator:
    """Validate Serial2 logs against validation rules."""

    def __init__(self, validation_rules: Dict = None):
        self.rules = validation_rules or {}
        self.results = []

    def validate_entry(self, entry: Dict) -> Dict:
        """
        Validate a single log entry.

        Args:
            entry: Log entry from Serial2

        Returns:
            Validation result with status and issues
        """
        result = {
            'entry_id': entry.get('id'),
            'valid': True,
            'issues': [],
            'warnings': []
        }

        # Check required fields
        if self.rules.get('require_timestamp') and not entry.get('utc_datetime'):
            result['issues'].append('Missing timestamp')
            result['valid'] = False

        if self.rules.get('require_module') and not entry.get('module'):
            result['issues'].append('Missing module')
            result['valid'] = False

        if self.rules.get('require_level') and not entry.get('level'):
            result['issues'].append('Missing log level')
            result['valid'] = False

        if self.rules.get('allow_missing_message') is False and not entry.get('message'):
            result['issues'].append('Missing message')
            result['valid'] = False

        # Check for errors/warnings in content
        level = entry.get('level', '').lower()
        if level == 'error':
            result['warnings'].append('Error level log found')
        elif level == 'fatal':
            result['issues'].append('Fatal level log found')
            result['valid'] = False

        return result

    def validate_entries(self, entries: List[Dict]) -> Dict:
        """
        Validate multiple log entries.

        Returns:
            Validation summary
        """
        results = {
            'total_entries': len(entries),
            'valid_entries': 0,
            'invalid_entries': 0,
            'with_errors': 0,
            'details': []
        }

        for entry in entries:
            result = self.validate_entry(entry)
            results['details'].append(result)

            if result['valid']:
                results['valid_entries'] += 1
            else:
                results['invalid_entries'] += 1

            if any('Error' in str(i) or 'Fatal' in str(i) for i in result['issues']):
                results['with_errors'] += 1

        return results

    def compare_with_expectations(self, entries: List[Dict], expected: Dict) -> Dict:
        """
        Compare logs against expected patterns.

        Args:
            entries: Log entries to check
            expected: Expected patterns (modules, keywords, levels)

        Returns:
            Comparison results
        """
        comparison = {
            'total': len(entries),
            'matching_modules': 0,
            'matching_keywords': 0,
            'mismatches': []
        }

        for entry in entries:
            if entry.get('module') in expected.get('modules', []):
                comparison['matching_modules'] += 1

            msg = entry.get('message', '')
            for kw in expected.get('keywords', []):
                if kw.strip('*') in msg:
                    comparison['matching_keywords'] += 1
                    break

        return comparison
