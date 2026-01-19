# <img src="examples/logo.webp" width="100%" alt="Swarm-IOSM Preview">

# Swarm Workflow (IOSM)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1-blue.svg)](https://github.com/rokoss21/swarm-iosm)
[![IOSM Ready](https://img.shields.io/badge/Methodology-IOSM-success)](https://github.com/rokoss21/IOSM)
[![Author](https://img.shields.io/badge/Author-rokoss21-orange)](https://github.com/rokoss21)

**The official Agent Skill for orchestrating complex development tasks using the [IOSM Methodology](https://github.com/rokoss21/IOSM).**

Swarm-IOSM turns your AI assistant into a professional Project Manager. It automates the **Improve → Optimize → Shrink → Modularize** cycle through parallel subagent execution, rigorous planning, and quality gates.

---

## 🧩 Philosophy

This tool is the technical implementation of the **IOSM** philosophy created by [rokoss21](https://github.com/rokoss21).

> **IOSM** stands for a cyclic refactoring and development process:
> *   **I**mprove: Make it work, increase clarity.
> *   **O**ptimize: Make it fast, efficient, and scalable.
> *   **S**hrink: Reduce code volume, remove redundancy.
> *   **M**odularize: Enforce strict boundaries and contracts.

Swarm-IOSM enforces these principles automatically via **Quality Gates** and **Orchestration Plans**.

---

## 🚀 Key Features

### 🧠 Intelligent Orchestration (v2.1)
- **Automated State Management:** The system maintains a "Single Source of Truth" (`iosm_state.md`) generated from immutable checkpoints. No manual tracking required.
- **Continuous Dispatch Loop:** Tasks are launched continuously as dependencies are met, maximizing parallelism.
- **Smart Model Selection:** Automatically routes tasks to the best model (Haiku for reads, Sonnet for code, Opus for architecture) to optimize cost/performance.

### 🛡️ Resilience & Reliability (v1.3)
- **Smart Retry System:** Auto-detects transient failures (network, timeouts) and retries up to 3 times.
- **Error Diagnosis:** Translates cryptic Python/Shell errors into actionable fixes (e.g., "Permission Denied" → "Run chmod").
- **Checkpointing:** State is saved to JSON after every event. Resume execution after a crash with a single command.

### ⚡ Parallel Execution (v1.2)
- **Resource Budgets:** Prevents API rate limits and OOM errors by capping background tasks (default: 6 BG / 2 FG).
- **Lock Manager:** Automatically prevents file conflicts by locking `touches` paths during execution.
- **Speedup:** Achieves 2-5x acceleration compared to sequential execution.

### 📊 Observability
- **Simulation Mode:** Dry-run your plan before spending tokens. See a Gantt chart of predicted execution.
- **Live Dashboard:** Watch progress in real-time with ASCII progress bars, velocity tracking, and ETA.
- **Dependency Visualization:** Generate Mermaid graphs to visualize task relationships.

### 🤖 Advanced Intelligence (v2.0)
- **Anti-Pattern Detection:** Warns about monolithic tasks or low parallelism.
- **Inter-Agent Communication:** Subagents share patterns via `shared_context.md`.
- **Template Customization:** Override templates per project.

---

## 📦 Installation

This Skill is designed for **Claude Code** or **Gemini CLI**.

```bash
# Clone into your skills directory
git clone https://github.com/rokoss21/swarm-iosm.git ~/.claude/skills/swarm-iosm
```

---

## 🛠️ Usage Workflow

### 1. Initialize Context
Setup the IOSM structure in your project:
```bash
/swarm-iosm setup
```

### 2. Start a New Track
Create a feature track. The agent will interview you to generate a **PRD** and **Implementation Plan**.
```bash
/swarm-iosm new-track "Refactor Auth Module"
```

### 3. Simulation (Optional)
Check how the execution will flow and estimate costs.
```bash
/swarm-iosm simulate
```

### 4. Execute
Launch the swarm. Subagents will work in parallel.
```bash
/swarm-iosm implement
```

### 5. Monitor
Watch the live dashboard.
```bash
/swarm-iosm watch
```

### 6. Integrate
Merge work and run quality gates.
```bash
/swarm-iosm integrate
```

---

## 💻 Commands Reference

### `/swarm-iosm setup`
Initialize project context for Swarm workflow. Creates `swarm/` directory structure.

### `/swarm-iosm new-track "<description>"`
Create a new feature/task track with PRD and implementation plan.

### `/swarm-iosm implement [track-id]`
Execute the implementation plan using parallel subagents. Launches background workers.

### `/swarm-iosm status [track-id]`
Show progress summary, blockers, and completion status.

### `/swarm-iosm watch [track-id]`
**Live Monitoring (v1.3):** Real-time ASCII dashboard with velocity and ETA.

### `/swarm-iosm simulate [track-id]`
**Dry-Run (v1.3):** Simulates execution with virtual time to identify bottlenecks.

### `/swarm-iosm resume [track-id]`
**Recovery (v1.3):** Resume an interrupted implementation from the latest checkpoint.

### `/swarm-iosm retry <task-id>`
**Smart Retry (v1.2):** Retry a failed task with optional mode changes (foreground/background).

### `/swarm-iosm integrate <track-id>`
Collect subagent reports, resolve conflicts, and run IOSM quality gates.

### `/swarm-iosm revert-plan <track-id>`
Generate a step-by-step rollback guide (does NOT execute git revert automatically).

---

## 🤖 Subagent Roles

The Skill defines standard subagent roles optimized for specific tasks:

| Role | Purpose | Tools | Use When |
|------|---------|-------|----------|
| **Explorer** | Analyze existing codebase (brownfield) | Read, Grep, Glob | Working with existing code |
| **Architect** | Design decisions and contracts | Read, Write (docs) | Complex features requiring design |
| **Implementer** | Parallel implementation | Read, Write, Edit, Bash | Independent modules |
| **TestRunner** | Verification and testing | Read, Bash, Write | After implementation |
| **SecurityAuditor** | Security review | Read, Grep, Bash | Auth, payments, sensitive data |
| **PerfAnalyzer** | Performance testing | Read, Bash (profiling) | High-traffic features, APIs |
| **DocsWriter** | Documentation | Read, Write, Edit | Public APIs, complex features |

---

## 🚦 IOSM Quality Gates

Every track is evaluated against strict criteria before integration:

| Gate | Focus | Criteria |
|------|-------|----------|
| **Gate-I** | **Improve** | Semantic clarity ≥ 0.95, No duplication |
| **Gate-O** | **Optimize** | P95 Latency defined, Tests passing |
| **Gate-S** | **Shrink** | API surface minimized, Deps reduced |
| **Gate-M** | **Modularize** | Clean contracts, No circular deps |

**Production threshold:** IOSM-Index ≥ 0.80

---

## 📚 Real-World Examples

### Example 1: Greenfield Feature (New Email System)
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

### Example 2: Brownfield Refactor (Payment Module)
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

### Example 3: Complex Architecture (Multi-Tenant)
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

---

## 🔧 Troubleshooting

### Background task fails silently?
*   **Cause:** Often due to permission errors or tools requiring user input (MCP) running in background.
*   **Fix:** Check `/bashes` for status. Use `/swarm-iosm retry <TID> --foreground` to debug interactively.

### "Loops without progress"?
*   **Cause:** Circular dependencies or all tasks blocked on user input.
*   **Fix:** Check `iosm_state.md` for blocking questions or circular logic.

### Permission Denied errors?
*   **Diagnosis:** The system now auto-diagnoses this (v1.2).
*   **Fix:** Use the suggested fix (e.g., `chmod`) and retry.

### Script not found?
*   **Fix:** Ensure you are running from the project root and the `.claude/skills` directory is correctly placed.

---

## 📂 File Structure

```
.claude/skills/swarm-iosm/     # Skill definition
  SKILL.md                      # Main Skill file
  templates/                    # Document templates (PRD, Plan, Reports)
  scripts/                      # Logic scripts (Planner, Validation, Metrics)

swarm/                          # Project workflow data (auto-created)
  tracks/                       # Feature/task tracks
    YYYY-MM-DD-NNN/            # Track directory
      plan.md                  # Implementation plan
      iosm_state.md            # Live state (Auto-generated)
      reports/                 # Subagent reports
      checkpoints/             # JSON State snapshots
      integration_report.md    # Final results
```

---

## 🤝 Contributing & Author

**Author:** [rokoss21](https://github.com/rokoss21)

This project is open-source. If you want to contribute to the IOSM methodology or this tool:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

**Contact:**
- GitHub: [@rokoss21](https://github.com/rokoss21)
- Project Link: [https://github.com/rokoss21/swarm-iosm](https://github.com/rokoss21/swarm-iosm)

---

## 📜 Version History

- **v2.1 (2026-01-19):** Automated State Engine, Status Sync CLI.
- **v2.0 (2026-01-19):** Inter-Agent Comm, Anti-Patterns, Visualization.
- **v1.3 (2026-01-19):** Simulation, Checkpointing, Live Monitoring.
- **v1.2 (2026-01-19):** Concurrency Limits, Cost Tracking, Error Diagnosis.
- **v1.0 (2026-01-17):** Initial Release.

---

**Happy Swarming! 🐝**
