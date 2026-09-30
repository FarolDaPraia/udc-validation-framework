# UDC Development Pipeline

## Overview

Hybrid Development Pipeline mit klaren Rollen, Workflows und Automatisierung für Features von Spezifikation bis Production.

```
FEATURE REQUEST
    ↓
┌─────────────────────────────────────────┐
│ PHASE 1: INTAKE (Architect/PO)          │
│ ├─ Review Spezifikation                 │
│ ├─ Zerlege in User Stories              │
│ ├─ Erstelle Acceptance Criteria         │
│ └─ Create GitHub Issues                 │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ PHASE 2: ASYNC REVIEW                   │
│ ├─ Senior Dev: Review User Stories      │
│ ├─ Dev: Feasibility Check               │
│ └─ GitHub Comments + Feedback           │
└────────────┬────────────────────────────┘
             ↓
      ┌──────────────┐
      │ Complex?     │
      │ Need Sync?   │
      └──┬─────────┬─┘
         │ NO      │ YES
         ↓         ↓
      READY   ┌─────────────────┐
      START   │ SYNC MEETING    │
              │ (30 min max)    │
              │ ├─ Architect    │
              │ ├─ Senior Dev   │
              │ └─ Dev          │
              └────────┬────────┘
                       ↓
┌─────────────────────────────────────────┐
│ PHASE 3: IMPLEMENTATION (Dev)           │
│ ├─ Create feature branch                │
│ ├─ Develop                              │
│ ├─ Unit Tests                           │
│ └─ Push to GitHub                       │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ PHASE 4: REVIEW (Senior Dev)            │
│ ├─ Code Review                          │
│ ├─ Test Review                          │
│ ├─ Acceptance Criteria Check            │
│ └─ Approve or Request Changes           │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ PHASE 5: MERGE & RELEASE (PO)           │
│ ├─ Merge to master                      │
│ ├─ Create Release Note                  │
│ └─ Tag version                          │
└─────────────────────────────────────────┘
```

---

## 1. Rollen & Verantwortungen

### Architect/PO (Product Owner)
**Verantwortung:**
- Feature Specifications reviewen
- In User Stories zerlegen
- Acceptance Criteria definieren
- GitHub Issues erstellen & managen
- Prioritäten setzen
- Final Approval vor Merge

**Zeit-Commitment:** 2-4h pro Feature

**Decisioner:** Anforderungen, Scope, Akzeptanz

---

### Senior Dev (Technical Lead)
**Verantwortung:**
- User Stories auf technische Machbarkeit reviewen
- Architecture & Design vorschlagen
- Code Review durchführen
- Testing Strategy reviewen
- Technische Risks identifizieren
- Junior Dev mentoring

**Zeit-Commitment:** 1-2h pro Feature

**Decisioner:** Technische Umsetzung, Quality Standards

---

### Dev (Developer)
**Verantwortung:**
- User Stories implementieren
- Unit Tests schreiben
- Code Quality checken
- Testing durchführen
- Feedback einarbeiten
- Dokumentation aktualisieren

**Zeit-Commitment:** 4-8h pro Feature

**Decisioner:** Implementation Details, Trade-offs

---

## 2. Phasen & Workflows

### PHASE 1: INTAKE (Architect/PO)

**Trigger:** Feature Spezifikation (z.B. aus Anforderungen, Tickets, etc.)

**Tasks:**

1. **Specification Review**
   - [ ] Lese Spezifikation komplett
   - [ ] Identifiziere Scope
   - [ ] Kläre unklare Punkte

2. **Breakdown zu User Stories**
   - [ ] Zerlege Feature in 3-5 User Stories
   - [ ] Jede Story = 1-2 Tage Dev-Arbeit
   - [ ] Stories sind unabhängig (wo möglich)

3. **Create GitHub Issues**
   - [ ] Ein Issue pro User Story
   - [ ] Verwende Template: USER_STORY_TEMPLATE.md
   - [ ] Labels: `type:user-story`, `status:intake`
   - [ ] Assign: Senior Dev + Dev
   - [ ] Link zur Original-Spezifikation

