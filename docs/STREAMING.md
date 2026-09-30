# Real-Time Streaming Architecture

## Overview

Das Streaming System ist für **Live Vehicle Logging** ausgelegt - es liest kontinuierlich Logs aus Serial2 und validiert sie in Real-Time.

```
Serial2.exe (Vehicle)
    ↓ tausende msgs/sec
┌─────────────────────────┐
│ LogStreamReader         │  ← Kontinuierlich .s2db lesen
│ (Poll-based)            │     ~100ms Latenz
└─────────────┬───────────┘
              ↓ raw entries
┌─────────────────────────┐
│ PreFilter               │  ← Ultra-fast Filter
│ (99% drop)              │     ~1-5 μs/entry
└─────────────┬───────────┘
              ↓ filtered
┌─────────────────────────┐
│ RingBuffer Queue        │  ← Backpressure handling
│ (Circular)              │     Memory-bounded
└─────────────┬───────────┘
              ↓ to validators
┌─────────────────────────┐
│ TestCaseValidator       │  ← Live Assertions
│ (State Machine)         │     Pass/Fail detection
└─────────────┬───────────┘
              ↓
        Pass/Fail Result
```

## Components

### 1. LogStreamReader (`src/streaming/reader.py`)

Liest Live-Logs aus SQLite Datenbank in Real-Time.

**Features:**
- Kontinuierliches Polling (~100ms Latenz)
- Stream via Generator (speichersparend)
- Batch-Mode für höheren Durchsatz
- Callback-System für Event-Handling
- Statistic Tracking

**Verwendung:**

```python
from src.streaming import LogStreamReader

# Initialisieren
reader = LogStreamReader(
    "vehicle.s2db",
    poll_interval=0.1,      # 100ms polling
    batch_size=100
)

# Stream einzelne Einträge
for entry in reader.stream():
    print(f"{entry.level}: {entry.message}")
    
# Oder in Batches
for batch in reader.stream_batch():
    print(f"Got {len(batch)} entries")
```

### 2. PreFilter (`src/streaming/pre_filter.py`)

Ultra-fast Filter zum Ausfiltern von 99% nicht-relevanter Logs.

**Features:**
- Pre-compiled Regex Patterns
- Short-circuit Evaluation
- ~1-5 Microsekunden pro Entry
- Pass-Rate Statistiken
- Multi-Rule (OR Logic)

**Performance:**
```
1,000 entries/sec Input
→ PreFilter (1-5 μs)
→ 10-50 entries/sec Output (99% drop)
→ Validator (ms-scale)
```

**Verwendung:**

```python
from src.streaming import PreFilter
from src.serial2 import FilterConfig
import json

# Initialisieren
pre_filter = PreFilter()

# Mit Config-Datei laden
with open("config/filters.json") as f:
    config = json.load(f)
pre_filter.add_rules_from_config(config)

# Filter anwenden
for entry in reader.stream():
    if pre_filter.should_pass(entry):
        # Process entry
        pass
```

## Real-Time Pipeline

### Beispiel: Fahrzeug-Test mit Validierung

```python
from src.streaming import LogStreamReader, PreFilter
from src.test_cases import TestCaseValidator
import json

# 1. Setup Reader
reader = LogStreamReader("vehicle.s2db")

# 2. Setup Filter
pre_filter = PreFilter()
with open("config/filters.json") as f:
    config = json.load(f)
pre_filter.add_rules_from_config(config)

# 3. Setup Validator
validator = TestCaseValidator("config/test_cases.json")

# 4. Process Stream
for entry in reader.stream():
    # Pre-filter: Drop 99%
    if not pre_filter.should_pass(entry):
        continue
    
    # Validate: Check Test Cases
    result = validator.process_entry(entry)
    
    # Action: Update test state
    if result['test_passed']:
        print(f"✓ Test passed: {result['test_name']}")
    elif result['test_failed']:
        print(f"✗ Test FAILED: {result['test_name']}")
        print(f"  Reason: {result['reason']}")
```

## Performance Characteristics

### Throughput

| Component | Input/sec | Output/sec | Latency |
|-----------|-----------|-----------|---------|
| Reader | ∞ | 1,000-10,000 | 100ms |
| PreFilter | 1,000 | 10-50 | 1-5 μs |
| Queue | 10-50 | 10-50 | <1ms |
| Validator | 10-50 | 1-10 | 1-10ms |

### Beispiel Real Vehicle:

