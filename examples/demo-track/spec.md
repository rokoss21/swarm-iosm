# Technical Spec: Redis Caching Layer

**Track:** demo-add-caching
**PRD:** [PRD.md](./PRD.md)
**Created:** 2026-01-17

---

## Context

Current architecture calculates natal charts on every request, causing:
- High database load (75% CPU during peak)
- Slow response times (450ms P95)
- No horizontal scaling capability

Adding Redis cache will decouple computation from request path.

---

## What / Why

### What
Implement Redis-based caching for `/api/natal/chart` endpoint.

### Why
- **Performance:** 90% of requests are repeat data (cacheable)
- **Scalability:** Cache enables horizontal scaling
- **Cost:** Reduce database instance size

---

## Constraints

### Technical
- Must work with existing FastAPI app
- No breaking changes to API contract
- Redis client: `redis-py` (already in use)
- Deployment: AWS ElastiCache (Redis 7.0)

### Business
- Budget: $50/month for Redis instance
- Timeline: 1 week implementation
- No downtime during rollout

### Security
- No PII in cache keys (use hash)
- Encrypt Redis connection (TLS)
- Set max memory limit (512MB)

---

## Out of Scope

- Cache invalidation on user data change (future epic)
- Multi-region Redis replication
- Cache warming on deploy
- Admin UI for cache management

---

## Acceptance Tests

### Test 1: Cache Hit
```python
def test_cache_hit():
    # First request (cache miss)
    response1 = client.post("/api/natal/chart", json=birth_data)
    assert response1.headers["X-Cache-Status"] == "MISS"

    # Second request (cache hit)
    response2 = client.post("/api/natal/chart", json=birth_data)
    assert response2.headers["X-Cache-Status"] == "HIT"
    assert response2.json() == response1.json()
```

### Test 2: Cache Miss
```python
def test_cache_miss_different_data():
    response1 = client.post("/api/natal/chart", json=birth_data_1)
    response2 = client.post("/api/natal/chart", json=birth_data_2)
    assert response1.headers["X-Cache-Status"] == "MISS"
    assert response2.headers["X-Cache-Status"] == "MISS"
```

### Test 3: Redis Unavailable (Graceful Degradation)
```python
def test_redis_down_fallback():
    # Stop Redis
    redis_client.close()

    # Should still work (direct DB query)
    response = client.post("/api/natal/chart", json=birth_data)
    assert response.status_code == 200
    assert response.headers["X-Cache-Status"] == "BYPASS"
```

### Test 4: TTL Expiration
```python
def test_cache_expiration():
    response1 = client.post("/api/natal/chart", json=birth_data)
    assert response1.headers["X-Cache-Status"] == "MISS"

    # Wait for TTL
    time.sleep(24 * 3600 + 1)

    response2 = client.post("/api/natal/chart", json=birth_data)
    assert response2.headers["X-Cache-Status"] == "MISS"
```

---

## Artifacts to Produce

### Code
- `backend/core/cache.py` — Redis client wrapper
- `backend/api/natal.py` — Update endpoint with caching
- `backend/tests/test_cache.py` — Cache integration tests

### Documentation
- `docs/caching.md` — Cache strategy guide
- `RUNBOOK.md` — Update with cache operations

### Infrastructure
- `terraform/redis.tf` — ElastiCache configuration
- `docker-compose.yml` — Add Redis for local dev

### Reports (Swarm artifacts)
- `reports/T01.md` — Performance analysis
- `reports/T02.md` — Redis integration
- `reports/T03.md` — Endpoint modification
- `reports/T04.md` — Testing
- `integration_report.md` — Final merge plan
- `iosm_report.md` — Quality gate results

---

## Rollback Assumptions

### If rollback needed:
1. **Feature flag:** Set `ENABLE_CACHE=false` (instant)
2. **Code revert:** Git revert to previous commit
3. **Redis:** Can be stopped without app impact

### Pre-conditions for rollback:
- Error rate >1%
- Cache hit rate <50% after 48h
- P95 latency worse than baseline

### Recovery time:
- Feature flag: <1 minute
- Code revert: <5 minutes (deploy pipeline)

---

## Architecture Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/natal/chart
       ↓
┌──────────────────────────────┐
│   FastAPI App                │
│  ┌────────────────────────┐  │
│  │ natal_chart_endpoint() │  │
│  └───────┬────────────────┘  │
│          │                   │
│          ↓                   │
│  ┌────────────────────────┐  │
│  │ cache.get(key)         │──┼──→ Redis (ElastiCache)
│  └───────┬────────────────┘  │       ↓
│          │                   │    HIT: return cached
│      MISS│                   │
│          ↓                   │
│  ┌────────────────────────┐  │
│  │ calculate_chart()      │──┼──→ PostgreSQL
│  └───────┬────────────────┘  │
│          │                   │
│          ↓                   │
│  ┌────────────────────────┐  │
│  │ cache.set(key, result) │──┼──→ Redis (cache write)
│  └───────┬────────────────┘  │
│          │                   │
│          ↓                   │
│      return result           │
└──────────────────────────────┘
```

---

## Implementation Phases (Linked to plan.md)

- **Phase 0:** Analysis (T01)
- **Phase 1:** Design (T02)
- **Phase 2:** Implementation (T03, T04, T05)
- **Phase 3:** Testing (T06)
- **Phase 4:** Integration & IOSM Gates (T07)

See [plan.md](./plan.md) for task breakdown.