**Output:** 3-5 GitHub Issues mit User Stories + Acceptance Criteria

**Duration:** 1-2h

**Beispiel User Story:**
```markdown
## User Story: Real-Time Log Streaming

### Description
As a Test Framework User
I want to stream logs in real-time from Serial2
So that I can validate test cases during execution

### Acceptance Criteria
- [ ] LogStreamReader reads .s2db in real-time
- [ ] Supports polling interval 10-1000ms
- [ ] Generator-based streaming (memory efficient)
- [ ] Callback system for event handling
- [ ] <100ms latency for new logs
- [ ] Unit tests with >80% coverage

### Technical Details
- SQLite WAL monitoring
- Non-blocking I/O
- Statistics tracking

### DoD (Definition of Done)
- [ ] Code reviewed by Senior Dev
- [ ] Unit tests pass
- [ ] Acceptance criteria met
- [ ] Documentation updated
```

---

### PHASE 2: ASYNC REVIEW

**Trigger:** GitHub Issues created

**Timeline:** 24-48h response time

**Participants:** Senior Dev + Dev (parallel review)

#### Senior Dev Review

**Checklist:**
- [ ] Technical feasibility
- [ ] Architecture makes sense
- [ ] No obvious gaps
- [ ] Resource estimates reasonable
- [ ] Dependencies clear

**Actions:**
- Add comments to GitHub Issue
- Suggest changes (if any)
- Approve or Request Review Meeting

**Output:** GitHub Comments with feedback

---

#### Dev Feasibility Check

**Checklist:**
- [ ] Understand requirements
- [ ] Identify potential blockers
- [ ] Estimate effort (story points)
- [ ] Technology choices known

**Actions:**
- Add comments to GitHub Issue
- Flag uncertainties
- Suggest improvements

**Output:** GitHub Comments + effort estimate

---

### Decision: Need Sync Meeting?

**SYNC Meeting if:**
- ✓ Complex architectural decisions
- ✓ Multiple technical approaches
- ✓ Cross-module impacts
- ✓ Disagreement between Senior Dev & Dev

**NO Sync Meeting if:**
- ✓ Clear consensus in comments
- ✓ Senior Dev approved as-is
- ✓ Straightforward implementation
- ✓ All feedback incorporated

**Approval Path:**
```
Senior Dev: "Looks good, approved ✓"
    +
Dev: "Ready to start"
    ↓
→ Move to PHASE 3: IMPLEMENTATION
```

---

### PHASE 2b: SYNC REVIEW MEETING (if needed)

**Duration:** 30 minutes max

**Participants:**
- Architect/PO
- Senior Dev
- Dev

**Agenda:**
1. Clarify requirements (5 min)
2. Technical approach discussion (15 min)
3. Resolve disagreements (5 min)
4. Final decision (5 min)

**Output:**
- Documented decision in GitHub Issue
- Updated User Story (if changed)
- Ready for Implementation

**Action:** Move issue to `status:ready`

---

### PHASE 3: IMPLEMENTATION (Dev)

**Trigger:** Issue status = `ready`

**Process:**

1. **Branch erstellen**
   ```bash
   git checkout -b feature/udc-streaming
   ```
   Format: `feature/<user-story-id>` oder `feature/<short-desc>`

2. **Implement**
   - Folge Code Style (see CODING_STANDARDS.md)
   - Write Unit Tests as you go
   - Commit messages: `WIP: User Story #123 - Short description`

3. **Testing**
   - Unit tests: >80% coverage
   - Manual testing: Follow test cases
   - Edge cases: Consider error scenarios

4. **Push & Create PR**
   ```bash
   git push origin feature/udc-streaming
   # Create Pull Request on GitHub
   # Link to Issue: "Closes #123"
   ```

**PR Template:**
```markdown
## Description
Closes #123

## Changes
- Implemented LogStreamReader
- Added PreFilter
- Unit tests for streaming

## Testing
- [ ] Unit tests pass
- [ ] Manual test passed
- [ ] Coverage >80%

## Checklist
- [ ] Code follows style guide
- [ ] No console logs
- [ ] Documentation updated
- [ ] Tests added/updated
```

