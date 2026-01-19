# Demo Track: Add Redis Caching

This is a **complete example track** demonstrating the full Swarm-IOSM workflow from PRD to production merge.

## 📋 What's Included

This directory contains all artifacts generated during a real Swarm-IOSM track:

```
demo-track/
├── README.md ........................ This file
├── PRD.md ........................... Product Requirements Document
├── spec.md .......................... Technical specification
├── plan.md .......................... Task breakdown with dependencies
├── continuous_dispatch_plan.md ...... Auto-generated orchestration plan
├── dependency_graph.mermaid ......... Task dependency visualization
├── iosm_state.md .................... Live execution state (auto-updated)
│
├── reports/ ......................... Subagent execution reports
│   ├── T01.md ....................... Explorer: Performance analysis
│   └── T03.md ....................... Implementer-A: Redis client
│
├── integration_report.md ............ Final merge plan & conflict resolution
├── iosm_report.md ................... IOSM quality gate evaluation
│
└── checkpoints/
    └── latest.json .................. Crash recovery checkpoint
```

## 🎯 Scenario

**Goal:** Add Redis caching to `/api/natal/chart` endpoint to improve performance.

**Complexity:** Medium
- 7 tasks (T01-T07)
- 5 files modified
- 2 parallel implementation streams
- IOSM gates enforced

**Results:**
- P95 latency: 450ms → 180ms (60% improvement)
- Cache hit rate: 82%
- IOSM-Index: 0.85 (passed ≥0.80 threshold)

## 📖 How to Use This Example

### 1. Understand the Workflow

Read files in this order:

1. **[PRD.md](./PRD.md)** — What problem we're solving and why
2. **[spec.md](./spec.md)** — Technical approach and acceptance tests
3. **[plan.md](./plan.md)** — Task breakdown (T01-T07) with dependencies
4. **[continuous_dispatch_plan.md](./continuous_dispatch_plan.md)** — Auto-generated orchestration
5. **[reports/T01.md](./reports/T01.md)** — Example subagent report (Explorer)
6. **[reports/T03.md](./reports/T03.md)** — Example subagent report (Implementer)
7. **[integration_report.md](./integration_report.md)** — How work was merged
8. **[iosm_report.md](./iosm_report.md)** — Quality gate evaluation

### 2. Study the Task Decomposition

**[plan.md](./plan.md)** shows how a medium-complexity feature breaks down:

- **Phase 0:** Analysis (T01 — Explorer, read-only)
- **Phase 1:** Design (T02 — Architect, ADR)
- **Phase 2:** Implementation (T03-T04 — 2 parallel Implementers)
- **Phase 3:** Testing (T05 — TestRunner)
- **Phase 4:** Integration (T06-T07 — Security + Merge)

### 3. Learn the Orchestration Strategy

**[continuous_dispatch_plan.md](./continuous_dispatch_plan.md)** shows:

- How tasks are classified (background vs foreground)
- File lock conflicts (which tasks can't run in parallel)
- Critical path analysis
- Estimated parallel speedup (1.8x in this example)

### 4. See Subagent Reports

**[reports/T01.md](./reports/T01.md)** demonstrates:
- Performance analysis results
- Recommendations for next tasks
- SpawnCandidates (auto-discovered work)
- IOSM quality checks

**[reports/T03.md](./reports/T03.md)** demonstrates:
- Code implementation details
- Test coverage metrics
- Shared Context updates (knowledge sharing between agents)

### 5. Understand Quality Gates

**[iosm_report.md](./iosm_report.md)** shows IOSM evaluation:

- **Gate-I (Improve):** 0.89 — Code clarity, no duplication
- **Gate-O (Optimize):** 1.0 — Performance targets met, tests passing
- **Gate-M (Modularize):** 1.0 — Clean module boundaries
- **IOSM-Index:** 0.85 ✅

## 🔍 Key Concepts Demonstrated

### 1. Continuous Dispatch

Tasks launched **immediately** when dependencies satisfied (not batched in waves):
- T01 (analysis) → T02 (design) → T03 + T04 (parallel) → T05 (tests)

### 2. File Lock Management

**Conflict detected:**
- T03 touches `cache.py` (new file)
- T04 touches `natal.py` (different file)
- ✅ Can run in parallel (no overlap)

### 3. Auto-Spawn Protocol

**T01 report** identified:
- SC-01: Optimize N+1 query (deferred)
- SC-02: Add cache warming (implemented in T07)

### 4. IOSM Gate Enforcement

**Gate-I failed initially** (0.72 < 0.75):
- Issue: Unclear variable names
- Fix: Renamed `h` → `param_hash` in T07
- Result: Gate-I improved to 0.89 ✅

## 📊 Compare to Your Project

Use this example to understand:

| Aspect | Demo Track | Your Track |
|--------|------------|------------|
| **Complexity** | Medium (7 tasks) | ? |
| **Parallelism** | 2 streams | ? |
| **IOSM-Index** | 0.85 | Target: ≥0.80 |
| **Speedup** | 1.8x (9h vs 16h) | ? |

## 🚀 Run Your Own Track

Based on this example:

```bash
# In Claude Code
/swarm-iosm new-track "Your feature description"

# Claude will:
1. Ask questions (like in PRD.md)
2. Generate plan.md (like this example)
3. Create orchestration_plan.md
4. Launch subagents
5. Generate reports/
6. Enforce IOSM gates
```

## 📚 Related Files

- **Templates used:**
  - `templates/prd.md` → Generated `PRD.md`
  - `templates/plan.md` → Generated `plan.md`
  - `templates/subagent_report.md` → Generated `reports/T*.md`
  - `templates/iosm_gates.md` → Used in `iosm_report.md`

- **Scripts used:**
  - `scripts/orchestration_planner.py` → Generated `continuous_dispatch_plan.md`
  - `scripts/validate_plan.py` → Validated `plan.md` structure
  - `scripts/summarize_reports.py` → Aggregated reports for integration

## ❓ Questions?

Compare your track to this example:

- **Missing files?** Check which templates weren't generated
- **Gates failing?** Compare your scores to 0.89 (Gate-I), 1.0 (Gate-O/M)
- **Too sequential?** Look at dependency graph vs this example's parallelism

## ✅ Validation Checklist

Your track is complete when you have:
- [ ] PRD.md (requirements)
- [ ] spec.md (technical design)
- [ ] plan.md (tasks)
- [ ] reports/ (all tasks)
- [ ] integration_report.md (merge plan)
- [ ] iosm_report.md (gates passed)

**This demo track has all ✅**

---

**Track Status:** COMPLETE ✅
**IOSM-Index:** 0.85 (approved for merge)
**Example Generated:** 2026-01-17
