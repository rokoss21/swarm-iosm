# Swarm Workflow (IOSM) - Agent Skill

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

### вњ… Structured Workflow
- Repeatable process for any complexity level
- Works for both greenfield (new) and brownfield (existing) projects
- All work tracked in standardized artifacts

### рџљЂ Parallel Execution & Concurrency (v1.2)
- **Continuous Dispatch:** Launches tasks as soon as dependencies are met
- **Resource Limits:** Prevents OOM/Rate limits (Max 6 background tasks by default)
- **Lock Manager:** Automatically prevents file access conflicts
- **Speedup:** Achieves 2-5x acceleration vs sequential execution

### рџ’° Cost Control & Model Optimization (v1.2)
- **Smart Model Selection:** Uses Haiku for read-only, Sonnet for code, Opus for security
- **Budget Tracking:** Stops execution if cost exceeds limit (default $10)
- **Cost Estimation:** Predicts track cost before execution

### рџ›ЎпёЏ Reliability & Resilience (v1.3)
- **Smart Retry:** Auto-retries transient failures (max 3 times)
- **Checkpointing:** Saves state after every step; resume after crash via `/swarm-iosm resume`
- **Error Diagnosis:** Translates cryptic errors into actionable fixes (e.g., "Run chmod +x")

### рџ“€ Observability & Simulation (v1.3)
- **Simulation Mode:** Dry-run execution with `/swarm-iosm simulate`
- **Live Dashboard:** Watch progress with `/swarm-iosm watch` (ASCII bars, Velocity, ETA)
- **Visualization:** Generate Mermaid dependency graphs

### рџ¤– Automated State Management (v2.1)
- **Single Source of Truth:** `iosm_state.md` is now auto-generated from JSON checkpoints.
- **Sync via CLI:** Use `--update-task <TID> --status DONE` to keep everything in sync.
- **Accuracy:** Eliminates manual calculation errors in budget and progress tracking.

### рџ§  Advanced Intelligence (v2.0)
- **Anti-Pattern Detection:** Warns about monolithic tasks or low parallelism
- **Inter-Agent Communication:** Subagents share patterns via `shared_context.md`
- **Template Customization:** Override templates per project

### рџ“Љ Quality Enforcement
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

Example:
```markdown
**DataEngineer** (data pipelines):
- Tools: Read, Bash (SQL), Write
- Output: ETL scripts, data validation
- When: Data processing features
```

### Custom Templates
Copy templates and modify for your needs:

```bash
cp templates/prd.md templates/prd_custom.md
# Edit prd_custom.md with your sections
```

Reference in SKILL.md:
```markdown
Generate PRD using [templates/prd_custom.md](templates/prd_custom.md)
```

### Integration with Conductor
This Skill is compatible with Conductor CLI patterns:
- `swarm/` mirrors `conductor/` structure
- `tracks/` similar to Conductor tracks
- Same spec/plan/metadata.json pattern

## Troubleshooting

### Skill not activating
**Symptom:** Claude doesn't use Swarm Skill when expected

**Fix:**
1. Check description in SKILL.md includes trigger words
2. Try explicit invocation: `/swarm-iosm new-track "..."`
3. Restart Claude Code

---

### Background subagent fails
**Symptom:** Background task fails with permission error

**Fix:**
1. Check `/bashes` for task status
2. Resume in foreground: find task ID, use Task tool with resume
3. Pre-approve permissions before launching background tasks

---

### Reports incomplete
**Symptom:** Subagent report missing sections

**Fix:**
1. Subagent brief must explicitly require report template
2. Include report template link in brief
3. Validate reports with `scripts/summarize_reports.py`

---

### File conflicts during integration
**Symptom:** Multiple subagents edited same file

**Fix:**
1. Review plan to minimize shared file edits
2. Use sequential tasks for shared files
3. Manual merge in integration phase

---

### IOSM gates failing
**Symptom:** IOSM-Index < 0.80

**Fix:**
1. Review gate criteria in `templates/iosm_gates.md`
2. Identify failing criteria
3. Create follow-up tasks to address issues
4. Re-run integration after fixes

## Scripts

### validate_plan.py
Validate plan structure and dependencies.

```bash
python .claude/skills/swarm-iosm/scripts/validate_plan.py swarm/tracks/2026-01-17-001/plan.md

# With dependency graph
python .claude/skills/swarm-iosm/scripts/validate_plan.py swarm/tracks/2026-01-17-001/plan.md --graph
```

---

### summarize_reports.py
Generate summary of all subagent reports.

```bash
python .claude/skills/swarm-iosm/scripts/summarize_reports.py swarm/tracks/2026-01-17-001

# JSON output
python .claude/skills/swarm-iosm/scripts/summarize_reports.py swarm/tracks/2026-01-17-001 --json
```

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

## Contributing

Improvements welcome! Key areas:
- Additional subagent roles
- Better IOSM automation
- Integration with CI/CD
- Custom templates for different domains

---

**Happy Swarming! 🐝**
