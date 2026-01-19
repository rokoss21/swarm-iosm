# Troubleshooting

Common issues and solutions for Swarm-IOSM.

---

## Skill Not Activating

### Symptom
```
Unknown skill: swarm-iosm
```

### Solutions

1. **Check installation path**
   ```bash
   # Should be in one of these locations:
   ls .claude/skills/swarm-iosm/SKILL.md          # project-level
   ls ~/.claude/skills/swarm-iosm/SKILL.md        # user-level
   ```

2. **Verify SKILL.md frontmatter**
   ```yaml
   ---
   name: swarm-iosm
   description: ...
   user-invocable: true
   ---
   ```

3. **Restart Claude Code**
   Skills are loaded on startup. Restart after installation.

4. **Try explicit path**
   ```
   /swarm-iosm setup
   ```

---

## Plan Validation Fails

### Symptom
```
❌ Validation failed:
  - T03: missing 'Touches'
  - T05: missing 'Effort'
```

### Solution

Add required fields to each task in `plan.md`:

```markdown
- [ ] **T03**: Implement feature
  - **Owner role:** Implementer
  - **Depends on:** T01, T02
  - **Touches:** `src/feature.py`, `tests/test_feature.py`
  - **Concurrency class:** write-local
  - **Needs user input:** false
  - **Effort:** M
  - **Acceptance:** Tests pass
```

**Required fields:**
- Touches (even if empty: `Touches: None`)
- Needs user input (`true` or `false`)
- Effort (`S`, `M`, `L`, `XL`)

---

## Background Task Fails Silently

### Symptom
Task launched in background but no report generated.

### Causes & Solutions

1. **MCP tools used in background**
   
   Background agents cannot use MCP tools reliably. Check if task requires:
   - Web fetch
   - External API calls
   - Custom MCP tools
   
   **Fix:** Mark task as `needs_user_input: true` to run in foreground.

2. **Permission denied**
   
   Background agents cannot request permissions.
   
   **Fix:** Pre-approve commands in brief or run in foreground.

3. **Unhandled question**
   
   Agent encountered ambiguity and stopped.
   
   **Fix:** Add pre-resolved questions to brief:
   ```markdown
   ### Pre-resolved Questions
   Q: Which auth method to use?
   A: JWT with RS256
   ```

---

## Infinite Loop / No Progress

### Symptom
```
loops_without_progress: 3
```

### Causes & Solutions

1. **Circular dependencies**
   ```
   T01 depends on T02
   T02 depends on T01
   ```
   
   **Fix:** Review dependency graph in `plan.md`. Break cycles.

2. **All tasks blocked on user input**
   
   **Fix:** Answer blocking questions in `iosm_state.md`:
   ```markdown
   ## Blocking Questions (needs user)
   
   ### Q1: Database choice
   **Answer:** PostgreSQL
   ```

3. **Spawn candidates creating loops**
   
   SC-01 spawns SC-02, SC-02 spawns SC-01.
   
   **Fix:** Check dedup keys. Same `touch|intent` should not spawn twice.

---

## File Conflicts Between Tasks

### Symptom
```
T03 blocked waiting for T04 to release `backend/core/__init__.py`
```

### Solution

Tasks touching same files run sequentially by design. Options:

1. **Wait** — T04 finishes, T03 runs automatically
2. **Refactor touches** — split file into smaller modules
3. **Merge tasks** — if they're tightly coupled

Check conflict matrix:
```bash
python scripts/orchestration_planner.py plan.md --continuous
# Look for "Lock Plan" section
```

---

## Gate Scores Too Low

### Gate-I (Improve) < 0.75

**Common issues:**
- Unclear naming → rename functions/variables
- Code duplication → extract shared logic
- Missing docstrings → add documentation
- Untracked TODOs → link to issues

### Gate-O (Optimize) failing

**Common issues:**
- Tests failing → fix tests or code
- Performance below target → profile and optimize
- No chaos tests → add resilience tests

### Gate-S (Shrink) < 0.80

**Common issues:**
- API surface too large → consolidate endpoints
- Too many dependencies → remove unused
- Onboarding > 15min → improve README

### Gate-M (Modularize) failing

**Common issues:**
- Circular dependencies → break cycles
- Missing contracts → add interface definitions
- High coupling → refactor module boundaries

---

## SpawnCandidate Explosion

### Symptom
```
spawn_budget_remaining: 0
```

### Solution

1. **Increase budget** (if justified)
   ```markdown
   spawn_budget_total: 30  # was 20
   ```

2. **Tighten auto-spawn rules**
   ```markdown
   auto_spawn_allowed: safe-only  # instead of 'all'
   ```

3. **Review severity ratings**
   - `low` → skip or defer
   - `medium` → batch with similar
   - `high` → prioritize
   - `critical` → stop and fix

---

## Scripts Not Running

### Symptom
```
python: command not found
# or
ModuleNotFoundError: No module named 'yaml'
```

### Solutions

1. **Check Python version**
   ```bash
   python --version  # need 3.7+
   python3 --version
   ```

2. **Use python3 explicitly**
   ```bash
   python3 scripts/orchestration_planner.py plan.md --validate
   ```

3. **No external dependencies required**
   Scripts use only stdlib (no pip install needed).

---

## Reports Missing Sections

### Symptom
Subagent report missing SpawnCandidates or IOSM checks.

### Solution

Remind subagent of required format. Reports MUST include:

```markdown
## SpawnCandidates

| ID | Subtask | Touches | Effort | User Input | Severity |
|----|---------|---------|--------|------------|----------|
(None identified)

## IOSM Quality Checks

- [x] Gate-I: Clear naming, no duplication
- [x] Gate-O: Tests passing
- [ ] Gate-S: N/A
- [x] Gate-M: Module boundaries clean
```

