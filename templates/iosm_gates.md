# IOSM Quality Gates — Detailed Criteria

**Based on:** IOSM methodology (Improve → Optimize → Shrink → Modularize)
**Purpose:** Enforce quality standards before production deployment
**Target IOSM-Index:** ≥0.80 for production merge

---

## Overview

The IOSM framework provides four quality gates that must be evaluated before integrating code:

1. **Gate-I (Improve)** - Code clarity and maintainability
2. **Gate-O (Optimize)** - Performance and resilience
3. **Gate-S (Shrink)** - Minimal surface area and complexity
4. **Gate-M (Modularize)** - Clean boundaries and contracts

Each gate is scored 0.0-1.0, and the IOSM-Index is the average of all four gates.

---

## Gate-I: Improve (Code Quality & Clarity)

**Philosophy:** Code should be self-documenting, consistent, and free of technical debt.

### Criteria

#### I-1: Semantic Clarity (Weight: 30%)
**Target:** ≥0.95

**Measurement:**
```python
# Good (score: 1.0)
def calculate_user_subscription_price(user_id: str, plan: str) -> Decimal:
    """Calculate monthly subscription price for user."""
    base_price = get_plan_base_price(plan)
    discount = get_user_discount(user_id)
    return base_price * (1 - discount)

# Bad (score: 0.3)
def calc(u, p):
    b = gp(p)
    d = gd(u)
    return b * (1 - d)
```

**Checklist:**
- [ ] All functions/classes have descriptive names (no abbreviations except domain-standard)
- [ ] Variable names explain intent (not just type: `user_id` not `uid`)
- [ ] No single-letter variables except in tight loops (`i`, `j` acceptable for indices)
- [ ] Magic numbers extracted to named constants
- [ ] Constants use UPPER_SNAKE_CASE
- [ ] Boolean variables/functions named as questions (`is_valid`, `has_permission`)

**Auto-check:**
```bash
# Use linting tools
pylint src/ --disable=all --enable=invalid-name,bad-naming
# Score = (passing items / total items)
```

---

#### I-2: Code Duplication (Weight: 25%)
**Target:** ≤5% duplicate code

**Measurement:**
```bash
# Use duplication detection tools
radon cc src/ -a -s
# Or
jscpd src/
# Score = max(0, 1 - (duplication% / 5%))
# Example: 3% duplication → score = 1 - (3/5) = 0.4 → scaled to 1.0 range = 0.8
```

**Checklist:**
- [ ] No copy-pasted code blocks (DRY principle)
- [ ] Common patterns extracted to functions/classes
- [ ] Shared logic in utility modules
- [ ] Similar code unified with parameters (not duplicated)

**Exceptions:**
- Test setup code (acceptable duplication)
- Trivial getters/setters (acceptable duplication)

---

#### I-3: Invariants Documented (Weight: 25%)
**Target:** 100% of public APIs

**Measurement:**
```python
# Good (score: 1.0)
def divide(numerator: float, denominator: float) -> float:
    """Divide two numbers.

    Args:
        numerator: The dividend
        denominator: The divisor

    Returns:
        The quotient

    Raises:
        ValueError: If denominator is zero

    Preconditions:
        - denominator != 0

    Postconditions:
        - result = numerator / denominator
    """
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator

# Bad (score: 0.0) - no preconditions documented
def divide(a, b):
    return a / b  # Will crash on b=0
```

**Checklist:**
- [ ] All public functions have docstrings
- [ ] Docstrings include preconditions (what must be true before calling)
- [ ] Docstrings include postconditions (what will be true after calling)
- [ ] Exception cases documented
- [ ] Type hints present (Python 3.6+)

**Auto-check:**
```bash
# Check docstring coverage
interrogate src/ -v
# Score = docstring coverage %
```

---

#### I-4: TODOs Tracked (Weight: 20%)
**Target:** 0 untracked TODOs

**Measurement:**
```bash
# Find all TODOs in code
grep -r "TODO\|FIXME\|HACK" src/

# Each TODO should reference a ticket
# Good:
# TODO(JIRA-123): Optimize this query

# Bad:
# TODO: fix this later
```

**Checklist:**
- [ ] All TODOs reference a ticket/issue (e.g., `TODO(JIRA-123)`)
- [ ] No FIXMEs or HACKs without tickets
- [ ] Temporary code has expiry date (`TODO(2026-02-01): Remove feature flag`)

