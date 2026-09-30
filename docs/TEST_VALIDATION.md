# Test Validation Framework

## Overview

Das Test Validation Framework führt Testfälle sequenziell aus und validiert erwartete Ergebnisse in Real-Time gegen Log-Streams von Serial2 und zukünftigen Backend APIs.

```
┌─────────────────────────────────────────────────────┐
│         Test Case Manager                           │
├─────────────────────────────────────────────────────┤
│  Load: config/test_cases.json                       │
│  Execute: Sequenziell Step-by-Step                  │
│  Validate: Parallel Adapters (Serial2 + Backend)    │
│  Report: Pass/Fail/Timeout Results                 │
└─────────────────────────────────────────────────────┘

Test Case JSON
    ↓
┌─────────────────┐
│ Step 1          │  Sequential
│ (Serial2 only)  │  Steps
│                 │
├─────────────────┤
│ Step 2          │
│ (Parallel)      │ → Serial2 Adapter
│                 │ → Backend Adapter (parallel)
└─────────────────┘
    ↓
Pass/Fail Report
```

---

## 1. JSON Format

### Test Case Structure

```json
{
  "test_cases": {
    "test_case_id": {
      "name": "Human-readable name",
      "description": "What this test validates",
      "category": "startup|runtime|error|validation",
      "preconditions": [
        "Vehicle ignition ON",
        "Serial2 logging active"
      ],
      "steps": [
        {
          "id": 1,
          "name": "Step name",
          "description": "What happens in this step",
          "action": {
            "source": "serial2|backend_api|manual",
            "type": "wait|trigger|validate",
            "description": "Action description",
            "api_call": "POST /endpoint (if trigger)"
          },
          "expected": [
            {
              "source": "serial2|backend_api",
              "message": "regex pattern (serial2)",
              "level": "Info|Warn|Error|Fatal",
              "timeout": 5,
              "timestamp": null
            },
            {
              "source": "backend_api",
              "endpoint": "/api/endpoint",
              "field": "response.field.name",
              "value": "expected_value",
              "timeout": 10,
              "timestamp": null
            }
          ]
        }
      ],
      "fail_conditions": [
        {
          "type": "error_log",
          "source": "serial2",
          "message": "regex pattern",
          "stop_test": true
        },
        {
          "type": "timeout",
          "stop_test": true
        }
      ]
    }
  }
}
```

### Field Descriptions

#### Test Case Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name |
| `description` | string | Yes | What test validates |
| `category` | string | No | startup, runtime, error, validation |
| `preconditions` | array | No | Manual or automated preconditions |
| `steps` | array | Yes | Ordered test steps |
| `fail_conditions` | array | No | Conditions that fail test immediately |

#### Step Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | number | Yes | Step number (1, 2, 3...) |
| `name` | string | Yes | Step display name |
| `description` | string | No | Detailed description |
| `action` | object | Yes | What action triggers validation |
| `expected` | array | Yes | Expected results (can be multiple) |

#### Action Object

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `source` | string | "serial2", "backend_api", "manual" | Source of action |
| `type` | string | "wait", "trigger", "validate" | Action type |
| `description` | string | - | Human readable |
| `api_call` | string | "POST /endpoint" | For trigger type |

**Action Types:**
- `wait`: Passiv - warte auf Logs/Events (kein Trigger)
- `trigger`: Aktiv - rufe Backend API oder ähnliches auf
- `validate`: Prüfe Bedingungen (keine neue Aktion)

#### Expected Object

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `source` | string | "serial2", "backend_api" | Validation source |
| `message` | string | regex | (Serial2 only) Message regex |
| `level` | string | "Info", "Warn", "Error", "Fatal" | (Serial2 only) Log level |
| `timeout` | number | seconds | Max time to wait for match |
| `endpoint` | string | path | (Backend only) API endpoint |
| `field` | string | "field.nested.name" | (Backend only) Response field path |
| `value` | string/number/bool | - | (Backend only) Expected value |
| `timestamp` | string | ISO 8601 | (auto-filled) When matched |

#### Fail Condition

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | "error_log", "timeout", "keyword" |
| `source` | string | "serial2", "backend_api" |
| `message` | string | Regex pattern to match |
| `stop_test` | boolean | Stop test immediately if matched |

