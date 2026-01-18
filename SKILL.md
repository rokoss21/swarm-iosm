---
name: swarm-iosm
version: 1.1.1
description: Orchestrate complex development with AUTOMATIC parallel subagent execution, continuous dispatch scheduling, dependency analysis, file conflict detection, and IOSM quality gates. Analyzes task dependencies, builds critical path, launches parallel background workers with lock management, monitors progress, auto-spawns from discoveries. Use for multi-file features, parallel implementation streams, automated task decomposition, brownfield refactoring, or when user mentions "parallel agents", "orchestrate", "swarm", "continuous dispatch", "automatic scheduling", "PRD", "quality gates", "decompose work", "Mixed/brownfield".
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, AskUserQuestion, TodoWrite
---

# Swarm Workflow (IOSM)

A structured workflow for complex development tasks that combines PRD-driven planning, parallel subagent execution, and IOSM (Improve→Optimize→Shrink→Modularize) quality gates.

## Quick Start

**For new features/projects (Greenfield):**
```
/swarm new-track "Add user authentication with JWT"
```

**For existing codebases (Brownfield):**
```
/swarm setup
/swarm new-track "Refactor payment processing module"
```

**Check progress:**
```
/swarm status
```

## When to Use This Skill

Use Swarm Workflow when:
- Task requires multiple parallel work streams (exploration, implementation, testing, docs)
- Need formal PRD and decomposition for complex features
- Want structured reports and traceability ("who did what and why")
- Brownfield refactoring that needs careful planning and rollback strategy
- Team collaboration requiring artifact-based handoffs
- Quality gates (IOSM) are needed for acceptance

Don't use for:
- Simple single-file changes
- Quick bug fixes
- Exploratory tasks without implementation

## Core Commands

### `/swarm setup`
Initialize project context for Swarm workflow.

**What it does:**
1. Creates `swarm/` directory structure
2. Generates project context files (product.md, tech-stack.md, workflow.md)
3. Initializes tracks.md registry

**When to use:** First time in a project, or when project context has significantly changed.

### `/swarm new-track "<description>"`
Create a new feature/task track with PRD and implementation plan.

**What it does:**
1. Requirements gathering (AskUserQuestion for mode/priorities/constraints)
2. Generate PRD (`swarm/tracks/<id>/PRD.md`)
3. Create spec (`spec.md`) and plan (`plan.md`) with phases/tasks/dependencies
4. Identify subagent roles needed
5. Create metadata.json with track info

**Arguments:** Brief description of the feature/task (e.g., "Add OAuth2 authentication")

### `/swarm implement [track-id]`
Execute the implementation plan using parallel subagents.

**What it does:**
1. Load plan from track
2. Identify parallelizable tasks vs. sequential chains
3. Launch subagents (suggests background for long-running, foreground for interactive)
4. Each subagent produces structured report in `reports/`
5. Monitor progress and collect outputs

**Arguments:** Optional track-id (defaults to most recent track)

### `/swarm status [track-id]`
Show progress summary for a track.

**What it does:**
1. Parse plan.md for task statuses
2. List completed reports
3. Show blockers and open questions
4. Display dependency chain status

### `/swarm integrate <track-id>`
Collect subagent reports and create integration plan.

**What it does:**
1. Read all reports from `swarm/tracks/<id>/reports/`
2. Identify conflicts and resolution strategy
3. Generate integration_report.md with merge order
4. Run IOSM quality gates
5. Create iosm_report.md with gate results and IOSM-Index

### `/swarm revert-plan <track-id>`
Generate rollback guide for a track (does not execute git revert).

**What it does:**
1. Analyze files touched (from reports)
2. Identify commits/changes to revert
3. Suggest checkpoint/branch strategy
4. Create rollback_guide.md with manual steps

## Instructions for Claude

---

## ORCHESTRATOR RESPONSIBILITIES

**CRITICAL:** The main agent (Claude) acts as **ORCHESTRATOR ONLY**. You coordinate subagents but DO NOT do implementation work yourself.

### MANDATORY RULES

#### ✅ ORCHESTRATOR DOES:

1. **Analyze & Plan**
   - Parse `plan.md` and build dependency graph
   - Generate `orchestration_plan.md` with waves/critical path
   - Detect file conflicts and resolve scheduling

2. **Launch Subagents**
   - Create detailed briefs for each subagent (using templates)
   - Launch parallel waves in **single message** (multiple Task tool calls)
   - Default to background mode (unless interactive)
   - Pre-resolve all questions for background tasks

3. **Monitor & Handle Blockers**
   - Use `/bashes` to track background tasks
   - Resume stuck tasks in foreground if needed
   - Apply fallback strategy (retry → resume → recovery task)

