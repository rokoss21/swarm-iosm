# Continuous Dispatch Plan — demo-track

**Generated:** 2026-01-19 01:34
**Mode:** Continuous Scheduling (v1.1)
**Strategy:** Dispatch immediately when READY, no wave barriers

---

## Summary

**Total tasks:** 4
**Estimated time (serial):** 2h 0m
**Estimated time (parallel):** 0h 0m
**Critical path:** T03 → T04 → T06
**Expected speedup:** ~1.0x
**Estimated cost:** $0.53
**Cost breakdown:** 4 sonnet

---

## Continuous Dispatch Rules

1. **CollectReady:** Find tasks with all deps completed
2. **ConflictCheck:** Verify no touches overlap with running tasks
3. **Classify:** Determine background vs foreground
4. **DispatchBatch:** Launch ALL ready tasks in SINGLE message
5. **Monitor:** Check outputs, collect SpawnCandidates
6. **AutoSpawn:** Create new tasks from discoveries
7. **GateCheck:** Continue until Gate targets met

---

## Task Registry

| Task | Role | Model | Concurrency | Mode | Effort | Deps | Touches |
|------|------|-------|-------------|------|--------|------|---------|
| T03 | Implementer-A | sonnet | write-local | BG | M (3 hours) ($0.132) | T02 | `backend/core/cache.py`, `backend/core/__init__.py` |
| T04 | Implementer-B | sonnet | write-local | BG | M (2 hours) ($0.132) | T03 | `backend/api/natal.py`, `tests/test_natal.py` |
| T05 | Implementer-C | sonnet | write-local | BG | M (2 hours) ($0.132) | T03 | `backend/api/transits.py`, `tests/test_transits.py` |
| T06 | TestRunner | sonnet | write-local | BG | M (2 hours) ($0.132) | T04, T05 | `tests/integration/`, `test_results.xml` |

---

## Initial Ready Set

Tasks ready at start (no dependencies):

- **T03**: Implement cache service (background)

**Action:** Launch all in single message

---

## Lock Plan (Touches Conflict Matrix)

No file conflicts detected. All write tasks can run in parallel.

---

## Expected Discoveries (auto-spawn candidates)

Based on `discoveries_expected` fields:

- **T03**: type errors, missing config
- **T04**: test failures, cache key collisions
- **T05**: test failures
- **T06**: race conditions, cache consistency issues

**Auto-spawn rules:**
- **T03**: safe-only
- **T04**: safe-only
- **T05**: safe-only
- **T06**: all

---

## Gate-Driven Continuation

Loop continues until Gate targets met (see plan.md).

**Auto-spawn triggers:**
- Gate-I gap → spawn clarity/duplication fixes
- Gate-M gap → spawn module boundary fixes
- Gate-O gap → spawn test/perf fixes

**Stop conditions:**
- All remaining tasks need user input
- Critical SpawnCandidate found
- Scope creep detected
- Contradiction without policy
- [v1.2] Cost limit exceeded (spent >= 100% of budget)

---

## Orchestrator Instructions

```
1. Initialize iosm_state.md
2. Dispatch initial ready set (single message, parallel)
3. LOOP:
   a. Monitor running tasks (/bashes)
   b. On task completion:
      - Update iosm_state.md (including cost tracking)
      - Check cost budget (v1.2):
        * If spent >= 80% of budget → ⚠️ WARNING
        * If spent >= 100% of budget → 🚨 STOP execution
      - Read SpawnCandidates from report
      - Auto-spawn eligible candidates
      - Release touches locks
      - Recalculate ready queue
   c. Dispatch new ready tasks immediately
   d. Check Gate targets
   e. If gates met → exit loop
   f. If all blocked on user → ask questions
   g. [v1.2] If budget exhausted → STOP and notify user
4. Generate final iosm_report.md
```
