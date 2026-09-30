"""
Real-Time Log Stream Reader
Reads and streams logs from Serial2 in real-time
"""

import sqlite3
import time
import threading
from pathlib import Path
from typing import Generator, Dict, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Single log entry from Serial2."""

    id: int
    pc_datetime: str
    target_datetime: str
    channel: int
    level: str
    module: str
    message: str
    utc_datetime: str
    line_number: int
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'pc_datetime': self.pc_datetime,
            'target_datetime': self.target_datetime,
            'channel': self.channel,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'utc_datetime': self.utc_datetime,
            'line_number': self.line_number,
            'timestamp': self.timestamp
        }


class LogStreamReader:
    """
    Real-time log stream reader for Serial2 .s2db databases.

    Supports:
    - Live monitoring of .s2db (SQLite WAL monitoring)
    - Streaming via generator pattern
    - Callbacks/event handlers
    - Backpressure handling
    - Configurable polling intervals
    """

    def __init__(
        self,
        db_path: str,
        poll_interval: float = 0.1,
        batch_size: int = 100,
        mode: str = "live"
    ):
        """
        Initialize streaming reader.

        Args:
            db_path: Path to .s2db database
            poll_interval: Polling interval in seconds (smaller = lower latency)
            batch_size: Batch size for processing
            mode: "live" (SQLite WAL) or "tail" (file-based)
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.mode = mode

        self.conn = None
        self.last_id = 0
        self.running = False
        self.callbacks: List[Callable[[LogEntry], None]] = []

        # Statistics
        self.stats = {
            'total_read': 0,
            'total_events': 0,
            'errors': 0,
            'start_time': None,
            'last_update': None
        }

    def connect(self) -> None:
        """Connect to database."""
        if self.conn is not None:
            return

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.isolation_level = None  # Autocommit mode
        logger.info(f"Connected to {self.db_path}")

        # Get initial last ID
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) FROM LogEntry")
        result = cursor.fetchone()
        self.last_id = result[0] if result[0] else 0
        logger.info(f"Starting from log ID: {self.last_id}")

    def disconnect(self) -> None:
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Disconnected from database")

    def stream(self) -> Generator[LogEntry, None, None]:
        """
        Stream log entries in real-time.

        Yields:
            LogEntry objects as they become available

        Usage:
            reader = LogStreamReader("test.s2db")
            for entry in reader.stream():
                print(f"{entry.level}: {entry.message}")
        """
        self.connect()
        self.stats['start_time'] = datetime.now()

        try:
            while True:
                entries = self._fetch_new_entries()

                for entry in entries:
                    self.stats['total_events'] += 1
                    yield entry

                    # Call registered callbacks
                    for callback in self.callbacks:
                        try:
                            callback(entry)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                            self.stats['errors'] += 1

                self.stats['last_update'] = datetime.now()

                if not entries:
                    # No new entries, sleep before polling again
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("Stream interrupted by user")
        except Exception as e:
            logger.error(f"Stream error: {e}")
            self.stats['errors'] += 1
            raise
        finally:
            self.disconnect()

    def stream_batch(self) -> Generator[List[LogEntry], None, None]:
        """
        Stream log entries in batches for better throughput.

        Yields:
            List[LogEntry] - batch of entries

        Usage:
            for batch in reader.stream_batch(batch_size=50):
                print(f"Processing {len(batch)} entries")
        """
        self.connect()
        self.stats['start_time'] = datetime.now()

        try:
            while True:
                batch = []

                for _ in range(self.batch_size):
                    entries = self._fetch_new_entries(limit=1)
                    if entries:
                        batch.extend(entries)
                    else:
                        break

                if batch:
                    self.stats['total_events'] += len(batch)
                    yield batch
                    self.stats['last_update'] = datetime.now()
                else:
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("Batch stream interrupted")
        except Exception as e:
            logger.error(f"Batch stream error: {e}")
            self.stats['errors'] += 1
            raise
        finally:
            self.disconnect()

    def _fetch_new_entries(self, limit: int = None) -> List[LogEntry]:
        """
        Fetch new log entries since last_id.

        Args:
            limit: Maximum number of entries to fetch

        Returns:
            List of new LogEntry objects
        """
        if not self.conn:
            return []

        try:
            cursor = self.conn.cursor()

            query = """
                SELECT id, pcDateTime, targetDateTime, channel, logLevel,
                       module, message, utcDateTime, lineNumber
                FROM LogEntry
                WHERE id > ?
                ORDER BY id
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, (self.last_id,))
            rows = cursor.fetchall()

            entries = []
            for row in rows:
                entry = LogEntry(
                    id=row['id'],
                    pc_datetime=row['pcDateTime'],
                    target_datetime=row['targetDateTime'],
                    channel=row['channel'],
                    level=row['logLevel'],
                    module=row['module'],
                    message=row['message'],
                    utc_datetime=row['utcDateTime'],
                    line_number=row['lineNumber']
                )
                entries.append(entry)
                self.last_id = entry.id

            self.stats['total_read'] += len(entries)
            return entries

        except Exception as e:
            logger.error(f"Fetch error: {e}")
            self.stats['errors'] += 1
            return []

    def register_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """
        Register a callback to be called for each log entry.

        Args:
            callback: Function that takes LogEntry as argument
        """
        self.callbacks.append(callback)
        logger.info(f"Registered callback: {callback.__name__}")

    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def get_stats(self) -> Dict:
        """Get streaming statistics."""
        stats = self.stats.copy()

        if stats['start_time']:
            elapsed = (datetime.now() - stats['start_time']).total_seconds()
            stats['elapsed_seconds'] = elapsed
            stats['events_per_second'] = stats['total_events'] / elapsed if elapsed > 0 else 0
            stats['reads_per_second'] = stats['total_read'] / elapsed if elapsed > 0 else 0

        return stats

    def print_stats(self) -> None:
        """Print current statistics."""
        stats = self.get_stats()

        print("\n=== STREAMING STATISTICS ===")
        print(f"Total read: {stats['total_read']:,}")
        print(f"Total events: {stats['total_events']:,}")
        print(f"Errors: {stats['errors']}")

        if 'elapsed_seconds' in stats:
            print(f"Elapsed: {stats['elapsed_seconds']:.1f}s")
            print(f"Events/sec: {stats['events_per_second']:.1f}")
            print(f"Reads/sec: {stats['reads_per_second']:.1f}")

        if stats['last_update']:
            print(f"Last update: {stats['last_update'].strftime('%H:%M:%S')}")
