# IOSM State — [Track ID]

**Created:** [YYYY-MM-DD HH:MM]
**Last Updated:** [YYYY-MM-DD HH:MM]
**Status:** INITIALIZING | IN_PROGRESS | GATES_MET | BLOCKED | COMPLETE
**Current Batch:** B-003

---

## Spawn Budget (v1.1.1)

| Metric | Value |
|--------|-------|
| spawn_budget_total | 20 |
| spawn_budget_used | 0 |
| spawn_budget_remaining | 20 |

**Per-Gate Budget:**
- Gate-I: 5 (used: 0)
- Gate-O: 8 (used: 0)
- Gate-M: 4 (used: 0)
- Gate-S: 3 (used: 0)

**Dedup Keys Seen:** (prevents duplicate spawns)
```
[empty]
```

---

## Anti-Loop Metrics (v1.1.1)

| Metric | Value | Limit |
|--------|-------|-------|
| loops_without_progress | 0 | 3 |
| total_loop_iterations | 0 | 50 |
| last_progress_timestamp | - | - |

**Progress = any task completion or gate improvement**

---

## Gate Targets (from plan.md)

| Gate | Target | Current | Delta | Status |
|------|--------|---------|-------|--------|
| Gate-I | ≥0.75 | - | - | pending |
| Gate-M | pass | - | - | pending |
| Gate-O | tests pass | - | - | pending |
| Gate-S | N/A | - | - | skip |

**Legend:**
- `pending` — Not yet evaluated
- `in_progress` — Being worked on
- `pass` — Target met ✅
- `gap` — Below target, auto-spawning remediation ❌
- `skip` — Not applicable for this track

---

## Current Loop State

### Task Queues

**Backlog:** [N tasks]
- T01: [title] (deps: none)
- T02: [title] (deps: T01)
- ...

**Ready Queue:** [N tasks]
- T03: [title] — ready to dispatch

**Running:** [N tasks]
- T04: [title] — background (started: HH:MM)
- T05: [title] — foreground (started: HH:MM)

**Blocked (user input):** [N tasks]
- T06: [title] — waiting for: [question]

**Blocked (conflict):** [N tasks]
- T07: [title] — waiting for: T04 to release `core/calculator.py`

**Done:** [N tasks]
- T01: [title] — completed: HH:MM

### Touches Lock Manager

Currently locked paths:
```
core/calculator.py      — locked by T04 (running)
backend/api/natal.py    — locked by T05 (running)
```

---

## Gate Progress Details

### Gate-I (Improve) — Current: [score] / Target: [target]

**Components:**
- I-1 Semantic Clarity: [score] / 1.0
- I-2 Code Duplication: [score] / 1.0
- I-3 Invariants Documented: [score] / 1.0
- I-4 TODOs Tracked: [score] / 1.0

