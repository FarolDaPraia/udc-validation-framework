# Claude Model Selection Guide

## Overview

Optimize token costs by selecting the right Claude model for each task type.

```
Haiku 4.5    (Fast & Cheap)    ← Simple tasks, fast turnaround
     ↓
Sonnet 5     (Balanced)         ← Standard feature work
     ↓
Opus 5       (Powerful)         ← Complex architecture, hard problems
```

---

## Model Characteristics

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **Haiku 4.5** | ⚡⚡⚡ Fast | 💰 Cheapest | Simple tasks, testing |
| **Sonnet 5** | ⚡⚡ Medium | 💰💰 Balanced | Feature dev, most work |
| **Opus 5** | ⚡ Slower | 💰💰💰 Most | Complex problems, architecture |

---

## Task Matrix: Model Selection

### USE HAIKU 4.5 (Cost-Optimized)

**Ideal for:**
- ✅ Unit tests writing
- ✅ Simple bug fixes
- ✅ Code formatting/linting
- ✅ Documentation updates
- ✅ Template creation
- ✅ Simple refactoring
- ✅ Config file creation
- ✅ Boilerplate code

**Examples:**
```
- Write unit test for existing function
- Fix typo in docstring
- Create .gitignore
- Format code style
- Write README section
```

**Token estimate:** 10-50K tokens
**Cost savings:** ~80% vs Opus

---

### USE SONNET 5 (Standard - Most Tasks)

**Ideal for:**
- ✅ Feature implementation
- ✅ Code review
- ✅ Bug diagnosis
- ✅ API design
- ✅ Performance optimization
- ✅ Testing strategy
- ✅ Documentation design
- ✅ Module refactoring
- ✅ Most daily development work

**Examples:**
```
- Implement user story (like US-1)
- Design API for new feature
- Review pull request
- Optimize function performance
- Debug complex issue
- Plan module architecture
```

**Token estimate:** 50-200K tokens
**Cost savings:** ~50% vs Opus

---

### USE OPUS 5 (Complex Problems)

**Ideal for:**
- ✅ System architecture design
- ✅ Hard problem solving
- ✅ Multi-file refactoring
- ✅ Framework design
- ✅ Complex debugging
- ✅ Algorithm design
- ✅ Major tech decisions
- ✅ Cross-module impact analysis

**Examples:**
```
- Design entire Test Validation Framework
- Solve complex performance issue
- Redesign core architecture
- Plan multi-feature initiative
- Evaluate major trade-offs
- Complex state machine design
```

**Token estimate:** 100-400K tokens
**Use rarely:** Only when necessary

---

## By Development Phase

### PHASE 1: INTAKE (PO Work)
**Model:** Haiku 4.5 or Sonnet 5
- Break down features: **Haiku** (templates)
- Create user stories: **Haiku** (structured)
- Define acceptance criteria: **Haiku** (clear)

### PHASE 2: REVIEW (Senior Dev)
**Model:** Sonnet 5
- Technical feasibility review: **Sonnet**
- Architecture validation: **Sonnet** (or **Opus** if complex)
- Risk assessment: **Sonnet**

### PHASE 3: IMPLEMENTATION (Dev)
**Model:** Haiku 4.5 or Sonnet 5
- Write unit tests: **Haiku** (boilerplate)
- Implement feature: **Sonnet** (main work)
- Simple refactoring: **Haiku**
- Performance optimization: **Sonnet**

### PHASE 4: CODE REVIEW (Senior Dev)
**Model:** Sonnet 5
- Review code: **Sonnet**
- Check tests: **Sonnet**
- Validate acceptance criteria: **Sonnet**

### PHASE 5: MERGE (PO)
**Model:** Haiku 4.5
- Merge & clean up: **Haiku**
- Create release notes: **Haiku**
- Update docs: **Haiku**

---

## User Stories: Model per Task

### Example: Test Validation Module

| US # | Task | Model | Reason |
|------|------|-------|--------|
| US-1 | Implement Manager | Sonnet | Core feature logic |
| US-1 | Write tests (16) | Haiku | Boilerplate tests |
| US-1 | Code review | Sonnet | Validate design |
| US-2 | Implement Validator | Sonnet | State machine (complex) |
| US-2 | Write tests | Haiku | Standard unit tests |
| US-3 | Implement Adapter | Sonnet | Integration logic |
| US-4 | Implement Reporter | Haiku | Data formatting |
| US-5 | Implement CLI | Sonnet | Command design |

**Total tokens estimate:**
- Haiku: 100K (tests, simple code)
- Sonnet: 300K (features, complex logic)
- **Opus: 0K** (not needed for this feature)

**Total cost:** ~40% of Opus-only approach

---

## Decision Framework

### Ask Yourself:

1. **Is this straightforward/templated?**
   - YES → **Haiku 4.5**
   - NO → Continue

2. **Does this require deep reasoning/design?**
   - YES → **Opus 5**
   - NO → Continue

3. **Is this standard feature work?**
   - YES → **Sonnet 5**
   - NO → Opus

### Decision Tree:

