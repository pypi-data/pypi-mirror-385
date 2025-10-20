# Compliance

## Purpose

Data compliance and privacy infrastructure including PII detection and anonymization, audit logging, GDPR/CCPA compliance tools, data retention policies, and consent management.

## What It Does

1. **PII Detection & Anonymization** - Automatically detect and anonymize personally identifiable information in logs, databases, and API responses
2. **Audit Logging** - Comprehensive audit trail for data access, modifications, and deletions with tamper-proof storage
3. **GDPR/CCPA Compliance** - Tools for data subject access requests (DSAR), right to deletion, data portability, and consent tracking
4. **Data Retention Policies** - Automated data lifecycle management with configurable retention periods and secure deletion
5. **Consent Management** - User consent tracking, preference centers, and granular permission management

## Agents Used

- **@claude/pii-detector** - Scans code and data for PII exposure and generates anonymization strategies
- **@claude/audit-architect** - Designs comprehensive audit logging system for compliance requirements
- **@claude/gdpr-implementor** - Implements GDPR/CCPA data subject rights and compliance workflows
- **@claude/retention-planner** - Creates data retention policies and automated cleanup procedures

## Commands

### `/compliance:init` - Initialize compliance infrastructure
**Usage**: `/compliance:init [--regulation=gdpr|ccpa|hipaa|all]`
**Example**: `/compliance:init --regulation=gdpr`

Sets up compliance infrastructure including PII detection, audit logging, consent management, and data retention policies.

**Spawns**: pii-detector, audit-architect, gdpr-implementor agents
**Outputs**:
- `src/compliance/pii-detector.{py|ts}` - PII detection and anonymization
- `src/compliance/audit-logger.{py|ts}` - Audit logging system
- `src/compliance/consent-manager.{py|ts}` - Consent tracking
- `config/compliance.yml` - Compliance configuration

---

### `/compliance:scan-pii` - Scan codebase for PII exposure
**Usage**: `/compliance:scan-pii [file-or-directory]`
**Example**: `/compliance:scan-pii src/`

Detects PII in code, logs, and data structures including emails, phone numbers, SSNs, credit cards, IP addresses.

**Spawns**: pii-detector agent
**Outputs**:
- `.multiagent/reports/pii-scan-{date}.md` - PII exposure report
- `.multiagent/reports/anonymization-plan-{date}.md` - Remediation steps

---

### `/compliance:audit-log` - Configure comprehensive audit logging
**Usage**: `/compliance:audit-log [--events=data-access|modifications|deletions|all]`
**Example**: `/compliance:audit-log --events=all`

Adds audit logging to data access points, capturing who accessed what data, when, and from where.

**Spawns**: audit-architect agent
**Outputs**:
- `src/compliance/audit-logger.{py|ts}` - Audit logging middleware
- `database/migrations/audit_log_table.sql` - Audit log schema
- `config/audit-events.yml` - Event definitions

---

### `/compliance:gdpr-tools` - Implement GDPR compliance tools
**Usage**: `/compliance:gdpr-tools [--feature=dsar|deletion|portability|all]`
**Example**: `/compliance:gdpr-tools --feature=all`

Creates endpoints and workflows for GDPR data subject rights: access requests, deletion, portability, consent withdrawal.

**Spawns**: gdpr-implementor agent
**Outputs**:
- `src/compliance/dsar.{py|ts}` - Data subject access request handler
- `src/compliance/deletion.{py|ts}` - Right to deletion (right to be forgotten)
- `src/compliance/portability.{py|ts}` - Data portability export
- API endpoints: `/api/dsar`, `/api/delete-my-data`, `/api/export-my-data`

---

### `/compliance:retention` - Configure data retention policies
**Usage**: `/compliance:retention [--default-period=30d|90d|1y|7y]`
**Example**: `/compliance:retention --default-period=90d`

Implements automated data lifecycle management with retention periods and secure deletion.