**Gap Analysis:**
- [ ] [What's missing for Gate-I, e.g., "3 functions with unclear names"]
- [ ] [What's missing, e.g., "5% duplication in core/"]

**Auto-spawn Queue (Gate-I remediation):**
- T-AUTO-01: "Improve naming in calculator.py" (spawned: HH:MM)
- T-AUTO-02: "Extract common pattern in api/" (spawned: HH:MM)

---

### Gate-M (Modularize) — Current: [pass/fail] / Target: [pass]

**Components:**
- M-1 Module Contracts: [score] / 1.0
- M-2 Change Surface: [%] / ≤20%
- M-3 Coupling: [circular deps count]
- M-4 Cohesion: [score] / 1.0

**Gap Analysis:**
- [ ] [What's missing, e.g., "Circular dep: auth → core → auth"]

**Auto-spawn Queue (Gate-M remediation):**
- T-AUTO-03: "Break circular dependency in auth" (spawned: HH:MM)

---

### Gate-O (Optimize) — Current: [pass/fail] / Target: [pass]

**Components:**
- O-1 Latency: P50=[ms], P95=[ms], P99=[ms]
- O-2 Error Rate: [%]
- O-3 Tests: [passed]/[total] ([%])
- O-4 Chaos Tests: [passed]/[total]

**Gap Analysis:**
- [ ] [What's missing, e.g., "3 failing tests in test_natal.py"]
- [ ] [What's missing, e.g., "P95 latency 250ms > target 200ms"]

**Auto-spawn Queue (Gate-O remediation):**
- T-AUTO-04: "Fix 3 failing tests" (spawned: HH:MM)
- T-AUTO-05: "Optimize slow query in natal.py" (spawned: HH:MM)

---

### Gate-S (Shrink) — Current: [score] / Target: [target]

**Components:**
- S-1 API Surface: [count] endpoints
- S-2 Dependencies: [count] packages
- S-3 Onboarding: [minutes]

**Gap Analysis:**
- [ ] [What's missing, e.g., "2 unused endpoints to remove"]

**Auto-spawn Queue (Gate-S remediation):**
- T-AUTO-06: "Remove deprecated /api/legacy endpoint" (spawned: HH:MM)

---

## SpawnCandidates Inbox

New SpawnCandidates from completed tasks (pending triage):

| Source | ID | Subtask | Effort | User Input | Severity | Action |
|--------|----|---------| -------|------------|----------|--------|
| T04 | SC-01 | Fix type error in auth.py | S | false | medium | → auto-spawn |
| T04 | SC-02 | Clarify API contract | M | true | high | → blocked_user |
| T05 | SC-03 | CRITICAL: SQL injection | M | true | critical | ⚠️ STOP |

**Triage Rules:**
- `severity=critical` → STOP loop, alert user
- `user_input=false, severity≠critical` → auto-spawn immediately
- `user_input=true` → add to blocked_user queue

---

## Blocking Questions (needs user)

### Q1: [Question title]
**From task:** T06
**Question:** [Detailed question]
**Options:**
1. [Option A] — [consequence]
2. [Option B] — [consequence]
**Recommendation:** [Subagent's suggestion]
**Blocking:** [What can't proceed until resolved]

### Q2: [Question title]
...

---

## Batch History (v1.1.1)

| Batch ID | Timestamp | Tasks | Mode | Status | Duration |
|----------|-----------|-------|------|--------|----------|
| B-001 | HH:MM | T01, T02 | BG, BG | done | 45m |
| B-002 | HH:MM | T03 | FG | done | 20m |
| B-003 | HH:MM | T04, T05, T06 | BG, BG, BG | running | - |

**Batch Constraints:**
- max_batch_size: 6
- current_running: 3
- slots_available: 3

---

## Loop History

| Iteration | Timestamp | Tasks Dispatched | Tasks Completed | SpawnCandidates | Gate Status |
|-----------|-----------|------------------|-----------------|-----------------|-------------|
| 1 | HH:MM | T01, T02, T03 | T01 | 2 | I:0.45, M:-, O:-, S:- |
| 2 | HH:MM | T04, T05 | T02, T03 | 1 | I:0.58, M:pass, O:-, S:- |
| 3 | HH:MM | T-AUTO-01 | T04 | 0 | I:0.68, M:pass, O:fail, S:- |
| ... | ... | ... | ... | ... | ... |

---

## Next Actions

Based on current state, orchestrator will:

1. **Dispatch ready tasks:** [list]
2. **Wait for running tasks:** [list]
3. **Auto-spawn for gate gaps:** [list]
4. **Ask user about:** [list of blocking questions]

**Estimated iterations to gate targets:** [N] (based on current velocity)

---

## Stop Condition Check (v1.1.1)

| Condition | Status | Threshold |
|-----------|--------|-----------|
| All gates met | [yes/no] | - |
| All tasks = needs_user_input | [yes/no] | - |
| Critical SpawnCandidate found | [yes/no] | severity=critical |
| Scope creep detected | [yes/no] | spawn > 50% of original |
| Contradiction detected | [yes/no] | - |
| Spawn budget exhausted | [yes/no] | remaining = 0 |
| Max loops without progress | [yes/no] | ≥ 3 |
| Max total iterations | [yes/no] | ≥ 50 |

**Decision:** CONTINUE | STOP (reason: [reason])

**If STOP:**
- [ ] Alert user with reason
- [ ] Save partial progress
- [ ] Generate interim iosm_report.md
- [ ] List blocking questions for user

---

## Notes

[Any additional context, observations, or decisions made during orchestration]

---

**File auto-updated by orchestrator after each batch.**
