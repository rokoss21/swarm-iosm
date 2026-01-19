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

### 🛡️ Resilience & Reliability
- **Smart Retry System:** Auto-detects transient failures (network, timeouts) and retries up to 3 times.
- **Error Diagnosis:** Translates cryptic Python/Shell errors into actionable fixes (e.g., "Permission Denied" → "Run chmod").
- **Checkpointing:** State is saved to JSON after every event. Resume execution after a crash with a single command.

### ⚡ Parallel Execution
- **Resource Budgets:** Prevents API rate limits and OOM errors by capping background tasks (default: 6 BG / 2 FG).
- **Lock Manager:** Automatically prevents file conflicts by locking `touches` paths during execution.
- **Speedup:** Achieves 2-5x acceleration compared to sequential execution.

### 📊 Observability
- **Simulation Mode:** Dry-run your plan before spending tokens. See a Gantt chart of predicted execution.
- **Live Dashboard:** Watch progress in real-time with ASCII progress bars, velocity tracking, and ETA.
- **Dependency Visualization:** Generate Mermaid graphs to visualize task relationships.

---

## 📦 Installation

This Skill is designed for **Claude Code** or **Gemini CLI**.

```bash
# Clone into your skills directory
git clone https://github.com/rokoss21/swarm-iosm.git ~/.claude/skills/swarm-iosm
```

---

## 🛠️ Usage

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

---

## 🚦 IOSM Quality Gates

Every track is evaluated against strict criteria before integration:

| Gate | Focus | Criteria |
|------|-------|----------|
| **Gate-I** | **Improve** | Semantic clarity ≥ 0.95, No duplication |
| **Gate-O** | **Optimize** | P95 Latency defined, Tests passing |
| **Gate-S** | **Shrink** | API surface minimized, Deps reduced |
| **Gate-M** | **Modularize** | Clean contracts, No circular deps |

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

### Version History

- **v2.1 (2026-01-19):** Automated State Engine, Status Sync CLI.
- **v2.0 (2026-01-19):** Inter-Agent Comm, Anti-Patterns, Visualization.
- **v1.3 (2026-01-19):** Simulation, Checkpointing, Live Monitoring.
- **v1.2 (2026-01-19):** Concurrency Limits, Cost Tracking, Error Diagnosis.
- **v1.0 (2026-01-17):** Initial Release.