4. **Integrate & Gate**
   - Collect all subagent reports
   - Resolve merge conflicts
   - Run IOSM quality gates
   - Generate `integration_report.md` and `iosm_report.md`

5. **Meta-work** (ONLY exception to "no implementation")
   - Update `plan.md` status
   - Fix metadata (`metadata.json`, `tracks.md`)
   - Resolve integration conflicts (merge reports)
   - Generate final reports/docs

#### ❌ ORCHESTRATOR NEVER DOES:

1. **Implementation work:**
   - ❌ Write application code (services, models, API, UI)
   - ❌ Write tests (unit, integration, performance)
   - ❌ Refactor existing code

2. **Analysis work:**
   - ❌ Explore codebase (that's Explorer's job)
   - ❌ Design architecture (that's Architect's job)
   - ❌ Run security scans (that's SecurityAuditor's job)

3. **Specialized work:**
   - ❌ Write documentation (that's DocsWriter's job)
   - ❌ Debug performance (that's PerfAnalyzer's job)

**Exception:** If a task is trivial (<5 min) meta-work (e.g., add entry to `tracks.md`), orchestrator MAY do it. But if it's real logic/code → delegate.

---

### ORCHESTRATION WORKFLOW

```
Phase 0: Requirements Intake
    ↓
Phase 1: PRD Generation
    ↓
Phase 2: Decomposition & Planning (create plan.md)
    ↓
[NEW] Phase 2.5: Orchestration Planning ← AUTOMATIC
    ↓
Phase 3: Subagent Execution (CONTINUOUS DISPATCH) ← v1.1
    ↓
Phase 4: Integration & IOSM Gates
    ↓
Phase 5: Deployment Prep
```

---

## CONTINUOUS DISPATCH LOOP (v1.1 — MANDATORY)

**Ключевое изменение v1.1:** Оркестратор работает в режиме **continuous scheduling** — как только задача становится READY, она запускается немедленно, без ожидания "конца волны".

### Главный принцип

> **"Работай в режиме continuous scheduling: как только появляется READY задача без конфликтов touches и без needs_user_input — немедленно запускай её в background, даже если другие задачи ещё выполняются. После каждого батча собирай SpawnCandidates из отчётов и автоматически добавляй их в backlog. Продолжай цикл, пока не достигнуты заданные IOSM Gate targets."**

### Continuous Orchestration Loop

```
LOOP (до достижения Gate targets):

  1. CollectReady()
     └─ Собрать задачи, у которых deps выполнены

  2. Classify()
     └─ Каждой задаче присвоить режим:
        - background: safe, no user input needed
        - foreground: needs user decision
        - blocked_user: needs_user_input=true, не можем авто-решить
        - blocked_conflict: touches пересекаются с running

  3. ConflictCheck()
     └─ Parallel launch ТОЛЬКО tasks без пересечения touches (для write)
     └─ Read-only tasks ВСЕГДА можно параллелить

  4. DispatchBatch()
     └─ Запустить READY tasks ОДНИМ СООБЩЕНИЕМ (max 3-6 per batch)
     └─ Приоритет: critical_path > high_severity_spawn > read-only_fillers
     └─ Каждый batch получает batch_id для трекинга
     └─ Не ждать "конца волны" — dispatch immediately

  5. Monitor()
     └─ Периодически читать outputs background tasks
     └─ Собирать SpawnCandidates из отчётов

  6. AutoSpawn()
     └─ Если найдены SpawnCandidates → создать новые tasks
     └─ Добавить в backlog и вернуться к шагу 1

  7. GateCheck()
     └─ Проверить условия Gate-I/M/O/S
     └─ Если достигнуты → остановиться + gate-report
     └─ Если нет → авто-spawn remediation tasks и продолжить

END LOOP
```

### Task States (внутренний трекинг)

| State | Описание |
|-------|----------|
| `backlog` | Все известные задачи |
| `ready` | Deps satisfied, можно запускать |
| `running` | Выполняется (background или foreground) |
| `blocked_user` | needs_user_input=true, ждёт решения |
| `blocked_conflict` | touches заняты другой running task |
| `done` | Завершена |

**Правило:** Если задача стала READY в момент, когда другие выполняются — **запускать сразу**, не ждать checkpoint.

### Touches Lock Manager

Для безопасного параллелизма оркестратор должен отслеживать "занятые" файлы:

```
touches_lock: Set[path] = {}

При запуске task:
  1. Проверить: task.touches ∩ touches_lock == ∅ ?
  2. Если да → touches_lock.add(task.touches), запустить
  3. Если нет → blocked_conflict, ждать освобождения

При завершении task:
  1. touches_lock.remove(task.touches)
  2. Пересчитать ready_queue (кто разблокировался?)
```

