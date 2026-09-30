# UDC Validation Framework - Backlog

## Priority: HIGH (Aktuell in Progress)

### Phase 2: Real-Time Streaming ✅ (DONE)
- [x] LogStreamReader - Live .s2db streaming
- [x] PreFilter - Ultra-fast filtering (99% drop)
- [ ] RingBuffer Queue - Backpressure handling
- [ ] TestCaseValidator - Live Pass/Fail detection
- [ ] Multi-threaded Processor - Parallel processing

### Phase 3: Backend API Integration
- [ ] BackendAPIParser - REST API client
- [ ] Log comparison - Serial2 vs API
- [ ] Discrepancy detection
- [ ] Automated alerts

## Priority: MEDIUM (Backlog - Evaluate First)

### Batch Processing Mode ⏳
**Status:** PARKED - Evaluate if needed after Real-Time validation

**Requirement:**
- [ ] Batch Reader - Liest alle Logs (statisch), processed schnell, stoppt
- [ ] Export .json → Batch Processor
- [ ] Offline testing capability
- [ ] Historical log analysis

**Questions to Answer:**
- Brauchen wir Offline-Testing wirklich?
- Oder nur Live-Validation?
- Wie häufig Offline-Reports?

**Decision Gate:** Validiert Real-Time → Dann evaluieren

---

### Hybrid Mode (Real-Time + Batch)
**Status:** PARKED - Depends on Batch Mode decision

- [ ] Auto-detect: Real-Time vs Batch
- [ ] Mode switching
- [ ] Unified statistics

---

## Priority: LOW (Future)

### Advanced Features
- [ ] Web Dashboard (live metrics)
- [ ] CI/CD Integration (Jenkins/GitHub Actions)
- [ ] Docker containerization
- [ ] IPC Socket Connection zu Serial2.exe (sub-ms latency)
- [ ] Machine Learning anomaly detection
- [ ] Performance analytics

---

## Current Sprint

### What's Running:
1. ✅ LogStreamReader (Real-Time)
2. ✅ PreFilter (99% drop)
3. 🔄 Next: TestCaseValidator

### Next Steps:
1. Build TestCaseValidator (State Machine)
2. Test with Real Vehicle Data
3. Validate Real-Time Performance
4. **THEN:** Decide on Batch Mode

---

## Decision Log

### 2026-09-30
- **Decision:** Park Batch Mode as Backlog
- **Reason:** Validate Real-Time first, don't over-engineer
- **Owner:** FarolDaPraia
- **Review:** After TestCaseValidator is complete

---

## Notes

- Real-Time ist die Priorität
- Batch könnte auch mit Export → externe Tools gelöst werden
- Erst production-ready machen, dann erweitern
