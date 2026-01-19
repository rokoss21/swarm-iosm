# <img src="examples/logo.webp" width="48" height="48" align="center" alt="Swarm-IOSM Logo"> Swarm Workflow (IOSM) - Agent Skill

[![Version](https://img.shields.io/badge/version-2.1-blue.svg)](https://github.com/rokoss21/swarm-iosm)
[![Quality](https://img.shields.io/badge/IOSM-Ready-green.svg)](https://github.com/rokoss21/swarm-iosm)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://github.com/rokoss21/swarm-iosm)

A comprehensive Claude Code Skill for orchestrating complex development tasks using PRD-driven planning, parallel subagent execution, and IOSM quality gates.

## Quick Start

### Installation

This Skill is already installed in your project at `.claude/skills/swarm-iosm/`.

To use it in other projects:

```bash
# Copy to project-level skills
cp -r .claude/skills/swarm-iosm /path/to/other/project/.claude/skills/

# Or copy to personal skills (available in all projects)
cp -r .claude/skills/swarm-iosm ~/.claude/skills/
```

### First Use

1. **Initialize project context:**
   ```
   /swarm-iosm setup
   ```

2. **Create your first track:**
   ```
   /swarm-iosm new-track "Add user authentication"
   ```

3. **Implement the plan:**
   ```
   /swarm-iosm implement
   ```

4. **Check progress:**
   ```
   /swarm-iosm status
   ```

## What This Skill Does

Swarm Workflow automates the full lifecycle of complex development tasks:

1. **Requirements Gathering** - Structured intake using questions and user choices
2. **PRD Generation** - Creates comprehensive Product Requirements Document
3. **Task Decomposition** - Breaks work into parallel-executable tasks with dependencies
4. **Subagent Orchestration** - Launches specialized agents (Explorer, Architect, Implementer, etc.)
5. **Progress Tracking** - Monitors task completion and blockers
6. **Integration** - Merges work from all subagents with conflict resolution
7. **Quality Gates** - Enforces IOSM quality standards before deployment

## Key Features

### ✅ Structured Workflow
- Repeatable process for any complexity level
- Works for both greenfield (new) and brownfield (existing) projects
- All work tracked in standardized artifacts

### 🚀 Parallel Execution & Concurrency (v1.2)
- **Continuous Dispatch:** Launches tasks as soon as dependencies are met
- **Resource Limits:** Prevents OOM/Rate limits (Max 6 background tasks by default)
- **Lock Manager:** Automatically prevents file access conflicts
- **Speedup:** Achieves 2-5x acceleration vs sequential execution

### 💰 Cost Control & Model Optimization (v1.2)
- **Smart Model Selection:** Uses Haiku for read-only, Sonnet for code, Opus for security
- **Budget Tracking:** Stops execution if cost exceeds limit (default $10)
- **Cost Estimation:** Predicts track cost before execution

### 🛡️ Reliability & Resilience (v1.3)
- **Smart Retry:** Auto-retries transient failures (max 3 times)
- **Checkpointing:** Saves state after every step; resume after crash via `/swarm-iosm resume`
- **Error Diagnosis:** Translates cryptic errors into actionable fixes (e.g., "Run chmod +x")

### 📊 Observability & Simulation (v1.3)
- **Simulation Mode:** Dry-run execution with `/swarm-iosm simulate`
- **Live Dashboard:** Watch progress with `/swarm-iosm watch` (ASCII bars, Velocity, ETA)
- **Visualization:** Generate Mermaid dependency graphs

### 🤖 Automated State Management (v2.1)
- **Single Source of Truth:** `iosm_state.md` is now auto-generated from JSON checkpoints.
- **Sync via CLI:** Use `--update-task <TID> --status DONE` to keep everything in sync.
- **Accuracy:** Eliminates manual calculation errors in budget and progress tracking.

### 🧠 Advanced Intelligence (v2.0)
- **Anti-Pattern Detection:** Warns about monolithic tasks or low parallelism
- **Inter-Agent Communication:** Subagents share patterns via `shared_context.md`
- **Template Customization:** Override templates per project

### 📈 Quality Enforcement
- IOSM quality gates (Improve, Optimize, Shrink, Modularize)
- Automated scoring and acceptance criteria
- Blocks low-quality code from production


## File Structure

```
.claude/skills/swarm-iosm/     # Skill definition
  SKILL.md                      # Main Skill file (instructions for Claude)
  README.md                     # This file
  templates/                    # Document templates
    prd.md                      # PRD template
    plan.md                     # Implementation plan template
    subagent_brief.md           # Brief template for subagents
    subagent_report.md          # Report template for subagents
    integration_report.md       # Integration report template
    iosm_gates.md              # IOSM quality gates criteria
  scripts/                      # Helper scripts
    validate_plan.py           # Validate plan structure
    summarize_reports.py       # Summarize subagent reports

swarm/                          # Project workflow data (auto-created)
  context/                      # Project-wide context
    product.md                  # Product description
    tech-stack.md              # Technology stack
    workflow.md                # Development workflow
  tracks/                       # Feature/task tracks
    2026-01-17-001/            # Example track
      intake.md                # Requirements
      PRD.md                   # Product requirements
      spec.md                  # Technical spec
      plan.md                  # Implementation plan
      metadata.json            # Track metadata
      reports/                 # Subagent reports
        T01.md
        T02.md
      integration_report.md    # Integration plan
      iosm_report.md          # Quality gate results
  tracks.md                    # Track index
```

## Commands

### `/swarm-iosm setup`
Initialize Swarm workflow in current project.

Creates `swarm/` directory with context files.

**When to use:** First time using Swarm in a project.

---

### `/swarm-iosm new-track "<description>"`
Create a new feature/task track.

**Example:**
```
/swarm-iosm new-track "Implement OAuth2 authentication"
```

**What happens:**
1. Requirements gathering (questions)
2. PRD generation
3. Task decomposition and planning
4. Track directory created with all artifacts

**Output:** Track ID (e.g., `2026-01-17-001`)

---

### `/swarm-iosm implement [track-id]`
Execute implementation plan using subagents.

**Example:**
```
/swarm-iosm implement 2026-01-17-001
```

**What happens:**
1. Loads plan from track
2. Identifies parallelizable tasks
3. Launches subagents (foreground or background)
4. Collects reports

**Options:**
- Omit track-id to use most recent track
- Automatically suggests background for long-running tasks

---

### `/swarm-iosm status [track-id]`
Show progress summary for a track.

**Example:**
```
/swarm-iosm status 2026-01-17-001
```

**Output:**
- Task completion status (TODO/DOING/DONE/BLOCKED)
- Available reports
- Blockers and open questions
- Overall progress percentage

---

### `/swarm-iosm watch [track-id]`
Open a live monitoring dashboard for a track. (v1.3)

**What it does:**
1. Calculates real-time metrics (velocity, ETA, progress %)
2. Renders an ASCII progress bar
3. Shows status of all tasks in the track
4. Refreshes data from reports and checkpoints

**Example usage:**
```
/swarm-iosm watch
```

---

### `/swarm-iosm simulate [track-id]`
Run a dry-run simulation of the implementation plan. (v1.3)

**What it does:**
1. Loads implementation plan and resource constraints
2. Simulates dispatch loop with virtual time
3. Identifies bottlenecks and potential conflicts
4. Generates ASCII timeline and simulation report
5. Estimates total parallel execution time vs serial

**Example usage:**
```
/swarm-iosm simulate
```

---

### `/swarm-iosm resume [track-id]`
Resume an interrupted implementation from the latest checkpoint. (v1.3)

**What it does:**
1. Loads latest checkpoint from `checkpoints/latest.json`
2. Reconciles state by reading all report files in `reports/`
3. Identifies completed vs pending tasks
4. Recalculates the ready queue
5. Shows a summary of progress and next steps

**Example usage:**
```
/swarm-iosm resume
```

---

### `/swarm-iosm retry <task-id> [--foreground] [--reset-brief]`
Retry a failed task with optional mode changes. (v1.2)

**What it does:**
1. Reads error diagnosis from task report using parse_errors.py
2. Shows error diagnosis to user with suggested fixes
3. Asks user to choose: apply fix, manual fix, or skip
4. Regenerates subagent brief with error context
5. Relaunches task using Task tool
6. Tracks retry count (max 3 per task)

**Arguments:**
- `<task-id>`: Task to retry (e.g., T04)
- `--foreground`: Force foreground execution (for interactive debugging)
- `--reset-brief`: Regenerate brief from scratch (vs. reuse existing)

**Retry Workflow:**
1. Identify errors via `/swarm-iosm status`
2. Apply fix (suggested in dashboard)
3. Retry via `/swarm-iosm retry TID`

---

### `/swarm-iosm integrate <track-id>`
Collect reports and create integration plan.

**Example:**
```
/swarm-iosm integrate 2026-01-17-001
```

**What happens:**
1. Reads all subagent reports
2. Identifies file conflicts
3. Creates merge order (respecting dependencies)
4. Runs IOSM quality gates
5. Generates integration report

**Output:** `integration_report.md` and `iosm_report.md`

---

### `/swarm-iosm revert-plan <track-id>`
Generate rollback guide (does NOT execute revert).

**Example:**
```
/swarm-iosm revert-plan 2026-01-17-001
```

**Output:** `rollback_guide.md` with manual rollback steps

---

## Subagent Roles

The Skill defines standard subagent roles:

### Explorer
**Purpose:** Analyze existing codebase (brownfield)
**Tools:** Read, Grep, Glob
**Output:** Architecture map, dependencies, test coverage
**Use when:** Working with existing code

### Architect
**Purpose:** Design decisions and contracts
**Tools:** Read, Write (docs)
**Output:** ADRs, API specs, interface contracts
**Use when:** Complex features requiring design

### Implementer (A/B/C/...)
**Purpose:** Parallel implementation
**Tools:** Read, Write, Edit, Bash (tests)
**Output:** Code, tests, implementation report
**Use when:** Independent modules

### TestRunner
**Purpose:** Verification and testing
**Tools:** Read, Bash, Write
**Output:** Test results, coverage reports
**Use when:** After implementation

### SecurityAuditor
**Purpose:** Security review
**Tools:** Read, Grep, Bash (scanners)
**Output:** Security findings, recommendations
**Use when:** Auth, payments, sensitive data

### PerfAnalyzer
**Purpose:** Performance testing
**Tools:** Read, Bash (profiling)
**Output:** Performance metrics, bottlenecks
**Use when:** High-traffic features, APIs

### DocsWriter
**Purpose:** Documentation
**Tools:** Read, Write, Edit
**Output:** README, API docs, guides
**Use when:** Public APIs, complex features

## IOSM Quality Gates

Every track must pass IOSM quality gates before production:

### Gate-I: Improve (Code Quality)
- ✅ Semantic clarity ≥0.95 (clear naming)
- ✅ Code duplication ≤5%
- ✅ Invariants documented (100% public APIs)
- ✅ TODOs tracked (all in issue tracker)

### Gate-O: Optimize (Performance)
- ✅ P50/P95/P99 latency measured
- ✅ Error budget defined
- ✅ Chaos tests passing
- ✅ No obvious inefficiencies

### Gate-S: Shrink (Minimal Surface)
- ✅ API surface reduced ≥20% (or justified)
- ✅ Dependency count stable/reduced
- ✅ Onboarding time ≤15 min

### Gate-M: Modularize (Clean Boundaries)
- ✅ Module contracts 100% defined
- ✅ Change surface ≤20% (localized)
- ✅ Low coupling, high cohesion
- ✅ No circular dependencies

**IOSM-Index = (Gate-I + Gate-O + Gate-S + Gate-M) / 4**

**Production threshold:** ≥0.80

See `templates/iosm_gates.md` for detailed criteria.

## Examples

### Example 1: Greenfield Feature
```
User: I need to add email notifications to the app

Claude (using Swarm Skill):
1. /swarm-iosm new-track "Add email notification system"
2. Gathers requirements (SMTP? SendGrid? Templates?)
3. Generates PRD with acceptance criteria
4. Creates plan with tasks:
   - T01: Design email templates (DocsWriter)
   - T02: Implement email service (Implementer-A)
   - T03: Add API endpoints (Implementer-B)
   - T04: Write tests (TestRunner)
5. Launches T01, T02, T03 in parallel (background)
6. Collects reports and integrates
7. Runs IOSM gates, creates integration report
```

### Example 2: Brownfield Refactor
```
User: Refactor the payment processing module

Claude (using Swarm Skill):
1. /swarm-iosm setup (if first time)
2. /swarm-iosm new-track "Refactor payment processing"
3. Suggests Plan mode (read-only exploration)
4. Launches Explorer to map current payment module
5. Architect creates refactoring plan (ADR)
6. Implementer refactors incrementally
7. TestRunner ensures no regressions
8. Integration report includes rollback guide
```

### Example 3: Large Multi-Module Feature
```
User: Implement multi-tenant architecture

Claude (using Swarm Skill):
1. /swarm-iosm new-track "Multi-tenant architecture"
2. Creates plan with 15 tasks across 4 phases
3. Phase 1 (Design):
   - T01: Architect designs tenant isolation
   - T02: Architect designs data model
4. Phase 2 (Implementation - parallel):
   - T04: Implementer-A (tenant middleware)
   - T05: Implementer-B (tenant models)
   - T06: Implementer-C (tenant API)
   - All run in background simultaneously
5. Phase 3 (Verification):
   - T08: TestRunner (integration tests)
   - T09: SecurityAuditor (tenant isolation audit)
6. Phase 4 (Integration):
   - Merge all work, resolve conflicts
   - IOSM gates, deployment plan
```

## Best Practices

### 1. Resolve Questions Upfront
Background subagents can't ask questions. Answer all questions before launching background tasks.

### 2. Use Plan Mode for Brownfield
Always start with read-only exploration (Plan mode) when working with existing code.

### 3. Parallelize Research, Sequence Implementation
- ✅ Run multiple Explorers in parallel (different modules)
- ✅ Run Implementers in parallel (different files)
- ❌ Don't parallel edit the same file

### 4. Demand Structured Reports
Every subagent must save a report using the template. This ensures traceability.

### 5. Run IOSM Gates Before Merge
Never merge to main without passing IOSM gates (≥0.80).

### 6. Create Rollback Plans
For production changes, always generate a rollback plan before deploying.

### 7. Monitor Background Tasks
Use `/bashes` to check on background subagents.

## Customization

### Custom Subagent Roles
Add your own roles by editing `SKILL.md` section "Subagent Taxonomy".

### Custom Templates
Copy templates and modify for your needs:

```bash
cp templates/prd.md templates/prd_custom.md
```

### Inter-Agent Communication (v2.0)
Subagents share knowledge via `shared_context.md`. Orchestrator merges updates after task completion.

## Version History

- **v2.1** (2026-01-19) - The "Engine" Update
  - Automated State Management (auto-generated `iosm_state.md`)
  - Status Sync CLI (`--update-task`)
  - Improved Report Conflict Detection

- **v2.0** (2026-01-19) - Advanced Features
  - Inter-Agent Communication (Shared Context)
  - Task Dependency Visualization (`--graph`)
  - Anti-Pattern Detection
  - Template Customization

- **v1.3** (2026-01-19) - Reliability & UX
  - Simulation Mode (`/swarm-iosm simulate`) with ASCII Timeline
  - Live Monitoring (`/swarm-iosm watch`)
  - Checkpointing & Resume (`/swarm-iosm resume`)

- **v1.2** (2026-01-19) - Production Ready
  - Concurrency Limits (Resource Budgets)
  - Cost Tracking & Model Selection (Haiku/Sonnet/Opus)
  - Intelligent Error Diagnosis & Retry (`/swarm-iosm retry`)

- **v1.1** (2026-01-17) - Continuous Dispatch
  - Continuous scheduling loop
  - Touches lock manager
  - Auto-spawn from SpawnCandidates

- **v1.0** (2026-01-17) - Initial Release
  - PRD generation, Task decomposition, Subagent orchestration

## References

- **Claude Code Documentation:** https://code.claude.com/docs/
- **Agent Skills Guide:** https://code.claude.com/docs/en/skills
- **Subagents Guide:** https://code.claude.com/docs/en/sub-agents
- **Conductor CLI:** https://github.com/gemini-cli-extensions/conductor

## License

This Skill is part of the AstroVisor project. Use freely in your projects.

---

**Happy Swarming! 🐝**