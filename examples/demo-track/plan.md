# Implementation Plan — demo-add-caching

**Feature:** Add Redis caching to API endpoints
**Track:** demo-add-caching
**Created:** 2026-01-17
**Status:** In Progress

---

## Overview

**Goal:** Implement caching layer to reduce database load on high-traffic endpoints

**Success criteria:** P95 latency reduced by 50%, cache hit rate >80%

**Estimated complexity:** Medium

---

## Gate Targets

| Gate | Target | Current | Status |
|------|--------|---------|--------|
| Gate-I | ≥0.75 | 0.72 | gap |
| Gate-M | pass | pass | pass |
| Gate-O | tests pass | 2 failing | gap |
| Gate-S | N/A | - | skip |

**Continuation rule:** Loop continues until Gate-I ≥0.75 and Gate-O passes.

---

## Phases

### Phase 0 — Analysis

- [x] **T01**: Analyze current API performance
  - **Owner role:** Explorer
  - **Depends on:** None
  - **Touches:** [read-only analysis]
  - **Concurrency class:** read-only
  - **Needs user input:** false
  - **Effort:** S (1 hour)
  - **Discoveries expected:** slow endpoints, N+1 queries
  - **Auto-spawn allowed:** safe-only
  - **Acceptance:** Performance baseline documented
  - **Artifacts:** `reports/T01.md`
  - **IOSM checks:** N/A
  - **Status:** DONE

### Phase 1 — Design

- [x] **T02**: Design caching strategy
  - **Owner role:** Architect
  - **Depends on:** T01
  - **Touches:** `docs/caching-adr.md`
  - **Concurrency class:** write-local
  - **Needs user input:** true
  - **Effort:** M (2 hours)
  - **Discoveries expected:** cache invalidation patterns
  - **Auto-spawn allowed:** none
  - **Acceptance:** ADR approved, cache keys defined
  - **Artifacts:** `reports/T02.md`, `docs/caching-adr.md`
  - **IOSM checks:** Gate-I, Gate-M
  - **Status:** DONE

### Phase 2 — Implementation

- [ ] **T03**: Implement cache service
  - **Owner role:** Implementer-A
  - **Depends on:** T02
  - **Touches:** `backend/core/cache.py`, `backend/core/__init__.py`
  - **Concurrency class:** write-local
  - **Needs user input:** false
  - **Effort:** M (3 hours)
  - **Discoveries expected:** type errors, missing config
  - **Auto-spawn allowed:** safe-only
  - **Acceptance:** CacheService class implemented, unit tests pass
  - **Artifacts:** `reports/T03.md`
  - **IOSM checks:** Gate-I, Gate-M
  - **Status:** DOING

- [ ] **T04**: Add caching to /api/natal endpoint
  - **Owner role:** Implementer-B
  - **Depends on:** T03
  - **Touches:** `backend/api/natal.py`, `tests/test_natal.py`
  - **Concurrency class:** write-local
  - **Needs user input:** false
  - **Effort:** M (2 hours)
  - **Discoveries expected:** test failures, cache key collisions
  - **Auto-spawn allowed:** safe-only
  - **Acceptance:** Endpoint uses cache, tests pass
  - **Artifacts:** `reports/T04.md`
  - **IOSM checks:** Gate-O
  - **Status:** TODO

- [ ] **T05**: Add caching to /api/transits endpoint
  - **Owner role:** Implementer-C
  - **Depends on:** T03
  - **Touches:** `backend/api/transits.py`, `tests/test_transits.py`
  - **Concurrency class:** write-local
  - **Needs user input:** false
  - **Effort:** M (2 hours)
  - **Discoveries expected:** test failures
  - **Auto-spawn allowed:** safe-only
  - **Acceptance:** Endpoint uses cache, tests pass
  - **Artifacts:** `reports/T05.md`
  - **IOSM checks:** Gate-O
  - **Status:** TODO

### Phase 3 — Verification

- [ ] **T06**: Integration testing
  - **Owner role:** TestRunner
  - **Depends on:** T04, T05
  - **Touches:** `tests/integration/`, `test_results.xml`
  - **Concurrency class:** write-local
  - **Needs user input:** false
  - **Effort:** M (2 hours)
  - **Discoveries expected:** race conditions, cache consistency issues
  - **Auto-spawn allowed:** all
  - **Acceptance:** All integration tests pass
  - **Artifacts:** `reports/T06.md`
  - **IOSM checks:** Gate-O
  - **Status:** TODO

---

## Dependency Graph

```
T01 (Analysis)
 └─> T02 (Design)
      └─> T03 (Cache Service)
           ├─> T04 (Natal caching) ─┐
           └─> T05 (Transits caching) ─┼─> T06 (Integration)
```

---

## Progress Tracking

**Last updated:** 2026-01-17 14:30
**Current phase:** Phase 2 — Implementation
**Completed tasks:** 2/6
**Blockers:** None

**Next steps:**
1. Complete T03 (cache service)
2. Parallel dispatch T04, T05
3. Integration testing T06
