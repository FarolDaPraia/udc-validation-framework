# Serial2 Log Parser - UDC Validation Framework

## Overview

Python script zum Auslesen und Validieren von Serial 2 Logs für das UDC (Universal Diagnostic Center) Fahrzeug-Testing Framework.

**Status**: ✓ 416 UDC-Einträge in der Test-Datenbank gefunden

## Features

- ✓ SQLite `.s2db` Datenbank auslesen
- ✓ Flexible Pattern-Filterung (udc*, *error*, etc.)
- ✓ Log-Level und Modul-Statistiken
- ✓ JSON Export für weitere Verarbeitung
- ✓ Validierungsbericht mit Zusammenfassung

## Installation

```bash
# Benötigt Python 3.7+
python3 --version

# Keine weiteren Dependencies erforderlich (sqlite3 im Standard)
```

## Usage

### Basic: Filter nach UDC-Logs

```bash
python3 serial2_log_parser.py <path-to-s2db> --pattern "udc*"
```

### Mit Statistiken

```bash
python3 serial2_log_parser.py <path-to-s2db> --stats
```

Zeigt:
- Log-Level Verteilung (Info, Warn, Error, etc.)
- Top 10 Module mit Eintrags-Counts
- Gefilterte Einträge

### Export zu JSON

```bash
python3 serial2_log_parser.py <path-to-s2db> --output results.json
```

Erzeugt strukturierte JSON mit:
- Timestamp und Quelle
- Filter-Pattern
- Validierungsergebnisse
- Alle gefilterten Log-Einträge

### Limit (große DBs)

```bash
python3 serial2_log_parser.py <path-to-s2db> --limit 100
```

### Case-sensitive Suche

```bash
python3 serial2_log_parser.py <path-to-s2db> --pattern "UDC" --case-sensitive
```

## Praktische Beispiele

### 1. Nur UDC-Fehler anschauen

```bash
python3 serial2_log_parser.py test.s2db --pattern "udc*"  # Alle UDC-Einträge
# Dann im Output nach "Error" suchen oder:
python3 serial2_log_parser.py test.s2db --pattern "*error*" --stats
```

### 2. Vollständiger Report generieren

```bash
python3 serial2_log_parser.py test.s2db \
  --pattern "udc*" \
  --output udc_report_$(date +%Y%m%d).json \
  --stats
```

### 3. Modul-spezifische Logs

```bash
python3 serial2_log_parser.py test.s2db --pattern "*SYSTEM-API*"
```

### 4. Zeitbereich prüfen (für später mit Backend API)

```bash
python3 serial2_log_parser.py test.s2db --pattern "udc*" --output filtered_logs.json
# Python script kann dann filtered_logs.json mit Backend-API-Logs vergleichen
```

## Testdaten

Test mit der aktuellen Log-Datenbank:

```bash
cd C:\Users\alexa\github\udc

# Full report
python3 serial2_log_parser.py "2026-09-30-09_55_37/2026-09-30-09_55_37/2026-09-30-09_55_37.s2db" \
  --pattern "udc*" \
  --output udc_validation_report.json \
  --stats
```

**Ergebnis:**
```
[OK] Connected to 2026-09-30-09_55_37/2026-09-30-09_55_37/2026-09-30-09_55_37.s2db
[OK] Total log entries: 155,687

=== LOG LEVEL DISTRIBUTION ===
  Info: 108,712
  Trace: 27,858
  Warn: 12,303
  Error: 6,775
  Fatal: 39

[FILTER] Pattern: 'udc*'
[OK] Found 416 matching entries

=== VALIDATION RESULTS ===
Total entries: 416
By log level:
  Error: 56
  Info: 354
  Warn: 6
Unique modules: 1 (SYSTEM-API)
```

## JSON Export Format

```json
{
  "timestamp": "2026-09-30T16:47:38.526882",
  "source": "path/to/2026-09-30-09_55_37.s2db",
  "filter_pattern": "udc*",
  "total_found": 416,
  "validation": {
    "total": 416,
    "by_level": {
      "Info": 354,
      "Error": 56,
      "Warn": 6
    },
    "by_module": {
      "SYSTEM-API": 416
    },
    "date_range": {
      "first": "1970-01-01T00:00:00.000",
      "last": "1970-01-01T00:00:00.000"
    }
  },
  "entries": [
    {
      "id": 119163,
      "pc_datetime": "2026-09-30T09:56:38.906",
      "target_datetime": "1970-01-01T15:34:53.903",
      "channel": 5,
      "level": "Info",
      "module": "SYSTEM-API",
      "message": "udc-control-manager: Default: Creating logger instance...",
      "utc_datetime": "1970-01-01T00:00:00.000",
      "line_number": -1
    },
    ...
  ]
}
```

## Nächste Schritte

### Phase 1: Serial 2 Validierung (DONE)
- ✓ Python script zum Auslesen der .s2db schreiben
- ✓ UDC-Pattern filtern
- ✓ Validierungsbericht generieren

### Phase 2: Backend API Integration (TODO)
```python
# API-Logs vergleichen mit Serial 2 Logs
# Automatische Validierung der Test Cases
# Abweichungen reportieren
```

### Phase 3: Test Case Integration (TODO)
```python
# Jeden Test Case gegen Serial 2 + Backend validieren
# Fehlgeschlagene Tests markieren
# Report mit Recommendations generieren
```

## Fehlerbehebung

### "Database locked" Error
→ Stelle sicher, dass die Serial 2 Tool nicht gleichzeitig das DB-File liest

### "No UDC entries found"
→ Logs enthalten möglicherweise noch keine UDC-Daten
→ Prüfe mit `--stats` welche Module vorhanden sind
→ Passe das Pattern an (z.B. `--pattern "SYSTEM-API"`)

### Unicode Errors auf Windows
→ Script nutzt UTF-8 encoding, sollte auf modernem Windows funktionieren
→ Falls nicht: `python3 -X utf8=1 serial2_log_parser.py ...`

## Architektur

```
C:\Users\alexa\github\udc\
├── serial2_log_parser.py          # Main parser script
├── SERIAL2_PARSER_README.md       # Dieses File
├── udc_validation_report.json     # Generierter Report
└── 2026-09-30-09_55_37/
    └── 2026-09-30-09_55_37/
        ├── 2026-09-30-09_55_37.s2db     # Serial 2 Log Database
        ├── channel_GCM.bin              # Binary Channel Data
        └── sysmon.txt                   # System Monitor Data
```

## API Reference

### Class: `Serial2LogParser`

```python
from serial2_log_parser import Serial2LogParser

parser = Serial2LogParser("path/to/file.s2db")

# Get total entries
count = parser.get_total_entries()  # → 155687

# Filter logs
results = parser.filter_logs("udc*", case_insensitive=True)
# → List[Dict] mit gefilterten Logs

# Get statistics
stats = parser.get_module_stats()  # → Dict[module_name: count]
levels = parser.get_log_levels()   # → Dict[level: count]

# Validate
validation = parser.validate_entries(results)
# → Dict mit Statistiken der Results
```

## Lizenz & Credits

Entwickelt für UDC TestConcept Prüfplatz Framework