```
Task
├─ Simple/Boilerplate? → HAIKU
├─ Complex/Architecture? → OPUS
└─ Standard Feature Work? → SONNET
```

---

## Implementation Rules

### In Development Pipeline:

**When requesting Claude:**
1. Always specify the model in the prompt/task
2. Document model choice in commit message (optional)
3. Use Haiku by default unless reason for higher model

**Pattern:**
```
Task: Implement feature X
Model: Sonnet 5 (feature implementation)
Reason: Core business logic, needs careful design

Task: Write 10 unit tests
Model: Haiku 4.5 (boilerplate tests)
Reason: Standard test structure, no complex logic

Task: Debug production issue
Model: Sonnet 5 (complex debugging)
Reason: Need full reasoning capability
```

---

## Cost Tracking

### Token Budget per Feature:

**Test Validation Module (5 US, 15 story points):**
- Haiku 4.5: 100K tokens = ~$0.15
- Sonnet 5: 300K tokens = ~$1.50
- **Total: ~$1.65**

**Same feature with Opus-only:**
- Opus 5: 500K tokens = ~$15.00
- **Cost difference: 9x more expensive**

### Savings Strategies:

1. **Use Haiku for tests** → 50% token savings
2. **Use Sonnet for features** → 70% vs Opus
3. **Use Opus only for hard problems** → Save for when needed
4. **Prefer focused prompts** → Fewer tokens needed

---

## When to Use Each Model

### HAIKU 4.5 - When Confident

✅ Use if:
- Task is well-defined
- Solution is standard/templated
- Limited reasoning needed
- Fast feedback is valuable
- Cost is important

❌ Don't use if:
- Complex design decisions needed
- Ambiguous requirements
- Need comprehensive analysis
- High-stakes decision

### SONNET 5 - Default Choice

✅ Use if:
- Standard feature development
- Code review & feedback
- API/module design
- Moderate complexity
- Good balance needed

❌ Don't use if:
- Very simple task (use Haiku)
- Very complex problem (use Opus)

### OPUS 5 - When Necessary

✅ Use if:
- Complex architecture
- Hard problem-solving needed
- Multi-file impact analysis
- Novel solution needed
- High-stakes decision

❌ Don't use if:
- Simple boilerplate work
- Standard feature implementation
- Clear solution exists

---

## Examples from This Project

### ✅ Good Model Choices

```
Task: Write TestCaseManager unit tests (16 tests)
Model: Haiku 4.5 ✓
Reason: Standard pytest pattern, boilerplate structure

Task: Implement TestCaseManager class (300 lines)
Model: Sonnet 5 ✓
Reason: Feature implementation, logic design needed

Task: Create Test Validation specification
Model: Opus 5 ✓
Reason: Architecture design, complex requirements
```

### ❌ Bad Model Choices

```
Task: Format Python code
Model: Opus 5 ✗ (Too expensive - use Haiku)

Task: Write boilerplate configuration
Model: Sonnet 5 ✗ (Overkill - use Haiku)

Task: Write a simple log parser
Model: Haiku 4.5 ✗ (Too simple - use Sonnet)
```

---

## Integration with Development Pipeline

### In GitHub Issues:

Add model recommendation to User Story:

```markdown
## User Story: Test Case Manager

### Model Selection
- Implementation: **Sonnet 5** (feature development)
- Tests: **Haiku 4.5** (boilerplate tests)
- Review: **Sonnet 5** (code review)

### Estimated Tokens
- Implementation: 100K (Sonnet)
- Tests: 20K (Haiku)
- Total: ~$1.20
```

### In Commits:

```
WIP: US-1 Test Case Manager

Model: Sonnet 5 (feature), Haiku 4.5 (tests)
Tokens used: ~120K
Cost: ~$1.20
```

---

## Monitoring & Optimization

### Track per Feature:

- Tokens used per model
- Cost per story point
- Model choices that worked well
- Areas for improvement

### Quarterly Review:

- Average tokens per feature
- Cost trends
- Model mix (% Haiku vs Sonnet vs Opus)
- Optimization opportunities

---

## Q&A

**Q: Should I always use Haiku?**
A: No. Haiku is cheap but slower and less capable. Use Sonnet for most work.

**Q: Is Opus ever worth it?**
A: Yes. For hard problems, complex architecture, major decisions. ~5-10% of tasks.

**Q: How do I know if task needs Opus?**
A: If you're unsure or it's complex → use Sonnet. If you're stuck → upgrade to Opus.

**Q: Can I switch models mid-task?**
A: Yes. Start with Haiku/Sonnet, if stuck → escalate to Sonnet/Opus.

---

**Version:** 1.0  
**Status:** Active Policy  
**Last Updated:** 2026-09-30

---

## Reference Pricing (Approximate)

```
Haiku 4.5:   $0.80 per 1M input  | $4 per 1M output
Sonnet 5:    $3 per 1M input     | $15 per 1M output
Opus 5:      $15 per 1M input    | $75 per 1M output

Example: 100K input tokens
Haiku:   ~$0.08
Sonnet:  ~$0.30
Opus:    ~$1.50
```