**Auto-check:**
```bash
# Count untracked TODOs
untracked=$(grep -r "TODO\|FIXME" src/ | grep -v "TODO(" | wc -l)
# Score = (untracked == 0) ? 1.0 : 0.0
```

---

### Gate-I Score Calculation

```
Gate-I = 0.30 * I-1 + 0.25 * I-2 + 0.25 * I-3 + 0.20 * I-4
```

**Pass threshold:** ≥0.85 (Excellent), ≥0.70 (Acceptable), <0.70 (Needs work)

---

## Gate-O: Optimize (Performance & Resilience)

**Philosophy:** Code should perform well under load and gracefully handle failures.

### Criteria

#### O-1: Latency Targets (Weight: 35%)
**Target:** Meet P50/P95/P99 targets from PRD

**Measurement:**
```bash
# Run performance benchmarks
pytest tests/perf/ --benchmark-only

# Compare to targets
# Example targets:
# P50: <100ms
# P95: <200ms
# P99: <500ms
```

**Checklist:**
- [ ] P50 latency measured and < target
- [ ] P95 latency measured and < target
- [ ] P99 latency measured and < target
- [ ] No obvious inefficiencies (N+1 queries, unnecessary loops)

**Scoring:**
```
For each percentile (P50, P95, P99):
  score_p = max(0, 1 - (actual - target) / target)

Gate-O-1 = (score_p50 + score_p95 + score_p99) / 3
```

---

#### O-2: Error Budget (Weight: 25%)
**Target:** Error rate < defined budget (typically 0.1%-1%)

**Measurement:**
```bash
# Run integration tests with fault injection
pytest tests/integration/ --chaos-mode

# Measure error rate
errors = failed_requests / total_requests
```

**Checklist:**
- [ ] Error handling present for all external calls
- [ ] Retries with exponential backoff for transient errors
- [ ] Circuit breaker pattern for cascading failures
- [ ] Graceful degradation when dependencies fail

**Scoring:**
```
If error_rate <= budget:
  score = 1.0
Else:
  score = max(0, 1 - (error_rate - budget) / budget)
```

---

#### O-3: Resource Efficiency (Weight: 20%)
**Target:** Memory/CPU within acceptable limits

**Measurement:**
```bash
# Profile memory usage
memory_profiler tests/perf/benchmark.py

# Profile CPU usage
py-spy record -o profile.svg -- python tests/perf/benchmark.py
```

**Checklist:**
- [ ] No memory leaks (memory stable over time)
- [ ] Memory usage < [defined limit, e.g., 500MB per instance]
- [ ] CPU usage reasonable (no infinite loops, efficient algorithms)
- [ ] Database connections properly pooled and closed

**Scoring:**
```
memory_score = (memory_used <= limit) ? 1.0 : 0.5
cpu_score = (cpu_usage <= limit) ? 1.0 : 0.5
leak_score = (no_leaks) ? 1.0 : 0.0

Gate-O-3 = (memory_score + cpu_score + leak_score) / 3
```

---

#### O-4: Chaos/Resilience Tests (Weight: 20%)
**Target:** System withstands common failures

**Measurement:**
```bash
# Test resilience scenarios
pytest tests/chaos/
# - Single instance failure
# - Database connection loss
# - Network partition
# - High load (10x normal)
```

**Checklist:**
- [ ] Withstands single instance failure (if distributed)
- [ ] Recovers from database connection loss
- [ ] Handles network timeouts gracefully
- [ ] Survives 10x load spike (degrades gracefully)

**Scoring:**
```
scenarios_passed / total_scenarios
```

---

### Gate-O Score Calculation

```
Gate-O = 0.35 * O-1 + 0.25 * O-2 + 0.20 * O-3 + 0.20 * O-4
```

**Pass threshold:** ≥0.75 (Excellent), ≥0.60 (Acceptable), <0.60 (Needs work)

---

## Gate-S: Shrink (Minimal Surface & Complexity)

**Philosophy:** Less is more. Minimize API surface, dependencies, and onboarding friction.

### Criteria

#### S-1: API Surface Area (Weight: 40%)
**Target:** ≤N endpoints (or justify growth)