---

## 2. Execution Flow

### Sequential Execution

```
Test Start
    ↓
Check Preconditions
    ↓
Step 1: Execute
    Action (source: serial2, type: wait)
    Expected: [serial2 message]
    ↓ (wait for match)
    Timeout? → FAIL
    Match? → Step PASS → Next
    Error? → FAIL
    ↓
Step 2: Execute (Parallel Adapters)
    Action (source: backend_api, type: trigger)
    Expected: [
      {source: serial2, message: "..."},
      {source: backend_api, endpoint: "/...", value: "..."}
    ]
    ↓ (parallel wait)
    Serial2 Adapter: Wait for Log
    Backend Adapter: POST /register, wait for Response
    ↓ (both complete)
    Both success? → Step PASS
    Any timeout? → FAIL
    Any error? → FAIL
    ↓
Step N: ... (continue sequentially)
    ↓
Test Complete
    ↓
Generate Report
```

### Adapter Execution (Parallel within Step)

```
Step 2 Expected Results:
[
  {source: "serial2", message: "..."},
  {source: "backend_api", endpoint: "/..."}
]

┌──────────────────────┐
│  Serial2 Adapter     │  Parallel
│  Wait for Log        │  Execution
│  Timeout: 10s        │
└──────────────────────┘
         ∧
         │
    ┌────┴────┐
    │ Step 2  │
    │Executor │
    │         │
    └────┬────┘
         │
         ∨
┌──────────────────────┐
│ Backend API Adapter  │  Parallel
│ POST /register       │  Execution
│ Wait for Response    │
│ Timeout: 10s         │
└──────────────────────┘

Result: PASS when BOTH succeed, FAIL when ANY fail/timeout
```

---

## 3. Example Test Cases

### Example 1: Simple Serial2-only Test

```json
{
  "test_cases": {
    "udc_startup": {
      "name": "UDC Startup Sequence",
      "description": "Validate UDC initializes correctly",
      "category": "startup",
      "preconditions": [
        "Vehicle ignition ON",
        "Serial2 logging active"
      ],
      "steps": [
        {
          "id": 1,
          "name": "Logger Initialization",
          "description": "Verify logger instance is created",
          "action": {
            "source": "serial2",
            "type": "wait"
          },
          "expected": [
            {
              "source": "serial2",
              "message": "udc-control-manager: .*Creating logger instance",
              "level": "Info",
              "timeout": 5
            }
          ]
        },
        {
          "id": 2,
          "name": "Version Check",
          "description": "Verify developer version is logged",
          "action": {
            "source": "serial2",
            "type": "wait"
          },
          "expected": [
            {
              "source": "serial2",
              "message": "Developer version: .*",
              "level": "Info",
              "timeout": 10
            }
          ]
        }
      ],
      "fail_conditions": [
        {
          "type": "error_log",
          "source": "serial2",
          "message": ".*Failed to initialize.*",
          "stop_test": true
        },
        {
          "type": "timeout",
          "stop_test": true
        }
      ]
    }
  }
}
```

### Example 2: Parallel Adapter Test (Future)

```json
{
  "test_cases": {
    "udc_backend_sync": {
      "name": "UDC Backend Synchronization",
      "description": "Validate UDC syncs with Backend API",
      "category": "runtime",
      "steps": [
        {
          "id": 1,
          "name": "Send Registration Request + Log Verification",
          "description": "Trigger backend registration and verify both Serial2 and API",
          "action": {
            "source": "backend_api",
            "type": "trigger",
            "description": "POST registration request",
            "api_call": "POST /udc/register"
          },
          "expected": [
            {
              "source": "serial2",
              "message": "registration.*completed",
              "level": "Info",
              "timeout": 5
            },
            {
              "source": "backend_api",
              "endpoint": "/udc/status",
              "field": "status",
              "value": "registered",
              "timeout": 10
            }
          ]
        }
      ]
    }
  }
}
```

---

## 4. CLI Commands

### Run Full Regression Test

```bash
python scripts/run_tests.py --mode full --output report.json --verbose
```

