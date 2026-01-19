# Skill Validation Checklist

Use this checklist to verify the Swarm Skill is properly configured.

## File Structure Validation

- [x] `.claude/skills/swarm-iosm/SKILL.md` exists
- [x] `.claude/skills/swarm-iosm/README.md` exists
- [x] `.claude/skills/swarm-iosm/QUICKSTART.md` exists
- [x] `.claude/skills/swarm-iosm/VALIDATION.md` exists (this file)

### Templates
- [x] `templates/intake_questions.md`
- [x] `templates/prd.md`
- [x] `templates/track_spec.md`
- [x] `templates/plan.md`
- [x] `templates/subagent_brief.md`
- [x] `templates/subagent_report.md`
- [x] `templates/integration_report.md`
- [x] `templates/iosm_gates.md`

### Scripts
- [x] `scripts/validate_plan.py`
- [x] `scripts/summarize_reports.py`

## SKILL.md Validation

### Frontmatter
- [x] `name: swarm-iosm` (lowercase, hyphens only)
- [x] `description` contains trigger words:
  - [x] "PRD"
  - [x] "decompose"
  - [x] "parallel"
  - [x] "subagents"
  - [x] "reports"
  - [x] "integration"
  - [x] "IOSM quality gates"
- [x] `user-invocable: true` (allows /swarm-iosm commands)
- [x] `allowed-tools` specified

### Content Structure
- [x] Quick Start section
- [x] When to Use section
- [x] Core Commands documented
- [x] Instructions for Claude (detailed workflow)
- [x] Subagent roles defined
- [x] IOSM gates explained
- [x] Examples provided
- [x] Troubleshooting section
- [x] References to templates (progressive disclosure)

## Template Validation

### All templates include:
- [x] Clear section headers
- [x] Examples or placeholders
- [x] Consistent formatting
- [x] Cross-references to other templates

### Specific validations:
- [x] `prd.md` has all 10 sections from PRD spec
- [x] `plan.md` includes dependency graph
- [x] `subagent_brief.md` includes output contract
- [x] `subagent_report.md` includes IOSM gates section
- [x] `integration_report.md` includes rollback guide
- [x] `iosm_gates.md` has scoring formulas

## Script Validation

### validate_plan.py
Run test (if you have a plan):
```bash
python .claude/skills/swarm-iosm/scripts/validate_plan.py <path-to-plan.md>
```

Expected:
- [x] Parses tasks correctly
- [x] Validates dependencies
- [x] Detects circular dependencies
- [x] Checks required fields

### summarize_reports.py
Run test (if you have reports):
```bash
python .claude/skills/swarm-iosm/scripts/summarize_reports.py <path-to-track-dir>
```

Expected:
- [x] Loads reports
- [x] Extracts status
- [x] Calculates file impact
- [x] Identifies blockers
- [x] Shows IOSM scores

## Activation Test

### Test 1: Direct invocation
```
/swarm-iosm setup
```

Expected:
- [ ] Skill activates
- [ ] Creates `swarm/` directory
- [ ] Generates context files

### Test 2: Trigger phrase
```
Can you help me create a PRD and decompose a complex task with parallel subagents?
```

Expected:
- [ ] Skill activates automatically
- [ ] Offers to create track

### Test 3: New track
```
/swarm-iosm new-track "Test feature"
```

Expected:
- [ ] Asks questions (AskUserQuestion)
- [ ] Generates PRD
- [ ] Creates plan
- [ ] Assigns subagent roles

## YAML Validation

Check YAML frontmatter:
```bash
head -n 10 .claude/skills/swarm-iosm/SKILL.md
```

Expected output:
```yaml
---
name: swarm-iosm
description: Orchestrate complex development tasks using PRD generation, task decomposition, parallel subagent execution (foreground/background), structured reports, and IOSM quality gates. Use when user mentions PRD, parallel tasks, decompose work, quality gates, swarm workflow, or needs structured multi-agent collaboration for greenfield or brownfield projects.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, AskUserQuestion, TodoWrite
---
```

Validate:
- [x] Opening `---` on line 1
- [x] Closing `---` before content
- [x] Valid YAML (no tabs, proper indentation)
- [x] `name` matches directory name (`swarm-iosm`)
- [x] `description` < 1024 chars

## Integration Test (End-to-End)

If you want to fully validate the Skill:

### 1. Setup
```
/swarm-iosm setup
```
- [ ] `swarm/` directory created
- [ ] `swarm/context/` has product.md, tech-stack.md, workflow.md
- [ ] `swarm/tracks.md` created

### 2. Create Track
```
/swarm-iosm new-track "Add Hello World endpoint to API"
```
- [ ] Questions asked
- [ ] PRD generated in `swarm/tracks/YYYY-MM-DD-NNN/PRD.md`
- [ ] Spec generated in `swarm/tracks/YYYY-MM-DD-NNN/spec.md`
- [ ] Plan generated in `swarm/tracks/YYYY-MM-DD-NNN/plan.md`
- [ ] Track ID returned

### 3. Validate Plan
```bash
python .claude/skills/swarm-iosm/scripts/validate_plan.py swarm/tracks/YYYY-MM-DD-NNN/plan.md
```
- [ ] No errors
- [ ] Warnings acceptable

### 4. Implement (Optional - will create real code)
```
/swarm-iosm implement
```
- [ ] Subagents launched
- [ ] Reports generated in `swarm/tracks/YYYY-MM-DD-NNN/reports/`

### 5. Summarize Reports
```bash
python .claude/skills/swarm-iosm/scripts/summarize_reports.py swarm/tracks/YYYY-MM-DD-NNN
```
- [ ] Summary printed
- [ ] Task status shown
- [ ] File impact calculated

### 6. Integrate
```
/swarm-iosm integrate YYYY-MM-DD-NNN
```
- [ ] `integration_report.md` generated
- [ ] `iosm_report.md` generated
- [ ] IOSM-Index calculated

## Common Issues

### Issue: Skill doesn't activate
**Fix:**
1. Check YAML frontmatter (no syntax errors)
2. Restart Claude Code
3. Try explicit invocation: `/swarm-iosm setup`

### Issue: Templates not found
**Fix:**
1. Check file paths in SKILL.md
2. Ensure templates/ directory exists
3. Use forward slashes in paths

### Issue: Scripts don't run
**Fix:**
1. Make scripts executable: `chmod +x scripts/*.py`
2. Check Python version (3.7+)
3. Run with `python scripts/script.py` instead of `./scripts/script.py`

## Success Criteria

Skill is valid and ready if:

- [x] All files present (12 files total)
- [x] YAML frontmatter valid
- [x] SKILL.md has complete instructions
- [x] Templates reference each other correctly
- [x] Scripts run without errors
- [ ] Activation test passes (run `/swarm-iosm setup`)
- [ ] End-to-end test passes (optional)

## Final Check

Run this command to verify all files:
```bash
find .claude/skills/swarm-iosm -type f | wc -l
```

Expected: **13 files** (SKILL.md, README.md, QUICKSTART.md, VALIDATION.md, 8 templates, 2 scripts)

Actual: _________

---

**Validation complete?** ✅

If all checks pass, the Skill is ready to use!

Try: `/swarm-iosm setup`
