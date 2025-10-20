# Performance

## Purpose

Performance optimization infrastructure including multi-layer caching strategies (Redis), rate limiting, queue management (Celery/Bull), connection pooling, and auto-scaling configurations.

## What It Does

1. **Caching Strategy** - Implement multi-layer caching (in-memory, Redis, CDN) with intelligent cache invalidation and warming
2. **Rate Limiting** - Protect APIs with rate limiting per user/IP, token bucket algorithms, and distributed rate limiting
3. **Queue Management** - Set up background job queues (Celery/Bull/RabbitMQ) for async processing and task scheduling
4. **Connection Pooling** - Configure database and API connection pools to reduce overhead and improve throughput
5. **Auto-scaling** - Define horizontal pod autoscaling (HPA) rules based on CPU, memory, and custom metrics

## Agents Used

- **@claude/cache-architect** - Designs optimal caching strategy for application access patterns
- **@claude/rate-limiter-configurator** - Configures rate limiting rules based on API endpoints and usage patterns
- **@claude/queue-designer** - Sets up task queues and workers for async processing
- **@claude/performance-analyzer** - Identifies bottlenecks and suggests optimization strategies

## Commands

### `/performance:init` - Initialize performance infrastructure
**Usage**: `/performance:init [--cache|--queues|--all]`
**Example**: `/performance:init --all`

Sets up performance infrastructure including Redis for caching, task queue workers, connection pools, and rate limiting middleware.

**Spawns**: cache-architect, queue-designer agents
**Outputs**:
- `docker-compose.performance.yml` - Redis, RabbitMQ services
- `src/cache/cache-manager.{py|ts}` - Caching layer
- `src/queues/worker.{py|ts}` - Task queue worker
- `config/rate-limits.yml` - Rate limiting rules

---

### `/performance:cache-strategy` - Design caching strategy for application
**Usage**: `/performance:cache-strategy [--analyze-only]`
**Example**: `/performance:cache-strategy`

Analyzes application code to identify cacheable operations, designs multi-layer cache strategy, and generates cache implementation.

**Spawns**: cache-architect agent
**Outputs**:
- `src/cache/` - Cache implementation modules
- `.multiagent/reports/cache-strategy-{date}.md` - Strategy document

---

### `/performance:rate-limits` - Configure API rate limiting
**Usage**: `/performance:rate-limits [--strict|--moderate|--permissive]`
**Example**: `/performance:rate-limits --moderate`

Analyzes API endpoints and configures appropriate rate limits per endpoint, user tier, and IP address.

**Spawns**: rate-limiter-configurator agent
**Outputs**:
- `src/middleware/rate-limiter.{py|ts}` - Rate limiting middleware
- `config/rate-limits.yml` - Rate limit configuration

---

### `/performance:queues` - Set up background task queues
**Usage**: `/performance:queues [--backend=celery|bull|rabbitmq]`
**Example**: `/performance:queues --backend=celery`

Configures task queue system for async processing, scheduled jobs, and heavy computations.

**Spawns**: queue-designer agent
**Outputs**:
- `src/queues/tasks.{py|ts}` - Task definitions
- `src/queues/worker.{py|ts}` - Worker process
- `config/celery.{py|js}` - Queue configuration

---

### `/performance:analyze` - Analyze application performance bottlenecks
**Usage**: `/performance:analyze [file-or-directory]`
**Example**: `/performance:analyze src/api/`

Scans code for performance issues: N+1 queries, missing caching, synchronous heavy operations, inefficient algorithms.

**Spawns**: performance-analyzer agent
**Outputs**:
- `.multiagent/reports/performance-analysis-{date}.md` - Detailed findings
- `.multiagent/reports/optimization-recommendations-{date}.md` - Action items

---

### `/performance:benchmark` - Run performance benchmarks
**Usage**: `/performance:benchmark [--endpoints|--database|--cache]`
**Example**: `/performance:benchmark --endpoints`

Executes performance tests on critical paths and generates benchmark report with baseline metrics.

