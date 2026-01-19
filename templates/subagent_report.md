# Subagent Report: Task [Task-ID] — [Task Title]

**Track:** [track-id]
**Task ID:** [T##]
**Role:** [Explorer / Architect / Implementer / TestRunner / etc]
**Completed:** [YYYY-MM-DD HH:MM]
**Status:** ✅ Complete | ⚠️ Partial | ❌ Blocked
**Effort:** [Actual hours spent]

---

## Summary (What Was Done)

[2-3 paragraph summary of what was accomplished]

**Key deliverables:**
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

**Acceptance criteria status:**
- [✅ / ❌] [Criterion 1]
- [✅ / ❌] [Criterion 2]
- [✅ / ❌] [Criterion 3]

---

## Decisions Made

Document all significant decisions with rationale:

### Decision 1: [Decision title, e.g., "Use Redis for caching"]

**Context:** [Why this decision was needed]

**Options considered:**
1. **Option A (chosen):** [Description]
   - Pros: [List]
   - Cons: [List]
2. **Option B:** [Description]
   - Pros: [List]
   - Cons: [List]

**Decision:** [What was chosen and why]

**Consequences:** [Impact of this decision, any future considerations]

**ADR:** [Link to ADR if created, or "None"]

---

### Decision 2: [Another decision]

[Same structure as above]

---

## Files Touched

Complete list of all files created, modified, or deleted:

### Touches Planned (from brief)
```
[Copy from brief - what you WERE ALLOWED to touch]
```

### Touches Actual (observed) — v1.1.1 CRITICAL
```
[List ALL files you ACTUALLY touched, even if not in plan]
```

**Lock Manager Alert:** If Touches Actual ≠ Touches Planned, orchestrator must update locks!

### Created
- `path/to/new_file1.py` - [Brief description of what this file does]
- `path/to/new_file2.py` - [Brief description]

### Modified
- `path/to/existing_file1.py` - [What changed and why]
  - Lines changed: [Approximate line count or range]
  - Key changes: [Bullet points of major changes]
- `path/to/existing_file2.py` - [What changed and why]
  - Lines changed: [Approximate line count or range]
  - Key changes: [Bullet points of major changes]

### Deleted
- `path/to/old_file.py` - [Why it was deleted]

### Unplanned Touches (if any)
Files touched that were NOT in the original brief:
- `path/to/unexpected.py` - [Why it was necessary]
  - **Risk:** [low/medium/high] — may conflict with other tasks
  - **Resolution:** [Created SpawnCandidate / Orchestrator should check]

### Total impact
- Files created: [N]
- Files modified: [N]
- Files deleted: [N]
- Unplanned touches: [N] ← **Alert if > 0**
- Total lines changed: [~N] (approximate)

---

## Implementation Details

[Optional section for complex implementations - explain architecture, algorithms, patterns used]

### Architecture
[Diagram or description of how components fit together]

### Key components
**[Component name]:**
- Purpose: [What it does]
- Interfaces: [How it's used]
- Dependencies: [What it depends on]

**[Another component]:**
- Purpose: [What it does]
- Interfaces: [How it's used]
- Dependencies: [What it depends on]

### Algorithms/Patterns
[Explain any non-trivial algorithms or design patterns used]

---

## Verification

All verification steps from the brief, with results:

### ✅ Verification Step 1: [e.g., "Unit tests"]
```bash
pytest tests/unit/test_module.py -v
```
**Result:** ✅ All 15 tests passed
**Coverage:** 87% (target: 80%)

### ✅ Verification Step 2: [e.g., "Integration tests"]
```bash
pytest tests/integration/test_feature.py -v
```
**Result:** ✅ All 8 tests passed

### ✅ Verification Step 3: [e.g., "Code style"]
```bash
black --check src/
flake8 src/
```
**Result:** ✅ No style violations

### ⚠️ Verification Step 4: [e.g., "Performance test"]
```bash
python tests/perf/benchmark.py
```
**Result:** ⚠️ P95 latency: 215ms (target: 200ms)
**Note:** Slightly above target, but acceptable for MVP. Recommend optimization in next iteration.

---

## Shared Context Updates (v2.0)

**Did you discover patterns or make decisions that others need to know?**

### Patterns Discovered
- [Pattern Name]: [Description]

### Decisions Made (affecting others)
- [Decision]: [Description]

### Questions for other agents
- Q: [Question]

---

## Errors Encountered

**If you encountered ANY errors during execution, document them here using this format:**

### E-01: [Error Type]

**File:** `path/to/file` (if applicable)
**Command/Operation:** [What you were doing when error occurred]
**Error message:**
```
[Paste exact error message here]
```

**Root cause:** [Your analysis of why this happened]

**Attempted fixes:** [What you tried to resolve it]

**Resolution:** [How it was resolved, or UNRESOLVED if still blocked]

**Suggested prevention:** [How to prevent this in future tasks]

---

**Example:**

### E-01: Permission Denied

**File:** `backend/migrations/001_create_users.sql`
**Command/Operation:** Running database migration via `python manage.py migrate`
**Error message:**
```
psycopg2.errors.InsufficientPrivilege: permission denied for schema public
```

**Root cause:** Database user 'app_user' lacks CREATE TABLE permission on schema 'public'

**Attempted fixes:**
1. Checked user permissions with `\du` in psql
2. Attempted to run with sudo (failed - wrong approach)

**Resolution:** UNRESOLVED - needs admin to grant permissions

**Suggested prevention:** Pre-check required database permissions in brief or setup script

---

**If no errors occurred, write:** "No errors encountered"

---

## IOSM Quality Gate Results

### Gate-I (Improve) ✅
- [✅] Clear naming: All functions/variables use descriptive names
- [✅] No magic numbers: Constants defined in `config.py`
- [✅] No duplication: DRY principle followed
- [✅] Invariants documented: Docstrings include preconditions/postconditions
- **Score:** 1.0 / 1.0

### Gate-O (Optimize) ⚠️
- [✅] Performance measured: Benchmarks run and documented
- [⚠️] P95 latency: 215ms (target: 200ms) - needs attention
- [✅] No N+1 queries: Used eager loading
- [✅] Memory usage: <50MB (acceptable)
- **Score:** 0.85 / 1.0

### Gate-S (Shrink) ✅
- [✅] Minimal API: Only 3 public methods exposed
- [✅] No new dependencies: Used existing libraries
- [✅] Concise code: No over-engineering
- **Score:** 1.0 / 1.0

### Gate-M (Modularize) ✅
- [✅] Clear boundaries: Module has single responsibility
- [✅] Well-defined contract: Interface documented
- [✅] Low coupling: Only depends on 2 other modules
- [✅] High cohesion: All functions relate to core purpose
- **Score:** 1.0 / 1.0

**Overall IOSM Score for this task:** 0.96 / 1.0 (Excellent)

---

## Risks & Edge Cases

Document risks identified and how they're mitigated:

### Risk 1: [e.g., "Race condition in concurrent requests"]
- **Description:** [Explain the risk]
- **Likelihood:** [High / Medium / Low]
- **Impact:** [High / Medium / Low]
- **Mitigation:** [What was done to address it]
- **Residual risk:** [Any remaining risk]

### Risk 2: [Another risk]
[Same structure]

### Edge Cases Handled
- [Edge case 1 and how it's handled]
- [Edge case 2 and how it's handled]

### Edge Cases NOT Handled (Known Limitations)
- [Edge case that's not handled, with justification]
- [Edge case deferred to future work]

---

## Blockers & Open Questions

### Blockers (Issues preventing completion)
- ❌ **[Blocker 1]:** [Description]
  - **Impact:** [What can't be done because of this]
  - **Needs:** [What's needed to unblock]
  - **Owner:** [Who should resolve this]

- ❌ **[Blocker 2]:** [Description]
  [Same structure]

### Open Questions (Need decisions)
- ❓ **[Question 1]:** [Description]
  - **Options:** [List possible answers]
  - **Impact:** [What depends on this decision]
  - **Recommended:** [Your suggestion]

- ❓ **[Question 2]:** [Description]
  [Same structure]

### Deferred Items (Intentionally not done)
- 🔜 **[Item 1]:** [What was deferred and why]
- 🔜 **[Item 2]:** [What was deferred and why]

---

## Handoff Notes to Integrator

Information the person integrating this work needs to know:

### Integration Instructions
1. [Step 1: e.g., "Merge this branch after T04 is integrated"]
2. [Step 2: e.g., "Run database migration script before deploying"]
3. [Step 3: e.g., "Update environment variable X in production"]

### Dependencies on Other Tasks
- **Depends on [Task ID]:** [What you need from them before integration]
- **Blocks [Task ID]:** [What they're waiting for from you]

### Conflicts/Overlaps with Other Tasks
- **May conflict with [Task ID]:** [Description of potential conflict and resolution strategy]

### Configuration Changes Needed
- Environment variable: `NEW_VAR=value` (add to `.env`)
- Config file: `config.yaml` - update section [X] with [Y]

### Deployment Notes
- [Special deployment considerations]
- [Rollback considerations]
- [Feature flag settings]

### Monitoring & Alerts
- **New metrics to track:** [Metric name and expected values]
- **New alerts to configure:** [Alert conditions]
- **Dashboard changes:** [What to add to monitoring dashboard]

---

## SpawnCandidates (v1.1.1 — MANDATORY)

**CRITICAL:** You MUST fill this section. If no discoveries, write "None identified."

During this task, the following new work items were identified:

| ID | Subtask | Touches | Effort | User Input | Severity | Dedup Key | Accept Criteria |
|----|---------|---------|--------|------------|----------|-----------|-----------------|
| SC-01 | [Description] | `path/to/file.py` | S/M/L | true/false | low/medium/high/critical | `file|intent` | [Verification] |
| SC-02 | [Description] | `path/to/file.py` | S/M/L | true/false | low/medium/high/critical | `file|intent` | [Verification] |

**Dedup Key Format:** `<primary_touch_filename>|<intent_category>`
- Examples: `auth.py|type-annot`, `natal.py|fix-test`, `api_spec|contract`
- Used by orchestrator to deduplicate across multiple worker reports

### SpawnCandidates Summary

- **Auto-spawn eligible (user_input=false, severity≠critical):** [N]
- **Needs user decision:** [N]
- **Critical (immediate escalation):** [N]

### Notes for Orchestrator

[Any context about SpawnCandidates that helps prioritization]

---

## Escalation Requests (v1.1)

Issues requiring user decision before proceeding:

### E-01: [Title, if any]
**Context:** [What you were doing]
**Question:** [What needs to be decided]
**Options:**
1. [Option A] — [consequence]
2. [Option B] — [consequence]
**Recommendation:** [Your suggestion]
**Impact if Deferred:** [What happens if we don't decide]

*(If no escalations needed, write "None")*

---

## Follow-up Tasks

Recommended next steps or improvements:

### High Priority (Should do soon)
- [ ] [Follow-up task 1, e.g., "Optimize query in module X to meet P95 target"]
- [ ] [Follow-up task 2]

### Medium Priority (Nice to have)
- [ ] [Improvement 1]
- [ ] [Improvement 2]

### Low Priority (Future consideration)
- [ ] [Enhancement 1]
- [ ] [Enhancement 2]

---

## Lessons Learned

Document insights for future tasks:

### What Went Well
- [Thing that worked well and should be repeated]
- [Another success]

### What Could Be Improved
- [Thing that could be done better next time]
- [Another area for improvement]

### Surprises / Unexpected Challenges
- [Unexpected issue encountered and how it was resolved]

---

## Artifacts & References

### Code Artifacts
- Main implementation: `path/to/code/`
- Tests: `path/to/tests/`
- Docs: `path/to/docs/`

### Documentation
- ADR: [Link or file path]
- API spec: [Link or file path]
- Diagrams: [Link or file path]

### External References
- [Link to library docs used]
- [Link to StackOverflow answer that helped]
- [Link to design inspiration]

---

## Appendix

[Optional: Add any supporting materials like code snippets, diagrams, test output, etc.]

### Test Output Example
```
[Paste relevant test output if helpful]
```

### Performance Metrics
```json
{
  "p50_latency_ms": 85,
  "p95_latency_ms": 215,
  "p99_latency_ms": 450,
  "throughput_rps": 1200,
  "memory_mb": 48
}
```

---

**Report completed by:** [Your role/name]
**Reviewed by:** [If applicable]
**Next step:** Integration by main agent (Task T12)
