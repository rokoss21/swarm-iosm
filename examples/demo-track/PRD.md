# PRD: Add Redis Caching to API Endpoints

**Track ID:** demo-add-caching
**Created:** 2026-01-17
**Status:** Implementation
**Owner:** Platform Team

---

## 1. Problem

High-traffic API endpoints experience increased latency and database load during peak hours:
- `/api/natal/chart` takes 450ms average (target: <100ms)
- Database CPU at 75% during peak
- User complaints about slow chart generation
- No caching layer exists

**Impact:**
- Poor user experience during prime hours (6PM-10PM)
- Risk of database overload
- Increased infrastructure costs

---

## 2. Goals / Non-goals

### Goals
- ✅ Reduce P95 latency to <200ms on cached endpoints
- ✅ Achieve >80% cache hit rate within 1 week
- ✅ Reduce database load by 50%+
- ✅ Zero downtime deployment

### Non-goals
- ❌ Cache invalidation strategy (separate epic)
- ❌ Distributed cache (single Redis instance for MVP)
- ❌ Cache for low-traffic endpoints (<100 req/day)

---

## 3. Users & Use-cases

**Primary users:**
- Web app users (95% of traffic)
- Mobile app users (5% of traffic)

**Use-case:**
1. User requests natal chart for known birth data
2. System checks Redis cache
3. If hit: return cached result (5ms)
4. If miss: calculate, cache for 24h, return

**Traffic profile:**
- 10,000 requests/day
- 60% repeat requests (same birth data)
- Peak: 1,000 requests/hour (6PM-10PM)

---

## 4. Scope (MVP / Later)

### MVP (This Track)
- Cache `/api/natal/chart` endpoint
- Redis integration with retry logic
- Basic cache key strategy (hash of input params)
- TTL: 24 hours
- Monitoring (cache hit rate, latency)

### Later
- Cache invalidation on user data change
- Multi-level cache (Redis + in-memory)
- Cache warming on deploy
- Advanced TTL strategies

---

## 5. Requirements

### Functional
1. **Cache Read:** Check Redis before calculation
2. **Cache Write:** Store result with 24h TTL
3. **Cache Miss:** Calculate and cache atomically
4. **Key Strategy:** `natal:chart:{hash(input_params)}`
5. **Serialization:** JSON format

### Non-functional
1. **Performance:** Cache read <5ms
2. **Availability:** Graceful degradation if Redis down
3. **Reliability:** Retry logic (3 attempts, exponential backoff)
4. **Observability:** Metrics exported to Prometheus

---

## 6. UX / API / Data

### API (No changes to external contract)
- Endpoint: `POST /api/natal/chart` (unchanged)
- Response format: Same as before
- Headers: Add `X-Cache-Status: HIT|MISS`

### Data
**Cache Entry:**
```json
{
  "key": "natal:chart:abc123",
  "value": {
    "chart_data": {...},
    "calculated_at": "2026-01-17T10:30:00Z"
  },
  "ttl": 86400
}
```

**Redis Schema:**
- Namespace: `natal:chart:*`
- Max keys: ~100,000 (based on unique birth data combinations)
- Memory estimate: 50MB (500 bytes/key × 100k)

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Redis failure | API down | Low | Fallback to direct DB query |
| Cache stampede | DB overload | Medium | Implement locking on cache miss |
| Stale data | Wrong results | Low | 24h TTL acceptable (birth data static) |
| Memory overflow | Redis OOM | Low | Set max memory policy (LRU eviction) |

---

## 8. Acceptance Criteria

### Must Have
- [x] P95 latency <200ms (from 450ms)
- [x] Cache hit rate >80% after 1 week
- [x] Zero errors in production
- [x] Monitoring dashboard live

### Nice to Have
- [ ] Admin UI to clear cache
- [ ] Cache warming script

---

## 9. Rollout / Migration plan

### Phase 1: Deploy (Week 1)
1. Deploy Redis instance (AWS ElastiCache)
2. Deploy code with feature flag OFF
3. Smoke test in staging

### Phase 2: Enable (Week 1)
1. Enable for 10% traffic
2. Monitor for 24h
3. Ramp to 50%, then 100%

### Phase 3: Validate (Week 2)
1. Measure cache hit rate
2. Confirm latency improvement
3. Check error rates

### Rollback Plan
- Feature flag toggle (instant)
- Redis can be stopped without app restart
- Database handles all traffic (pre-cache state)

---

## 10. IOSM Targets

| Gate | Baseline | Target | Expected Δ |
|------|----------|--------|-----------|
| **Gate-I** | 0.72 | ≥0.75 | +0.03 (improve naming, reduce duplication) |
| **Gate-O** | 2 tests failing | All pass | Fix + add cache integration tests |
| **Gate-M** | Pass | Pass | No new circular deps |
| **Gate-S** | N/A | N/A | No API surface change |

**IOSM-Index target:** ≥0.80

**Auto-spawn triggers:**
- If Gate-I fails: Spawn "Improve cache key naming clarity"
- If Gate-O fails: Spawn "Fix failing integration tests"

---

## Appendix: Related Links

- Slack discussion: #backend-performance
- Performance baseline: [Grafana Dashboard](http://grafana.internal/dashboard/api-latency)
- Redis docs: https://redis.io/docs/
- Original ticket: PROJ-1234
