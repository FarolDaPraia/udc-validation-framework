# UDC Validation Framework - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     UDC Validation Framework                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐    ┌─────────────┐ │
│  │   Serial2    │         │ Backend API  │    │  Test Case  │ │
│  │   .s2db DB   │         │  (Future)    │    │  Validator  │ │
│  └──────┬───────┘         └──────┬───────┘    └──────┬──────┘ │
│         │                        │                   │         │
│         └────────────┬───────────┴───────────────────┘         │
│                      │                                          │
│              ┌───────▼────────┐                                │
│              │  Parser Layer  │                                │
│              │  ├─ Serial2    │                                │
│              │  ├─ Backend    │                                │
│              │  └─ Config     │                                │
│              └────────┬────────┘                                │
│                       │                                        │
│              ┌────────▼──────────┐                             │
│              │  Filter Engine    │                             │
│              │  ├─ Keywords      │                             │
│              │  ├─ Modules       │                             │
│              │  └─ Log Levels    │                             │
│              └────────┬──────────┘                             │
│                       │                                        │
│              ┌────────▼────────────┐                           │
│              │  Validator Layer    │                           │
│              │  ├─ Entry Validate  │                           │
│              │  ├─ Compare         │                           │
│              │  └─ Report Gen      │                           │
│              └────────┬────────────┘                           │
│                       │                                        │
│              ┌────────▼──────────┐                             │
│              │  Output Layer     │                             │
│              │  ├─ JSON Export   │                             │
│              │  ├─ Console       │                             │
│              │  └─ Reports       │                             │
│              └───────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

## Module Architecture

### 1. Serial2 Module (`src/serial2/`)

**Responsibility:** Read and parse Serial2 `.s2db` SQLite databases

```python
Serial2LogParser
├── __init__(db_path)
├── get_total_entries() → int
├── filter_logs(pattern) → List[Dict]
├── filter_by_config(config) → List[Dict]
├── get_module_stats() → Dict
├── get_log_levels() → Dict
└── validate_entries(entries) → Dict

FilterConfig
├── __init__(config_path)
├── get_filter(name) → Dict
├── list_filters() → Dict[str, Dict]
├── get_enabled_filters() → Dict[str, Dict]
├── enable_filter(name) → None
└── disable_filter(name) → None
```

### 2. Validators Module (`src/validators/`)

**Responsibility:** Validate logs against rules and test cases

```python
Serial2Validator
├── __init__(validation_rules)
├── validate_entry(entry) → Dict
├── validate_entries(entries) → Dict
└── compare_with_expectations(entries, expected) → Dict
```

### 3. Backends Module (`src/backends/`)

**Responsibility:** Connect to and parse external APIs (TODO)

```python
BackendAPIParser
├── __init__(api_url, api_token)
├── fetch_logs(filters) → List[Dict]
├── post_validation(result) → Dict
└── compare_logs(serial2_logs, api_logs) → Dict
```

## Data Flow

### Workflow 1: Serial2 Parsing & Validation

```
User invokes validate.py
    ↓
Load FilterConfig from config/filters.json
    ↓
Initialize Serial2LogParser with .s2db
    ↓
Apply Filter (by name or pattern)
    ├─ Filter modules
    ├─ Filter keywords
    └─ Filter log levels
    ↓
Get filtered entries (List[Dict])
    ↓
Run Serial2Validator
    ├─ Check required fields
    ├─ Check for error levels
    └─ Generate validation report
    ↓
Export results (JSON, Console, etc.)
```

### Workflow 2: Backend API Integration (Future)

```
BackendAPIParser.fetch_logs(filters)
    ↓
Compare with Serial2Logs
    ├─ Match entries by timestamp
    ├─ Match entries by message
    └─ Detect discrepancies
    ↓
Generate comparison report
    ├─ Matches
    ├─ Mismatches
    └─ Missing entries
    ↓
Post validation result via BackendAPIParser.post_validation()
```

## Configuration System

### Filter Configuration (`config/filters.json`)

```json
{
  "filters": {
    "filter_name": {
      "description": "Human description",
      "enabled": true|false,
      "modules": ["MODULE1", "MODULE2"],
      "keywords": ["pattern1*", "*pattern2"],
      "log_levels": ["Info", "Error", "Fatal"]
    }
  },
  "validation_rules": {
    "require_timestamp": true,
    "require_module": true,
    "require_level": true,
    "allow_missing_message": false
  }
}
```

### Validation Rules (`config/validation_rules.json` - TODO)

```json
{
  "required_fields": ["timestamp", "module", "level"],
  "forbidden_levels": ["Fatal"],
  "expected_modules": ["SYSTEM-API"],
  "expected_keywords": ["udc*"],
  "error_threshold": 0.05
}
```

### Test Cases (`config/test_cases.json` - TODO)

```json
{
  "test_cases": {
    "test_udc_startup": {
      "description": "UDC startup validation",
      "expected_logs": {
        "modules": ["SYSTEM-API"],
        "keywords": ["udc-control*"],
        "min_count": 5
      },
      "max_errors": 0
    }
  }
}
```

## Interface Specifications

### CLI Interface