**Duration:** 4-8h (depending on story)

---

### PHASE 4: CODE REVIEW (Senior Dev)

**Trigger:** Pull Request created

**Timeline:** 24h review time (SLA)

**Checklist:**

- **Functionality**
  - [ ] Implements user story correctly
  - [ ] All acceptance criteria met
  - [ ] No obvious bugs

- **Code Quality**
  - [ ] Follows project style guide
  - [ ] No code duplication
  - [ ] Reasonable complexity
  - [ ] Error handling present

- **Testing**
  - [ ] Unit tests present
  - [ ] Coverage >80%
  - [ ] Edge cases tested
  - [ ] No skipped tests

- **Documentation**
  - [ ] Code comments where needed
  - [ ] README updated (if applicable)
  - [ ] Docstrings present

**Review Actions:**

```
Approve:        "Looks good! ✓"
                → Can merge

Request Changes: "Please fix: ..."
                → Dev makes changes, push new commits

Comment:        "Consider: ..." (suggestions, not blocking)
                → Dev can address or explain
```

**Output:** 
- GitHub Review Approval or "Changes Requested"
- Detailed comments
- Suggestions for improvement

---

### PHASE 5: MERGE & RELEASE (Architect/PO)

**Trigger:** Senior Dev approved PR

**Timeline:** Same day (merge ASAP)

**Process:**

1. **Verify**
   - [ ] All CI checks pass
   - [ ] Senior Dev approved
   - [ ] No merge conflicts

2. **Merge**
   - [ ] Squash & merge (single commit)
   - [ ] Commit message: `Merge pull request #PR_ID: User Story #ISSUE_ID - Description`
   - [ ] Delete feature branch

3. **Update Issue**
   - [ ] Close GitHub Issue
   - [ ] Add label: `status:done`
   - [ ] Document completion date

4. **Release Notes (if applicable)**
   - [ ] Add to CHANGELOG.md
   - [ ] Tag version (semantic versioning)
   - [ ] Create GitHub Release

**Example Release Note:**
```markdown
## v0.3.0 - Real-Time Streaming

### Features
- LogStreamReader: Real-time log streaming from Serial2
- PreFilter: Ultra-fast filtering (99% drop rate, 1-5 μs/entry)
- Callback system for event handling

### Improvements
- Memory-efficient generator-based streaming
- Statistics tracking for performance monitoring

### Fixes
- Fixed polling interval handling

### Migration
No breaking changes. Backward compatible with v0.2.x

### Contributors
- Senior Dev (Review)
- Dev (Implementation)
```

---

## 3. GitHub Labels & Status

### Status Labels
- `status:intake` - In Intake Phase (PO review)
- `status:review` - Under Review (Senior Dev)
- `status:ready` - Ready to implement
- `status:in-progress` - Dev is working on it
- `status:review-pr` - PR created, waiting Senior Dev review
- `status:done` - Merged and complete

### Type Labels
- `type:user-story` - User Story
- `type:bug` - Bug fix
- `type:enhancement` - Enhancement
- `type:docs` - Documentation
- `type:test` - Testing

### Priority Labels
- `priority:critical` - Block everything else
- `priority:high` - Do next sprint
- `priority:medium` - Normal
- `priority:low` - Nice to have

### Component Labels
- `component:streaming` - Streaming module
- `component:test-cases` - Test validation
- `component:backend-api` - Backend integration
- `component:cli` - CLI tools

---

## 4. SLA & Timelines

| Phase | Owner | Duration | SLA |
|-------|-------|----------|-----|
| Intake | PO | 1-2h | 24h |
| Async Review | Senior Dev | 1-2h | 24-48h |
| Sync Meeting | Team | 30min | 24h (if needed) |
| Implementation | Dev | 4-8h | 3 days |
| Code Review | Senior Dev | 1h | 24h |
| Merge | PO | 15min | Same day |

