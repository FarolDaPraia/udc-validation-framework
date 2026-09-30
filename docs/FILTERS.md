# Serial2 Filter System - Erweiterungsguide

## Übersicht

Das neue Filter-System ist **flexibel und erweiterbar** für zukünftige Keywords und Module.

### Aktuelle Konfiguration

```json
{
  "filters": {
    "udc_logs": {
      "enabled": true,
      "modules": ["SYSTEM-API"],
      "keywords": ["udc-control*", "udc_control*"],
      "log_levels": ["Info", "Warn", "Error", "Fatal"]
    },
    "udc_errors": {
      "enabled": false,
      "modules": ["SYSTEM-API"],
      "keywords": ["udc*"],
      "log_levels": ["Error", "Fatal"]
    }
  }
}
```

## CLI-Befehle

### 1. Filter anzeigen

```bash
python3 serial2_log_parser.py <db_path> --list-filters
```

Output:
```
=== AVAILABLE FILTERS ===

[ON] udc_logs
    Description: UDC Control Manager logs
    Modules: SYSTEM-API
    Keywords: udc-control*, udc_control*
    Levels: Info, Warn, Error, Fatal

[OFF] udc_errors
    Description: UDC Error and Fatal logs
    ...
```

### 2. Mit aktivierten Filtern (aus Config)

Alle Logs mit `enabled: true` werden automatisch verwendet:

```bash
python3 serial2_log_parser.py <db_path> --stats --limit 100
```

### 3. Spezifischen Filter verwenden

```bash
python3 serial2_log_parser.py <db_path> --filter udc_errors
python3 serial2_log_parser.py <db_path> --filter audio_logs
python3 serial2_log_parser.py <db_path> --filter positioning_logs
```

### 4. CLI-Pattern überschreiben (Direct Search)

```bash
python3 serial2_log_parser.py <db_path> --pattern "diagnos*"
python3 serial2_log_parser.py <db_path> --pattern "*error*" --case-sensitive
```

### 5. Mit Export

```bash
# UDC-Fehler exportieren
python3 serial2_log_parser.py <db_path> --filter udc_errors --output errors.json

# Audio-Logs exportieren
python3 serial2_log_parser.py <db_path> --filter audio_logs --output audio.json

# Alle aktivierten Filter mit Export
python3 serial2_log_parser.py <db_path> --output all_logs.json --stats
```

## Neue Filter hinzufügen

### Beispiel 1: Neuen UDC-Subsystem-Filter hinzufügen

**In `filter_config.json`:**

```json
{
  "filters": {
    ...
    "udc_database": {
      "description": "UDC Database-related logs (FUTURE)",
      "enabled": false,
      "modules": ["SYSTEM-API", "DATABASE_MGR"],
      "keywords": ["database*", "db_*", "persist*"],
      "log_levels": ["Info", "Warn", "Error"]
    }
  }
}
```

### Beispiel 2: Backend API Integration Filter

```json
{
  "filters": {
    ...
    "backend_api": {
      "description": "Backend API validation logs",
      "enabled": false,
      "modules": ["SYSTEM-API", "HTTP_CLIENT"],
      "keywords": ["api_*", "endpoint*", "request*", "response*"],
      "log_levels": ["Info", "Warn", "Error", "Trace"]
    }
  }
}
```

### Beispiel 3: Multi-Module Vehicle Testing

```json
{
  "filters": {
    ...
    "vehicle_diagnostics": {
      "description": "All vehicle diagnostic subsystems",
      "enabled": false,
      "modules": ["SYSTEM-API", "CAN_BUS", "OBD2_HANDLER", "DIAGNOSTIC_CORE"],
      "keywords": ["diagnostic*", "can_*", "obd*", "fault*"],
      "log_levels": ["Info", "Warn", "Error", "Fatal"]
    }
  }
}
```

### Beispiel 4: Performance-Testing Filter

```json
{
  "filters": {
    ...
    "performance": {
      "description": "Performance and timing measurements",
      "enabled": false,
      "modules": ["TRACE-SYSTEM", "PERFORMANCE_MGR"],
      "keywords": ["perf*", "timing*", "latency*", "throughput*"],
      "log_levels": ["Info", "Trace"]
    }
  }
}
```

## Filter-Struktur Erklärung

