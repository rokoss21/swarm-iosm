# Quick Start

Get Swarm-IOSM running in 5 minutes.

---

## Try Without Claude (Demo Track)

Test the orchestration planner locally before using Claude Code:

```bash
# 1. Clone the repo
git clone https://github.com/rokoss21/swarm-iosm.git
cd swarm-iosm

# 2. Copy demo track to workspace
mkdir -p swarm/tracks
cp -r examples/demo-track swarm/tracks/demo

# 3. Validate the plan
python scripts/orchestration_planner.py swarm/tracks/demo/plan.md --validate

# 4. Generate continuous dispatch plan
python scripts/orchestration_planner.py swarm/tracks/demo/plan.md --continuous

# 5. Open the generated plan
cat swarm/tracks/demo/continuous_dispatch_plan.md
```

You should see task registry, initial ready set, and lock conflict matrix.

---

## Installation

```bash
# Project-level (recommended)
git clone https://github.com/rokoss21/swarm-iosm.git .claude/skills/swarm-iosm

# Or user-level (all projects)
git clone https://github.com/rokoss21/swarm-iosm.git ~/.claude/skills/swarm-iosm
```

Verify: type `/swarm-iosm` in Claude Code.

---

## Two Operating Modes

| Mode | How it works | Best for |
|------|--------------|----------|
| **Auto** | `/swarm-iosm implement` runs the full loop | Most users |
| **Manual** | You dispatch tasks via `iosm_state.md` | Learning, debugging |

Choose **Auto** mode for your first track.

---

## Happy Path (Auto Mode)

### Step 1: Create Track

```
/swarm-iosm new-track "Add user authentication with JWT"
```

Claude asks questions → generates PRD → creates `plan.md`.

### Step 2: Verify Plan

Check the generated plan has required fields:

```markdown
- [ ] **T01**: Design auth API
  - **Owner role:** Architect
  - **Depends on:** None
  - **Touches:** `docs/auth.md`, `api/contracts/auth.yaml`
  - **Concurrency class:** write-local
  - **Needs user input:** true
  - **Effort:** M
  - **Acceptance:** API contract approved
```

### Step 3: Implement

```
/swarm-iosm implement
```

Claude launches parallel subagents, monitors progress, auto-spawns from discoveries.

### Step 4: Monitor

Watch these files:
- `swarm/tracks/<id>/iosm_state.md` — live progress (**Auto-generated, do not edit**)
- `swarm/tracks/<id>/reports/` — subagent reports

### Step 5: Integrate

```
/swarm-iosm integrate <track-id>
```

Claude merges work, runs IOSM quality gates, generates `iosm_report.md`.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/swarm-iosm setup` | Initialize project context |
| `/swarm-iosm new-track "<desc>"` | Create new feature track |
| `/swarm-iosm implement` | Execute plan (Auto mode) |
| `/swarm-iosm status` | Check progress |
| `/swarm-iosm watch` | Live monitoring (v1.3) |
| `/swarm-iosm simulate` | Dry-run implementation (v1.3) |
| `/swarm-iosm resume` | Resume after crash (v1.3) |
| `/swarm-iosm retry <task-id>` | Retry failed task (v1.2) |
| `/swarm-iosm integrate <id>` | Merge and run gates |

---

## Cost Tracking (v1.2)

Swarm-IOSM automatically estimates and tracks API costs.

**Check current spend:**
View `swarm/tracks/<id>/iosm_state.md`:

```markdown
## Cost Tracking
- budget_total: $10.00
- spent_so_far: $2.45
- remaining: $7.55
```

**Model Selection:**
- **Haiku:** Read-only tasks (cheap)
- **Sonnet:** Most coding tasks (balanced)
- **Opus:** Architecture/Security (high quality)

**Budget Alerts:**
- You get a warning at 80% usage.
- Execution pauses at 100% usage.

---

## Handling Errors (v1.2)

When a task fails, Swarm-IOSM provides intelligent error diagnosis:

### View errors
```bash
/swarm-iosm status
```

Output shows:
```
❌ T04: Permission Denied
   File: backend/migrations/001.sql
   Fix: GRANT CREATE ON DATABASE app TO user;
   Retry: /swarm-iosm retry T04 --foreground
```

### Retry a failed task
```bash
# Standard retry
/swarm-iosm retry T04

# Force foreground (interactive)
/swarm-iosm retry T04 --foreground

# Regenerate brief
/swarm-iosm retry T04 --reset-brief
```

### Error recovery process

1. **Identify** — `/swarm-iosm status` shows all errors
2. **Diagnose** — Error includes type, file, reason, fixes
3. **Fix** — Apply suggested fix or fix manually
4. **Retry** — Use retry command with appropriate flags

### Example: Fixing import error
```bash
# Error shows: ModuleNotFoundError: No module named 'pyswisseph'
/swarm-iosm status
# Output suggests: pip install pyswisseph

# Install the module
pip install pyswisseph

# Retry the task
/swarm-iosm retry T05
```

### Max retries

Each task can be retried up to **3 times**. After 3 failures, task is marked as `PERMANENTLY_FAILED` and requires manual intervention.

---

## Key Files

```
swarm/tracks/<track-id>/
├── plan.md                      # Task definitions
├── continuous_dispatch_plan.md  # Generated execution plan
├── iosm_state.md                # Live state (queues, locks, gates)
├── reports/                     # Subagent reports (T01.md, T02.md...)
├── integration_report.md        # Final merge report
└── iosm_report.md               # Quality gate results
```

---

## Next Steps

- **Manual mode?** See [RUNBOOK.md](./RUNBOOK.md) for Continuous Dispatch operations
- **Problems?** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Deep dive?** See [SKILL.md](./SKILL.md) for full specification
