# PRD: [Feature Name]

**Version:** 1.0
**Date:** [YYYY-MM-DD]
**Track ID:** [track-id]
**Owner:** [name/team]
**Status:** Draft | Review | Approved | Implemented

---

## 1. Problem

**Current state:**
[What is the current situation? What pain points exist?]

**Impact:**
[Who is affected? How much does this cost (time/money/quality)?]

**Why now:**
[Why is this a priority now? What changed?]

---

## 2. Goals / Non-goals

### Goals
1. [Primary goal - measurable outcome]
2. [Secondary goal]
3. [Tertiary goal]

### Non-Goals (explicitly out of scope for MVP)
- [Thing we're NOT doing in this iteration]
- [Feature/change deferred to later]
- [Complexity we're avoiding]

---

## 3. Users & Use Cases

### Primary Personas
1. **[Persona name]** (e.g., "API Consumer")
   - Role: [description]
   - Pain point: [specific problem]
   - Value: [what they gain]

2. **[Persona name]** (e.g., "System Administrator")
   - Role: [description]
   - Pain point: [specific problem]
   - Value: [what they gain]

### Use Cases
1. **UC-1: [Name]**
   - Actor: [who]
   - Trigger: [what initiates]
   - Flow: [step-by-step]
   - Outcome: [end state]

2. **UC-2: [Name]**
   - Actor: [who]
   - Trigger: [what initiates]
   - Flow: [step-by-step]
   - Outcome: [end state]

---

## 4. Scope

### MVP (Must-Have)
- [Feature/capability that MUST be in first release]
- [Critical functionality]
- [Minimum viable interface]

### V1.1 (Should-Have)
- [Enhancement for next iteration]
- [Nice-to-have that requires more time]

### Future (Could-Have)
- [Ideas for later consideration]
- [Advanced features deferred]

---

## 5. Requirements

### Functional Requirements

**FR-1: [Capability name]**
- Description: [what it does]
- Acceptance: [how to verify it works]
- Priority: Must / Should / Could

**FR-2: [Capability name]**
- Description: [what it does]
- Acceptance: [how to verify it works]
- Priority: Must / Should / Could

[Add more as needed]

### Non-Functional Requirements

**NFR-1: Performance**
- Latency: [P50/P95/P99 targets, e.g., "P95 < 200ms"]
- Throughput: [requests/sec, e.g., "1000 req/s sustained"]
- Resource usage: [memory/CPU constraints]

**NFR-2: Security**
- Authentication: [method, e.g., "OAuth2 + JWT"]
- Authorization: [access control model]
- Data protection: [encryption, PII handling]
- Compliance: [GDPR/SOC2/etc]

**NFR-3: Reliability**
- Availability: [target uptime, e.g., "99.9%"]
- Error budget: [acceptable failure rate]
- Disaster recovery: [RTO/RPO targets]

**NFR-4: Scalability**
- User growth: [expected scale, e.g., "10K → 100K users"]
- Data growth: [storage projections]
- Geographic distribution: [multi-region?]

**NFR-5: Maintainability**
- Code quality: [test coverage ≥80%, etc]
- Documentation: [API docs, runbooks]
- Observability: [logging, metrics, tracing]

---

## 6. UX / API / Data

### User Experience (if applicable)
- **UI mockups:** [link or description]
- **User flows:** [critical paths]
- **Accessibility:** [WCAG compliance, screen readers, etc]
- **Internationalization:** [languages, locales]

### API Design (if applicable)
**Endpoints:**
```
POST /api/v1/resource
GET /api/v1/resource/{id}
PUT /api/v1/resource/{id}
DELETE /api/v1/resource/{id}
```

**Request/Response examples:**
```json
// POST /api/v1/resource
{
  "field": "value"
}

// Response
{
  "id": "uuid",
  "field": "value",
  "created_at": "2026-01-17T12:00:00Z"
}
```

**Error handling:**
- 400: Validation errors
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 429: Rate limited
- 500: Internal error

### Data Model
**Entities:**
```
Resource {
  id: UUID (PK)
  name: String (required, indexed)
  status: Enum (active, inactive)
  created_at: Timestamp
  updated_at: Timestamp
}
```

**Migrations:**
- [New tables/columns needed]
- [Data backfill strategy]
- [Rollback plan]

**PII/Sensitive Data:**
- [What data is PII?]
- [Encryption at rest/in transit?]
- [Retention policy?]

---

## 7. Risks & Mitigations

| Risk | Impact (H/M/L) | Probability (H/M/L) | Mitigation |
|------|----------------|---------------------|------------|
| [Technical risk, e.g., "External API latency"] | H | M | [Strategy, e.g., "Cache responses, implement circuit breaker"] |
| [Operational risk, e.g., "Database migration downtime"] | M | L | [Strategy, e.g., "Blue-green deployment, run migration offline"] |
| [Business risk, e.g., "User adoption low"] | H | M | [Strategy, e.g., "Beta test with early adopters, gather feedback"] |

---

## 8. Acceptance Criteria

### Functional Acceptance
- [ ] All FR-1 through FR-N requirements met
- [ ] All use cases (UC-1, UC-2) executable and verified
- [ ] API endpoints return expected responses (if applicable)
- [ ] UI flows complete without errors (if applicable)

### Non-Functional Acceptance
- [ ] Performance: P95 latency < [target]
- [ ] Security: No critical vulnerabilities (OWASP top 10)
- [ ] Reliability: 99.9% uptime in staging for 7 days
- [ ] Test coverage ≥ [target]% (unit + integration)

### Documentation Acceptance
- [ ] API documentation complete (OpenAPI/Swagger)
- [ ] User guide / README updated
- [ ] Runbook for operations (deploy, monitor, troubleshoot)
- [ ] ADRs (Architecture Decision Records) for major choices

---

## 9. Rollout / Migration Plan

### Deployment Strategy
- **Approach:** [Blue-green / Canary / Rolling / Big bang]
- **Phases:**
  1. [Phase 1: e.g., "Deploy to staging"]
  2. [Phase 2: e.g., "Canary 5% of production traffic"]
  3. [Phase 3: e.g., "Full rollout"]

### Feature Flags
- `feature.new_capability.enabled` (default: false)
- [Rollout percentage control]

### Monitoring & Alerts
- **Key metrics:** [latency, error rate, throughput]
- **Alerts:** [thresholds for paging]
- **Dashboards:** [link to Grafana/Datadog/etc]

### Rollback Plan
- **Trigger:** [When to rollback, e.g., "Error rate > 5%"]
- **Steps:**
  1. [e.g., "Disable feature flag"]
  2. [e.g., "Revert deployment"]
  3. [e.g., "Restore database from backup if needed"]

---

## 10. IOSM Targets

### Gate-I (Improve) Targets
- Semantic clarity: ≥0.95 (clear naming, no magic numbers)
- Code duplication: ≤5%
- Invariants documented: 100% of public APIs
- TODOs tracked: All TODOs in issue tracker

### Gate-O (Optimize) Targets
- P50 latency: ≤[X]ms
- P95 latency: ≤[Y]ms
- P99 latency: ≤[Z]ms
- Error budget: [e.g., "0.1% error rate"]
- Chaos tests: [e.g., "Withstand single instance failure"]

### Gate-S (Shrink) Targets
- API surface: ≤[N] endpoints (or justify growth)
- Dependency count: Stable or reduced by [X]%
- Onboarding time: ≤15 min for new contributor

### Gate-M (Modularize) Targets
- Module contracts: 100% defined and documented
- Change surface: ≤20% (impact localized)
- Coupling: Low (use dependency graph analysis)
- Cohesion: High (single responsibility per module)

### Expected IOSM-Index
**Current baseline:** [e.g., 0.65]
**Target post-implementation:** [e.g., 0.82]
**Delta:** +0.17

---

## Appendix

### References
- [Link to design doc]
- [Link to competitive analysis]
- [Link to user research]

### Open Questions
- [Question 1 needing resolution]
- [Question 2 needing stakeholder input]

### Change Log
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-17 | [Name] | Initial draft |
