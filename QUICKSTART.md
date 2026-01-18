# Swarm Workflow - Quick Start Guide

Get started with Swarm in 5 minutes.

---

## Happy Path (v1.1.1) — 6 Steps

**For users who want to start NOW:**

```
Step 1: /swarm new-track "Add user authentication"
        → Answer intake questions
        → Get track ID (e.g., 2026-01-17-001)

Step 2: Edit swarm/tracks/<id>/plan.md
        → Ensure each task has:
          - Touches: `file1.py, folder/`
          - Concurrency class: read-only | write-local | write-shared
          - Needs user input: true | false

Step 3: Validate plan
        $ python .claude/skills/swarm-iosm/scripts/orchestration_planner.py \
            swarm/tracks/<id>/plan.md --validate

Step 4: Generate continuous dispatch plan
        $ python .claude/skills/swarm-iosm/scripts/orchestration_planner.py \
            swarm/tracks/<id>/plan.md --continuous
        → Creates: continuous_dispatch_plan.md, iosm_state.md

Step 5: Run Dispatch Loop
        → Open iosm_state.md — see Ready Queue
        → Dispatch all ready tasks in SINGLE message (Task tool)
        → Monitor with /bashes
        → On completion: read reports, update iosm_state, dispatch next

Step 6: Check gates
        → When all tasks done, check Gate Targets in iosm_state.md
        → If all pass → /swarm integrate <track-id>
        → If gaps → auto-spawn remediation tasks
```

**Key files to watch:**
- `iosm_state.md` — live state, queues, gates, spawn budget
- `reports/Txx.md` — subagent outputs, SpawnCandidates
- `continuous_dispatch_plan.md` — task registry, lock plan

---

## Installation

Already installed! This Skill is located at:
```
.claude/skills/swarm-iosm/
```

Claude Code will automatically discover it.

## First Track (3 Steps)

### Step 1: Initialize (first time only)

```
/swarm setup
```

This creates the `swarm/` directory structure.

### Step 2: Create a Track

```
/swarm new-track "Add user authentication with JWT"
```

Claude will:
1. Ask questions about requirements
2. Generate PRD
3. Create implementation plan
4. Give you a track ID (e.g., `2026-01-17-001`)

### Step 3: Implement

```
/swarm implement
```

Claude will:
1. Launch subagents (parallel when possible)
2. Each subagent produces a report
3. Collect reports when done

## Check Progress

```
/swarm status
```

Shows:
- Task completion (TODO/DOING/DONE/BLOCKED)
- Available reports
- Blockers

## Integration

After all tasks complete:

```
/swarm integrate <track-id>
```

Generates:
- `integration_report.md` (merge plan)
- `iosm_report.md` (quality gates)

## Example Session

```
You: I need to add email notifications to the app

Claude: I'll use the Swarm workflow for this. Let me start by creating a track.
        /swarm new-track "Add email notification system"

        [Questions appear - answer them]

        ✅ Track created: 2026-01-17-001
        ✅ PRD generated
        ✅ Plan created with 8 tasks

        Ready to implement?

You: Yes, go ahead

Claude: /swarm implement

        Launching subagents:
        - T01 (Architect): Email template design [foreground]
        - T02 (Implementer-A): Email service implementation [background]
        - T03 (Implementer-B): API endpoints [background]

        [Wait for completion]

        ✅ All tasks complete. Ready for integration.

You: /swarm integrate 2026-01-17-001

Claude: [Analyzes reports, creates integration plan, runs IOSM gates]

        ✅ Integration complete
        ✅ IOSM-Index: 0.92 (Excellent)
        ✅ Ready for deployment

        Reports saved:
        - swarm/tracks/2026-01-17-001/integration_report.md
        - swarm/tracks/2026-01-17-001/iosm_report.md
```

## Commands Cheat Sheet

| Command | Purpose |
|---------|---------|
| `/swarm setup` | Initialize Swarm in project (first time) |
| `/swarm new-track "<desc>"` | Create new feature track |
| `/swarm implement [track-id]` | Execute implementation plan |
| `/swarm status [track-id]` | Check progress |
| `/swarm integrate <track-id>` | Merge work, run quality gates |
| `/swarm revert-plan <track-id>` | Generate rollback guide |

## Key Concepts