**Spawns**: Uses existing testing infrastructure
**Outputs**:
- `.multiagent/reports/benchmark-{date}.md` - Performance metrics
- `.multiagent/memory/performance-baselines.json` - Historical baselines

---

## Architecture

```
User runs /performance:{command}
      ↓
Command orchestrates:
1. Run script (profile code, measure response times, check Redis)
2. Invoke agent (design cache strategy, identify bottlenecks)
3. Generate from templates (cache layer, rate limiter, queue workers)
4. Validate output (test cache hits, verify rate limits work)
5. Display summary (cache hit rates, bottlenecks found, queue status)
```

## How It Works

1. **Command Invocation**: User runs `/performance:{command}` with optional backend/strategy arguments
2. **Script Execution**: Scripts profile application, measure baseline performance, check infrastructure availability
3. **Agent Analysis**: Intelligent agents analyze access patterns, identify bottlenecks, design optimal caching strategy
4. **Template Generation**: Agents generate cache managers, rate limiters, queue workers from templates
5. **Output Validation**: System tests cache functionality, validates rate limiting works, starts queue workers
6. **User Feedback**: Display performance improvements, cache hit rates, identified bottlenecks with fixes

## Directory Structure

```
.multiagent/performance/
├── README.md              # This file
├── docs/                  # Conceptual documentation
│   ├── caching-strategies.md
│   ├── rate-limiting.md
│   ├── queue-management.md
│   ├── connection-pooling.md
│   └── auto-scaling.md
├── templates/             # Generation templates
│   ├── caching/
│   │   ├── cache-manager.template.py
│   │   ├── cache-manager.template.ts
│   │   ├── redis-config.template.yml
│   │   └── cache-decorator.template.py
│   ├── rate-limiting/
│   │   ├── rate-limiter.template.py
│   │   ├── rate-limiter.template.ts
│   │   └── rate-limit-config.template.yml
│   ├── queues/
│   │   ├── celery-tasks.template.py
│   │   ├── bull-queue.template.ts
│   │   ├── worker.template.py
│   │   └── rabbitmq-config.template.yml
│   ├── database/
│   │   ├── connection-pool.template.py
│   │   └── connection-pool.template.ts
│   └── docker/
│       └── docker-compose.performance.template.yml
├── scripts/               # Mechanical operations only
│   ├── profile-performance.sh
│   ├── benchmark-endpoints.sh
│   └── check-cache-hit-rate.sh
└── memory/               # Agent state storage
    └── performance-baselines.json
```

## Templates

Templates in this subsystem:

- `templates/caching/cache-manager.template.py` - Python cache manager with Redis backend
- `templates/caching/cache-manager.template.ts` - TypeScript cache manager with Redis backend
- `templates/caching/redis-config.template.yml` - Redis configuration with persistence
- `templates/rate-limiting/rate-limiter.template.py` - Python rate limiting middleware
- `templates/rate-limiting/rate-limiter.template.ts` - TypeScript rate limiting middleware
- `templates/rate-limiting/rate-limit-config.template.yml` - Rate limit rules per endpoint
- `templates/queues/celery-tasks.template.py` - Celery task definitions
- `templates/queues/bull-queue.template.ts` - Bull queue setup for Node.js
- `templates/queues/worker.template.py` - Queue worker process
- `templates/database/connection-pool.template.py` - Database connection pooling
- `templates/docker/docker-compose.performance.template.yml` - Redis, RabbitMQ, workers

## Scripts

Mechanical scripts in this subsystem:

- `scripts/profile-performance.sh` - Profiles application code to identify slow functions
- `scripts/benchmark-endpoints.sh` - Runs load tests against API endpoints
- `scripts/check-cache-hit-rate.sh` - Reports Redis cache hit/miss ratio

## Outputs

This subsystem generates:

```
docker-compose.performance.yml       # Performance infrastructure

src/cache/
├── cache-manager.{py|ts}           # Cache layer implementation
├── cache-keys.{py|ts}              # Cache key generation
└── __init__.{py|ts}

src/middleware/
├── rate-limiter.{py|ts}            # Rate limiting middleware
└── __init__.{py|ts}

src/queues/
├── tasks.{py|ts}                   # Background task definitions
├── worker.{py|ts}                  # Worker process
└── __init__.{py|ts}

src/database/
└── pool.{py|ts}                    # Connection pool manager

config/
├── redis.yml                       # Redis configuration
├── rate-limits.yml                 # Rate limiting rules
└── celery.{py|js}                  # Queue configuration

kubernetes/
└── hpa-rules.yml                   # Auto-scaling policies

.multiagent/reports/
├── cache-strategy-*.md             # Caching strategy document
├── performance-analysis-*.md       # Bottleneck analysis
└── benchmark-*.md                  # Performance benchmarks
```

## Usage Example

```bash
# Step 1: Initialize performance infrastructure (Redis + queues)
/performance:init --all

# Step 2: Design caching strategy based on application
/performance:cache-strategy

# Step 3: Configure rate limiting for API endpoints
/performance:rate-limits --moderate

# Step 4: Set up background task queues
/performance:queues --backend=celery

# Step 5: Analyze code for performance bottlenecks
/performance:analyze src/

# Step 6: Run performance benchmarks
/performance:benchmark --endpoints

# Result: Application has caching, rate limiting, queues, and performance baseline
# Redis: localhost:6379
# RabbitMQ: localhost:5672
# Cache hit rate: Check with scripts/check-cache-hit-rate.sh
```

## Troubleshooting

### Cache always returns misses
**Problem**: Redis configured but cache hit rate is 0%
**Solution**:
```bash
# Check Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping

# Verify cache keys are being set
redis-cli KEYS '*'

# Check cache implementation is used
grep -r "cache_manager" src/

# Run cache hit rate script
~/.multiagent/performance/scripts/check-cache-hit-rate.sh
```

### Rate limiter blocking legitimate requests
**Problem**: Users hitting rate limits during normal usage
**Solution**:
```bash
# Check current rate limit config
cat config/rate-limits.yml

# Review rate limiter logs for patterns
grep "rate_limit" logs/application.log

# Adjust limits for specific endpoints
# Edit config/rate-limits.yml

# Consider implementing per-user tiers
# Free: 100 req/hour, Pro: 1000 req/hour, Enterprise: unlimited
```

### Queue workers not processing jobs
**Problem**: Tasks queued but not executing
**Solution**:
```bash
# Check if worker process is running
ps aux | grep celery  # or grep node for Bull

# Verify queue backend is accessible
# For RabbitMQ:
curl http://localhost:15672/api/overview

# Check for errors in worker logs
tail -f logs/celery-worker.log

# Test queue connection manually
python -c "from src.queues.tasks import add; add.delay(2, 2)"

# Start worker if not running
celery -A src.queues worker --loglevel=info
```

### Database connection pool exhausted
**Problem**: "Too many connections" or connection timeouts
**Solution**:
```bash
# Check current pool size configuration
cat config/database.yml | grep pool

# Monitor active connections
# PostgreSQL:
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Increase pool size if needed
# Edit config/database.yml: pool_size: 20

# Check for connection leaks (not closing connections)
grep -r "\.connect()" src/ | grep -v "\.close()"

# Review slow queries that hold connections
tail -f logs/slow-queries.log
```

## Related Subsystems

- **ai-infrastructure**: AI API calls benefit from semantic caching to reduce costs
- **observability**: Monitors cache hit rates, queue lengths, response times
- **reliability**: Circuit breakers prevent cascade failures from slow operations
- **deployment**: Auto-scaling rules deployed with application

## Future Enhancements

Planned features for this subsystem:

- [ ] Semantic caching for AI responses based on embedding similarity
- [ ] Adaptive rate limiting that adjusts based on system load
- [ ] Queue priority management with deadline scheduling
- [ ] Read-through and write-through cache patterns
- [ ] Cache warming strategies for predictable access patterns
- [ ] Distributed rate limiting across multiple instances
- [ ] Dead letter queue handling for failed tasks
- [ ] Connection pool health monitoring and auto-recovery
- [ ] Predictive auto-scaling based on traffic patterns
- [ ] Cache analytics dashboard showing hit rates by key pattern