**Spawns**: retention-planner agent
**Outputs**:
- `src/compliance/retention.{py|ts}` - Retention policy engine
- `config/retention-policies.yml` - Retention rules per data type
- `scripts/cleanup-expired-data.sh` - Automated cleanup script

---

### `/compliance:consent` - Set up consent management system
**Usage**: `/compliance:consent [--granularity=simple|granular]`
**Example**: `/compliance:consent --granular`

Creates user consent tracking system with preference centers and opt-in/opt-out management.

**Spawns**: gdpr-implementor agent
**Outputs**:
- `src/compliance/consent-manager.{py|ts}` - Consent tracking
- `database/migrations/consent_table.sql` - Consent storage schema
- `src/ui/consent-banner.{jsx|vue}` - Cookie consent UI component

---

### `/compliance:report` - Generate compliance status report
**Usage**: `/compliance:report [--regulation=gdpr|ccpa|hipaa]`
**Example**: `/compliance:report --regulation=gdpr`

Generates comprehensive compliance report showing PII exposure, audit coverage, consent rates, and gaps.

**Spawns**: audit-architect agent
**Outputs**:
- `.multiagent/reports/compliance-status-{date}.md` - Compliance scorecard
- `.multiagent/reports/compliance-gaps-{date}.md` - Remediation roadmap

---

## Architecture

```
User runs /compliance:{command}
      ↓
Command orchestrates:
1. Run script (scan for PII, check audit logs, review data retention)
2. Invoke agent (design anonymization, create audit schema, generate DSAR handlers)
3. Generate from templates (PII detectors, audit loggers, consent trackers)
4. Validate output (test PII masking, verify audit logs persist, check DSAR works)
5. Display summary (PII found, audit coverage %, compliance gaps)
```

## How It Works

1. **Command Invocation**: User runs `/compliance:{command}` with optional regulation/feature arguments
2. **Script Execution**: Scripts scan for PII patterns, check existing audit logs, measure data retention
3. **Agent Analysis**: Intelligent agents identify PII exposure risks, design audit schema, create GDPR workflows
4. **Template Generation**: Agents generate PII detectors, audit logging middleware, consent management systems
5. **Output Validation**: System tests PII anonymization works, audit logs persist correctly, DSAR endpoints function
6. **User Feedback**: Display PII exposure count, audit coverage percentage, compliance scorecard, gaps to address

## Directory Structure

```
.multiagent/compliance/
├── README.md              # This file
├── docs/                  # Conceptual documentation
│   ├── pii-detection.md
│   ├── audit-logging.md
│   ├── gdpr-compliance.md
│   ├── ccpa-compliance.md
│   └── data-retention.md
├── templates/             # Generation templates
│   ├── pii/
│   │   ├── pii-detector.template.py
│   │   ├── pii-detector.template.ts
│   │   └── anonymization-rules.template.yml
│   ├── audit/
│   │   ├── audit-logger.template.py
│   │   ├── audit-logger.template.ts
│   │   ├── audit-schema.template.sql
│   │   └── audit-middleware.template.py
│   ├── gdpr/
│   │   ├── dsar-handler.template.py
│   │   ├── dsar-handler.template.ts
│   │   ├── deletion-handler.template.py
│   │   └── portability-exporter.template.py
│   ├── consent/
│   │   ├── consent-manager.template.py
│   │   ├── consent-manager.template.ts
│   │   ├── consent-banner.template.jsx
│   │   └── consent-schema.template.sql
│   └── retention/
│       ├── retention-engine.template.py
│       ├── retention-policies.template.yml
│       └── cleanup-job.template.py
├── scripts/               # Mechanical operations only
│   ├── scan-for-pii.sh
│   ├── check-audit-coverage.sh
│   └── validate-retention-policies.sh
└── memory/               # Agent state storage
    └── compliance-baselines.json
```

## Templates

Templates in this subsystem:

- `templates/pii/pii-detector.template.py` - Python PII detection using regex and NLP
- `templates/pii/pii-detector.template.ts` - TypeScript PII detection
- `templates/pii/anonymization-rules.template.yml` - Anonymization strategies per PII type
- `templates/audit/audit-logger.template.py` - Python audit logging middleware
- `templates/audit/audit-logger.template.ts` - TypeScript audit logging middleware
- `templates/audit/audit-schema.template.sql` - Audit log database schema
- `templates/gdpr/dsar-handler.template.py` - Data subject access request handler
- `templates/gdpr/deletion-handler.template.py` - Right to deletion implementation
- `templates/gdpr/portability-exporter.template.py` - Data portability export in JSON/CSV
- `templates/consent/consent-manager.template.py` - Consent tracking and verification
- `templates/consent/consent-banner.template.jsx` - Cookie consent UI component
- `templates/retention/retention-engine.template.py` - Automated data cleanup engine
- `templates/retention/retention-policies.template.yml` - Retention rules configuration

## Scripts

Mechanical scripts in this subsystem:

- `scripts/scan-for-pii.sh` - Scans code and logs for PII patterns (emails, SSN, credit cards)
- `scripts/check-audit-coverage.sh` - Verifies all data access points have audit logging
- `scripts/validate-retention-policies.sh` - Checks retention policies are enforced correctly

## Outputs

This subsystem generates:

```
src/compliance/
├── pii-detector.{py|ts}            # PII detection and anonymization
├── audit-logger.{py|ts}            # Audit logging middleware
├── consent-manager.{py|ts}         # Consent tracking system
├── dsar-handler.{py|ts}            # Data subject access requests
├── deletion-handler.{py|ts}        # Right to deletion
├── portability.{py|ts}             # Data portability exports
├── retention-engine.{py|ts}        # Data retention automation
└── __init__.{py|ts}

src/middleware/
└── audit-middleware.{py|ts}        # Request/response audit logging

src/ui/components/
├── consent-banner.{jsx|vue}        # Cookie consent banner
└── privacy-preferences.{jsx|vue}   # User preference center

database/migrations/
├── audit_log_table.sql             # Audit log schema
├── consent_table.sql               # User consent records
└── retention_metadata.sql          # Retention policy metadata

config/
├── pii-patterns.yml                # PII detection patterns
├── audit-events.yml                # Auditable event definitions
├── retention-policies.yml          # Data retention rules
└── compliance.yml                  # General compliance config

api/endpoints/
├── dsar.{py|ts}                    # POST /api/dsar
├── delete-my-data.{py|ts}          # POST /api/delete-my-data
└── export-my-data.{py|ts}          # GET /api/export-my-data

scripts/
└── cleanup-expired-data.sh         # Cron job for data deletion

.multiagent/reports/
├── pii-scan-*.md                   # PII exposure report
├── audit-coverage-*.md             # Audit logging coverage
├── compliance-status-*.md          # Overall compliance scorecard
└── compliance-gaps-*.md            # Remediation roadmap
```

## Usage Example

```bash
# Step 1: Initialize compliance infrastructure for GDPR
/compliance:init --regulation=gdpr

# Step 2: Scan codebase for PII exposure
/compliance:scan-pii src/

# Step 3: Add comprehensive audit logging
/compliance:audit-log --events=all

# Step 4: Implement GDPR data subject rights
/compliance:gdpr-tools --feature=all

# Step 5: Configure data retention policies
/compliance:retention --default-period=90d

# Step 6: Set up consent management
/compliance:consent --granular

# Step 7: Generate compliance status report
/compliance:report --regulation=gdpr

# Result: GDPR-compliant application with PII protection, audit logging, DSAR support
# Endpoints:
# - POST /api/dsar (data subject access request)
# - POST /api/delete-my-data (right to be forgotten)
# - GET /api/export-my-data (data portability)
# - GET /api/consent (manage consent preferences)
```