```
Vehicle generates: 5,000 msgs/sec
  ↓ Reader (100ms poll)
  5,000 msgs/sec → LogStreamReader
  ↓ PreFilter (udc* + level check)
  50 msgs/sec → Filtered (1%)
  ↓ Validator (state machine)
  5-10 msgs/sec → Test Results
```

## Configuration

### filters.json

```json
{
  "filters": {
    "udc_logs": {
      "enabled": true,
      "modules": ["SYSTEM-API"],
      "keywords": ["udc-control*", "udc_*"],
      "log_levels": ["Info", "Warn", "Error", "Fatal"]
    }
  }
}
```

### test_cases.json (TODO)

```json
{
  "test_cases": {
    "udc_startup": {
      "description": "UDC Startup Validation",
      "steps": [
        {
          "name": "LoggerInit",
          "expect": "udc-control-manager: Creating logger",
          "timeout": 5
        },
        {
          "name": "VersionCheck",
          "expect": "Developer version: *",
          "timeout": 10
        }
      ]
    }
  }
}
```

## API Reference

### LogStreamReader

```python
class LogStreamReader:
    def stream() → Generator[LogEntry]
    def stream_batch() → Generator[List[LogEntry]]
    def register_callback(callback: Callable)
    def get_stats() → Dict
    def print_stats()
```

### PreFilter

```python
class PreFilter:
    def add_rule(rule: FilterRule)
    def add_rules_from_config(config: Dict)
    def should_pass(entry: LogEntry) → bool
    def filter_batch(entries: List[LogEntry]) → List[LogEntry]
    def get_stats() → Dict
    def get_pass_rate() → float
```

## Usage Examples

### Example 1: Simple Stream with Filter

```bash
python scripts/stream_logs.py vehicle.s2db --filter udc_logs
```

### Example 2: Batch Processing

```bash
python scripts/stream_logs.py vehicle.s2db --batch --filter udc_logs
```

### Example 3: Programmatic

```python
from src.streaming import LogStreamReader, PreFilter
import json

reader = LogStreamReader("vehicle.s2db")
pre_filter = PreFilter()

with open("config/filters.json") as f:
    config = json.load(f)
pre_filter.add_rules_from_config(config)

count = 0
for entry in reader.stream():
    if pre_filter.should_pass(entry):
        print(entry.message)
        count += 1
        if count >= 1000:
            break

reader.print_stats()
pre_filter.print_stats()
```

## Testing

### Static Database Test

```bash
python scripts/test_streaming.py
```

### Live Vehicle Test (TODO)

```bash
# Mit echter Vehicle-Datenbank
python scripts/stream_logs.py /path/to/live/vehicle.s2db --filter udc_logs
```

## Optimization Tips

### 1. Filter Tuning

```python
# Spezifische Keywords → höhere Pass Rate
"keywords": ["udc-control*"]  # ~0.5% pass rate

# Breite Keywords → mehr Overhead
"keywords": ["*"]  # 100% pass rate
```

### 2. Polling Interval

```python
# Schneller (lower latency, mehr CPU)
poll_interval=0.01  # 10ms

# Langsamer (higher latency, weniger CPU)
poll_interval=1.0   # 1s
```

### 3. Batch Size

```python
# Größere Batches → höherer Durchsatz
batch_size=1000

# Kleinere Batches → niedrigere Latenz
batch_size=10
```

## Known Limitations

1. **SQLite Polling**: Hat ~100ms Latenz (nicht sub-millisekunden)
   - Für Production: Könnte zu Socket-based IPC upgegradet werden

2. **WAL File**: Benötigt Write-Ahead Logging aktiviert
   - Standardmäßig in modernen SQLite

3. **Single-threaded**: Reader läuft in Main Thread
   - Validator sollte in separatem Thread laufen

## Future Enhancements

### Phase 2: Queue & Backpressure

```python
from src.streaming import RingBuffer

buffer = RingBuffer(max_size=10000)

for entry in reader.stream():
    if pre_filter.should_pass(entry):
        try:
            buffer.put(entry, timeout=1.0)
        except Full:
            print("Backpressure: Buffer full, dropping entries")
```

### Phase 3: Multi-threaded Validation

```python
import threading
from queue import Queue

# Reader in Thread 1
# Filter in Thread 2
# Validator in Thread 3
```

### Phase 4: IPC with Serial2.exe

```python
# Direct Socket/IPC connection zu Serial2.exe
# Statt SQLite Polling (sub-millisecond latency)
```

---

**Version:** 0.2.0  
**Status:** Reader & PreFilter Complete, Queue/Validator in Progress  
**Last Updated:** 2026-09-30