**Measurement:**
```bash
# Count public API endpoints/functions
# For REST API:
grep -r "@app.route\|@router" src/ | wc -l

# For library:
grep -r "^def [^_]" src/ | wc -l  # Public functions (no leading underscore)
```

**Checklist:**
- [ ] Only necessary endpoints exposed
- [ ] No duplicate endpoints (consolidate similar operations)
- [ ] Private/internal functions prefixed with `_`
- [ ] API versioned if breaking changes expected

**Scoring:**
```
If api_surface <= baseline:
  score = 1.0
Else if justified:
  score = 0.8  # Growth is justified
Else:
  score = max(0, 1 - (api_surface - baseline) / baseline)
```

---

#### S-2: Dependency Count (Weight: 30%)
**Target:** Stable or reduced dependencies

**Measurement:**
```bash
# Count dependencies
# Python:
pip list --format=freeze | wc -l

# Node:
npm list --depth=0 | wc -l
```

**Checklist:**
- [ ] No unnecessary dependencies added
- [ ] Dependencies well-maintained (not abandoned)
- [ ] Dependencies security-scanned (no known CVEs)
- [ ] Prefer standard library over external deps

**Scoring:**
```
If dependency_count <= baseline:
  score = 1.0
Else:
  growth_rate = (dependency_count - baseline) / baseline
  score = max(0, 1 - growth_rate)
```

---

#### S-3: Onboarding Time (Weight: 30%)
**Target:** ≤15 minutes for new contributor to run project

**Measurement:**
```bash
# Time a new developer from:
# - Clone repo
# - Install dependencies
# - Run tests
# - See working demo

# Target: ≤15 min
```

**Checklist:**
- [ ] README has quick start (single command to run)
- [ ] Dependencies install without issues
- [ ] Tests run without manual setup
- [ ] No hidden configuration required

**Scoring:**
```
If onboarding_time <= 15 min:
  score = 1.0
Else:
  score = max(0, 1 - (onboarding_time - 15) / 15)
```

---

### Gate-S Score Calculation

```
Gate-S = 0.40 * S-1 + 0.30 * S-2 + 0.30 * S-3
```

**Pass threshold:** ≥0.80 (Excellent), ≥0.65 (Acceptable), <0.65 (Needs work)

---

## Gate-M: Modularize (Clean Boundaries & Contracts)

**Philosophy:** Code should have clear module boundaries with well-defined contracts.

### Criteria

#### M-1: Module Contracts (Weight: 30%)
**Target:** 100% of modules have defined contracts

**Measurement:**
```python
# Good (score: 1.0) - Clear contract
class PaymentProcessor:
    """Process payments via external gateway.

    Contract:
    - Input: payment_request (validated PaymentRequest object)
    - Output: payment_result (PaymentResult with transaction_id)
    - Errors: PaymentError, ValidationError
    - Idempotency: Yes (retry-safe via idempotency_key)
    - SLA: P95 < 500ms
    """
    def process_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        ...

# Bad (score: 0.0) - No contract
def pay(data):
    ...
```

**Checklist:**
- [ ] All modules have documented interfaces
- [ ] Contracts include input/output types
- [ ] Error conditions documented
- [ ] Idempotency guarantees stated
- [ ] Performance characteristics stated (if relevant)

**Scoring:**
```
modules_with_contracts / total_modules
```

---

#### M-2: Change Surface (Weight: 25%)
**Target:** ≤20% of codebase touched by change

**Measurement:**
```bash
# Calculate change surface
total_files=$(find src/ -name "*.py" | wc -l)
changed_files=$(git diff --name-only main | wc -l)
change_surface=$(echo "scale=2; $changed_files / $total_files" | bc)
```

