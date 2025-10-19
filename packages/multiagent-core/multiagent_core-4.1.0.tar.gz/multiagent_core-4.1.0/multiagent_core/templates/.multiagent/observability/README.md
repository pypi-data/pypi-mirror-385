# Observability

## Purpose

Monitoring, metrics, logging, and alerting infrastructure for production applications including Prometheus, Grafana, distributed tracing, and AI-specific metrics.

## What It Does

1. **Metrics Collection** - Deploy Prometheus for metrics scraping, custom application metrics, and AI cost/performance tracking
2. **Visualization** - Set up Grafana dashboards for system health, AI performance, cost trends, and custom business metrics
3. **Distributed Tracing** - Implement OpenTelemetry/Jaeger for request tracing across services and AI API calls
4. **Log Aggregation** - Configure centralized logging (ELK stack or alternatives) with structured logs and search
5. **Alerting** - Define alert rules for system health, cost thresholds, AI errors, and performance degradation

## Agents Used

- **@claude/observability-setup** - Generates monitoring stack configuration for Prometheus, Grafana, and logging
- **@claude/dashboard-generator** - Creates custom Grafana dashboards based on application metrics
- **@claude/alert-configurator** - Analyzes application requirements and creates intelligent alert rules
- **@claude/tracing-instrumentor** - Adds distributed tracing instrumentation to application code

## Commands

### `/observability:start` - Initialize monitoring stack for project (Phase 1: Setup)
**Usage**: `/observability:start [--stack=prometheus|elk|all]`
**Example**: `/observability:start --stack=all`

Deploys monitoring infrastructure including Prometheus, Grafana, and optionally ELK stack. Sets up Docker Compose configurations, initializes dashboards, and configures data sources.

**Spawns**: observability-setup agent
**Outputs**:
- `docker-compose.observability.yml` - Monitoring services
- `prometheus/prometheus.yml` - Prometheus config
- `grafana/dashboards/` - Pre-built dashboards
- `grafana/datasources/` - Data source configs

---

### `/observability:mid` - Check monitoring health and data collection (Phase 2: Progress)
**Usage**: `/observability:mid`
**Example**: `/observability:mid`

Validates that monitoring stack is collecting metrics, dashboards are rendering data, and alerts are configured correctly. Shows summary of active metrics, dashboard status, and any collection issues.

**Spawns**: observability-validator agent
**Outputs**: Terminal status report with health checks

---

### `/observability:end` - Validate monitoring before production (Phase 3: Completion)
**Usage**: `/observability:end`
**Example**: `/observability:end`

Comprehensive validation that monitoring is production-ready: all metrics collecting, dashboards accessible, alerts tested, logs flowing, and tracing working.

**Spawns**: observability-validator agent
**Outputs**:
- `.multiagent/reports/observability-readiness-{date}.md` - Readiness report
- Pass/fail for production deployment gate

---

### `/observability:dashboard` - Generate custom Grafana dashboard
**Usage**: `/observability:dashboard [--type=ai|api|system|business]`
**Example**: `/observability:dashboard --type=ai`

Creates tailored Grafana dashboard based on application type. AI dashboards include cost, token usage, latency; API dashboards show endpoint performance, error rates.

**Spawns**: dashboard-generator agent
**Outputs**:
- `grafana/dashboards/{name}-dashboard.json` - Grafana dashboard definition

---

### `/observability:alerts` - Configure alert rules
**Usage**: `/observability:alerts [--severity=critical|warning|info]`
**Example**: `/observability:alerts --severity=critical`

Analyzes application and generates intelligent alert rules for Prometheus Alertmanager. Includes AI cost thresholds, error rate spikes, latency degradation, and resource exhaustion.

**Spawns**: alert-configurator agent
**Outputs**:
- `prometheus/alerts/rules.yml` - Alert rule definitions
- `.multiagent/docs/alert-playbook.md` - Response procedures

---

### `/observability:trace` - Add distributed tracing instrumentation
**Usage**: `/observability:trace [file-or-directory]`
**Example**: `/observability:trace src/api/`