```json
{
  "filter_name": {
    "description": "Human-readable description",
    "enabled": true|false,                    // true = auto-used with --stats
    "modules": ["MODULE1", "MODULE2"],        // Nur diese Module
    "keywords": ["keyword1*", "*keyword2"],   // Patterns in Messages
    "log_levels": ["Info", "Error"]           // Log-Levels zum Filtern
  }
}
```

### Wildcard-Patterns

- `udc*` → Alle Messages die mit "udc" beginnen
- `*control*` → Alle Messages die "control" enthalten
- `*manager` → Alle Messages die mit "manager" enden
- `audio*` → Audio-related entries
- `diagnos*` → Diagnostic entries

## Praktische Workflows

### Workflow 1: Tägliche Validierung

```bash
# Morgens: Alle aktivierten Filter prüfen
python3 serial2_log_parser.py latest.s2db --stats

# Fehler ins Detail gehen
python3 serial2_log_parser.py latest.s2db --filter udc_errors --output errors_today.json

# Report generieren
python3 serial2_log_parser.py latest.s2db --filter all_udc --output report.json
```

### Workflow 2: Neue Feature Testing

```bash
# Neuen Filter für Feature erstellen
# z.B. "bluetooth_module" in filter_config.json

# Aktivieren
python3 serial2_log_parser.py test.s2db --filter bluetooth_module --stats

# Debug wenn nötig
python3 serial2_log_parser.py test.s2db --pattern "*bluetooth*" --limit 20
```

### Workflow 3: Vergleich Serial2 vs Backend API

```bash
# Serial2 Logs exportieren
python3 serial2_log_parser.py device.s2db --filter all_udc --output serial2_logs.json

# Backend API Logs separat exportieren (später)
# python3 backend_api_parser.py ... --output api_logs.json

# Validierung in separatem Script:
# python3 validate_logs.py serial2_logs.json api_logs.json
```

## Zukünftige Erweiterungen

Folgende Filter sind vorbereitet für Erweiterung:

1. ✓ `udc_logs` - UDC Control Manager (ACTIVE)
2. ✓ `udc_errors` - UDC Error Handling (READY)
3. ⚠️ `audio_logs` - Audio subsystem (PLANNED)
4. ⚠️ `positioning_logs` - GNSS/GPS (PLANNED)
5. ⚠️ `all_udc` - Comprehensive UDC (READY)

### Hinzufügen ohne Code-Änderung

**Nur `filter_config.json` bearbeiten:**
- Neue Filter hinzufügen
- Keywords erweitern
- Module hinzufügen
- Enable/Disable togglen

**Keine Python-Code-Änderungen nötig!**

## Test Commands

```bash
# Alles testen
python3 serial2_log_parser.py <db> --list-filters        # Alle Filter
python3 serial2_log_parser.py <db> --filter udc_logs      # Enabled
python3 serial2_log_parser.py <db> --filter udc_errors    # Disabled
python3 serial2_log_parser.py <db> --filter audio_logs    # Future
python3 serial2_log_parser.py <db> --pattern "*" --limit 1  # Direct

# Statistiken
python3 serial2_log_parser.py <db> --stats

# Export alle Varianten
python3 serial2_log_parser.py <db> --filter udc_errors --output test.json
python3 serial2_log_parser.py <db> --pattern "udc*" --output test.json
```

## Integration mit Test Cases

```python
# Später in validation_framework.py:
from serial2_log_parser import Serial2LogParser, FilterConfig

config = FilterConfig("filter_config.json")
parser = Serial2LogParser("test.s2db")

# Spezifischen Filter für Test-Case verwenden
test_filter = config.get_filter("udc_logs")
logs = parser.filter_by_config(test_filter)

# Validierung durchführen
if len(logs) > 0 and any(e['level'] == 'Error' for e in logs):
    print("TEST FAILED: Errors found")
else:
    print("TEST PASSED")
```

## Support & Troubleshooting

### Neuer Filter funktioniert nicht?

1. Filter in `--list-filters` sichtbar?
2. Module und Keywords stimmen?
3. Case-sensitive prüfen (Wildcard hilft!)
4. Mit `--pattern` direct testen

### Performance bei vielen Logs?

- `--limit` verwenden um erste Ergebnisse zu prüfen
- Spezifischere Keywords verwenden
- Nur relevante Module in Filter

### Filter ändern ohne neustart?

- Bearbeite `filter_config.json`
- Script lädt Config neu bei jedem Start
- Keine Neukompilierung nötig