**Checklist:**
- [ ] Changes localized to relevant modules
- [ ] No widespread refactoring (unless that's the goal)
- [ ] Core/shared code stable (minimal changes)

**Scoring:**
```
If change_surface <= 0.20:
  score = 1.0
Else:
  score = max(0, 1 - (change_surface - 0.20) / 0.20)
```

---

#### M-3: Coupling Analysis (Weight: 25%)
**Target:** Low coupling (few dependencies between modules)

**Measurement:**
```bash
# Use dependency analysis tools
# Python:
pydeps src/ --show-deps

# Check:
# - Afferent coupling (Ca): How many modules depend on this
# - Efferent coupling (Ce): How many modules this depends on
# - Instability (I): Ce / (Ca + Ce)

# Target: Average I = 0.3-0.7 (balanced)
```

**Checklist:**
- [ ] No circular dependencies (DAG structure)
- [ ] Core modules have low efferent coupling (don't depend on many things)
- [ ] Utility modules have high afferent coupling (many depend on them, they depend on few)

**Scoring:**
```
circular_deps = count_circular_dependencies()
If circular_deps == 0:
  base_score = 1.0
Else:
  base_score = max(0, 1 - circular_deps * 0.2)

# Adjust for instability
avg_instability = calculate_average_instability()
If 0.3 <= avg_instability <= 0.7:
  instability_score = 1.0
Else:
  instability_score = 0.7

Gate-M-3 = (base_score + instability_score) / 2
```

---

#### M-4: Cohesion Analysis (Weight: 20%)
**Target:** High cohesion (module elements belong together)

**Measurement:**
```bash
# Check cohesion heuristics:
# - All functions in module relate to same concept?
# - Single Responsibility Principle (SRP) followed?
```

**Checklist:**
- [ ] Each module has single, clear responsibility
- [ ] No "god classes" (classes doing too much)
- [ ] No "utility dumping ground" modules
- [ ] Functions in module use shared data/state

**Scoring:**
```
# Manual assessment (0.0-1.0)
# - 1.0: Perfect SRP, all elements highly related
# - 0.7: Mostly cohesive with minor violations
# - 0.4: Some unrelated elements
# - 0.0: Module is a dumping ground
```

---

### Gate-M Score Calculation

```
Gate-M = 0.30 * M-1 + 0.25 * M-2 + 0.25 * M-3 + 0.20 * M-4
```

**Pass threshold:** ≥0.80 (Excellent), ≥0.65 (Acceptable), <0.65 (Needs work)

---

## IOSM-Index Calculation

### Final Score

```
IOSM-Index = (Gate-I + Gate-O + Gate-S + Gate-M) / 4
```

### Interpretation

| IOSM-Index | Rating | Action |
|------------|--------|--------|
| ≥0.90 | Excellent | Approve for production immediately |
| 0.80-0.89 | Good | Approve with minor recommendations |
| 0.70-0.79 | Acceptable | Approve with follow-up tasks |
| 0.60-0.69 | Needs Work | Block until improvements made |
| <0.60 | Poor | Major refactoring required |

### Production Deployment Threshold

**Minimum IOSM-Index for production:** 0.80

**Exceptions:**
- Experimental features: 0.70 (with feature flag)
- Hot fixes: 0.60 (with rollback plan)
- Prototypes: No minimum (not for production)

---

## IOSM Report Template

Use this structure for `iosm_report.md`:

```markdown
# IOSM Report — [Track ID]

## Summary
- **IOSM-Index:** [score] / 1.0
- **Rating:** [Excellent / Good / Acceptable / Needs Work]
- **Recommendation:** [Approve / Approve with conditions / Block]

## Gate-I: Improve
- **Score:** [score] / 1.0
- I-1 Semantic Clarity: [score]
- I-2 Code Duplication: [score]
- I-3 Invariants Documented: [score]
- I-4 TODOs Tracked: [score]
- **Issues:** [List issues]
- **Evidence:** [Links to reports, tool output]

## Gate-O: Optimize
- **Score:** [score] / 1.0
- O-1 Latency: [score]
- O-2 Error Budget: [score]
- O-3 Resource Efficiency: [score]
- O-4 Chaos Tests: [score]
- **Issues:** [List issues]
- **Evidence:** [Performance reports, metrics]

## Gate-S: Shrink
- **Score:** [score] / 1.0
- S-1 API Surface: [score]
- S-2 Dependencies: [score]
- S-3 Onboarding: [score]
- **Issues:** [List issues]
- **Evidence:** [Metrics, measurements]

## Gate-M: Modularize
- **Score:** [score] / 1.0
- M-1 Contracts: [score]
- M-2 Change Surface: [score]
- M-3 Coupling: [score]
- M-4 Cohesion: [score]
- **Issues:** [List issues]
- **Evidence:** [Dependency graphs, analysis]

## Detailed Findings
[Elaboration on any issues]

## Recommendations
[Actionable improvements]

## Approval Decision
[Approve / Conditional Approve / Block] - [Justification]
```

---

## Automation

### Recommended Tools

**Python:**
```bash
# Code quality
pylint src/
flake8 src/
black --check src/

# Duplication
radon cc src/ -a -s
jscpd src/

# Docstrings
interrogate src/ -v

# Dependencies
pip list --outdated
safety check

# Performance
pytest tests/perf/ --benchmark-only
```

**JavaScript/TypeScript:**
```bash
# Code quality
eslint src/
prettier --check src/

# Duplication
jscpd src/

# Dependencies
npm outdated
npm audit

# Performance
artillery run perf/load-test.yaml
```

### CI/CD Integration

Add IOSM gates to CI pipeline:

```yaml
# .github/workflows/iosm.yml
name: IOSM Quality Gates

on: [pull_request]

jobs:
  gate-i:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check code quality
        run: |
          pylint src/ --fail-under=8.5
          interrogate src/ --fail-under=90

  gate-o:
    runs-on: ubuntu-latest
    steps:
      - name: Run performance tests
        run: pytest tests/perf/ --benchmark-compare

  gate-s:
    runs-on: ubuntu-latest
    steps:
      - name: Check API surface
        run: ./scripts/check_api_surface.sh

  gate-m:
    runs-on: ubuntu-latest
    steps:
      - name: Check dependencies
        run: pydeps src/ --noshow --max-bacon=2
```

---

## IOSM Gates Schedule (Recommended for Mixed/Brownfield)

For typical brownfield workflows, run IOSM gates at these checkpoints:

### Gate-I (Improve) — After Design Phase (Wave 1-2)

**When:** After Explorer + Architect complete, before mass implementation

**Why:** Ensure clarity of requirements, contracts, invariants before writing code

**What to check:**
- [ ] Requirements clarity ≥0.95 (no ambiguous terms)
- [ ] All interfaces have explicit contracts (types, preconditions, postconditions)
- [ ] Invariants documented (what MUST be true)
- [ ] No "magic numbers" in specs (use named constants)
- [ ] TODOs tracked (all open questions in issue tracker)

**Block if:** Requirements ambiguous, contracts missing, invariants unclear

---

### Gate-M (Modularize) — After Implementation Phase (Wave 3)

**When:** After core implementation, before testing

**Why:** Ensure clean module boundaries and minimal change surface

**What to check:**
- [ ] Clear module contracts (public API defined)
- [ ] Change surface ≤20% (localized impact if module changes)
- [ ] Low coupling, high cohesion (modules independent)
- [ ] No circular dependencies
- [ ] Interface/implementation separation (if applicable)

**Block if:** Tight coupling, unclear boundaries, circular deps

---

### Gate-O (Optimize) — After Testing Phase (Wave 4)

**When:** After integration tests, perf tests complete

**Why:** Ensure performance and resilience targets met

**What to check:**
- [ ] P50/P95/P99 latency measured and within targets
- [ ] Error budget defined and measured
- [ ] Basic chaos tests passing (network failures, timeouts)
- [ ] No obvious inefficiencies (N+1 queries, memory leaks)
- [ ] Resource usage acceptable (CPU, memory, disk)

**Block if:** Performance targets missed, resilience issues

---

### Gate-S (Shrink) — Before Release (Wave 5)

**When:** Before final deployment/merge to main

**Why:** Minimize API surface and maximize simplicity

**What to check:**
- [ ] API surface reduced ≥20% (or growth justified)
- [ ] Dependency count stable or reduced (no new unnecessary deps)
- [ ] Onboarding time ≤15min for new contributor
- [ ] Documentation concise and complete
- [ ] No "dead code" (unused functions/classes removed)

**Block if:** API bloat, unnecessary complexity, poor docs

---

### Final IOSM-Index Calculation

```
IOSM-Index = (Gate-I + Gate-O + Gate-S + Gate-M) / 4
```

**Each gate scored 0.0 - 1.0 based on criteria met.**

**Production threshold:** ≥0.80

**Scoring guide:**
- 1.0: All criteria met, excellent
- 0.8-0.99: Most criteria met, minor issues documented
- 0.6-0.79: Some criteria missed, remediation plan needed
- <0.6: Major issues, DO NOT merge to production

---

## References

- IOSM Methodology: [Internal documentation or whitepaper link]
- Code Quality Metrics: https://refactoring.guru/
- Performance Testing: https://locust.io/
- Dependency Analysis: https://pydeps.readthedocs.io/
