# Reliability

## Purpose

Reliability and resilience patterns including circuit breakers, graceful degradation, health checks, retry logic with exponential backoff, bulkheads, and disaster recovery procedures.

## What It Does

1. **Circuit Breakers** - Prevent cascade failures by automatically stopping calls to failing services with configurable thresholds and recovery
2. **Graceful Degradation** - Maintain core functionality when dependencies fail by falling back to cached data or reduced features
3. **Health Checks** - Deep health monitoring for application, database, cache, and external services with automatic recovery
4. **Retry Logic** - Intelligent retry with exponential backoff, jitter, and circuit breaker integration for transient failures
5. **Bulkheads** - Isolate resources and thread pools to prevent single component failures from affecting entire system

## Agents Used

- **@claude/circuit-breaker-configurator** - Analyzes service dependencies and configures circuit breaker patterns
- **@claude/health-check-generator** - Creates comprehensive health checks for all system components
- **@claude/retry-strategist** - Designs retry strategies based on failure patterns and SLAs
- **@claude/resilience-architect** - Reviews architecture for single points of failure and designs resilience improvements

## Commands

### `/reliability:init` - Initialize reliability patterns for project
**Usage**: `/reliability:init [--pattern=circuit-breaker|retry|health-check|all]`
**Example**: `/reliability:init --pattern=all`

Sets up reliability infrastructure including circuit breakers, health check endpoints, retry decorators, and graceful degradation patterns.

**Spawns**: circuit-breaker-configurator, health-check-generator agents
**Outputs**:
- `src/reliability/circuit-breaker.{py|ts}` - Circuit breaker implementation
- `src/reliability/retry.{py|ts}` - Retry logic with backoff
- `src/health/` - Health check endpoints
- `config/reliability.yml` - Reliability configuration

---

### `/reliability:circuit-breaker` - Add circuit breaker to services
**Usage**: `/reliability:circuit-breaker [file-or-service]`
**Example**: `/reliability:circuit-breaker src/services/payment-api.py`

Analyzes service calls and wraps them with circuit breakers to prevent cascade failures during outages.

**Spawns**: circuit-breaker-configurator agent
**Outputs**:
- Modified source files with circuit breaker decorators
- `config/circuit-breakers.yml` - Circuit breaker thresholds

---

### `/reliability:health-checks` - Generate comprehensive health checks
**Usage**: `/reliability:health-checks [--deep|--shallow]`
**Example**: `/reliability:health-checks --deep`

Creates health check endpoints that test database connectivity, cache availability, external API status, and application readiness.

**Spawns**: health-check-generator agent
**Outputs**:
- `src/health/health-check.{py|ts}` - Health check endpoint
- `src/health/probes.{py|ts}` - Individual probe implementations
- `/health` endpoint configuration for load balancers

---

### `/reliability:retry-strategy` - Configure retry logic for operations
**Usage**: `/reliability:retry-strategy [file-or-directory]`
**Example**: `/reliability:retry-strategy src/api/`

Adds intelligent retry logic with exponential backoff to API calls, database operations, and external service integrations.

**Spawns**: retry-strategist agent
**Outputs**:
- Modified source files with retry decorators
- `config/retry-policies.yml` - Retry configuration

---

### `/reliability:analyze` - Identify single points of failure
**Usage**: `/reliability:analyze`
**Example**: `/reliability:analyze`

Scans architecture for reliability issues: missing circuit breakers, lack of health checks, no retry logic, unprotected external calls.

**Spawns**: resilience-architect agent
**Outputs**:
- `.multiagent/reports/reliability-analysis-{date}.md` - Vulnerability report
- `.multiagent/reports/resilience-recommendations-{date}.md` - Improvements

---

### `/reliability:disaster-recovery` - Generate disaster recovery plan
**Usage**: `/reliability:disaster-recovery [--rto=1h|4h|24h] [--rpo=0|15m|1h]`
**Example**: `/reliability:disaster-recovery --rto=1h --rpo=15m`

Creates disaster recovery procedures, backup strategies, and failover plans based on RTO/RPO requirements.

**Spawns**: resilience-architect agent
**Outputs**:
- `.multiagent/docs/disaster-recovery-plan.md` - DR procedures
- `scripts/backup-restore.sh` - Backup automation
- `kubernetes/multi-region-config.yml` - Multi-region deployment

---

## Architecture