**Правила конфликтов:**
- `read-only` задачи → **всегда параллельно** (не берут lock)
- `write-local` → параллельно если touches не пересекаются
- `write-shared` → строго последовательно

### Lock Granularity (v1.1.1)

**Иерархия конфликтов:**

```
Lock по ПАПКЕ (core/) конфликтует:
  ├─ с любым lock внутри (core/a.py, core/b.py)
  └─ с lock на саму папку (core/)

Lock по ФАЙЛУ (core/a.py) конфликтует:
  ├─ только с тем же файлом
  └─ с lock на родительскую папку (core/)
```

**Нормализация путей:**
- Всегда использовать `/` (forward slash)
- Убирать trailing slash (`core/` → `core`)
- Приводить к lowercase (для Windows)
- Использовать относительные пути от корня проекта

**Пример проверки конфликта:**
```python
def conflicts(lock_a: str, lock_b: str) -> bool:
    a, b = normalize(lock_a), normalize(lock_b)
    return a == b or a.startswith(b + '/') or b.startswith(a + '/')
```

### Read-Only Safety Rules

**Проблема:** "read-only" задачи могут случайно писать в cache, lockfiles, __pycache__.

**Решение:** read-only задачи ДОЛЖНЫ:
1. НЕ запускать команды, меняющие файлы (`npm install`, `pip install`)
2. Писать временные артефакты ТОЛЬКО в `swarm/tracks/<id>/scratch/`
3. Использовать флаги `--dry-run`, `--check` где возможно

**scratch_dir правило:**
```
swarm/tracks/<track-id>/scratch/   ← read-only tasks пишут сюда
  ├─ T00_analysis.json
  ├─ T03_coverage.xml
  └─ ...
```

Эта папка НЕ требует lock и НЕ конфликтует ни с кем.

### Auto-Background Classification

Оркестратор автоматически классифицирует задачи:

**Auto-background** (safe, запускать без вопросов):
- Concurrency class = `read-only`
- Или `write-local` + `needs_user_input=false` + no policy conflicts
- effort >= M и нет choice points

**Auto-foreground** (нужен пользователь):
- Меняется API контракт/формат ответа
- Нужна "истина" (источники, бизнес-логика, астрология)
- Падают тесты и нужно решить "фиксить код или тест"
- High-risk изменения без тестов
- needs_user_input=true

### SpawnCandidates Protocol

Каждый субагент ОБЯЗАН писать в отчёте секцию `SpawnCandidates`:

```markdown
## SpawnCandidates

При работе обнаружены новые work items:

| ID | Subtask | Touches | Effort | User Input | Severity | Dedup Key | Accept Criteria |
|----|---------|---------|--------|------------|----------|-----------|-----------------|
| SC-01 | Fix missing type annotation in auth.py | `backend/auth.py` | S | false | medium | auth.py|type-annot | mypy passes |
| SC-02 | Clarify API contract for /natal/aspects | `docs/api_spec.yaml` | M | true | high | api_spec|contract | Contract approved |
```

**Dedup Key формат:** `<primary_touch>|<intent_category>`
- Используется для дедупликации одинаковых кандидатов от разных воркеров

**Оркестратор обязан:**
1. После каждого task completion — читать SpawnCandidates
2. **Дедуплицировать** по dedup_key (первый wins)
3. Если `needs_user_input=false` и `severity != critical` → auto-spawn
4. Если `needs_user_input=true` → добавить в blocked_user queue
5. Прогнать новые tasks через планнер и dispatch

### Spawn Protection (v1.1.1)

**Защита от бесконечного размножения задач:**

#### (A) Spawn Budget

В `iosm_state.md` отслеживать:

```markdown
## Spawn Budget
- spawn_budget_total: 20
- spawn_budget_used: 7
- spawn_budget_remaining: 13
- spawn_budget_per_gate:
  - Gate-I: 5 (used: 2)
  - Gate-O: 8 (used: 3)
  - Gate-M: 4 (used: 2)
  - Gate-S: 3 (used: 0)
```

**Правила:**
- При исчерпании budget → STOP, спросить пользователя
- `severity=critical` игнорирует budget (всегда spawn)
- User может увеличить budget командой

#### (B) Dedup Rules

```python
def dedup_key(candidate) -> str:
    return f"{candidate.touches[0]}|{candidate.intent_category}"

# Оркестратор хранит:
seen_dedup_keys: Set[str] = set()

# При обработке SpawnCandidate:
if candidate.dedup_key in seen_dedup_keys:
    skip  # дубль
else:
    seen_dedup_keys.add(candidate.dedup_key)
    process(candidate)
```

