"""
Serial2 Adapter - US-3
Validates test expectations against Serial2 log stream
"""

import re
import time
from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of matching an expected condition."""
    matched: bool
    timestamp: Optional[str] = None
    wait_time_seconds: float = 0.0
    entry: Optional[Dict] = None
    error: Optional[str] = None


class Serial2Adapter:
    """
    Validate test expectations against Serial2 logs.

    Features:
    - Regex pattern matching on log messages
    - Log level filtering
    - Timeout handling per validation
    - Timestamp recording
    - Integration with LogStreamReader + PreFilter
    """

    def __init__(self, log_stream=None):
        """
        Initialize Serial2 Adapter.

        Args:
            log_stream: Optional LogStreamReader instance for live streaming
        """
        self.log_stream = log_stream
        self.compiled_patterns = {}
        self.stats = {
            'total_validations': 0,
            'matched': 0,
            'timeout': 0,
            'total_wait_time': 0.0
        }

    def validate(
        self,
        expected: Dict,
        logs: list = None,
        timeout: float = 10.0
    ) -> MatchResult:
        """
        Validate expected result against Serial2 logs.

        Args:
            expected: Expected result definition with 'message', 'level', 'timeout'
            logs: Optional list of log entries to check (for testing)
            timeout: Timeout in seconds

        Returns:
            MatchResult with match status and details
        """
        self.stats['total_validations'] += 1

        message_pattern = expected.get('message')
        expected_level = expected.get('level')
        timeout_val = expected.get('timeout', timeout)

        if not message_pattern:
            return MatchResult(
                matched=False,
                error="No message pattern in expected result"
            )

        start_time = time.time()

        # Compile regex pattern
        pattern_key = f"{message_pattern}:{expected_level}"
        if pattern_key not in self.compiled_patterns:
            try:
                self.compiled_patterns[pattern_key] = re.compile(
                    message_pattern, re.IGNORECASE
                )
            except re.error as e:
                logger.error(f"Invalid regex pattern: {e}")
                return MatchResult(
                    matched=False,
                    error=f"Invalid regex: {e}"
                )

        compiled_pattern = self.compiled_patterns[pattern_key]

        # Check provided logs or use stream
        if logs:
            return self._check_logs(
                compiled_pattern, expected_level, logs, start_time, timeout_val
            )
        elif self.log_stream:
            return self._stream_logs(
                compiled_pattern, expected_level, start_time, timeout_val
            )
        else:
            return MatchResult(
                matched=False,
                error="No logs provided and no log stream configured"
            )

    def _check_logs(
        self,
        pattern,
        expected_level: str,
        logs: list,
        start_time: float,
        timeout: float
    ) -> MatchResult:
        """Check provided logs for match."""
        for log_entry in logs:
            message = log_entry.get('message', '')
            level = log_entry.get('level', '')

            # Check level if specified
            if expected_level and level != expected_level:
                continue

            # Check message pattern
            if pattern.search(message):
                wait_time = time.time() - start_time
                self.stats['matched'] += 1
                self.stats['total_wait_time'] += wait_time

                logger.info(
                    f"Match found in {wait_time:.2f}s: {message[:100]}"
                )

                return MatchResult(
                    matched=True,
                    timestamp=log_entry.get('utc_datetime'),
                    wait_time_seconds=wait_time,
                    entry=log_entry
                )

            # Check timeout
            if time.time() - start_time > timeout:
                self.stats['timeout'] += 1
                logger.warning(f"Timeout after {timeout}s waiting for pattern")
                return MatchResult(
                    matched=False,
                    wait_time_seconds=timeout,
                    error=f"Timeout after {timeout}s"
                )

        # No match found
        return MatchResult(
            matched=False,
            wait_time_seconds=time.time() - start_time,
            error="Pattern not found in logs"
        )

    def _stream_logs(
        self,
        pattern,
        expected_level: str,
        start_time: float,
        timeout: float
    ) -> MatchResult:
        """Stream logs from LogStreamReader."""
        try:
            for entry in self.log_stream.stream():
                message = entry.message
                level = entry.level

                # Check level if specified
                if expected_level and level != expected_level:
                    continue

                # Check message pattern
                if pattern.search(message):
                    wait_time = time.time() - start_time
                    self.stats['matched'] += 1
                    self.stats['total_wait_time'] += wait_time

                    return MatchResult(
                        matched=True,
                        timestamp=entry.utc_datetime,
                        wait_time_seconds=wait_time,
                        entry=entry.to_dict() if hasattr(entry, 'to_dict') else None
                    )

                # Check timeout
                if time.time() - start_time > timeout:
                    self.stats['timeout'] += 1
                    return MatchResult(
                        matched=False,
                        wait_time_seconds=timeout,
                        error=f"Timeout after {timeout}s"
                    )

        except Exception as e:
            logger.error(f"Stream error: {e}")
            return MatchResult(
                matched=False,
                error=f"Stream error: {e}"
            )

        return MatchResult(
            matched=False,
            wait_time_seconds=time.time() - start_time,
            error="End of stream reached"
        )

    def get_stats(self) -> Dict:
        """Get validation statistics."""
        avg_wait = (
            self.stats['total_wait_time'] / self.stats['matched']
            if self.stats['matched'] > 0 else 0
        )

        return {
            'total_validations': self.stats['total_validations'],
            'matched': self.stats['matched'],
            'timeout': self.stats['timeout'],
            'match_rate': self.stats['matched'] / self.stats['total_validations'] if self.stats['total_validations'] > 0 else 0,
            'avg_wait_time': avg_wait
        }

    def print_stats(self) -> None:
        """Print validation statistics."""
        stats = self.get_stats()

        print("\n=== SERIAL2 ADAPTER STATISTICS ===")
        print(f"Total validations: {stats['total_validations']}")
        print(f"Matched: {stats['matched']}")
        print(f"Timeout: {stats['timeout']}")
        print(f"Match rate: {stats['match_rate']:.1%}")
        print(f"Avg wait time: {stats['avg_wait_time']:.2f}s")