```
User runs /reliability:{command}
      ↓
Command orchestrates:
1. Run script (test services, check dependencies, measure response times)
2. Invoke agent (identify failure points, design resilience patterns)
3. Generate from templates (circuit breakers, retry logic, health checks)
4. Validate output (test failures trigger circuit breaker, retries work)
5. Display summary (protected services, health check status, SPOF report)
```

## How It Works

1. **Command Invocation**: User runs `/reliability:{command}` with optional pattern/threshold arguments
2. **Script Execution**: Scripts test service connectivity, measure failure rates, check existing protections
3. **Agent Analysis**: Intelligent agents identify vulnerable dependencies, design circuit breaker thresholds, create health checks
4. **Template Generation**: Agents generate circuit breaker wrappers, retry decorators, health probe implementations
5. **Output Validation**: System simulates failures to verify circuit breakers trip, retries execute, health checks detect issues
6. **User Feedback**: Display protected services, circuit breaker status, health check results, identified vulnerabilities

## Directory Structure

```
.multiagent/reliability/
├── README.md              # This file
├── docs/                  # Conceptual documentation
│   ├── circuit-breakers.md
│   ├── retry-patterns.md
│   ├── health-checks.md
│   ├── graceful-degradation.md
│   └── disaster-recovery.md
├── templates/             # Generation templates
│   ├── circuit-breaker/
│   │   ├── circuit-breaker.template.py
│   │   ├── circuit-breaker.template.ts
│   │   └── circuit-breaker-config.template.yml
│   ├── retry/
│   │   ├── retry-decorator.template.py
│   │   ├── retry-decorator.template.ts
│   │   └── retry-policies.template.yml
│   ├── health/
│   │   ├── health-check-endpoint.template.py
│   │   ├── health-check-endpoint.template.ts
│   │   ├── database-probe.template.py
│   │   └── api-probe.template.py
│   ├── degradation/
│   │   ├── fallback-handler.template.py
│   │   └── fallback-handler.template.ts
│   └── kubernetes/
│       ├── readiness-probe.template.yml
│       └── liveness-probe.template.yml
├── scripts/               # Mechanical operations only
│   ├── test-circuit-breakers.sh
│   ├── check-health-endpoints.sh
│   └── simulate-failures.sh
└── memory/               # Agent state storage
    └── failure-history.json
```

## Templates

Templates in this subsystem:

- `templates/circuit-breaker/circuit-breaker.template.py` - Python circuit breaker implementation
- `templates/circuit-breaker/circuit-breaker.template.ts` - TypeScript circuit breaker implementation
- `templates/circuit-breaker/circuit-breaker-config.template.yml` - Threshold configuration
- `templates/retry/retry-decorator.template.py` - Python retry with exponential backoff
- `templates/retry/retry-decorator.template.ts` - TypeScript retry with exponential backoff
- `templates/retry/retry-policies.template.yml` - Retry policy definitions per service
- `templates/health/health-check-endpoint.template.py` - Health check HTTP endpoint
- `templates/health/database-probe.template.py` - Database connectivity probe
- `templates/health/api-probe.template.py` - External API health probe
- `templates/degradation/fallback-handler.template.py` - Graceful degradation fallback logic
- `templates/kubernetes/readiness-probe.template.yml` - K8s readiness probe config
- `templates/kubernetes/liveness-probe.template.yml` - K8s liveness probe config

## Scripts

Mechanical scripts in this subsystem:

- `scripts/test-circuit-breakers.sh` - Simulates failures to verify circuit breakers trip
- `scripts/check-health-endpoints.sh` - Tests all health check endpoints return correct status
- `scripts/simulate-failures.sh` - Chaos engineering - randomly kill dependencies to test resilience

## Outputs

This subsystem generates:

```
src/reliability/
├── circuit-breaker.{py|ts}         # Circuit breaker implementation
├── retry.{py|ts}                   # Retry logic with backoff
├── bulkhead.{py|ts}                # Resource isolation
└── __init__.{py|ts}

src/health/
├── health-check.{py|ts}            # Main health endpoint
├── probes/
│   ├── database.{py|ts}            # Database probe
│   ├── cache.{py|ts}               # Redis probe
│   ├── external-api.{py|ts}        # External service probe
│   └── disk-space.{py|ts}          # Disk space probe
└── __init__.{py|ts}

config/
├── circuit-breakers.yml            # Circuit breaker thresholds
├── retry-policies.yml              # Retry configuration
└── health-checks.yml               # Health check configuration

kubernetes/
├── readiness-probe.yml             # K8s readiness config
├── liveness-probe.yml              # K8s liveness config
└── multi-region.yml                # Multi-region deployment

.multiagent/docs/
└── disaster-recovery-plan.md       # DR procedures

.multiagent/reports/
├── reliability-analysis-*.md       # Vulnerability assessment
└── resilience-recommendations-*.md # Improvement plan
```