---

## 5. File Templates

### USER_STORY_TEMPLATE.md
```markdown
## User Story: [Title]

### Description
As a [role]
I want to [feature]
So that [benefit]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Technical Details
- [Implementation hints]
- [Architecture notes]

### Definition of Done
- [ ] Code reviewed
- [ ] Tests added
- [ ] Docs updated
```

### FEATURE_TEMPLATE.md
```markdown
## Feature: [Title]

### Problem Statement
[What problem does this solve?]

### Proposed Solution
[High-level solution]

### Scope
- In scope: [Features included]
- Out of scope: [Future work]

### Technical Approach
[Architecture, design decisions]

### User Stories
1. Story 1
2. Story 2
3. Story 3

### Acceptance Criteria
- [ ] All user stories complete
- [ ] No critical bugs
- [ ] Documentation updated
- [ ] Performance acceptable

### Timeline
- Intake: 1-2h
- Implementation: 2-3 days
- Review: 1 day
- Total: 3-4 days
```

---

## 6. Communication & Escalation

### Daily Standup (optional, if team present)
- "What did I do?"
- "What will I do?"
- "Any blockers?"

### Weekly Sync (optional)
- Review progress
- Prioritize next features
- Discuss blockers

### Escalation Path
```
Dev blocked?
  → Comment on Issue
  → Tag Senior Dev
  → Response within 4h

Senior Dev blocked?
  → Comment on Issue
  → Tag Architect/PO
  → Response within 4h

Need immediate help?
  → Slack/Direct message
  → Async fallback: GitHub
```

---

## 7. Metrics & Monitoring

### Track per Feature:
- Time in Intake
- Time in Review
- Time in Implementation
- Time in Code Review
- Total cycle time

### Quality Metrics:
- Test coverage (target: >80%)
- Code review comments per PR
- Rework rate (% requiring changes)
- Bug escape rate

### Team Metrics:
- Velocity (stories per sprint)
- Lead time (spec → merged)
- Deployment frequency

---

## 8. Continuous Improvement

### Weekly Retrospective
- What went well?
- What could improve?
- Action items for next features

### Process Evolution
- Adjust SLAs based on data
- Improve templates based on feedback
- Automate repetitive tasks

---

## 9. Example: End-to-End Flow

```
Day 1 (PO - 2h)
  Create Feature: "Real-Time Streaming"
  ↓
  Intake: Review Spec
  ↓
  Create 3 User Stories:
  - LogStreamReader
  - PreFilter
  - Integration Tests
  ↓
  Create GitHub Issues (#101, #102, #103)

Day 2 (Senior Dev + Dev - 2h async review)
  Senior Dev Review:
    "Architecture looks good, approved ✓"
  Dev Feasibility:
    "3-4 days total, all doable"
  ↓
  Status: ready

Day 2 (Dev - 6h implementation)
  feature/udc-streaming branch
  Implement LogStreamReader
  Add unit tests
  Create PR #10

Day 3 (Senior Dev - 1h review)
  Code Review: 3 comments
  "Looks good, approved ✓"

Day 3 (PO - 15min merge)
  Merge PR #10
  Close Issue #101
  Update CHANGELOG.md

Day 4 (Dev - continue with Issue #102)
  ...repeat for next story...

Timeline:
Spec → Merged: 3 days
Intake: 0.5 days
Review: 1 day
Implementation: 1.5 days
Code Review: 0.5 days
```

---

## 10. Tools & Automation

### GitHub Setup
- [x] Issue templates (USER_STORY_TEMPLATE.md)
- [x] PR template (see section 3)
- [x] Branch protection rules
- [x] Automated status labels (GitHub Actions)
- [ ] Auto-assign reviewers

### GitHub Actions (TODO)
- [ ] Auto-label issues
- [ ] Check PR against Acceptance Criteria
- [ ] Run tests on PR
- [ ] Notify on SLA breach

---

**Version:** 1.0.0  
**Status:** Specification Complete  
**Last Updated:** 2026-09-30