#### (C) Severity Threshold

| Severity | Auto-spawn условие |
|----------|-------------------|
| `critical` | ВСЕГДА (даже если budget=0), STOP loop и alert |
| `high` | Если gate fail ИЛИ user запросил |
| `medium` | Если gate fail И budget > 0 |
| `low` | Только по явному запросу user |

#### (D) Anti-Loop Protection

```markdown
## Anti-Loop Metrics (in iosm_state.md)
- loops_without_progress: 0  # сбрасывается при любом task completion
- max_loops_without_progress: 3
- total_loop_iterations: 15
- max_total_iterations: 50
```

**Правило:** Если `loops_without_progress >= 3` → STOP, analyze why stuck

### Gate-Driven Continuation

Оркестратор продолжает LOOP пока не достигнуты Gate targets:

**Обновлять `iosm_state.md` после каждого батча:**

```markdown
# IOSM State — [Track ID]

**Updated:** 2026-01-17 15:30
**Status:** IN_PROGRESS

## Gate Targets (from plan.md)
- Gate-I: ≥0.75 (current: 0.68) ❌
- Gate-M: pass (current: pass) ✅
- Gate-O: tests pass (current: 3 failing) ❌
- Gate-S: N/A

## Auto-Spawn Queue
Based on gate gaps, auto-spawning:
- T15: "Improve naming clarity in core/calculator.py" (Gate-I gap)
- T16: "Fix 3 failing integration tests" (Gate-O gap)

## Blocking Questions (needs user)
- Q1: Should we fix test_natal_aspects.py or update expected values?

## Next Actions
Waiting for T15, T16 to complete. Then re-evaluate gates.
```

**Правила продолжения:**
- Если Gate-I ниже порога → auto-spawn "Improve clarity / reduce duplication"
- Если Gate-O не pass → auto-spawn "fix failing tests"
- Если Gate-M не pass → auto-spawn "remove circular import / clarify boundaries"
- Продолжать пока gates не достигнуты

### Stop Conditions

Оркестратор ОБЯЗАН остановиться и спросить пользователя если:

1. **Все remaining tasks = needs_user_input=true** — нечего делать автономно
2. **Противоречие** — "fix code vs fix tests" без политики
3. **High-risk** — изменение бизнес-логики без источника/эталона
4. **Scope creep** — auto-spawn выходит за рамки PRD
5. **Critical severity** — SpawnCandidate с severity=critical

### Wave Checkpoints (не барьеры)

Waves остаются для **отчётности и checkpoints**, но НЕ для blocking:

```
Wave 1: [T01, T02] — checkpoint для Gate-I review
Wave 2: [T03, T04, T05] — checkpoint для Gate-M review
Wave 3: [T06, T07] — checkpoint для Gate-O review
```

**Но:** Если T03 завершился раньше T02, и T04 depends_on T03 — **запускать T04 сразу**, не ждать Wave 2 checkpoint.

---

### PHASE 2.5: ORCHESTRATION PLANNING (AUTOMATIC)

**Goal:** Transform `plan.md` into executable `orchestration_plan.md` with waves, modes, conflict resolution.

**When:** After `plan.md` is created, before launching subagents.

**Steps:**

1. **Validate plan.md has required fields:**
   ```bash
   python .claude/skills/swarm-iosm/scripts/orchestration_planner.py swarm/tracks/<id>/plan.md --validate
   ```

   Check all tasks have:
   - `Touches` (files/folders)
   - `Needs user input` (true/false)
   - `Effort` (S/M/L/XL or minutes)

   **If missing:** Tasks without these fields CANNOT be auto-scheduled. Ask user to add them OR infer from context.

2. **Generate orchestration plan:**
   ```bash
   python .claude/skills/swarm-iosm/scripts/orchestration_planner.py swarm/tracks/<id>/plan.md --generate
   ```

   This creates `swarm/tracks/<id>/orchestration_plan.md` with:
   - Dependency graph
   - Critical path (longest path through dependencies)
   - Execution waves (parallel grouping)
   - File conflict matrix
   - Background readiness checklist
   - Time estimates (serial vs parallel)

3. **Review with user:**
   Show orchestration plan summary:
   ```
   Generated orchestration plan:
   - 5 waves (14 tasks total)
   - Wave 1: 1 task (Explorer, background)
   - Wave 2: 3 tasks parallel (Architects, foreground)
   - Wave 3: 3 tasks parallel (Implementers, background)
   - Wave 4: 3 tasks (Tests, background)
   - Wave 5: 3 tasks (Integration, mixed)

   Estimated time: 27-42h parallel (vs 60-80h serial)
   Speedup: ~1.8x

   Ready to execute? (yes/no)
   ```