Instruments code with OpenTelemetry tracing spans, automatically identifying trace points at API endpoints, database calls, and AI requests.

**Spawns**: tracing-instrumentor agent
**Outputs**: Modified source files with tracing added

---

## Architecture

```
User runs /observability:{command}
      ↓
Command orchestrates:
1. Run script (check Docker, validate configs, test endpoints)
2. Invoke agent (generate dashboards, analyze metrics, configure alerts)
3. Generate from templates (Prometheus config, Grafana dashboards, alert rules)
4. Validate output (start services, test dashboard load, trigger test alerts)
5. Display summary (URLs for Grafana, alert status, metric counts)
```

## How It Works

1. **Command Invocation**: User runs `/observability:{command}` with optional stack/type arguments
2. **Script Execution**: Scripts check prerequisites (Docker installed, ports available), validate existing configs
3. **Agent Analysis**: Intelligent agents analyze application structure, identify metrics to track, generate appropriate dashboards
4. **Template Generation**: Agents fill templates for Prometheus config, Grafana dashboards, alerting rules
5. **Output Validation**: System starts monitoring services, verifies metrics flowing, tests dashboard access
6. **User Feedback**: Display monitoring URLs, metric collection status, alert configuration summary

## Directory Structure

```
.multiagent/observability/
├── README.md              # This file
├── docs/                  # Conceptual documentation
│   ├── prometheus-setup.md
│   ├── grafana-dashboards.md
│   ├── distributed-tracing.md
│   ├── elk-stack.md
│   └── alerting-best-practices.md
├── templates/             # Generation templates
│   ├── prometheus/
│   │   ├── prometheus.template.yml
│   │   ├── alert-rules.template.yml
│   │   └── scrape-configs.template.yml
│   ├── grafana/
│   │   ├── dashboard-ai.template.json
│   │   ├── dashboard-api.template.json
│   │   ├── dashboard-system.template.json
│   │   └── datasource.template.yml
│   ├── tracing/
│   │   ├── otel-config.template.yml
│   │   └── jaeger-config.template.yml
│   ├── logging/
│   │   ├── fluentd.template.conf
│   │   └── elasticsearch.template.yml
│   └── docker/
│       └── docker-compose.observability.template.yml
├── scripts/               # Mechanical operations only
│   ├── check-monitoring-health.sh
│   ├── test-metric-collection.sh
│   └── validate-dashboards.sh
└── memory/               # Agent state storage
    └── baseline-metrics.json
```

## Templates

Templates in this subsystem:

- `templates/prometheus/prometheus.template.yml` - Main Prometheus server configuration
- `templates/prometheus/alert-rules.template.yml` - Alertmanager rule definitions
- `templates/grafana/dashboard-ai.template.json` - AI-specific metrics dashboard
- `templates/grafana/dashboard-api.template.json` - API performance dashboard
- `templates/grafana/dashboard-system.template.json` - System resource dashboard
- `templates/grafana/datasource.template.yml` - Grafana data source config
- `templates/tracing/otel-config.template.yml` - OpenTelemetry collector config
- `templates/tracing/jaeger-config.template.yml` - Jaeger tracing backend config
- `templates/logging/fluentd.template.conf` - Fluentd log collector config
- `templates/docker/docker-compose.observability.template.yml` - Complete monitoring stack

## Scripts

Mechanical scripts in this subsystem:

- `scripts/check-monitoring-health.sh` - Tests Prometheus, Grafana, and tracing endpoints
- `scripts/test-metric-collection.sh` - Verifies metrics are being scraped and stored
- `scripts/validate-dashboards.sh` - Checks all dashboards load without errors

## Outputs

This subsystem generates:

```
docker-compose.observability.yml     # Monitoring stack services

prometheus/
├── prometheus.yml                   # Main config
├── alerts/
│   └── rules.yml                   # Alert definitions
└── targets/
    └── scrape-configs.yml          # Scrape target configs

grafana/
├── dashboards/
│   ├── ai-metrics.json             # AI cost & performance
│   ├── api-performance.json        # API endpoint metrics
│   └── system-health.json          # Resource utilization
├── datasources/
│   └── prometheus.yml              # Prometheus data source
└── provisioning/
    └── dashboards.yml              # Dashboard provisioning

jaeger/                              # Distributed tracing
└── jaeger-config.yml

logging/                             # If ELK stack enabled
├── fluentd.conf
└── elasticsearch.yml

.multiagent/reports/
├── observability-readiness-*.md    # Production readiness report
└── alert-playbook.md               # Alert response procedures
```

## Usage Example

```bash
# Step 1: Initialize monitoring stack (Prometheus + Grafana)
/observability:start --stack=prometheus

# Step 2: Check that metrics are being collected
/observability:mid

# Step 3: Add AI-specific dashboard
/observability:dashboard --type=ai

# Step 4: Configure critical alerts
/observability:alerts --severity=critical

# Step 5: Add tracing to API endpoints
/observability:trace src/api/

# Step 6: Validate production readiness
/observability:end

# Result: Full observability stack with dashboards, alerts, and tracing
# Access Grafana: http://localhost:3000 (admin/admin)
# Access Prometheus: http://localhost:9090
# Access Jaeger: http://localhost:16686
```

## Troubleshooting

### Grafana dashboards show "No data"
**Problem**: Dashboards configured but not displaying metrics
**Solution**:
```bash
# Check Prometheus is scraping targets
curl http://localhost:9090/api/v1/targets

# Verify data source connection in Grafana
curl http://localhost:3000/api/datasources

# Test if app is exposing metrics
curl http://localhost:8000/metrics

# Run health check script
~/.multiagent/observability/scripts/check-monitoring-health.sh
```

### Alerts not firing despite conditions met
**Problem**: Alert rules configured but Alertmanager not triggering
**Solution**:
```bash
# Check alert rule syntax
promtool check rules prometheus/alerts/rules.yml

# Verify Alertmanager is running
docker ps | grep alertmanager

# Check alert status in Prometheus
curl http://localhost:9090/api/v1/alerts

# Review Alertmanager config
cat alertmanager/alertmanager.yml
```

### Traces not appearing in Jaeger
**Problem**: Distributed tracing instrumented but traces missing
**Solution**:
```bash
# Verify OpenTelemetry collector is running
docker ps | grep otel-collector

# Check if application is exporting traces
# Look for OTLP export logs in application

# Test Jaeger query API
curl http://localhost:16686/api/services

# Verify trace instrumentation in code
grep -r "tracer\|span" src/
```

### Prometheus high memory usage
**Problem**: Prometheus consuming excessive memory/disk
**Solution**:
```bash
# Check retention settings
cat prometheus/prometheus.yml | grep retention

# Review scrape interval (may be too frequent)
cat prometheus/prometheus.yml | grep scrape_interval

# Reduce metric cardinality (remove high-cardinality labels)
# Check for label explosion in metrics

# Consider using recording rules for aggregations
```

## Related Subsystems

- **ai-infrastructure**: Provides AI cost/token metrics that observability stack monitors
- **performance**: Caching and rate limiting metrics feed into observability dashboards
- **reliability**: Circuit breaker states and health checks monitored by observability
- **deployment**: Monitoring stack deployed alongside application services

## Future Enhancements

Planned features for this subsystem:

- [ ] Automatic anomaly detection using machine learning on metrics
- [ ] Log-based alerting with pattern matching
- [ ] Service dependency mapping and automatic trace visualization
- [ ] Cost attribution by service/feature using metrics
- [ ] Automated dashboard generation from code annotations
- [ ] Integration with incident management (PagerDuty, Opsgenie)
- [ ] Custom metric exporters for business KPIs
- [ ] Distributed tracing correlation with logs
- [ ] Metric retention policies and downsampling
- [ ] Multi-environment dashboard comparison (staging vs production)
