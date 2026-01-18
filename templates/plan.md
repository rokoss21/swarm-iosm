# Implementation Plan — [Track ID]

**Feature:** [Feature name]
**Track:** [track-id]
**Created:** [YYYY-MM-DD]
**Status:** Planning | In Progress | Integration | Complete

---

## Overview

**Goal:** [One-sentence summary of what this plan achieves]

**Success criteria:** [How we know we're done]

**Estimated complexity:** [Low / Medium / High / Very High]

---

## Task Field Definitions (REQUIRED for Orchestration)

Each task MUST have these fields for automatic wave scheduling:

### Touches
**Purpose:** Detect file conflicts for parallel scheduling

**Format:** Comma-separated relative paths (files or folders)

**Example:** `core/auth.py`, `api/endpoints/`, `tests/test_auth.py`

**Rule:** Tasks with overlapping `touches` will be scheduled sequentially (automatic conflict avoidance)

### Concurrency Class (v1.1)
**Purpose:** Determine lock behavior for continuous dispatch

**Values:**
- `read-only` → No lock needed, always parallel
- `write-local` → Lock on touches, parallel if no overlap
- `write-shared` → Strict sequential execution

**Default:** `write-local` if task modifies files, `read-only` for analysis tasks

### Needs user input
**Purpose:** Choose foreground (interactive) vs background (autonomous) execution

**Values:**
- `true` → Foreground (user decisions needed, dangerous operations, design choices)
- `false` → Background eligible (clear contract, autonomous work, no approvals needed)

**Important:** Background subagents CANNOT ask questions or request permissions mid-execution. All questions must be resolved before launch.

### Effort
**Purpose:** Estimate time and choose background mode

**Values:**
- `S` (Small: <1 hour) → Usually foreground (not worth backgrounding)
- `M` (Medium: 1-4 hours) → Background eligible
- `L` (Large: 4-12 hours) → Background recommended
- `XL` (Extra Large: >12 hours) → Background strongly recommended

**Or specific:** `2h`, `90min`, `30m`

**Rule:** Tasks with `effort >= M` and `needs_user_input = false` will run in background by default.

### Discoveries Expected (v1.1)
**Purpose:** Anticipate what new work may emerge from this task

**Format:** List of likely discovery types

**Example:** `type errors, missing tests, API inconsistencies`

**Usage:** Helps orchestrator anticipate auto-spawn and allocate buffer time

### Auto-spawn Allowed (v1.1)
**Purpose:** Define what subtasks can be auto-created from SpawnCandidates

**Values:**
- `all` → Any subtask can be auto-spawned
- `safe-only` → Only read-only or low-risk subtasks
- `none` → All subtasks require user approval
- Specific types: `tests, docs, lint-fixes, type-annotations`

**Default:** `safe-only`

---

## Gate Targets (v1.1 — REQUIRED for Continuous Dispatch)

Define IOSM gate thresholds that determine when to stop the continuous loop:

```markdown
### Gate Targets

| Gate | Target | Current | Status |
|------|--------|---------|--------|
| Gate-I | ≥0.75 | - | pending |
| Gate-M | pass (no circular deps) | - | pending |
| Gate-O | all tests pass | - | pending |
| Gate-S | N/A | - | skip |

**Continuation rule:** Loop continues until ALL non-skipped gates are met.

**Auto-spawn triggers:**
- Gate-I gap → spawn "improve clarity" tasks
- Gate-M gap → spawn "fix module boundaries" tasks
- Gate-O gap → spawn "fix failing tests" tasks
```

---

## Phases

### Phase 0 — Intake & Repository Analysis (Brownfield Only)

**Goal:** Understand current codebase before making changes

**Tasks:**
- [ ] **T00**: Repository mapping and architecture analysis
  - **Owner role:** Explorer
  - **Depends on:** None
  - **Touches:** [Entire codebase - read-only analysis]
  - **Concurrency class:** read-only
  - **Needs user input:** false
  - **Effort:** M (2-4 hours)
  - **Discoveries expected:** circular deps, dead code, missing tests, undocumented APIs
  - **Auto-spawn allowed:** safe-only
  - **Acceptance:** Architecture map created, dependencies documented
  - **Artifacts:** `reports/T00.md` (repo map), `context/architecture.md`
  - **IOSM checks:** N/A (research only)
  - **Status:** TODO

---

### Phase 1 — Design & Architecture

**Goal:** Establish contracts, interfaces, and architectural decisions before implementation

**Tasks:**

- [ ] **T01**: Design API contracts and interfaces
  - **Owner role:** Architect
  - **Depends on:** T00 (if brownfield)
  - **Touches:** `docs/ADR-XXX.md`, `api/contracts/`, `api_spec.yaml`
  - **Needs user input:** true
  - **Effort:** L (4-6 hours)
  - **Acceptance:**
    - All interfaces defined with types/schemas
    - ADR written for major decisions
    - Contract tests outlined
  - **Artifacts:** `reports/T01.md`, `ADR-XXX.md`, `api_spec.yaml`
  - **IOSM checks:** Gate-M (contracts), Gate-I (clarity)
  - **Status:** TODO

- [ ] **T02**: Database schema design and migration plan
  - **Owner role:** Architect
  - **Depends on:** T01
  - **Touches:** `migrations/`, `models/`, `docs/schema.png`
  - **Needs user input:** true
  - **Effort:** M (3-5 hours)
  - **Acceptance:**
    - Schema diagram created
    - Migration scripts written (forward + rollback)
    - Data integrity constraints defined
  - **Artifacts:** `reports/T02.md`, `migrations/YYYYMMDD_description.sql`, `schema.png`
  - **IOSM checks:** Gate-M (data contracts), Gate-S (minimal schema)
  - **Status:** TODO

- [ ] **T03**: Security and auth design
  - **Owner role:** SecurityAuditor
  - **Depends on:** T01
  - **Touches:** `docs/auth_flow.md`, `docs/threat_model.md`
  - **Needs user input:** false
  - **Effort:** S (2-3 hours)
  - **Acceptance:**
    - Auth flow documented
    - Threat model created
    - Security requirements from PRD addressed
  - **Artifacts:** `reports/T03.md`, `docs/auth_flow.md`, `threat_model.md`
  - **IOSM checks:** Gate-I (security invariants)
  - **Status:** TODO

**Phase 1 Exit Criteria:**
- All contracts and interfaces approved
- ADRs reviewed
- No blockers for implementation

---

### Phase 2 — Implementation

**Goal:** Build the functionality defined in Phase 1

**Parallel Streams:**

#### Stream A: Core Implementation

- [ ] **T04**: Implement core business logic
  - **Owner role:** Implementer-A
  - **Depends on:** T01, T02
  - **Touches:** `core/`, `services/`, `tests/unit/test_core.py`
  - **Needs user input:** false
  - **Effort:** L (8-12 hours)
  - **Acceptance:**
    - All core functions implemented per contract
    - Unit tests written (coverage ≥80%)
    - No hardcoded values (use config)
  - **Artifacts:** `reports/T04.md`, `core/*.py`, `tests/unit/test_core.py`
  - **IOSM checks:** Gate-I (clarity, no duplication), Gate-M (cohesion)
  - **Status:** TODO

#### Stream B: API Layer

- [ ] **T05**: Implement API endpoints
  - **Owner role:** Implementer-B
  - **Depends on:** T01
  - **Touches:** `api/`, `routes/`, `tests/integration/test_api.py`
  - **Needs user input:** false
  - **Effort:** L (6-8 hours)
  - **Acceptance:**
    - All endpoints from spec implemented
    - Request/response validation working
    - API tests passing (integration)
  - **Artifacts:** `reports/T05.md`, `api/*.py`, `tests/integration/test_api.py`
  - **IOSM checks:** Gate-I (clarity), Gate-S (minimal surface)
  - **Status:** TODO

#### Stream C: Database Layer

- [ ] **T06**: Implement data access layer
  - **Owner role:** Implementer-C
  - **Depends on:** T02
  - **Touches:** `models/`, `repositories/`, `tests/integration/test_db.py`
  - **Needs user input:** false
  - **Effort:** M (4-6 hours)
  - **Acceptance:**
    - Models implemented per schema
    - Repository pattern (if applicable)
    - Database tests passing
  - **Artifacts:** `reports/T06.md`, `models/*.py`, `tests/integration/test_db.py`
  - **IOSM checks:** Gate-M (data contracts), Gate-O (query performance)
  - **Status:** TODO

#### Stream D: Frontend/UI (if applicable)

- [ ] **T07**: Implement UI components
  - **Owner role:** Implementer-D
  - **Depends on:** T05 (API must be defined)
  - **Touches:** `frontend/components/`, `frontend/pages/`
  - **Needs user input:** false
  - **Effort:** XL (10-15 hours)
  - **Acceptance:**
    - All screens from UX mockups implemented
    - Responsive design (mobile/desktop)
    - Accessibility (WCAG AA)
  - **Artifacts:** `reports/T07.md`, `frontend/components/*.tsx`
  - **IOSM checks:** Gate-I (clarity), Gate-S (minimal components)
  - **Status:** TODO

**Phase 2 Exit Criteria:**
- All implementation tasks complete
- Unit tests passing
- Code reviewed (if team process)

---

### Phase 3 — Verification & Testing

**Goal:** Ensure implementation meets all requirements and quality gates

**Tasks:**

- [ ] **T08**: Integration testing
  - **Owner role:** TestRunner
  - **Depends on:** T04, T05, T06, T07
  - **Touches:** `tests/integration/`, `test_results.xml`
  - **Needs user input:** false
  - **Effort:** M (4-6 hours)
  - **Acceptance:**
    - All use cases from PRD tested
    - End-to-end flows working
    - Edge cases covered
  - **Artifacts:** `reports/T08.md`, `tests/integration/*.py`, `test_results.xml`
  - **IOSM checks:** Gate-I (tests as spec), Gate-O (performance baselines)
  - **Status:** TODO

- [ ] **T09**: Performance testing
  - **Owner role:** PerfAnalyzer
  - **Depends on:** T08
  - **Touches:** `tests/performance/`, `performance_results.json`
  - **Needs user input:** false
  - **Effort:** M (3-4 hours)
  - **Acceptance:**
    - P50/P95/P99 latency measured
    - Load testing (target RPS achieved)
    - No memory leaks detected
  - **Artifacts:** `reports/T09.md`, `performance_results.json`
  - **IOSM checks:** Gate-O (perf targets met)
  - **Status:** TODO

- [ ] **T10**: Security audit
  - **Owner role:** SecurityAuditor
  - **Depends on:** T04, T05
  - **Touches:** [Read-only scan of implementation files], `security_scan_results.json`
  - **Needs user input:** false
  - **Effort:** S (2-3 hours)
  - **Acceptance:**
    - OWASP top 10 checks pass
    - Auth/authz verified
    - PII handling compliant
  - **Artifacts:** `reports/T10.md`, `security_scan_results.json`
  - **IOSM checks:** Gate-I (security invariants)
  - **Status:** TODO

- [ ] **T11**: Documentation
  - **Owner role:** DocsWriter
  - **Depends on:** T08 (final API stable)
  - **Touches:** `docs/`, `README.md`, `API.md`, `openapi.yaml`
  - **Needs user input:** false
  - **Effort:** M (4-6 hours)
  - **Acceptance:**
    - API docs complete (OpenAPI/Swagger)
    - User guide updated
    - Runbook created (deploy, monitor, troubleshoot)
  - **Artifacts:** `reports/T11.md`, `docs/*.md`, `openapi.yaml`
  - **IOSM checks:** Gate-S (onboarding time)
  - **Status:** TODO

**Phase 3 Exit Criteria:**
- All tests passing
- Performance targets met
- Security scan clean
- Documentation complete

---

### Phase 4 — Integration & Release

**Goal:** Merge all work, run IOSM gates, prepare for deployment

**Tasks:**

- [ ] **T12**: Integration and conflict resolution
  - **Owner role:** Orchestrator (main agent)
  - **Depends on:** All Phase 2-3 tasks
  - **Touches:** `integration_report.md`, [conflict resolution in merged files]
  - **Needs user input:** true
  - **Effort:** M (2-4 hours)
  - **Acceptance:**
    - All subagent reports reviewed
    - File conflicts resolved
    - Integration tests passing
  - **Artifacts:** `integration_report.md`, final merged code
  - **IOSM checks:** All gates (I, O, S, M)
  - **Status:** TODO

- [ ] **T13**: IOSM quality gate evaluation
  - **Owner role:** Orchestrator (main agent)
  - **Depends on:** T12
  - **Touches:** `iosm_report.md`
  - **Needs user input:** false
  - **Effort:** S (1-2 hours)
  - **Acceptance:**
    - All IOSM gates evaluated
    - IOSM-Index calculated
    - Gate failures documented with remediation plan
  - **Artifacts:** `iosm_report.md`
  - **IOSM checks:** Final gate evaluation
  - **Status:** TODO

- [ ] **T14**: Deployment preparation
  - **Owner role:** Implementer (DevOps focus)
  - **Depends on:** T13 (gates passed)
  - **Touches:** `deploy/`, CI/CD configs, `rollback_guide.md`
  - **Needs user input:** true
  - **Effort:** M (3-4 hours)
  - **Acceptance:**
    - Deployment scripts tested
    - Feature flags configured
    - Monitoring/alerts set up
    - Rollback plan validated
  - **Artifacts:** `reports/T14.md`, `deploy/*.sh`, `rollback_guide.md`
  - **IOSM checks:** Gate-M (deployment contracts)
  - **Status:** TODO
  - **Estimated effort:** [e.g., "3-4 hours"]

**Phase 4 Exit Criteria:**
- IOSM-Index ≥ 0.80 (or exceptions documented)
- All artifacts delivered
- Ready for production deployment

---

## Dependency Graph

```
T00 (Repo Analysis - brownfield only)
 ├─> T01 (API Design)
 │    ├─> T03 (Security Design)
 │    ├─> T04 (Core Implementation)
 │    └─> T05 (API Implementation)
 │         └─> T07 (UI Implementation)
 └─> T02 (DB Design)
      └─> T06 (DB Implementation)

T04, T05, T06, T07 --> T08 (Integration Tests)
T08 --> T09 (Performance Tests)
T04, T05 --> T10 (Security Audit)
T08 --> T11 (Documentation)

All Phase 2-3 --> T12 (Integration)
T12 --> T13 (IOSM Gates)
T13 --> T14 (Deployment Prep)
```

---

## Risk Register

| Task | Risk | Impact | Mitigation |
|------|------|--------|------------|
| T04 | Core logic complexity higher than estimated | High | Break into subtasks, add buffer time |
| T05 | API contract changes during implementation | Medium | Freeze contract early, version API |
| T09 | Performance targets not met | High | Profile early, optimize critical paths |
| T12 | Integration conflicts between streams | Medium | Daily sync, shared style guide |

---

## Resource Allocation

| Role | Tasks | Total Effort | Notes |
|------|-------|--------------|-------|
| Explorer | T00 | 2-4h | Brownfield only |
| Architect | T01, T02, T03 | 9-14h | Sequential (design phase) |
| Implementer-A | T04 | 8-12h | Can run parallel with B, C |
| Implementer-B | T05 | 6-8h | Can run parallel with A, C |
| Implementer-C | T06 | 4-6h | Can run parallel with A, B |
| Implementer-D | T07 | 10-15h | Depends on T05 stability |
| TestRunner | T08 | 4-6h | After all implementation |
| PerfAnalyzer | T09 | 3-4h | After integration tests |
| SecurityAuditor | T03, T10 | 4-6h | T03 parallel with design, T10 after impl |
| DocsWriter | T11 | 4-6h | After API stabilizes |
| Main Agent | T12, T13, T14 | 6-10h | Integration phase |

**Total estimated effort:** [Sum ranges, e.g., "60-90 hours"]

---

## Progress Tracking

**Last updated:** [YYYY-MM-DD HH:MM]

**Current phase:** [Phase number]

**Completed tasks:** [X/Y]

**Blockers:**
- [None | List current blockers]

**Next steps:**
1. [Next immediate action]
2. [Following action]

---

## Notes

- Use `/swarm status` to view real-time progress
- Update task status in this file as work progresses
- Blockers should be escalated immediately
- Subagent reports in `reports/` directory

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-01-17 | [Name] | Initial plan |