### Track
A "track" is one feature or task. Each track has:
- PRD (requirements)
- Plan (tasks with dependencies)
- Reports (what each subagent did)
- Integration report (merge plan)

### Subagents
Specialized agents that execute tasks:
- **Explorer** - Analyze codebase
- **Architect** - Design decisions
- **Implementer** - Write code
- **TestRunner** - Run tests
- **SecurityAuditor** - Security review

### IOSM Gates
Quality checks before production:
- **Gate-I (Improve)** - Code clarity
- **Gate-O (Optimize)** - Performance
- **Gate-S (Shrink)** - Minimal surface
- **Gate-M (Modularize)** - Clean boundaries

**Target:** IOSM-Index ≥ 0.80

## File Structure

After running `/swarm setup` and creating a track:

```
swarm/
├── context/
│   ├── product.md          # Product description
│   ├── tech-stack.md       # Tech stack
│   └── workflow.md         # Development workflow
├── tracks/
│   └── 2026-01-17-001/     # Your track
│       ├── intake.md       # Requirements
│       ├── PRD.md          # Product requirements
│       ├── spec.md         # Technical spec
│       ├── plan.md         # Implementation plan
│       ├── reports/        # Subagent reports
│       │   ├── T01.md
│       │   └── T02.md
│       ├── integration_report.md
│       └── iosm_report.md
└── tracks.md               # Index of all tracks
```

## Tips

1. **Answer questions upfront** - Background subagents can't ask questions
2. **Use Plan mode for existing code** - Start with read-only exploration
3. **Parallelize wisely** - Different files = parallel, same file = sequential
4. **Check IOSM gates** - Aim for ≥0.80 before production

## Next Steps

