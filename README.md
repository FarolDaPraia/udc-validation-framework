# UDC Validation Framework - Prüfplatz v01

**Validierungssystem für Serial2 Logs und Backend API Integration**

## 📋 Überblick

Das UDC Validation Framework ist ein Python-basiertes System zur automatisierten Validierung von Fahrzeug-Test-Logs (Serial2) für das Universal Diagnostic Center (UDC).

**Hauptfunktionen:**
- ✓ Flexible Log-Filterung basierend auf Konfigurationsdateien
- ✓ Serial2 `.s2db` SQLite Datenbank Parser
- ✓ Modulare Architektur für zukünftige API-Integration
- ✓ Automatisierte Test Case Validierung
- ✓ JSON Export für Reporting

## 📁 Projektstruktur

```
udc-validation-framework/
├── README.md                          # Dieses File
├── docs/                              # Dokumentation
│   ├── ARCHITECTURE.md                # System-Architektur
│   ├── FILTERS.md                     # Filter-Konfiguration
│   └── SERIAL2.md                     # Serial2 Parser Referenz
│
├── src/                               # Python-Quellcode
│   ├── __init__.py
│   ├── serial2/                       # Serial2 Log Parser
│   │   ├── __init__.py
│   │   ├── parser.py                  # Hauptparser für .s2db
│   │   └── filter.py                  # Filter-Konfiguration Manager
│   │
│   ├── backends/                      # Backend-Konnektoren (TODO)
│   │   ├── __init__.py
│   │   └── api.py                     # REST API Client
│   │
│   ├── validators/                    # Validierungslogik
│   │   ├── __init__.py
│   │   ├── serial2_validator.py       # Serial2 Log Validator
│   │   └── api_validator.py           # Backend API Validator (TODO)
│   │
│   └── utils/                         # Hilfsmodule
│       └── __init__.py
│
├── config/                            # Konfigurationsdateien
│   ├── filters.json                   # Log-Filter Definitionen
│   ├── validation_rules.json          # Validierungs-Regeln (TODO)
│   └── test_cases.json                # Test Case Definitionen (TODO)
│
├── scripts/                           # CLI-Tools & Scripts
│   ├── validate.py                    # Hauptvalidierungs-Script
│   ├── export_logs.py                 # Log-Export Tool
│   └── compare_logs.py                # Serial2 vs API Vergleich (TODO)
│
├── tests/                             # Unit Tests
│   ├── __init__.py
│   ├── test_serial2_parser.py
│   ├── test_filters.py
│   └── fixtures/                      # Test-Dateien
│       └── sample_logs/
│
├── reports/                           # Generierte Validierungs-Reports
│   └── .gitkeep
│
├── examples/                          # Verwendungsbeispiele
│   └── quickstart.py                  # Quick-Start Script
│
└── requirements.txt                   # Python Dependencies
```

## 🚀 Quick Start

### 1. Installation

```bash
# Python 3.7+ erforderlich
pip install -r requirements.txt
```

### 2. Serial2 Logs validieren

```bash
# Mit aktivierten Filtern (aus config/filters.json)
python scripts/validate.py <path-to-db.s2db> --stats

# Mit spezifischem Filter
python scripts/validate.py <path-to-db.s2db> --filter udc_errors

# Mit Export
python scripts/validate.py <path-to-db.s2db> --filter udc_logs --output report.json
```

### 3. Verfügbare Filter anzeigen

```bash
python scripts/validate.py <db.s2db> --list-filters
```

## 🔧 Verwendung

### Beispiel 1: Tägliche Validierung

```bash
cd C:\Users\alexa\github\udc

# Test-Datenbank prüfen
python scripts/validate.py \
  "2026-09-30-09_55_37/2026-09-30-09_55_37/2026-09-30-09_55_37.s2db" \
  --stats --filter udc_logs
```

**Output:**
```
[OK] Connected to ...s2db
[OK] Total entries: 155,687
=== LOG STATISTICS ===
  Info: 108,712
  Trace: 27,858
  Warn: 12,303
  Error: 6,775
  Fatal: 39
[FILTER] udc_logs
[OK] Found 416 matching entries
=== VALIDATION RESULTS ===
Valid: 416
Invalid: 0
With errors: 0
```

### Beispiel 2: Fehleranalyse

```bash
# Nur UDC-Fehler exportieren
python scripts/validate.py <db.s2db> --filter udc_errors --output errors.json

# JSON enthält dann:
{
  "total_entries": 56,
  "valid_entries": 56,
  "invalid_entries": 0,
  "entries": [
    {
      "id": 119166,
      "level": "Error",
      "module": "SYSTEM-API",
      "message": "udc-control-manager: IpcCommunicator: Failed to initialize..."
    },
    ...
  ]
}
```

### Beispiel 3: Neuen Filter hinzufügen

**In `config/filters.json`:**

```json
{
  "filters": {
    "my_custom_filter": {
      "description": "My test filter",
      "enabled": false,
      "modules": ["SYSTEM-API"],
      "keywords": ["my_keyword*"],
      "log_levels": ["Info", "Error"]
    }
  }
}
```