```bash
# List filters
python scripts/validate.py <db> --list-filters

# Use config-based filter
python scripts/validate.py <db> --filter <filter_name>

# Direct pattern search
python scripts/validate.py <db> --pattern "keyword*"

# With export
python scripts/validate.py <db> --filter <name> --output report.json

# With statistics
python scripts/validate.py <db> --stats
```

### Python API

```python
# Parse logs
from src.serial2 import Serial2LogParser, FilterConfig

parser = Serial2LogParser("test.s2db")
config = FilterConfig("config/filters.json")

filter_def = config.get_filter("udc_logs")
logs = parser.filter_by_config(filter_def)

# Validate
from src.validators import Serial2Validator

validator = Serial2Validator()
results = validator.validate_entries(logs)

# Export
import json
with open("report.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Data Structures

### Log Entry (from Serial2)

```python
{
    'id': int,                              # Database ID
    'pc_datetime': str,                     # PC timestamp
    'target_datetime': str,                 # Target timestamp
    'channel': int,                         # Channel number
    'level': str,                           # Log level (Info, Error, etc.)
    'module': str,                          # Source module
    'message': str,                         # Log message
    'utc_datetime': str,                    # UTC timestamp
    'line_number': int                      # Line number
}
```

### Filter Configuration

```python
{
    'description': str,
    'enabled': bool,
    'modules': List[str],
    'keywords': List[str],
    'log_levels': List[str]
}
```

### Validation Result

```python
{
    'total_entries': int,
    'valid_entries': int,
    'invalid_entries': int,
    'with_errors': int,
    'details': [
        {
            'entry_id': int,
            'valid': bool,
            'issues': List[str],
            'warnings': List[str]
        },
        ...
    ]
}
```

## Error Handling

### Error Levels

1. **Critical** - Database connection fails, invalid config
   - Stop execution
   - Return error code 1

2. **Warning** - Missing entries, partial results
   - Continue execution
   - Log warnings
   - Include in report

3. **Info** - Successful operations, statistics
   - Log to console
   - Include in report

### Exception Hierarchy

```python
Exception
├── FileNotFoundError
│   ├── DB file not found
│   └── Config file not found
├── ValueError
│   ├── Invalid filter name
│   └── Invalid log level
├── sqlite3.Error
│   └── Database connection error
└── IOError
    └── Output file write error
```

## Testing Strategy

### Unit Tests (`tests/`)

```python
# test_serial2_parser.py
- Test database connection
- Test log filtering (by pattern, by config)
- Test statistics calculation
- Test edge cases (empty DB, large DB)

# test_filters.py
- Test filter loading from JSON
- Test filter enable/disable
- Test filter by module/keyword/level

# test_validators.py
- Test entry validation
- Test batch validation
- Test comparison logic
```

### Integration Tests

```python
# End-to-end workflow
1. Load sample.s2db
2. Apply filter
3. Validate entries
4. Export JSON
5. Verify output
```

## Performance Considerations

### Optimization Points

1. **Database Queries**
   - Use indexed columns (module, logLevel)
   - Batch WHERE clauses
   - Limit result size

2. **Memory Usage**
   - Stream large result sets
   - Use generators for large datasets
   - Limit in-memory cache

3. **Filter Performance**
   - Pre-compile regex patterns
   - Cache filter configs
   - Parallel processing (future)

### Benchmarks

```
Database: 155,687 log entries
Filter "udc*": 416 entries
Parse time: ~2 seconds
Filter time: ~1 second
Export time: ~0.5 seconds
Total: ~3.5 seconds
```

## Security Considerations

### Input Validation

- Validate file paths (no directory traversal)
- Validate filter names (alphanumeric + underscore)
- Sanitize SQL patterns (prevent injection)
- Validate JSON config format

### Data Protection

- No credentials in code (use env vars/config)
- No sensitive data in logs
- Sanitize output reports
- Read-only database access

## Future Enhancements

### Phase 2: API Integration

```
Backend API Parser
├── REST client (requests lib)
├── Authentication (token/JWT)
├── Log fetching with filters
├── Result posting
└── Error handling & retry
```

### Phase 3: Advanced Validation

```
Test Case Framework
├── Load test cases from config
├── Map serial2 logs to test steps
├── Detect test pass/fail
├── Generate test reports
└── CI/CD integration
```

### Phase 4: Analytics

```
Analytics Engine
├── Performance metrics
├── Trend analysis
├── Compliance checking
├── Automated alerts
└── Dashboard/UI (web)
```

## Deployment Architecture

### Development

```
Local Machine
├── Git repo
├── Python virtual env
└── Sample .s2db files
```

### CI/CD (Future)

```
GitHub Actions / Jenkins
├── Run tests
├── Lint code
├── Build artifacts
├── Run validation on builds
└── Archive reports
```

### Production (Future)

```
Docker Container
├── Python 3.9+ base image
├── Validation Framework code
├── Config volume mount
├── Output volume mount
└── Log volume mount
```

## References

- SQLite3: https://www.sqlite.org/
- Python typing: https://docs.python.org/3/library/typing.html
- JSON Schema: https://json-schema.org/

---

**Version:** 0.1.0  
**Status:** Design Complete, Implementation in Progress  
**Last Updated:** 2026-09-30