## Troubleshooting

### PII still appearing in logs after anonymization
**Problem**: Sensitive data being logged despite PII detector
**Solution**:
```bash
# Check PII detector is initialized in logging config
grep "pii_detector" config/logging.yml

# Verify PII patterns are comprehensive
cat config/pii-patterns.yml

# Test PII detector manually
python -c "from src.compliance.pii_detector import anonymize; print(anonymize('email@example.com'))"

# Add custom PII patterns
# Edit config/pii-patterns.yml to add domain-specific patterns

# Review recent logs for PII
~/.multiagent/compliance/scripts/scan-for-pii.sh logs/
```

### Audit logs not capturing all data access
**Problem**: Some database queries not appearing in audit log
**Solution**:
```bash
# Check audit middleware is registered
grep "audit_middleware" src/app.{py,ts}

# Verify audit events configuration
cat config/audit-events.yml

# Check audit coverage
~/.multiagent/compliance/scripts/check-audit-coverage.sh

# Add audit logging to missing endpoints
# Decorate functions with @audit_log decorator

# Query audit log to see what's being captured
SELECT event_type, COUNT(*) FROM audit_log GROUP BY event_type;
```

### DSAR request timing out
**Problem**: Data subject access request takes too long or fails
**Solution**:
```bash
# Check DSAR handler implementation
cat src/compliance/dsar-handler.{py,ts}

# Review data export query performance
# May need indexes on user_id columns

# Consider async DSAR with email notification
# Large exports should be queued as background jobs

# Check database query logs for slow queries
tail -f logs/slow-queries.log

# Test DSAR for test user
curl -X POST http://localhost:8000/api/dsar \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_id": "test-user"}'
```

### Data not being deleted per retention policy
**Problem**: Expired data still present in database
**Solution**:
```bash
# Check retention policies configuration
cat config/retention-policies.yml

# Verify cleanup cron job is running
crontab -l | grep cleanup-expired-data

# Manually run cleanup script
bash scripts/cleanup-expired-data.sh --dry-run

# Check retention metadata table
SELECT data_type, retention_days, last_cleanup
FROM retention_metadata;

# Review deletion logic
cat src/compliance/retention-engine.{py,ts}

# Ensure soft delete vs hard delete is configured correctly
# GDPR may require hard delete for right to erasure
```

### Consent banner not appearing for users
**Problem**: Cookie consent banner not showing on website
**Solution**:
```bash
# Check consent component is imported
grep "ConsentBanner" src/ui/App.{jsx,tsx,vue}

# Verify consent manager is initialized
grep "consent_manager" src/main.{py,ts,js}

# Check browser console for JavaScript errors
# Open DevTools and look for consent-related errors

# Test consent status check
curl http://localhost:8000/api/consent/status

# Review consent banner CSS (may be hidden)
grep "consent-banner" src/styles/

# Check if user already consented (banner hides after consent)
# Clear cookies and reload
```

## Related Subsystems

- **security**: Encryption for PII at rest, secure API keys for compliance tools
- **observability**: Monitors audit log volume, PII detection alerts, consent rates
- **ai-infrastructure**: PII detection in AI prompts/responses, audit AI data usage
- **deployment**: Ensure compliance configs deployed to production environments

## Future Enhancements

Planned features for this subsystem:

- [ ] Real-time PII detection in API requests/responses
- [ ] Machine learning-based PII detection for complex patterns
- [ ] Automated GDPR compliance scoring and certification readiness
- [ ] Data lineage tracking (where PII flows through system)
- [ ] Consent version management and change history
- [ ] Integration with privacy management platforms (OneTrust, TrustArc)
- [ ] Differential privacy for analytics on sensitive data
- [ ] Blockchain-based immutable audit logs
- [ ] Automated breach notification workflows
- [ ] Multi-language consent forms and privacy policies