- Read full documentation: [README.md](README.md)
- Explore templates: [templates/](templates/)
- Check example workflows: [README.md](README.md#examples)

## Troubleshooting

**Skill not activating?**
- Try explicit command: `/swarm new-track "..."`

**Background task stuck?**
- Check status: `/bashes`
- Resume: Use Task tool with task ID

**Need help?**
- Read detailed docs: [README.md](README.md)
- Check templates for examples

---

## Release Notes v1.1.1

### What's New: Continuous Dispatch Loop

**v1.1.1** переходит от статичных "waves" к **continuous scheduling**:

| v1.0 (Waves) | v1.1.1 (Continuous) |
|--------------|---------------------|
| Ждём конца волны | Dispatch сразу при READY |
| Статичный план | Динамический граф задач |
| Ручной spawn | Auto-spawn из SpawnCandidates |
| Волновые checkpoints | Gate-driven continuation |

### Key Features

1. **Continuous Orchestration Loop**
   - CollectReady → Classify → ConflictCheck → DispatchBatch → Monitor → AutoSpawn → GateCheck
   - Максимум параллелизма при соблюдении lock constraints

2. **Touches Lock Manager**
   - Иерархия: папка vs файл
   - Concurrency classes: read-only, write-local, write-shared
   - scratch_dir для read-only артефактов

3. **SpawnCandidates Protocol**
   - Субагенты создают SpawnCandidates в отчётах
   - Dedup по ключу `<file>|<intent>`
   - Auto-spawn для safe candidates

4. **Spawn Protection**
   - Budget per gate (default: 20 total)
   - Severity threshold (critical > high > medium > low)
   - Anti-loop: max 3 iterations without progress

5. **Gate-Driven Continuation**
   - Loop до достижения Gate-I, Gate-M, Gate-O, Gate-S targets
   - iosm_state.md для live трекинга

6. **Touched Actual Tracking**
   - Субагенты репортят фактически изменённые файлы
   - Alert при расхождении с планом

---

## Operational Runbook: Continuous Dispatch

### Before Starting

```bash
# 1. Validate plan has required v1.1 fields
python .claude/skills/swarm-iosm/scripts/orchestration_planner.py \
    swarm/tracks/<id>/plan.md --validate

# 2. Generate continuous dispatch plan
python .claude/skills/swarm-iosm/scripts/orchestration_planner.py \
    swarm/tracks/<id>/plan.md --continuous
```

This creates:
- `continuous_dispatch_plan.md` — task registry, lock plan, initial ready set
- `iosm_state.md` — live state tracking (if not exists)

### During Execution

**Orchestrator Loop:**

```
1. Open iosm_state.md
2. Check Ready Queue — dispatch all in SINGLE message
3. Run /bashes to monitor background tasks
4. On task completion:
   a. Read reports/<TXX>.md
   b. Check Touches Actual vs Planned (alert if different)
   c. Parse SpawnCandidates → auto-spawn eligible
   d. Update iosm_state.md (queues, locks, gates)
5. Check Stop Conditions:
   - All gates met? → EXIT with iosm_report.md
   - Spawn budget exhausted? → STOP, ask user
   - loops_without_progress >= 3? → STOP, analyze
6. If not stopped → GOTO 2
```

### Reading iosm_state.md

**Key sections to check:**

```markdown
## Spawn Budget
spawn_budget_remaining: 13  ← если 0, спросить user

## Anti-Loop Metrics
loops_without_progress: 2   ← если >=3, проблема

## Current Loop State
Ready Queue: [T05, T06]     ← dispatch эти
Running: [T04]              ← мониторить
Blocked (user): [T07]       ← нужен вопрос

## Gate Targets
Gate-I: ≥0.75 (current: 0.68) ❌  ← gap, нужен auto-spawn
Gate-O: tests pass (current: 3 failing) ❌
```

### Handling Common Situations

**1. Task blocked on user input**

```
Blocked (user): T07 — waiting for: "Fix code or fix test?"
```

→ Use AskUserQuestion, get answer, update brief, re-dispatch

**2. Touches conflict**

```
Blocked (conflict): T08 — waiting for T04 to release core/calculator.py
```

→ Wait for T04 to complete, then T08 auto-moves to Ready

**3. SpawnCandidates with severity=critical**

```
| SC-03 | SQL injection in db.py | M | true | critical | db.py|security |
```

→ STOP loop immediately, alert user, do NOT auto-spawn

**4. Unplanned touches detected**

```
### Unplanned Touches (if any)
- `backend/config.py` - Had to update config format
  - Risk: medium
```

→ Update touches_lock, check for conflicts with running tasks

**5. Gate gap detected**

```
Gate-I: ≥0.75 (current: 0.68) ❌
```

→ Auto-spawn remediation tasks (if budget > 0):
- "Improve naming in calculator.py"
- "Reduce duplication in api/"

### Batch Size Guidelines

| Scenario | Recommended Batch Size |
|----------|----------------------|
| All background, no conflicts | 4-6 |
| Mixed BG/FG | 3-4 |
| Many write-shared | 1-2 |
| Critical path tasks | 2-3 (prioritize) |

### Stop Condition Checklist

Before exiting loop, verify:

- [ ] All gates met (or exceptions documented)
- [ ] No critical SpawnCandidates pending
- [ ] No blocked_user tasks remaining
- [ ] iosm_report.md generated
- [ ] integration_report.md complete

### Emergency: Loop Stuck

If `loops_without_progress >= 3`:

1. Check Running tasks — are they actually making progress?
2. Check Blocked (conflict) — is there a deadlock?
3. Check SpawnCandidates — are we spawning but not completing?
4. Manual intervention: resume stuck task in foreground

```bash
# Check background task output
tail -n 100 <task_output_file>

# Resume in foreground if needed
# Use Task tool with resume parameter
```

---

**Ready to swarm? Start with:**

```
/swarm setup
/swarm new-track "Your feature"
```

Then follow the Continuous Dispatch Runbook above.

---

## Golden Rules (Operating Manifest)

**Background Agent Protocol:**
- Background → NO guessing, only Escalation Request
- If ambiguous → STOP, create Escalation Request, wait for resolution

**File Management:**
- `Touches Planned` (from brief) → MANDATORY
- `Touches Actual` (in report) → MANDATORY
- Unplanned touches → SpawnCandidate with severity≥high

**Lock Management:**
- Folder lock > File lock (folder blocks all inside)
- read-only tasks → no lock needed
- write-local → parallel if no touch overlap
- write-shared → sequential only

**Batch Constraints:**
- Max batch size: 3-6 tasks per dispatch
- Priority: critical_path > high_severity > read-only_fillers

**Gate-Driven Continuation:**
- Loop continues until Gate targets met
- Gate fail → spawn budget temporarily increased
- Auto-spawn triggers: Gate-I gap → clarity tasks, Gate-O gap → test fixes