**Options:**
- `--mode full`: Run all enabled test cases
- `--output <file>`: Save report to JSON
- `--verbose`: Show detailed logs
- `--live`: Show real-time progress

**Output:**
```
Test Run: 2026-09-30 16:45:00
────────────────────────────────

[1/5] udc_startup
  ✓ Step 1: Logger Initialization (1.2s)
  ✓ Step 2: Version Check (2.1s)
  ✓ PASSED (3.3s)

[2/5] udc_error_handling
  ✗ Step 1: Error Detection (timeout after 5.0s)
  ✗ FAILED: Timeout waiting for error log

[3/5] ...

Summary:
────────
Passed: 3/5
Failed: 2/5
Errors: 0
Duration: 45.2s
```

### Run Single Test Case

```bash
python scripts/run_tests.py --test udc_startup --verbose
```

### Run Regression Suite

```bash
python scripts/run_tests.py --suite regression
```

**Available Suites:**
- `regression`: All critical tests
- `startup`: Startup sequence tests
- `runtime`: Runtime validation tests
- `error_handling`: Error scenario tests

### Run by Category

```bash
python scripts/run_tests.py --category startup --verbose
```

---

## 5. JSON Configuration File

**Location:** `config/test_cases.json`

**Structure:**
```
config/
└── test_cases.json
    ├── test_cases
    │   ├── udc_startup
    │   ├── udc_error_handling
    │   ├── udc_backend_sync
    │   └── ...
    ├── suites
    │   ├── regression
    │   ├── startup
    │   ├── runtime
    │   └── error_handling
    └── defaults
        ├── timeout
        ├── log_level_filter
        └── fail_fast
```

---

## 6. Test Result Report

### JSON Report Format

```json
{
  "test_run": {
    "start_time": "2026-09-30T16:45:00Z",
    "end_time": "2026-09-30T16:46:00Z",
    "duration_seconds": 60,
    "total_tests": 5,
    "passed": 3,
    "failed": 2,
    "errors": 0
  },
  "test_results": [
    {
      "test_id": "udc_startup",
      "name": "UDC Startup Sequence",
      "status": "PASSED",
      "duration_seconds": 3.3,
      "steps": [
        {
          "id": 1,
          "name": "Logger Initialization",
          "status": "PASSED",
          "duration_seconds": 1.2,
          "expected_results": [
            {
              "source": "serial2",
              "status": "MATCHED",
              "message": "udc-control-manager: Creating logger instance",
              "timestamp": "2026-09-30T16:45:01.200Z",
              "wait_time_seconds": 1.2
            }
          ]
        },
        {
          "id": 2,
          "name": "Version Check",
          "status": "PASSED",
          "duration_seconds": 2.1,
          "expected_results": [
            {
              "source": "serial2",
              "status": "MATCHED",
              "message": "Developer version: 2026CW40",
              "timestamp": "2026-09-30T16:45:03.300Z",
              "wait_time_seconds": 2.1
            }
          ]
        }
      ]
    },
    {
      "test_id": "udc_error_handling",
      "name": "UDC Error Handling",
      "status": "FAILED",
      "duration_seconds": 5.0,
      "steps": [
        {
          "id": 1,
          "name": "Error Detection",
          "status": "FAILED",
          "duration_seconds": 5.0,
          "failure_reason": "TIMEOUT",
          "expected_results": [
            {
              "source": "serial2",
              "status": "TIMEOUT",
              "message": "pattern.*error.*not found",
              "timeout_seconds": 5.0
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 7. State Machine Execution

### State Diagram

```
┌──────────────┐
│   IDLE       │
│ (start)      │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ LOAD CONFIG  │
│ test_cases   │
└──────┬───────┘
       │
       ↓
┌──────────────────┐
│ CHECK            │
│ PRECONDITIONS    │
└──────┬───────────┘
       │
       ↓
