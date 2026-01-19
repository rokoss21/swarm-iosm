# Runbook: Continuous Dispatch Operations

Manual operations guide for Swarm-IOSM orchestration.

Use this when you want full control over the dispatch loop instead of `/swarm-iosm implement`.

---

## When to Use Manual Mode

- Learning how the system works
- Debugging dispatch issues
- Fine-grained control over task execution
- Custom gate evaluation

---

## The Continuous Dispatch Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    DISPATCH LOOP                            │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Collect  │ → │ Classify │ → │ Dispatch │              │
│  │  Ready   │    │  Mode    │    │  Batch   │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       ↑                               │                     │
│       │         ┌──────────┐          ↓                     │
│       └─────────│  Gate    │←── Monitor + Spawn             │
│                 │  Check   │                                │
│                 └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Manual Dispatch

### Step 1: Initialize State

Create `iosm_state.md` from template:

```bash
cp templates/iosm_state.md swarm/tracks/<track-id>/iosm_state.md
```

### Step 2: Generate Dispatch Plan

```bash
python scripts/orchestration_planner.py swarm/tracks/<track-id>/plan.md --continuous
```

This creates `continuous_dispatch_plan.md` with:
- Task registry (all tasks with metadata)
- Initial ready set (tasks with no dependencies)
- Lock conflict matrix

### Step 3: Identify Ready Tasks

From `continuous_dispatch_plan.md`, find the **Initial Ready Set**:

```markdown
## Initial Ready Set

Tasks ready at start (no dependencies):

- **T01**: Explore codebase (background)
- **T02**: Design API contracts (foreground)
```

### Step 4: Classify Execution Mode

| Condition | Mode |
|-----------|------|
| `needs_user_input: true` | Foreground |
| `effort: S` (small) | Foreground |
| `concurrency_class: write-shared` | Foreground |
| Otherwise | Background |

### Step 5: Dispatch Batch

**Critical: Launch ALL ready tasks in a SINGLE message.**

Example dispatch message to Claude:

```
Launch these tasks in parallel:

**T01 (Background):**
- Role: Explorer
- Goal: Analyze codebase architecture
- Touches: read-only
- Output: reports/T01.md

**T03 (Background):**
- Role: Implementer-A  
- Goal: Implement auth middleware
- Touches: backend/auth.py, tests/test_auth.py
- Output: reports/T03.md

**T02 (Foreground):**
- Role: Architect
- Goal: Design API contracts
- Touches: docs/api_spec.yaml
- Output: reports/T02.md

Use Task tool with run_in_background=true for T01 and T03.
Execute T02 in foreground (needs user input).
```

### Step 6: Monitor Running Tasks

Check background task output:

```
/tasks
```

Read task output files or use `TaskOutput` tool.

### Step 7: Process Completed Tasks

When a task completes:

1. **Read the report** (`reports/T##.md`)
2. **Extract SpawnCandidates** — new tasks discovered
3. **Release locks** — update `iosm_state.md`
4. **Recalculate ready queue** — deps now satisfied

### Step 8: Auto-Spawn from Discoveries

If report contains SpawnCandidates:

```markdown
## SpawnCandidates

| ID | Subtask | Touches | Effort | User Input | Severity |
|----|---------|---------|--------|------------|----------|
| SC-01 | Fix type errors | `auth.py` | S | false | medium |
```

For `severity != critical` and `user_input == false`:
- Add to backlog automatically
- Assign T-AUTO-## ID

For `severity == critical`:
- **STOP loop immediately**
- Alert user

### Step 9: Check Gate Progress

After each batch, evaluate gates:

```markdown
## Gate Progress

| Gate | Target | Current | Status |
|------|--------|---------|--------|
| Gate-I | ≥0.75 | 0.68 | gap |
| Gate-M | pass | pass | pass |
| Gate-O | tests pass | 3 failing | gap |
```

### Step 10: Continue or Stop

**Continue if:**
- Ready queue not empty
- Gates not met
- Spawn budget remaining

**Stop if:**
- All gates met
- All tasks need user input
- Critical SpawnCandidate found
- Spawn budget exhausted (20 max)
- Loop stuck (3 iterations without progress)

---

## Lock Management

### Lock Rules

```
File lock:    backend/auth.py         — blocks this file only
Folder lock:  backend/core/           — blocks all files inside
```

### Conflict Detection

Tasks with overlapping `touches` must run sequentially:

```markdown
## Lock Plan

- `backend/core/__init__.py`: T03, T04 — **sequential only**
```

### Updating iosm_state.md

After task completes:

```markdown
### Touches Lock Manager

Currently locked paths:
```
backend/auth.py      — locked by T04 (running)
backend/api/         — locked by T05 (running)
```
```

---

## Golden Rules for Background Subagents

1. **Never guess** — if ambiguous, create Escalation Request
2. **Stay in scope** — only touch files in your `Touches` list
3. **Report everything** — SpawnCandidates, blockers, decisions
4. **Stop at safe points** — don't commit incomplete work
5. **No MCP tools** — they may fail in background mode

---

## State File Updates

After each batch completion, update `iosm_state.md`:

```markdown
## Batch History

| Batch | Timestamp | Tasks | Status | Duration |
|-------|-----------|-------|--------|----------|
| B-001 | 14:30 | T01, T02 | done | 45m |
| B-002 | 15:20 | T03, T04, T05 | running | - |
```

---

## Common Operations

### Resuming After Interruption

1. Read `iosm_state.md` to find current state
2. Check `reports/` for completed tasks
3. Recalculate ready queue
4. Continue dispatch loop

### Handling Escalations

When subagent reports Escalation Request:

```markdown
## Escalation Requests

### E-01: TTL Strategy Choice
**Question:** Should cache TTL be fixed (5min) or configurable?
**Options:**
1. Fixed 5min — simpler
2. Configurable — more flexible
**Recommendation:** Configurable
```

Respond in foreground, then re-queue task or spawn follow-up.

### Force-Stopping the Loop

If loop is stuck:

1. Check `loops_without_progress` in `iosm_state.md`
2. If ≥3, stop and diagnose
3. Generate interim `iosm_report.md`
4. List blocking questions for user

---

## Metrics to Watch

| Metric | Warning | Critical |
|--------|---------|----------|
| loops_without_progress | ≥2 | ≥3 |
| total_loop_iterations | ≥30 | ≥50 |
| spawn_budget_remaining | ≤5 | 0 |
| blocked_user queue | ≥3 tasks | ≥5 tasks |

---

## See Also

- [QUICKSTART.md](./QUICKSTART.md) — 5-minute intro
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) — Common issues
- [templates/iosm_state.md](./templates/iosm_state.md) — State file template
- [templates/subagent_brief.md](./templates/subagent_brief.md) — Task brief template