## Usage Example

```bash
# Step 1: Initialize reliability patterns
/reliability:init --pattern=all

# Step 2: Add circuit breakers to external services
/reliability:circuit-breaker src/services/

# Step 3: Generate health check endpoints
/reliability:health-checks --deep

# Step 4: Add retry logic to API calls
/reliability:retry-strategy src/api/

# Step 5: Analyze for single points of failure
/reliability:analyze

# Step 6: Generate disaster recovery plan
/reliability:disaster-recovery --rto=1h --rpo=15m

# Result: Application has circuit breakers, health checks, retry logic, DR plan
# Health endpoint: http://localhost:8000/health
# Readiness: http://localhost:8000/health/ready
# Liveness: http://localhost:8000/health/alive
```

## Troubleshooting

### Circuit breaker not tripping on failures
**Problem**: Service continues calling failing dependency
**Solution**:
```bash
# Check circuit breaker configuration
cat config/circuit-breakers.yml

# Verify circuit breaker is wrapping the service call
grep -r "circuit_breaker" src/services/

# Test circuit breaker manually
~/.multiagent/reliability/scripts/test-circuit-breakers.sh

# Check failure threshold (may be set too high)
# Default: 5 failures in 10 seconds trips circuit
# Edit config/circuit-breakers.yml to lower threshold

# Review circuit breaker state
# Should log: "Circuit OPEN for service X"
grep "Circuit OPEN" logs/application.log
```

### Health check always returns 200 even when dependencies down
**Problem**: Health endpoint reports healthy but database/cache unavailable
**Solution**:
```bash
# Check if deep health checks are enabled
cat config/health-checks.yml | grep deep

# Verify probes are implemented for all dependencies
ls -la src/health/probes/

# Test individual probes
python -c "from src.health.probes.database import check; print(check())"

# Review health check implementation
cat src/health/health-check.{py,ts}

# Ensure health endpoint aggregates all probes
grep "check_database\|check_cache\|check_api" src/health/
```

### Retries causing request timeouts
**Problem**: Too many retries leading to slow response times
**Solution**:
```bash
# Check retry policy configuration
cat config/retry-policies.yml

# Reduce max retries or increase backoff
# Edit config/retry-policies.yml:
# max_retries: 3 → 2
# backoff_multiplier: 2 → 1.5

# Add timeout to prevent infinite retries
# Add: timeout: 5000  # 5 seconds max

# Consider using circuit breaker instead of retries
# Circuit breaker fails fast when service is down

# Review retry logs to see patterns
grep "Retry attempt" logs/application.log | tail -20
```

### Application not recovering from dependency outage
**Problem**: After external service recovers, app still degraded
**Solution**:
```bash
# Check circuit breaker half-open state
# Circuit should try requests after timeout
grep "Circuit HALF_OPEN" logs/application.log

# Verify health checks are recovering
curl http://localhost:8000/health

# Review circuit breaker timeout settings
cat config/circuit-breakers.yml | grep timeout
# Default: 60 seconds before retry

# May need to manually reset circuit breaker
# Or restart application to clear circuit state

# Check for resource exhaustion (connection pools)
# May need to restart to free resources
```

## Related Subsystems

- **observability**: Monitors circuit breaker states, retry attempts, health check failures
- **ai-infrastructure**: AI API calls protected with circuit breakers and retry logic
- **performance**: Circuit breakers prevent slow services from exhausting resources
- **deployment**: Health checks used by load balancers and Kubernetes orchestration

## Future Enhancements

Planned features for this subsystem:

- [ ] Adaptive circuit breaker thresholds based on traffic patterns
- [ ] Chaos engineering automation (controlled failure injection)
- [ ] Service mesh integration (Istio/Linkerd) for resilience
- [ ] Automatic rollback on deployment health check failures
- [ ] Distributed circuit breaker state (shared across instances)
- [ ] Predictive failure detection using ML on metrics
- [ ] Automated disaster recovery testing and validation
- [ ] Cross-region traffic failover automation
- [ ] Resource quota management and bulkhead enforcement
- [ ] Integration with incident management for automatic escalation