---

## Integration Fails

### Symptom
`/swarm-iosm integrate` reports conflicts or missing reports.

### Solutions

1. **Check all tasks complete**
   ```bash
   ls swarm/tracks/<id>/reports/
   # Should have T01.md, T02.md, etc. for all tasks
   ```

2. **Resolve file conflicts**
   If multiple tasks modified same file, manual merge may be needed.

3. **Re-run failed tasks**
   ```
   /swarm-iosm implement  # will resume from where it stopped
   ```

---

## Common Errors (v1.2)

### Permission Denied

**Symptom:**
```
Task T04 failed: Permission denied: backend/migrations/001.sql
```

**Diagnosis:**
User or process lacks necessary permissions to access/modify the file.

**Common causes:**
- Database user lacks CREATE/ALTER privileges
- File system permissions (chmod/chown issues)
- Running as wrong user

**Suggested fixes:**
1. Check permissions: `ls -la backend/migrations/001.sql`
2. Grant database permission: `GRANT CREATE ON DATABASE app TO user;`
3. Run with elevated privileges (if safe): `chmod +x file.sh`
4. Mark task as foreground for manual approval

**Retry:**
```bash
/swarm-iosm retry T04 --foreground
```

---

### Module Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'pyswisseph'
ImportError: cannot import name 'X'
```

**Diagnosis:**
Python module not installed in current environment.

**Suggested fixes:**
1. Install module: `pip install pyswisseph`
2. Check requirements.txt includes the module
3. Activate virtual environment: `source venv/bin/activate` or `venv\Scripts\activate`
4. Run: `pip install -r requirements.txt`

**Prevention:**
Add all required modules to requirements.txt for future tracks.

**Retry:**
```bash
/swarm-iosm retry T05
```

---

### Test Failures

**Symptom:**
```
3 failed, 12 passed in 5.2s
Test: test_natal_calculation FAILED
```

**Diagnosis:**
Code changes broke existing tests.

**Suggested fixes:**
1. Review test output for specific failures
2. Run tests locally: `pytest tests/test_natal.py -v`
3. **Decision needed:** Fix code OR update tests?
   - If test is correct → Fix the code
   - If test is outdated → Update the test
4. Consider marking task as foreground for decision

**Retry:**
```bash
/swarm-iosm retry T08 --foreground  # For decision-making
```

---

### MCP Tool Unavailable

**Symptom:**
```
MCP tool 'some-tool' not available in background mode
Tool requires user interaction
```

**Diagnosis:**
Task tried to use MCP tool while running in background mode.

**Suggested fixes:**
1. Mark task with `needs_user_input: true` in plan.md
2. Avoid MCP tools in background tasks
3. Use standard tools only (Read, Write, Bash) in background
4. Force foreground mode for this task

**Retry:**
```bash
/swarm-iosm retry T03 --foreground
```

---

### File Not Found

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'
ENOENT: backend/models/user.py
```

**Diagnosis:**
File doesn't exist at expected path.

**Suggested fixes:**
1. Verify file path: `ls backend/models/user.py`
2. Check if file was supposed to be created by dependency task
3. Review task's "Touches" field — may be missing
4. Check if dependency task actually completed successfully

**Prevention:**
Ensure all "Touches" files are listed in task definition.

**Retry:**
```bash
/swarm-iosm retry T06  # After verifying file exists
```

---

### Timeout

**Symptom:**
```
TimeoutError: Task exceeded time limit
Task ran for more than 30 minutes
```

**Diagnosis:**
Task took longer than expected.

**Suggested fixes:**
1. Increase effort estimate in plan.md (M → L, L → XL)
2. Break task into smaller subtasks
3. Retry with --foreground (no timeout limit)
4. Check for infinite loops or hanging processes

**Retry:**
```bash
/swarm-iosm retry T09 --foreground
```

---

## Error Recovery Workflow (v1.2)

### Step 1: Identify the error
```bash
/swarm-iosm status
```
Shows all tasks with errors and suggested fixes.

### Step 2: Review error diagnosis
Each error includes:
- **Error type** (e.g., Permission Denied)
- **Affected file**
- **Root cause**
- **Suggested fixes** (2-4 options)
- **Retry command**

### Step 3: Choose action
- **Automatic fix** → Apply suggested commands
- **Manual fix** → Fix yourself, then retry
- **Skip** → Mark task as failed, continue

### Step 4: Retry the task
```bash
/swarm-iosm retry <task-id> [options]
```

Options:
- `--foreground`: Run interactively (for debugging)
- `--reset-brief`: Regenerate brief from scratch

### Step 5: Verify fix
Check task report to confirm error is resolved.

---

## Error Severity Levels

| Severity | Meaning | Auto-Spawn? | Retry Strategy |
|----------|---------|-------------|----------------|
| Low | Non-blocking warning | ✅ Yes | Standard retry |
| Medium | Task blocked but fixable | ❌ No | Standard retry |
| High | Task blocked, needs attention | ❌ No | Foreground retry |
| Critical | Cannot continue without fix | ❌ No | Manual + Foreground |

---

## Getting Help

1. **Check examples**
   ```bash
   cat examples/demo-track/plan.md
   cat examples/demo-track/reports/T01.md
   ```

2. **Validate your plan**
   ```bash
   python scripts/orchestration_planner.py your-plan.md --validate
   ```

3. **Open an issue**
   https://github.com/rokoss21/swarm-iosm/issues

---

## See Also

- [QUICKSTART.md](./QUICKSTART.md) — Getting started
- [RUNBOOK.md](./RUNBOOK.md) — Manual operations
- [SKILL.md](./SKILL.md) — Full specification