4. **Pre-resolve questions for background tasks:**
   For each task marked `needs_user_input: false` but you suspect may need decisions:
   - Use AskUserQuestion NOW (before launching)
   - Document answers in subagent brief

   **Example:**
   ```
   Wave 3 has 3 background implementers.
   Before launching background tasks, let me clarify:

   [AskUserQuestion with 2-3 questions about API design, error handling, testing strategy]

   These answers will be included in subagent briefs so they can work autonomously.
   ```

**Output:** `orchestration_plan.md` ready, all questions resolved, ready for Phase 3 execution.

---

### Phase 1: Requirements Intake (Universal)

When user invokes `/swarm new-track` or triggers this Skill:

1. **Determine mode** using AskUserQuestion:
   - Greenfield (new feature from scratch)
   - Brownfield (modify existing codebase)

2. **If Brownfield:** Suggest Plan mode first:
   ```
   "I recommend starting in Plan mode (read-only exploration) to safely analyze the codebase before making changes. Shall I proceed with Plan mode first?"
   ```
   - If yes: Use Task tool with Explore agent to map codebase
   - If no: Proceed with caution warnings

3. **Gather requirements** using AskUserQuestion for:
   - **Priority**: Speed / Quality / Cost
   - **Change strictness**: Safe (minimal changes) / Normal / Aggressive refactor
   - **Test strategy**: TDD (tests first) / Post-tests / Smoke only
   - **Permissions**: What tools/operations are allowed

4. **Ask text questions** for:
   - Goal: "What defines 'done' for this task? (1-2 sentences)"
   - Context: "Product/users/environment context?"
   - Constraints: "Tech stack, versions, deadlines, restrictions?"
   - Interfaces: "API/UI/CLI changes needed?"
   - Data: "Data sources, migrations, PII concerns?"
   - Risks: "What could go wrong?"
   - Definition of Done: "Tests? Docs? Deployment?"

5. **Save intake** to `swarm/tracks/<track-id>/intake.md`

### Phase 2: PRD Generation

Using intake data, generate `swarm/tracks/<track-id>/PRD.md` following template:

```markdown
# PRD: <Feature Name>
## 1. Problem
## 2. Goals / Non-goals
## 3. Users & Use-cases
## 4. Scope (MVP / Later)
## 5. Requirements
### Functional
### Non-functional
## 6. UX / API / Data
## 7. Risks & Mitigations
## 8. Acceptance Criteria
## 9. Rollout / Migration plan
## 10. IOSM Targets (Gates + expected index delta)
```

See [templates/prd.md](templates/prd.md) for detailed template.

### Phase 3: Decomposition & Planning

From PRD, create `spec.md` and `plan.md`:

**spec.md** (Conductor-style):
- Context
- What / Why
- Constraints
- Out of scope
- Acceptance tests
- Artifacts to produce
- Rollback assumptions

**plan.md** (WBS with dependencies):
- Phases (0: Intake, 1: Design, 2: Implementation, 3: Verification, 4: Integration)
- Tasks with:
  - owner_role (Explorer/Architect/Implementer/TestRunner/etc)
  - depends_on (task IDs)
  - files_modules (scope)
  - acceptance criteria
  - artifacts (reports/T01.md, etc)
  - iosm_checks (which gates apply)
  - status (TODO/DOING/DONE/BLOCKED)

See [templates/plan.md](templates/plan.md) for structure.

### Phase 3: Subagent Execution

**Goal:** Execute `orchestration_plan.md` using parallel waves of subagents.

**CRITICAL:** Launch subagents in PARALLEL WAVES, not one-by-one.

---

#### Standardized Subagent Roles

Use these predefined roles:

1. **Explorer** (brownfield analysis)
   - Tools: Read, Grep, Glob
   - Output: Architecture map, dependencies, test coverage, code style
   - When: Always for brownfield, before making changes

2. **Architect** (design decisions)
   - Tools: Read, Write (ADRs)
   - Output: ADR documents, interface contracts, API specs
   - When: Complex features, API changes, architectural decisions

3. **Implementer-{A,B,C}** (parallel implementation)
   - Tools: Read, Write, Edit, Bash (tests)
   - Output: Code changes, unit tests, implementation report
   - When: Independent modules that can be developed in parallel

4. **TestRunner** (verification)
   - Tools: Read, Bash, Write
   - Output: Test results, coverage report, failure analysis
   - When: After implementation, before integration

