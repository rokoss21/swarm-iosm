<p align="center">
  <img src="examples/logo.webp" alt="Swarm-IOSM Logo" width="400">
</p>

# Swarm-IOSM

**Parallel Subagent Orchestration Engine for Claude Code**

[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blue?style=for-the-badge)](https://claude.ai/code)
[![IOSM](https://img.shields.io/badge/IOSM-v1.0-purple?style=for-the-badge)](https://github.com/rokoss21/IOSM)
[![Version](https://img.shields.io/badge/version-1.1.1-green?style=for-the-badge)](./SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-orange?style=for-the-badge)](./LICENSE)

---
## Overview

**Swarm-IOSM** is an [Agent Skill](https://claude.ai/code) for Claude Code that implements the [IOSM methodology](https://github.com/rokoss21/IOSM) as an executable orchestration engine for parallel development.

It transforms complex development tasks into coordinated parallel work streams by combining:

- **[IOSM Quality Gates](https://github.com/rokoss21/IOSM)** — Improve → Optimize → Shrink → Modularize
- **PRD-driven planning** — Structured requirements gathering and decomposition
- **Continuous dispatch scheduling** — Parallel subagent execution with dependency analysis
- **File conflict detection** — Lock management for safe parallel writes
- **Auto-spawn protocol** — Dynamic task creation from discoveries

---

## Foundation: The IOSM Methodology

This skill is built on [**IOSM (Improve → Optimize → Shrink → Modularize)**](https://github.com/rokoss21/IOSM) — a reproducible methodology for continuous system improvement that combines engineering rigor with business rationality.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           IOSM FRAMEWORK                                   │
│                   https://github.com/rokoss21/IOSM                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐    │
│    │ IMPROVE  │ →  │ OPTIMIZE │ →  │  SHRINK  │ →  │   MODULARIZE     │    │
│    │          │    │          │    │          │    │                  │    │
│    │ Clarity  │    │ Speed    │    │ Simplify │    │ Decompose        │    │
│    │ No dups  │    │ Resil.   │    │ Surface  │    │ Contracts        │    │
│    │ Invars   │    │ Chaos    │    │ Deps     │    │ Coupling         │    │
│    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────────┬─────────┘    │
│         │               │               │                   │              │
│    ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐    ┌────────▼─────────┐    │
│    │ Gate-I   │    │ Gate-O   │    │ Gate-S   │    │     Gate-M       │    │
│    │ ≥0.85    │    │ ≥0.75    │    │ ≥0.80    │    │     ≥0.80        │    │
│    └──────────┘    └──────────┘    └──────────┘    └──────────────────┘    │
│                                                                            │
│    IOSM-Index = (Gate-I + Gate-O + Gate-S + Gate-M) / 4                    │
│    Production threshold: ≥ 0.80                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### IOSM Core Principles

| Pillar | Purpose | Key Metrics |
|--------|---------|-------------|
| **Improve** | Achieve structural clarity | Semantic coherence ≥0.95, Duplication ≤5% |
| **Optimize** | Maximize efficiency & resilience | P95 latency, Error budget, Chaos tests |
| **Shrink** | Minimize complexity | API surface -20%, Onboarding ≤15min |
| **Modularize** | Design for evolution | Contracts 100%, No circular deps |

> *"IOSM turns concepts into an executable discipline, ready for CI/CD automation."*
> — [IOSM Specification](https://github.com/rokoss21/IOSM)

---

## What Swarm-IOSM Adds

While [IOSM](https://github.com/rokoss21/IOSM) defines the **methodology**, Swarm-IOSM provides the **execution engine**:

| IOSM (Methodology) | Swarm-IOSM (Execution) |
|--------------------|------------------------|
| Quality gate definitions | Gate enforcement in Claude Code |
| Algorithm specification | Continuous dispatch loop |
| Configuration schema | Live `iosm_state.md` tracking |
| Manual orchestration | Parallel subagent automation |
| CI/CD integration patterns | Background/foreground mode selection |

**Swarm-IOSM = IOSM methodology + Claude Code parallel execution**

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR (Main Agent)                    │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Continuous Dispatch Loop                                       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │ │
│  │  │ Collect  │→ │ Classify │→ │ Conflict │→ │ Dispatch Batch   │ │ │
│  │  │  Ready   │  │  Modes   │  │  Check   │  │ (parallel)       │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │ │
│  │       ↑                                           │             │ │
│  │       │        ┌──────────┐  ┌──────────┐         ↓             │ │
│  │       └────────│  IOSM    │←─│ Auto-    │←────────┘             │ │
│  │                │  Gates   │  │ Spawn    │                       │ │
│  │                └──────────┘  └──────────┘                       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                   │                                  │
│               ┌───────────────────┼───────────────────┐              │
│               ↓                   ↓                   ↓              │
│  ┌────────────────────┐ ┌────────────────────┐ ┌─────────────────┐   │
│  │   Subagent (BG)    │ │   Subagent (BG)    │ │  Subagent (FG)  │   │
│  │   Explorer         │ │   Implementer-A    │ │  Architect      │   │
│  │   read-only        │ │   write-local      │ │  needs_user     │   │
│  └────────────────────┘ └────────────────────┘ └─────────────────┘   │
│               │                   │                   │              │
│               ↓                   ↓                   ↓              │
│         reports/T01.md      reports/T02.md      reports/T03.md       │
│         + SpawnCandidates   + SpawnCandidates   + Escalations        │
└──────────────────────────────────────────────────────────────────────┘
```

### Core Execution Principles

1. **Orchestrator Does NOT Implement** — The main agent coordinates only. All real work delegated to subagents.

2. **Continuous Dispatch** — Tasks launch immediately when ready, no wave barriers.

3. **Lock Discipline** — File conflicts detected and prevented via touches lock manager.

4. **Gate-Driven Continuation** — Loop continues until IOSM gate targets met.

5. **Auto-Spawn Protocol** — Subagents report discoveries → orchestrator spawns new tasks.

---

## Installation

### Option 1: Project-Level (Recommended)

```bash
# Clone into your project's .claude/skills directory
git clone https://github.com/rokoss21/swarm-iosm.git .claude/skills/swarm-iosm
```

### Option 2: User-Level (All Projects)

```bash
# Clone into your personal skills directory
git clone https://github.com/rokoss21/swarm-iosm.git ~/.claude/skills/swarm-iosm
```

### Verify Installation

In Claude Code, type `/swarm-iosm` — you should see the skill activate.

---

## Quick Start

### 1. Initialize Project

```
/swarm-iosm setup
```

Creates `swarm/` directory with project context.

### 2. Create a Track

```
/swarm-iosm new-track "Add user authentication with JWT"
```

Claude will:
- Gather requirements (questions)
- Generate PRD
- Decompose into parallel tasks
- Create implementation plan with IOSM gate targets

### 3. Validate & Generate Dispatch Plan

```bash
# Validate plan has required fields
python .claude/skills/swarm-iosm/scripts/orchestration_planner.py \
    swarm/tracks/<track-id>/plan.md --validate

# Generate continuous dispatch plan (v1.1)
python .claude/skills/swarm-iosm/scripts/orchestration_planner.py \
    swarm/tracks/<track-id>/plan.md --continuous
```

### 4. Execute

```
/swarm-iosm implement
```

Orchestrator launches parallel subagents, monitors progress, enforces IOSM gates.

### 5. Integrate

```
/swarm-iosm integrate <track-id>
```

Generates `integration_report.md` and `iosm_report.md` with quality gate results.

---

## Commands

| Command | Description |
|---------|-------------|
| `/swarm-iosm setup` | Initialize project context |
| `/swarm-iosm new-track "<desc>"` | Create new feature track |
| `/swarm-iosm implement [track-id]` | Execute implementation plan |
| `/swarm-iosm status [track-id]` | Check progress |
| `/swarm-iosm integrate <track-id>` | Merge work, run IOSM quality gates |
| `/swarm-iosm revert-plan <track-id>` | Generate rollback guide |

---

## IOSM Quality Gates in Swarm

Each gate is evaluated using criteria from the [IOSM specification](https://github.com/rokoss21/IOSM):

### Gate-I: Improve (Code Quality)
```yaml
gate_I:
  semantic_coherence: 0.95    # Clear naming, no magic numbers
  duplication_max: 0.05       # ≤5% duplicate code
  invariants_documented: true # Preconditions/postconditions
  todos_tracked: true         # All TODOs in issue tracker
```

### Gate-O: Optimize (Performance)
```yaml
gate_O:
  latency_ms: { p50: 100, p95: 200, p99: 500 }
  error_budget_respected: true
  chaos_tests_pass: true
  no_obvious_inefficiencies: true
```

### Gate-S: Shrink (Minimal Surface)
```yaml
gate_S:
  api_surface_reduction: 0.20  # Or justified growth
  dependency_count_stable: true
  onboarding_time_minutes: 15
```

### Gate-M: Modularize (Clean Boundaries)
```yaml
gate_M:
  contracts_defined: 1.0       # 100% of modules
  change_surface_max: 0.20     # ≤20% touched by change
  no_circular_deps: true
  coupling_acceptable: true
```

---

## Subagent Roles

| Role | Purpose | Mode | Tools |
|------|---------|------|-------|
| **Explorer** | Codebase analysis (IOSM baseline) | Background | Read, Grep, Glob |
| **Architect** | Design decisions | Foreground | Read, Write (docs) |
| **Implementer-{A,B,C}** | Parallel implementation | Background | Read, Write, Edit, Bash |
| **TestRunner** | Gate-O verification | Background | Read, Bash, Write |
| **SecurityAuditor** | Gate-I security invariants | Background | Read, Grep, Bash |
| **PerfAnalyzer** | Gate-O performance | Background | Read, Bash |
| **DocsWriter** | Gate-S onboarding | Background | Read, Write, Edit |

---

## Continuous Dispatch (v1.1)

Key innovation: **No wave barriers**. Tasks dispatch immediately when dependencies satisfied.

### Task States

```
backlog → ready → running → done
              ↘ blocked_user
              ↘ blocked_conflict
```

### Concurrency Classes

| Class | Lock Behavior | Parallelism |
|-------|---------------|-------------|
| `read-only` | No lock | Always parallel |
| `write-local` | Lock on touches | Parallel if no overlap |
| `write-shared` | Exclusive lock | Sequential only |

### SpawnCandidates Protocol

Subagents MUST report discoveries for auto-spawn:

```markdown
## SpawnCandidates

| ID | Subtask | Touches | Effort | User Input | Severity | Accept Criteria |
|----|---------|---------|--------|------------|----------|-----------------|
| SC-01 | Fix type error (Gate-I) | `auth.py` | S | false | medium | mypy passes |
| SC-02 | Add missing test (Gate-O) | `tests/` | M | false | high | coverage ≥80% |
```

---

## File Structure

```
.claude/skills/swarm-iosm/
├── SKILL.md              # Main skill definition (1000+ lines)
├── README.md             # Documentation
├── QUICKSTART.md         # Operational runbook
├── VALIDATION.md         # Validation checklist
├── templates/
│   ├── plan.md           # Implementation plan template
│   ├── prd.md            # PRD template
│   ├── subagent_brief.md # Subagent instructions
│   ├── subagent_report.md# Report format
│   ├── iosm_gates.md     # IOSM quality gate criteria
│   ├── iosm_state.md     # Live state tracking
│   └── integration_report.md
├── scripts/
│   ├── orchestration_planner.py  # Plan → dispatch plan
│   ├── validate_plan.py          # Plan validator
│   └── summarize_reports.py      # Report aggregator
└── examples/
    └── demo-track/       # Example track

swarm/                    # Project workflow data (auto-created)
├── context/
│   ├── product.md
│   ├── tech-stack.md
│   └── workflow.md
├── tracks/
│   └── YYYY-MM-DD-NNN/
│       ├── PRD.md
│       ├── plan.md
│       ├── continuous_dispatch_plan.md
│       ├── iosm_state.md
│       ├── reports/
│       ├── integration_report.md
│       └── iosm_report.md
└── tracks.md
```

---

## Spawn Protection (v1.1.1)

Prevents infinite task proliferation:

### Budget System

```markdown
## Spawn Budget
- spawn_budget_total: 20
- spawn_budget_per_gate:
  - Gate-I: 5 (clarity/duplication fixes)
  - Gate-O: 8 (performance/test fixes)
  - Gate-M: 4 (boundary fixes)
  - Gate-S: 3 (surface reduction)
```

### Deduplication

```
Dedup Key = <primary_touch>|<intent_category>
Example: "auth.py|type-annot"
```

### Anti-Loop Protection

```markdown
## Anti-Loop Metrics
- loops_without_progress: 0  # max: 3
- total_loop_iterations: 15  # max: 50
```

---


## When to Use

**Use Swarm-IOSM for:**
- Multi-file features requiring coordination
- Brownfield refactoring with IOSM gate enforcement
- Parallel implementation streams
- Tasks requiring formal acceptance criteria
- Quality-gated production deployments

**Don't use for:**
- Single-file changes
- Quick bug fixes
- Exploratory research

---

## Integration with IOSM Ecosystem

### IOSM Methodology
The theoretical foundation. See [IOSM](https://github.com/rokoss21/IOSM) for:
- Complete specification
- Gate criteria definitions
- `iosm.yaml` configuration schema
- CI/CD integration patterns

### Swarm-IOSM (This Repo)
The Claude Code execution engine implementing IOSM for parallel agent orchestration.

### FACET Ecosystem
For deterministic AI contracts, see:
- [FACET Standard](https://github.com/rokoss21/facet-standard) — Contract Layer for AI
- [FACET Compiler](https://github.com/rokoss21/facet-compiler) — Reference Implementation (Rust)

---

## Contributing

Contributions welcome. Key areas:

- Additional subagent role templates
- Gate automation scripts (CI/CD)
- Language-specific IOSM checkers
- Integration examples

See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Version History

### v1.1.1 (2026-01-17)
- Lock granularity (folder/file hierarchy)
- Read-only safety rules (scratch_dir)
- Spawn protection (budget, dedup, severity threshold)
- Anti-loop protection
- Batch constraints (max 3-6 per batch)

### v1.1.0 (2026-01-15)
- Continuous dispatch loop (no wave barriers)
- Gate-driven continuation
- Auto-spawn from SpawnCandidates
- Touches lock manager
- iosm_state.md for progress tracking

### v1.0.0 (2026-01-10)
- Initial release
- PRD generation
- Wave-based orchestration
- IOSM quality gates

---

## Author

**Emil Rokossovskiy** ([@rokoss21](https://github.com/rokoss21))

AI & Platform Engineer. Creator of:
- [IOSM Methodology](https://github.com/rokoss21/IOSM)
- [FACET Ecosystem](https://github.com/rokoss21/facet-standard)

---

## License

[MIT](./LICENSE)

---

## Related Projects

| Project | Description |
|---------|-------------|
| [IOSM](https://github.com/rokoss21/IOSM) | The methodology this skill implements |
| [FACET Standard](https://github.com/rokoss21/facet-standard) | Deterministic Contract Layer for AI |
| [FACET Compiler](https://github.com/rokoss21/facet-compiler) | Reference Compiler (Rust) |
| [FACET Agents](https://github.com/rokoss21/facet-agents) | Conformance Test Agents |

---

<p align="center">
  <b>IOSM: Improve → Optimize → Shrink → Modularize</b>
  <br>
  <i>Orchestrate complexity. Enforce quality. Ship faster.</i>
</p>