**Dann nutzen:**

```bash
python scripts/validate.py <db.s2db> --filter my_custom_filter
```

## 📖 Dokumentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technische Architektur & Design
- **[FILTERS.md](docs/FILTERS.md)** - Filter-System Erweiterungsguide
- **[SERIAL2.md](docs/SERIAL2.md)** - Serial2 Parser API Reference

## 🧪 Testing

```bash
# Unit Tests ausführen
python -m pytest tests/

# Mit Coverage
python -m pytest tests/ --cov=src/
```

## 📋 Module Overview

### `src.serial2.parser.Serial2LogParser`

Hauptparser für Serial2 `.s2db` Datenbanken.

```python
from src.serial2 import Serial2LogParser

parser = Serial2LogParser("test.s2db")
entries = parser.filter_logs("udc*")
stats = parser.get_module_stats()
```

### `src.serial2.filter.FilterConfig`

Filter-Konfiguration Manager.

```python
from src.serial2 import FilterConfig

config = FilterConfig("config/filters.json")
udc_filter = config.get_filter("udc_logs")
entries = parser.filter_by_config(udc_filter)
```

### `src.validators.Serial2Validator`

Validierungslogik für Log-Einträge.

```python
from src.validators import Serial2Validator

validator = Serial2Validator()
results = validator.validate_entries(entries)
```

## 🔜 Roadmap

### Phase 1: ✅ Serial2 Parsing
- [x] .s2db Parser
- [x] Flexible Filter-Config
- [x] Log Export (JSON)
- [x] Modulare Architektur

### Phase 2: 🔄 Backend API Integration
- [ ] REST API Client
- [ ] Log Fetching
- [ ] Serial2 vs API Vergleich
- [ ] Automatische Discrepancy Detection

### Phase 3: 🎯 Test Case Automation
- [ ] Test Case Framework
- [ ] Automatische Validierung
- [ ] Result Reporting
- [ ] CI/CD Integration

### Phase 4: 📊 Advanced Analytics
- [ ] Performance Metrics
- [ ] Trend Analysis
- [ ] Compliance Checking
- [ ] Automated Alerts

## 🛠️ Entwicklung

### Neues Modul hinzufügen

1. Ordner in `src/` erstellen
2. `__init__.py` mit Exports erstellen
3. Module implementieren
4. In `src/__init__.py` exportieren
5. Tests in `tests/` hinzufügen

### Neuen Filter hinzufügen

1. In `config/filters.json` neuen Eintrag hinzufügen
2. `enabled: false` setzen (als Standard)
3. Filter aktivieren mit `--filter <name>`

### Code Style

```bash
# Linting
python -m pylint src/

# Formatting
python -m black src/
```

## ⚙️ Konfiguration

### `config/filters.json`

Definiert verfügbare Log-Filter:

```json
{
  "filters": {
    "filter_name": {
      "description": "Filter description",
      "enabled": true,
      "modules": ["MODULE1", "MODULE2"],
      "keywords": ["keyword1*", "*keyword2"],
      "log_levels": ["Info", "Error"]
    }
  }
}
```

### Environment Variables (TODO)

```bash
UDC_DB_PATH=path/to/db
UDC_API_URL=http://backend.api
UDC_API_TOKEN=secret
```

## 📊 Beispiel-Daten

Im Repository enthalten:

```
2026-09-30-09_55_37/
├── 2026-09-30-09_55_37.s2db        # Serial2 Datenbank (155.687 Einträge)
├── channel_GCM.bin                  # Binary Channel Data
└── sysmon.txt                       # System Monitor Data
```

**Statistiken:**
- Gesamt Logs: 155.687
- UDC Logs: 416
- UDC Fehler: 56
- Module: 92
- Log Levels: 5 (Info, Trace, Warn, Error, Fatal)

## 🐛 Troubleshooting

### "Filter config not found"

```bash
# Stelle sicher dass config/filters.json existiert
# Oder spezifiziere den Pfad:
python scripts/validate.py <db.s2db> --config /path/to/filters.json
```

### "No UDC entries found"

```bash
# Prüfe verfügbare Filter
python scripts/validate.py <db.s2db> --list-filters

# Oder nutze Direct Pattern Search
python scripts/validate.py <db.s2db> --pattern "*any_keyword*"
```

### Database Locked Error

- Stelle sicher dass Serial2 Tool die DB nicht öffnet
- Verwende Read-Only Mode (später)

## 📞 Support & Contribution

**Issues?**
- Siehe `/docs/ARCHITECTURE.md` für Technical Design
- Siehe `/docs/FILTERS.md` für Filter-Erweiterung
- Siehe `/docs/SERIAL2.md` für API Details

**Beitragen?**
1. Feature Branch erstellen
2. Code ändern + Tests
3. Pull Request öffnen

## 📄 Lizenz

UDC Validation Framework - Internal Use Only

---

**Version:** 0.1.0  
**Status:** Beta  
**Letztes Update:** 2026-09-30