5. **SecurityAuditor** (security review)
   - Tools: Read, Grep, Bash (security scanners)
   - Output: Security findings, remediation suggestions
   - When: Auth/payment features, external APIs, data handling

6. **PerfAnalyzer** (performance review)
   - Tools: Read, Bash (profiling)
   - Output: Performance metrics, bottleneck analysis
   - When: Data processing, APIs, high-traffic features

7. **DocsWriter** (documentation)
   - Tools: Read, Write, Edit
   - Output: README updates, API docs, user guides
   - When: Public APIs, complex features, user-facing changes

**Parallelization Rules:**

✅ **Parallel (can run simultaneously):**
- Different modules/files with no shared state
- Independent research tasks (Explorer on different subsystems)
- Docs + Implementation (if API is stable)
- Multiple Implementers on separate components

❌ **Sequential (must run in order):**
- Tasks with dependencies (Architect → Implementer)
- Shared file modifications (two agents editing same file)
- Test → Fix → Re-test cycles

**Background vs Foreground:**

Use **background** (`run_in_background: true` in Task tool) when:
- Long-running operations (tests, builds, analysis)
- No user input needed (all questions resolved upfront)
- Permissions pre-approved
- Can tolerate "fire and forget" mode

Use **foreground** (default) when:
- Need user clarifications during execution
- Interactive debugging/problem-solving
- Permission escalations expected
- Results needed immediately for next step

**IMPORTANT:** Background subagents cannot use AskUserQuestion (tool call will fail). Resolve all questions BEFORE launching background tasks.

### Background Limitations (CRITICAL)

**Background subagents CANNOT reliably use:**

| Tool/Feature | Status | Reason |
|--------------|--------|--------|
| `AskUserQuestion` | BLOCKED | Auto-denied, no user interaction |
| Permission prompts | BLOCKED | Auto-denied, may fail silently |
| MCP tools | UNSTABLE | May be unavailable in background context |
| External APIs | RISKY | Network errors not recoverable |
| Long git operations | RISKY | May timeout or conflict |

**Rule of thumb:**
- **Background** = autonomous code/tests/read/local-only operations
- **Foreground** = MCP, external integrations, user decisions, risky operations

**Pre-flight checklist for background tasks:**
1. All questions pre-resolved in brief
2. No MCP tools required
3. No external API calls (or wrap with fallback)
4. No interactive permissions needed
5. Touches clearly defined (no surprises)

**If task needs MCP or external calls → force foreground:**
```markdown
- **Needs user input:** true  ← even if technically "safe"
- **Note:** Requires MCP/external API, must run foreground
```

---

#### Step 1: Load Orchestration Plan

Read `swarm/tracks/<id>/orchestration_plan.md` to understand:
- How many waves
- Which tasks in each wave
- Which tasks are parallel vs sequential
- Which tasks are background vs foreground

---

#### Step 2: Execute Waves (ONE WAVE AT A TIME)

For each wave in the orchestration plan:

##### A. Prepare Subagent Briefs

For each task in the wave:
1. Generate brief using [templates/subagent_brief.md](templates/subagent_brief.md)
2. Fill in all sections:
   - Goal, Scope, Context
   - Dependencies (what previous tasks delivered)
   - Constraints (technical, performance, security)
   - Output contract (code + tests + report)
   - Verification steps
   - Acceptance criteria
   - **Pre-resolved questions** (for background tasks)
   - IOSM checks to pass

3. Include report template requirement:
   ```
   You MUST save report to: swarm/tracks/<id>/reports/<task-id>.md
   Use template: .claude/skills/swarm-iosm/templates/subagent_report.md
   ```

##### B. Launch Wave (CRITICAL: PARALLEL IN SINGLE MESSAGE)

**For parallel tasks in wave:**

Launch ALL tasks in wave SIMULTANEOUSLY using **single message with multiple Task tool calls**.

**Example (Wave 3: 3 implementers):**

```
I'm launching Wave 3 with 3 parallel implementers (all background):

[Single message with 3 Task tool calls]

Task 1 (T04 - Implementer-A):
- subagent_type: general-purpose
- description: Implement core business logic
- prompt: [Full brief for T04]
- run_in_background: true

Task 2 (T05 - Implementer-B):
- subagent_type: general-purpose
- description: Implement API endpoints
- prompt: [Full brief for T05]
- run_in_background: true

Task 3 (T06 - Implementer-C):
- subagent_type: general-purpose
- description: Implement data access layer
- prompt: [Full brief for T06]
- run_in_background: true

Monitoring: Use /bashes to track progress
Expected completion: 8-12 hours
```

**NEVER launch tasks one-by-one if they can run parallel. ALWAYS use single message.**

##### C. Monitor Progress

