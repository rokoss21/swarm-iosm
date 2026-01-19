# Requirements Intake Template

Use this template to gather comprehensive requirements before creating PRD and plan.

---

## Mode Selection (AskUserQuestion)

**Question:** Is this a greenfield (new from scratch) or brownfield (existing codebase) project?

**Options:**
1. **Greenfield** - New feature/project from scratch
2. **Brownfield** - Modifying/refactoring existing code

**Impact:**
- Greenfield: Skip repo analysis, focus on design
- Brownfield: Start with Plan mode, analyze existing architecture

---

## Priority & Constraints (AskUserQuestion)

**Question 1:** What is your primary optimization goal?

**Options:**
1. **Speed** - Ship fast, iterate later
2. **Quality** - High quality, thorough testing
3. **Cost** - Minimal resources, simple solution

---

**Question 2:** How strict should we be with changes to existing code?

**Options:**
1. **Safe** - Minimal changes, avoid refactoring
2. **Normal** - Balanced approach
3. **Aggressive** - Refactor freely for better design

---

**Question 3:** What is your testing strategy?

**Options:**
1. **TDD** - Write tests first, then implementation
2. **Post-tests** - Implement first, add tests after
3. **Smoke only** - Basic smoke tests, not comprehensive

---

**Question 4:** Which tools/operations should be allowed? (Multi-select)

**Options:**
1. **Bash commands** (git, npm, pytest, etc.)
2. **Edit files** (modify existing code)
3. **Write files** (create new files)
4. **Delete files** (remove files)

---

## Goal & Definition of Done (Text Questions)

### 1. Goal
**Question:** What is the goal of this task? What defines "done"?

**Format:** 1-2 sentences describing the desired outcome.

**Example:**
> "Add user authentication to the API. Done when users can register, login, and access protected endpoints with JWT tokens."

**Your answer:**
[Your response here]

---

### 2. Context
**Question:** What context should we know about the product, users, or environment?

**Format:** Brief description of relevant background.

**Example:**
> "This is a SaaS product for small businesses. Users are non-technical. The API is used by a React frontend and mobile apps."

**Your answer:**
[Your response here]

---

### 3. Constraints
**Question:** What are the technical or business constraints?

**Format:** List of constraints (tech stack, deadlines, restrictions, etc.)

**Examples:**
- "Must use Python 3.9+ and FastAPI"
- "Deadline: 2 weeks from start"
- "Cannot introduce breaking changes to existing API"
- "Must work on PostgreSQL 12+"

**Your answer:**
[Your response here]

---

### 4. Interfaces
**Question:** What interfaces are involved? (API/UI/CLI/SDK/etc.)

**Format:** List of interfaces and their nature.

**Examples:**
- "REST API with JSON payloads"
- "React UI for user management"
- "CLI tool for admin operations"

**Your answer:**
[Your response here]

---

### 5. Data
**Question:** What data is involved? Are there migrations, PII concerns, data sources?

**Format:** Description of data considerations.

**Examples:**
- "New 'users' table with email (PII) and hashed passwords"
- "Migration from old auth system (1000 existing users)"
- "Data source: OAuth provider (Google, GitHub)"

**Your answer:**
[Your response here]

---

### 6. Risks
**Question:** What could go wrong? What are the main risks?

**Format:** List of potential risks.

**Examples:**
- "OAuth provider downtime breaks login"
- "Password hashing too slow (latency spike)"
- "Migration loses existing user data"

**Your answer:**
[Your response here]

---

### 7. Definition of Done
**Question:** What specific criteria must be met to consider this complete?

**Format:** Checklist of completion criteria.

**Examples:**
- [ ] All API endpoints implemented and tested
- [ ] Unit test coverage ≥80%
- [ ] Documentation updated (README, API docs)
- [ ] Deployed to staging and verified
- [ ] Security scan passed (no critical vulnerabilities)

**Your answer:**
[Your checklist here]

---

## Non-Functional Requirements (Text Questions)

### 8. Performance
**Question:** What are the performance requirements?

**Format:** Specific latency/throughput targets.

**Examples:**
- "P95 latency <200ms"
- "Support 1000 requests/sec"
- "Response time <100ms for 95% of requests"

**Your answer:**
[Your response here]

---

### 9. Security
**Question:** What are the security requirements?

**Format:** List security considerations.

**Examples:**
- "OWASP Top 10 compliance"
- "Passwords hashed with bcrypt (12 rounds)"
- "JWTs expire after 1 hour, refresh tokens after 30 days"
- "HTTPS only, no plaintext credentials"

**Your answer:**
[Your response here]

---

### 10. Reliability
**Question:** What are the reliability/availability requirements?

**Format:** Uptime targets, error budgets, disaster recovery.

**Examples:**
- "99.9% uptime SLA"
- "Error budget: 0.1% of requests"
- "RTO: 1 hour, RPO: 5 minutes"

**Your answer:**
[Your response here]

---

### 11. Scalability
**Question:** What are the scalability requirements?

**Format:** Expected growth, resource limits.

**Examples:**
- "Scale from 100 to 10,000 users in 6 months"
- "Database size: up to 1TB"
- "Multi-region deployment (US, EU)"

**Your answer:**
[Your response here]

---

### 12. Maintainability
**Question:** What are the maintainability requirements?

**Format:** Code quality, documentation, observability.

**Examples:**
- "Test coverage ≥80%"
- "All public APIs documented (OpenAPI)"
- "Logging: structured JSON logs"
- "Metrics: Prometheus-compatible"

**Your answer:**
[Your response here]

---

## Optional: Specific Technical Details

### 13. Technology Choices (if known)
**Question:** Are there specific technologies that must be used?

**Format:** List of required technologies.

**Examples:**
- "Authentication: OAuth2 + JWT (PyJWT library)"
- "Database: PostgreSQL with SQLAlchemy ORM"
- "API framework: FastAPI"

**Your answer:**
[Your response here]

---

### 14. Integration Points
**Question:** What external systems/services does this integrate with?

**Format:** List of integrations with brief description.

**Examples:**
- "Google OAuth for social login"
- "SendGrid for email notifications"
- "Stripe for payment processing"

**Your answer:**
[Your response here]

---

### 15. Migration Plan (if brownfield)
**Question:** Is there an existing system to migrate from? What's the migration strategy?

**Format:** Description of migration approach.

**Examples:**
- "Dual-run old and new auth for 2 weeks"
- "Migrate users in batches (100 at a time)"
- "Feature flag: `auth.v2.enabled` (gradually roll out)"

**Your answer:**
[Your response here]

---

## Summary (Auto-generated)

After collecting all answers, summarize:

**Mode:** [Greenfield / Brownfield]
**Priority:** [Speed / Quality / Cost]
**Change strictness:** [Safe / Normal / Aggressive]
**Test strategy:** [TDD / Post-tests / Smoke only]
**Allowed tools:** [List]

**Goal:** [1-2 sentence summary]

**Key constraints:**
- [Constraint 1]
- [Constraint 2]

**Key risks:**
- [Risk 1]
- [Risk 2]

**NFRs:**
- Performance: [target]
- Security: [requirements]
- Reliability: [SLA]

**Definition of Done:**
- [Criterion 1]
- [Criterion 2]

---

## Next Steps

With this intake complete:

1. Generate PRD using [templates/prd.md](prd.md)
2. Create spec using [templates/track_spec.md](track_spec.md)
3. Decompose into plan using [templates/plan.md](plan.md)
4. Launch subagents per plan

---

**Notes:**
- Save this intake to: `swarm/tracks/<track-id>/intake.md`
- Reference intake when writing PRD
- Update intake if requirements change
