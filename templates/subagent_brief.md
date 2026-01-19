# Subagent Brief: Task [Task-ID] — [Task Title]

**Track:** [track-id]
**Task ID:** [T##]
**Role:** [Explorer / Architect / Implementer / TestRunner / etc]
**Created:** [YYYY-MM-DD]
**Mode:** [Foreground / Background]

---

## Goal

[Clear, one-sentence statement of what this task must achieve]

**Success looks like:** [Concrete outcome description]

---

## Scope

### In Scope
- [Specific capability/module/file to work on]
- [Specific requirement to implement]
- [Specific analysis to perform]

### Out of Scope (do NOT touch)
- [Files/modules that should not be modified]
- [Features/changes that are NOT part of this task]
- [Changes that conflict with other parallel tasks]

---

## Context

### Background
[Brief context: why this task exists, how it fits in the overall feature]

### Dependencies
**This task depends on:**
- [Task ID]: [What was delivered by that task]
- [Task ID]: [What was delivered by that task]

**Tasks depending on this:**
- [Task ID]: [What they need from you]

### Related Files/Modules
[Key files and modules relevant to this task - helps subagent navigate codebase]

**Primary files:**
- `path/to/file1.py` - [brief description]
- `path/to/file2.py` - [brief description]

**Related files:**
- `path/to/related.py` - [why it matters]

**Test files:**
- `tests/path/to/test_file.py` - [where to add tests]

---

## Constraints

### Technical Constraints
- [e.g., "Must use existing authentication system, do not create new auth"]
- [e.g., "Keep API backward compatible - no breaking changes"]
- [e.g., "Must work with Python 3.9+"]

### Non-Technical Constraints
- [e.g., "No external dependencies without approval"]
- [e.g., "Code style: follow Black formatter"]
- [e.g., "All changes must have tests (coverage ≥80%)"]

### Performance Constraints
- [e.g., "Response time must be <200ms P95"]
- [e.g., "Memory usage must not exceed X MB"]

### Security Constraints
- [e.g., "No PII in logs"]
- [e.g., "All inputs must be validated"]
- [e.g., "Use parameterized queries (no SQL injection)"]

---

## Output Contract

You MUST deliver the following artifacts:

### 1. Code/Implementation (if applicable)
- [List specific files to create/modify]
- [Expected functions/classes/endpoints]

### 2. Tests (if applicable)
- Unit tests with ≥[X]% coverage
- Integration tests for [specific scenarios]
- Test data/fixtures if needed

### 3. Report (MANDATORY)
**Save to:** `swarm/tracks/[track-id]/reports/[Task-ID].md`

**Report must include:**
- Summary (what_done)
- Decisions made (with rationale)
- Files touched (complete list)
- Verification steps (how you tested)
- Risks / edge cases identified
- Blockers / open questions
- Handoff notes to integrator

**Use this template:** [templates/subagent_report.md](../templates/subagent_report.md)

### 4. Error Reporting (MANDATORY if errors occur)

**Critical:** If you encounter ANY error during execution, you MUST document it in your report.

**Error reporting requirements:**
1. Use "Errors Encountered" section in report template
2. Include: error type, file, command, exact error message, root cause
3. Document attempted fixes (what you tried)
4. Mark resolution status (resolved vs. unresolved)
5. Suggest prevention strategy for future tasks

**Do NOT:**
- ❌ Silently ignore errors
- ❌ Skip error details ("it didn't work")
- ❌ Assume orchestrator knows what went wrong

**Format:** Use structured format (E-01, E-02, etc.) from template

**Why this matters:** Orchestrator uses error information to:
- Generate actionable fixes for user
- Decide retry strategy (foreground vs background)
- Prevent same error in future tasks
- Track common failure patterns

**If no errors:** Write "No errors encountered" in the section.

### 5. Additional Artifacts (if applicable)
- [e.g., "ADR document: docs/ADR-XXX.md"]
- [e.g., "API spec: api/openapi.yaml"]
- [e.g., "Performance report: perf_results.json"]

---

## Verification Steps

After completing implementation, you MUST run these verification steps:

### Step 1: [e.g., "Run unit tests"]
```bash
pytest tests/unit/test_[module].py -v
```
**Expected result:** [e.g., "All tests pass"]

### Step 2: [e.g., "Run integration tests"]
```bash
pytest tests/integration/test_[feature].py -v
```
**Expected result:** [e.g., "All tests pass"]

### Step 3: [e.g., "Check code style"]
```bash
black --check path/to/files/
flake8 path/to/files/
```
**Expected result:** [e.g., "No style violations"]

### Step 4: [e.g., "Manual smoke test"]
[Description of manual verification if needed]
**Expected result:** [What should happen]

---

## Acceptance Criteria

This task is complete when:

- [ ] [Specific functional requirement met, e.g., "API endpoint returns correct response"]
- [ ] [Specific test requirement met, e.g., "Unit test coverage ≥80%"]
- [ ] [Specific quality requirement met, e.g., "No security vulnerabilities"]
- [ ] [Report saved to required location with all sections]
- [ ] [All verification steps pass]

---

## Questions & Clarifications

**IMPORTANT:** If running in **background mode**, you CANNOT ask questions during execution.
All questions MUST be resolved NOW before starting.

### Pre-resolved Questions
**Q:** [Anticipated question 1]
**A:** [Answer/clarification]

**Q:** [Anticipated question 2]
**A:** [Answer/clarification]

### Open Questions (for foreground mode only)
- [Question that may need user input during execution]

---

## Background Mode Constraints

**If this task runs in BACKGROUND:**

⚠️ **You CANNOT use:**
- `AskUserQuestion` (will auto-deny or fail)
- Interactive permissions requests (will auto-deny)
- MCP tools (may be unavailable in background - known limitation)

✅ **You CAN use:**
- All standard tools (Read, Write, Edit, Bash, Grep, Glob, Task)
- Pre-approved bash commands (if listed in this brief)
- Autonomous decision-making (document rationale in report)

**Critical:** All questions MUST be answered in "Pre-resolved Questions" section above.

**If you encounter an unresolved question:**
1. Document in report: "BLOCKER: <question>"
2. Make best-effort decision (document rationale)
3. Mark task as NEEDS_REVIEW in report
4. Continue with remaining work (don't halt completely)

---

## Lock Discipline (v1.1)

**CRITICAL:** You MUST NOT touch files outside your `Touches` list.

### Your Touches (files you may modify)
```
[List of files/folders from brief]
```

### Lock Rules
1. **Only modify files in your Touches list** — other files may be locked by parallel tasks
2. **Read any file** — reading is always allowed
3. **If you need to modify an unlisted file:**
   - Document in SpawnCandidates (not in this task)
   - Do NOT edit it directly
4. **If another task's output conflicts with yours:**
   - Document conflict in report
   - Suggest resolution strategy
   - Let orchestrator decide

### Violation Consequences
- Modifying unlisted files may cause merge conflicts
- Orchestrator may need to revert your changes
- Your task may be marked PARTIAL or BLOCKED

---

## SpawnCandidates Protocol (v1.1 — MANDATORY)

During your work, you WILL discover new issues, improvements, or subtasks. You MUST document them in your report using this format:

### When to Create SpawnCandidates

Create a SpawnCandidate when you find:
- Missing tests for code you touched
- Type errors in related files
- Dead code or unused imports
- Missing documentation
- Inconsistent API patterns
- Performance issues (but can't fix now)
- Security concerns (outside your scope)
- Refactoring opportunities

### SpawnCandidates Format (in your report)

```markdown
## SpawnCandidates

| ID | Subtask | Touches | Effort | User Input | Severity | Accept Criteria |
|----|---------|---------|--------|------------|----------|-----------------|
| SC-01 | [Brief description] | `file1.py`, `file2.py` | S/M/L | true/false | low/medium/high/critical | [How to verify done] |
```

### Field Guidelines

- **ID:** Sequential SC-01, SC-02, etc.
- **Subtask:** Imperative form ("Fix X", "Add Y", "Remove Z")
- **Touches:** Files that subtask would modify (for lock planning)
- **Effort:** S (<1h), M (1-4h), L (4-12h)
- **User Input:**
  - `false` if clear how to fix (auto-spawn eligible)
  - `true` if needs decision (e.g., "fix code vs fix test")
- **Severity:**
  - `low` — nice to have, won't block
  - `medium` — should fix, but not urgent
  - `high` — important for quality gates
  - `critical` — STOP and escalate to user immediately
- **Accept Criteria:** Measurable verification (e.g., "mypy passes", "test coverage ≥80%")

### Example SpawnCandidates

```markdown
## SpawnCandidates

| ID | Subtask | Touches | Effort | User Input | Severity | Accept Criteria |
|----|---------|---------|--------|------------|----------|-----------------|
| SC-01 | Add type annotations to calculator.py | `core/calculator.py` | S | false | medium | mypy passes with no errors |
| SC-02 | Fix failing test_natal_aspects.py | `tests/test_natal.py` | M | true | high | User decides: fix test or fix code |
| SC-03 | Remove dead import in auth.py | `backend/auth.py` | S | false | low | No unused imports warning |
| SC-04 | CRITICAL: SQL injection in query builder | `core/db.py` | M | true | critical | Parameterized queries only |
```

### What Orchestrator Does With SpawnCandidates

1. **severity=critical** → STOP loop, alert user immediately
2. **user_input=false, severity≠critical** → Auto-spawn as new task
3. **user_input=true** → Add to blocked_user queue, ask user later
4. Tasks added to backlog, scheduled per dependency rules

---

## When to Request Foreground Escalation (v1.1)

Even in background mode, you may encounter situations requiring user input. Document these as **Escalation Requests** in your report:

### Escalate When

1. **Ambiguous requirement** — spec doesn't say what to do
2. **Breaking change** — your fix would break existing API
3. **Test vs Code conflict** — unclear which is "correct"
4. **Security decision** — needs human judgment
5. **Scope creep** — task is much bigger than estimated
6. **Critical SpawnCandidate** — found urgent issue

### Escalation Format (in report)

```markdown
## Escalation Requests

### E-01: [Brief title]
**Context:** [What you were doing when this came up]
**Question:** [Specific question for user]
**Options:**
1. [Option A] — [consequence]
2. [Option B] — [consequence]
**Recommendation:** [Your suggestion]
**Impact if Deferred:** [What happens if we don't decide now]
```

### Orchestrator Response

- Orchestrator will resume task in foreground to resolve
- Or provide answer and re-queue task
- Or defer to integration phase

---

## IOSM Quality Checks

This task must pass these IOSM gates:

### Gate-I (Improve)
- [ ] Clear naming (no abbreviations unless domain-standard)
- [ ] No magic numbers (use named constants)
- [ ] No code duplication
- [ ] Invariants documented (preconditions/postconditions)

### Gate-O (Optimize)
- [ ] Performance measured (if applicable)
- [ ] No obvious inefficiencies (N+1 queries, etc)
- [ ] Resource usage acceptable

### Gate-S (Shrink)
- [ ] Minimal API surface (only expose what's needed)
- [ ] No unnecessary dependencies added
- [ ] Code is concise (no over-engineering)

### Gate-M (Modularize)
- [ ] Clear module boundaries
- [ ] Well-defined contracts/interfaces
- [ ] Low coupling, high cohesion
- [ ] Changes localized (minimal blast radius)

---

## Resources

### Documentation
- [Link to relevant docs]
- [Link to design decisions (ADRs)]

### Examples
- [Link to similar code in codebase]
- [Link to reference implementation]

### Tools
- [Commands/scripts that might help]
- [Testing utilities]

---

## Timeline

**Estimated effort:** [X-Y hours]
**Deadline (if any):** [YYYY-MM-DD]
**Priority:** [High / Medium / Low]

---

## Notes

[Any additional context, warnings, or tips for the subagent]

---

**Remember:**
1. Save report to `swarm/tracks/[track-id]/reports/[Task-ID].md`
2. Follow the output contract exactly
3. Run all verification steps before marking complete
4. If blocked, document in report (don't silently fail)
5. If in background mode, all questions must be pre-answered