While wave is running:

1. **Check background tasks periodically:**
   ```
   /bashes
   ```

2. **Check task output files (if provided):**
   ```bash
   tail -n 50 /path/to/task/output/file
   ```

3. **If task completes:**
   - Verify report exists: `swarm/tracks/<id>/reports/T##.md`
   - Check acceptance criteria met
   - Mark status in `plan.md`: `Status: DONE`

4. **If task blocks/fails:**
   - Apply fallback strategy (see below)

##### D. Fallback Strategy (if subagent fails)

**Scenario 1: Transient error (timeout, network)**
- **Action:** Retry once automatically
- **Command:** Re-launch same brief

**Scenario 2: Permission/question blocker**
- **Action:** Resume in foreground
- **How:** Use TaskOutput to get task_id, then Task tool with resume parameter
- **Example:**
  ```
  Task blocked on permission for "run database migrations"
  → Resume in foreground, approve permission, continue
  ```

**Scenario 3: Logic gap (unclear contract/spec)**
- **Action:** Create recovery task
- **Steps:**
  1. Create new task for Architect: "Clarify [missing requirement]"
  2. Run Architect task (foreground)
  3. Update brief for blocked task
  4. Re-launch subagent

**Scenario 4: Unrecoverable failure**
- **Action:** Mark BLOCKED and continue
- **Steps:**
  1. Update `plan.md`: `Status: BLOCKED(reason: ...)`
  2. Save partial work in `reports/T##-partial.md`
  3. Add to integration report: "T## blocked, manual resolution needed"
  4. Continue with other waves (don't block entire workflow)

---

#### Step 3: Wave Completion Check

Before proceeding to next wave:

- [ ] All tasks in wave completed OR marked BLOCKED
- [ ] All reports saved to `reports/`
- [ ] No merge conflicts detected (if parallel edits)
- [ ] All acceptance criteria met (or exceptions documented)

**If wave has blockers:**
- Document in `orchestration_plan.md` (update Progress section)
- Decide: resolve now OR defer to integration phase

---

#### Step 4: Proceed to Next Wave

Repeat Step 2 for next wave.

**Important:**
- Respect dependencies: Wave N can only start when all Wave N-1 tasks are DONE or BLOCKED
- Update `orchestration_plan.md` with actual completion times (for future estimation)

---

#### Step 5: All Waves Complete

When all waves finished:
- Update `plan.md`: `Status: Integration`
- Proceed to Phase 4 (Integration & IOSM Gates)

---

#### PARALLEL LAUNCH EXAMPLES

**Example 1: Wave 2 (3 foreground tasks)**

```
Launching Wave 2 (Design phase) with 3 tasks:

[Single message with 3 Task calls, all foreground]

These tasks will run interactively (you'll see their prompts).
Expected: ~4-6 hours for slowest task (T01)
```

**Example 2: Wave 3 (3 background tasks)**

```
Launching Wave 3 (Implementation) with 3 background tasks:

[Single message with 3 Task calls, all run_in_background: true]

Monitor with: /bashes
Check outputs in: swarm/tracks/2026-01-17-001/reports/
```

**Example 3: Mixed wave (2 parallel + 1 sequential)**

```
Wave 4a: Launching 2 parallel tasks (T08, T10):

[Single message with 2 Task calls, background]

When T08 completes, I'll launch Wave 4b (T09 depends on T08).
```

### Phase 4: Integration & IOSM Gates

After subagents complete:

1. **Read all reports** from `swarm/tracks/<id>/reports/`
2. **Validate** each report has required sections (see templates/subagent_report.md)
3. **Identify conflicts:**
   - File modification overlaps
   - Contradictory decisions
   - Dependency mismatches
4. **Generate integration_report.md** with:
   - What changed (by task)
   - Conflict resolutions
   - Merge order (respecting dependencies)
   - Final verification checklist
   - Rollback guide

See [templates/integration_report.md](templates/integration_report.md).

#### IOSM Quality Gates Evaluation

After integration_report.md is complete, run IOSM gates on integrated result:

**Gate-I (Improve):**
- Semantic clarity ≥0.95 (clear naming, no magic numbers)
- Code duplication ≤5%
- Invariants documented
- All TODOs tracked

**Gate-O (Optimize):**
- P50/P95/P99 latency measured
- Error budget defined
- Basic chaos/resilience tests passing
- No obvious N+1 queries or memory leaks

**Gate-S (Shrink):**
- API surface reduced ≥20% (or justified growth)
- Dependency count stable or reduced
- Onboarding time ≤15min for new contributor

**Gate-M (Modularize):**
- Clear module contracts
- Change surface ≤20% (localized impact)
- Coupling/cohesion metrics acceptable
- No circular dependencies

**Calculate IOSM-Index:**
```
IOSM-Index = (Gate-I + Gate-O + Gate-S + Gate-M) / 4
```

Target: ≥0.80 for production merge.

Generate `swarm/tracks/<id>/iosm_report.md` with gate results.

See [templates/iosm_gates.md](templates/iosm_gates.md) for detailed criteria.

## File Structure

The Skill creates this structure:

```
.claude/skills/swarm-iosm/     # Skill definition
  SKILL.md                      # This file
  templates/                    # Progressive disclosure templates
  scripts/                      # Validation/analysis scripts

swarm/                          # Project workflow data
  context/                      # Project-wide context
    product.md
    tech-stack.md
    workflow.md
  tracks/                       # Feature/task tracks
    <YYYY-MM-DD-NNN>/          # Track directory
      intake.md                 # Requirements intake
      PRD.md                    # Product requirements
      spec.md                   # Technical spec
      plan.md                   # Implementation plan
      metadata.json             # Track metadata
      reports/                  # Subagent reports
        T01.md
        T02.md
        ...
      integration_report.md     # Integration plan
      iosm_report.md           # Quality gate results
      rollback_guide.md        # Revert instructions (if needed)
  tracks.md                     # Track registry/index
```

## Best Practices

1. **Always resolve questions upfront** - Background subagents can't ask questions
2. **Use Plan mode for brownfield** - Safe exploration before changes
3. **Parallelize research, sequence implementation** - Avoid file conflicts
4. **Demand structured reports** - Traceability and integration depend on it
5. **Run IOSM gates before merge** - Quality enforcement
6. **Create rollback plans** - Safety net for production changes
7. **Use TodoWrite** - Track overall Swarm workflow progress
8. **Monitor background tasks** - Use `/bashes` command

## Common Patterns

### Pattern 1: Greenfield Feature
```
/swarm new-track "Add email notification system"
→ Intake (quick, no repo analysis)
→ PRD + Plan generation
→ Parallel: Architect (API design) + DocsWriter (email templates)
→ Sequential: Implementer (core) → TestRunner → Integration
```

### Pattern 2: Brownfield Refactor
```
/swarm setup
/swarm new-track "Refactor payment processing"
→ Plan mode: Explorer analyzes payment module
→ Architect creates migration plan
→ Parallel: Implementer-A (new code) + TestRunner (regression tests)
→ Integration with rollback guide
```

### Pattern 3: Large Feature with Many Tasks
```
/swarm new-track "Multi-tenant architecture"
→ Generate plan with 15+ tasks
→ Phase 1: Sequential design (Architect → review)
→ Phase 2: Parallel implementation (3x Implementer background)
→ Phase 3: Sequential integration (merge → test → gates)
```

## Troubleshooting

**Background subagent fails with permission error:**
- Resume in foreground: Find task in `/bashes`, get task ID, resume
- Pre-approve permissions: Use AskUserQuestion before launching

**Reports missing or incomplete:**
- Subagent brief must explicitly require report template
- Validate reports using `scripts/summarize_reports.py`

**File conflicts during integration:**
- Plan should minimize shared file edits
- Use git branches per subagent (advanced)
- Integration report must resolve conflicts manually

**IOSM gates failing:**
- Review gate criteria in templates/iosm_gates.md
- Some gates may be aspirational (document exceptions)
- Iterate: fail → fix → re-check

## Advanced Usage

See additional documentation:
- [templates/](templates/) - All templates with detailed examples
- [scripts/](scripts/) - Helper scripts for validation and analysis

## Dependencies

- Claude Code with Task tool support
- Git (for version control and rollback)
- Project-specific: Python/Node/etc for running tests

## Version

Swarm Workflow (IOSM) v1.1.1 - 2026-01-17

**v1.1 Changes:**
- Continuous Dispatch Loop (не ждём волну — запускаем сразу при READY)
- Gate-driven continuation (работаем до достижения Gate targets)
- Auto-spawn из SpawnCandidates в отчётах
- Touches lock manager (конфликты файлов)
- iosm_state.md для трекинга прогресса к гейтам

**v1.1.1 Changes:**
- Lock Granularity (folder vs file hierarchy, path normalization)
- Read-Only Safety Rules (scratch_dir для артефактов)
- Spawn Protection (budget, dedup keys, severity threshold)
- Anti-Loop Protection (max iterations, progress tracking)
- Batch Constraints (max 3-6 per batch, priority ordering, batch_id)
- Touched Actual tracking (plan vs actual diff, unplanned touches alert)
- Operational Runbook в QUICKSTART.md