┌──────────────────────┐
│ EXECUTE STEP         │
│ (sequential)         │
│ ├─ Action           │
│ └─ Expected (||)     │
└──────┬───────────────┘
       │
       ├─→ ✓ All Expected Matched
       │   └─→ STEP PASSED
       │       └─→ More steps?
       │           ├─ Yes: Next Step
       │           └─ No: Test Completed
       │
       ├─→ ✗ Timeout / Error
       │   └─→ STEP FAILED
       │       └─→ Fail-fast?
       │           ├─ Yes: Test Failed (abort)
       │           └─ No: Continue?
       │
       └─→ ⏱️ Timeout
           └─→ TEST TIMEOUT (abort)

┌──────────────┐
│ GENERATE     │
│ REPORT       │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   DONE       │
└──────────────┘
```

---

## 8. Timestamp Documentation

Timestamps werden **dokumentiert, aber nicht validiert**.

### Timestamp Fields

```json
{
  "step": {
    "id": 1,
    "expected": [
      {
        "source": "serial2",
        "message": "...",
        "timestamp": "2026-09-30T16:45:01.200Z"  ← Auto-filled when matched
      }
    ]
  }
}
```

**Verwendung:**
- Debugging: Wann hat Step gestartet/geendet?
- Tracing: Zeitlicher Ablauf der Steps
- Analyse: Performance-Messungen

**KEINE Validierung:**
- Kein Time-Delta Check zwischen Steps
- Kein Cross-Medium Correlation (Serial2 vs Backend)
- Nur dokumentieren für Debugging-Zwecke

---

## 9. Error Handling

### Fail Conditions

```json
{
  "fail_conditions": [
    {
      "type": "error_log",
      "source": "serial2",
      "message": ".*Fatal.*",
      "stop_test": true
    },
    {
      "type": "timeout",
      "stop_test": true
    },
    {
      "type": "keyword",
      "source": "serial2",
      "message": "Initialization failed",
      "stop_test": true
    }
  ]
}
```

### Handling Strategy

1. **During Execution:** Monitor fail conditions continuously
2. **Early Detection:** Stop test immediately if critical fail condition matched
3. **Logging:** Document which condition triggered failure
4. **Report:** Include fail reason in test result

---

## 10. Integration with Streaming

### Connection to LogStreamReader & PreFilter

```python
# 1. Load Test Cases
test_manager = TestCaseManager("config/test_cases.json")
test_manager.load_test("udc_startup")

# 2. Start Streaming
reader = LogStreamReader("vehicle.s2db")
pre_filter = PreFilter()
pre_filter.add_rules_from_config(config)

# 3. Validate Steps
for entry in reader.stream():
    if pre_filter.should_pass(entry):
        # Feed to test validator
        result = test_manager.process_entry(entry)
        
        # Handle result
        if result['step_passed']:
            print(f"✓ Step {result['step_id']} PASSED")
        elif result['step_failed']:
            print(f"✗ Step {result['step_id']} FAILED: {result['reason']}")
            break
```

---

## 11. Future Extensions

### Phase 2: Backend API Adapter (TODO)

```json
{
  "expected": [
    {
      "source": "backend_api",
      "endpoint": "/udc/status",
      "field": "status",
      "value": "registered",
      "timeout": 10
    }
  ]
}
```

### Phase 3: AI-based Error Analysis (TODO)

For ambiguous test failures, AI can help analyze:
- Log pattern changes (developer changed log schema)
- Timing issues (race conditions)
- Environmental factors

---

## 12. Best Practices

### Writing Good Test Cases

1. **Clear preconditions:** What must be true before test starts?
2. **Atomic steps:** Each step validates one thing
3. **Reasonable timeouts:** Not too aggressive, not too loose
4. **Fail conditions:** Catch known error patterns
5. **Documentation:** Clear names and descriptions

### Example Good Test Case

```json
{
  "udc_startup": {
    "name": "UDC Startup",
    "description": "Verify UDC initializes and logs startup sequence",
    "preconditions": ["Vehicle ignition ON", "Serial2 active"],
    "steps": [
      {
        "id": 1,
        "name": "Logger Creation",
        "action": {"source": "serial2", "type": "wait"},
        "expected": [{
          "source": "serial2",
          "message": "Creating logger instance",
          "timeout": 5
        }]
      }
    ]
  }
}
```

---

**Version:** 1.0.0  
**Status:** Specification Complete, Implementation Pending  
**Last Updated:** 2026-09-30
