# MultiAgent Core

**Production-ready multi-agent development framework with intelligent automation**

[![PyPI version](https://badge.fury.io/py/multiagent-core.svg)](https://pypi.org/project/multiagent-core/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Quick Start

```bash
# Install from PyPI
pip install multiagent-core

# Initialize a new project
multiagent init my-project
cd my-project

# Check installation
multiagent status
```

## What is MultiAgent Core?

A comprehensive framework that transforms any project into a coordinated multi-agent development environment. Provides:

- 🤖 **Agent Coordination** - Claude, Copilot, Qwen, Gemini, Codex working in parallel via git worktrees
- 🔌 **MCP Integration** - Model Context Protocol servers with on-demand loading (43-48% more context)
- 📋 **Automated Workflows** - Slash commands for testing, deployment, PR reviews, and documentation
- 🔧 **Smart Project Detection** - Auto-detects tech stack and generates optimal configurations
- 🔒 **Security First** - Built-in secret scanning, compliance checks, and safe deletion protocols
- 📊 **Comprehensive Testing** - Unified testing strategy with intelligent project detection
- 🚀 **Production-Ready AI Infrastructure** - Cost tracking, monitoring, caching, reliability patterns, GDPR compliance

## 📐 Scales from Simple to Complex

The framework works for **any project size**:

| Type | Setup Time | Use Case |
|------|-----------|----------|
| **Landing Page** | 10 min | Portfolio, single-page sites |
| **Website** | 30 min | Marketing sites, blogs |
| **Web App** | 2-4 hrs | SaaS, dashboards |
| **AI App** | 6-8 hrs | AI-powered platforms |
| **SaaS** | Days | Enterprise systems |

**Same commands, different depth.** Start with a landing page, grow to AI SaaS.

```bash
# Landing page
/core:project-setup 001 --type=landing-page
# ✅ Live in 10 minutes

# Later: Upgrade to web app
/core:upgrade-to web-app
# ✅ Adds backend + database, keeps everything else
```

📖 **Details**: [docs/architecture/04-operations-reference.md#project-type-system](docs/architecture/04-operations-reference.md#project-type-system)

## 🎯 AI SaaS Production Readiness

For AI-powered applications, the framework provides **production-grade infrastructure** out of the box:

### AI Infrastructure
- **Cost Tracking**: Monitor AI costs across OpenAI, Anthropic, Gemini
- **Model Orchestration**: Automatic fallbacks, rate limiting, circuit breakers
- **Prompt Management**: Versioned prompts with A/B testing
- **Token Optimization**: Context window management and caching

### Observability
- **Prometheus + Grafana**: Full monitoring stack with AI-specific metrics
- **Distributed Tracing**: OpenTelemetry/Jaeger integration
- **Alert Rules**: 30+ production alerts (costs, latency, errors)
- **SLI/SLO Tracking**: Production readiness validation

### Performance
- **Multi-Layer Caching**: L1 (in-memory) → L2 (Redis) → L3 (DB)
- **Rate Limiting**: Per-endpoint, per-user, per-IP with token bucket
- **Queue Management**: Celery/Bull for async processing
- **Auto-Scaling**: HPA configurations with custom metrics

### Reliability
- **Circuit Breakers**: Prevent cascading failures
- **Retry Logic**: Exponential backoff with jitter
- **Health Checks**: Kubernetes-compatible liveness/readiness probes
- **Graceful Degradation**: Bulkhead patterns and fallback chains

### Compliance
- **GDPR Tools**: Complete API for access, erasure, portability, rectification
- **PII Detection**: Automatic scanning and anonymization
- **Audit Logging**: Immutable compliance trail
- **Consent Management**: Granular consent tracking with withdrawal support

**Impact**: Reduces time to production from **10-12 weeks to 2-3 weeks** for AI SaaS applications.

📖 **Full Details**: [AI_INFRASTRUCTURE_BUILD_SUMMARY.md](AI_INFRASTRUCTURE_BUILD_SUMMARY.md)

## Core Commands

```bash
multiagent init              # Initialize framework in project
multiagent status            # Show component installation status
multiagent detect            # Detect project tech stack
multiagent doctor            # Health check and diagnostics
multiagent env-init          # Generate smart environment config
multiagent upgrade           # Update all components

# Template Management
multiagent templates list    # List available template variants
multiagent templates swap    # Swap active template (e.g., docker → podman)
multiagent templates add     # Add custom template variant
multiagent templates active  # Show currently active templates
```

**What `multiagent init` does**:
- Installs global framework to `~/.multiagent/`
- Sets up MCP server registry in `~/.multiagent/config/` with update protection
- Migrates existing registry from `~/.claude/` (if found)
- Creates project configs (`.mcp.json`, `.vscode/mcp.json`)
- Registers project for automatic template updates
- Initializes git repository (optional)
- Sets up GitHub integration (optional)

📖 **Full details**: [docs/architecture/03-system-setup.md#installation--initialization](docs/architecture/03-system-setup.md#installation--initialization)

## Slash Commands

Powerful automation via Claude Code slash commands:

### 🤖 AI Infrastructure
- `/ai-infrastructure:init` - Initialize AI cost tracking & orchestration
- `/ai-infrastructure:cost-report` - Generate AI cost analysis
- `/ai-infrastructure:model-health` - Check AI provider health

### 📊 Observability
- `/observability:start` - Deploy monitoring stack (Prometheus, Grafana, Jaeger)
- `/observability:mid` - Monitor metrics collection
- `/observability:end` - Validate production readiness

### ⚡ Performance
- `/performance:init` - Initialize caching, rate limiting, queues
- `/performance:analyze` - Analyze bottlenecks (N+1, slow queries)
- `/performance:cache-strategy` - Design multi-layer caching

### 🛡️ Reliability
- `/reliability:init` - Initialize circuit breakers & resilience
- `/reliability:analyze` - Identify single points of failure
- `/reliability:circuit-breaker` - Add circuit breakers to services

### 🔒 Compliance
- `/compliance:init` - Initialize PII detection & audit logging
- `/compliance:scan-pii` - Scan for exposed PII
- `/compliance:gdpr-tools` - Implement GDPR tools (DSAR, deletion, portability)

### 🧪 Testing
- `/testing:test` - Unified testing with intelligent routing
- `/testing:test-generate` - Generate test structure from tasks
- `/testing:test-prod` - Production readiness validation

### 🚀 Deployment
- `/deployment:deploy-prepare` - Orchestrate deployment prep
- `/deployment:deploy-validate` - Validate deployment config
- `/deployment:deploy-run` - Execute local deployment
- `/deployment:deploy` - Deploy to cloud platforms
- `/deployment:prod-ready` - Comprehensive production scan

### 🔄 Iteration
- `/iterate:tasks` - Apply task layering for parallel work
- `/iterate:sync` - Sync entire spec ecosystem
- `/iterate:adjust` - Live development adjustments

### 👁️ Supervision
- `/supervisor:start` - Pre-work agent verification
- `/supervisor:mid` - Progress monitoring
- `/supervisor:end` - Pre-PR completion checks

### 🔀 Git Automation
- `/git:worktree-create` - Create isolated worktree for parallel development
- `/git:worktree-cleanup` - Remove worktree and cleanup branches
- `/git:commit-smart` - Generate standardized commit messages
- `/git:branch-cleanup` - Cleanup merged and stale branches

### 📝 Documentation
- `/docs:init`, `/docs:update`, `/docs:validate`

### 🐙 GitHub Integration
- `/github:create-issue` - Create issues with templates
- `/github:pr-review` - Analyze PR feedback
- `/github:discussions` - Manage discussions

### 🔌 MCP Server Management
- `/mcp:setup` - Interactive wizard for API key configuration
- `/mcp:list` - Show all available MCP servers
- `/mcp:add <server>` - Add server to current project
- `/mcp:remove <server>` - Remove server from project
- `/mcp:status` - Show project's MCP configuration
- `/mcp:clear` - Remove all servers (maximize context)

### 🔧 Build System
- `/build:subsystem` - Create new subsystem with standardized structure
- `/build:slash-command` - Create new slash command
- `/build:agent` - Create new agent definition
- `/build:analyze` - Analyze existing subsystems or architecture
- `/build:enhance` - Enhance existing subsystem components
- `/build:remove` - **Remove subsystem/command/agent with impact analysis**

## MCP Integration

**Model Context Protocol (MCP) servers extend Claude Code with custom tools and integrations.**

MultiAgent Core uses a **two-tier MCP system** to maximize context window:

1. **Global Registry** (`~/.claude/mcp-servers-registry.json`) - Available servers catalog
2. **Per-Project Config** (`.mcp.json`, `.vscode/mcp.json`) - Load only what's needed

### Quick Start

```bash
# One-time setup: Add API keys to shell config
/mcp:config edit

# View available servers
/mcp:list

# Add servers to your project
/mcp:add github memory

# Check project status
/mcp:status
```

### Available MCP Servers

**Standard Servers:**
- `github` - GitHub API integration
- `postman` - API testing & collections
- `memory` - Persistent conversation memory
- `playwright` - Browser automation
- `filesystem` - File/directory operations
- `supabase` - Supabase backend operations

**Custom Servers (with local/remote variants):**
- `signalhire` - Talent search API
- `airtable` - Database operations
- `twilio` - SMS/voice communications
- `calendly` - Appointment scheduling

### Context Window Optimization

**Problem:** Auto-loading all MCP servers = ~96,000 tokens wasted
**Solution:** Load servers on-demand = 43-48% more context available

```bash
# ❌ Bad: Global auto-load (wastes tokens everywhere)
~/.claude/settings.json with all servers

# ✅ Good: Per-project as needed
cd project-a && /mcp:add github memory
cd project-b && /mcp:add postman
cd project-c                              # No servers = max context
```

### API Key Management

API keys are stored in `~/.bashrc` (single source of truth) and **hardcoded** into project configs:

```bash
# View configured keys
/mcp:check

# Add/update keys
/mcp:config edit
# Or manually: nano ~/.bashrc
# Add: export POSTMAN_API_KEY="your-key"
source ~/.bashrc
```

**Security:**
- Keys stored in `~/.bashrc` (not committed to git)
- Project configs (`.mcp.json`, `.vscode/mcp.json`) are gitignored
- `/mcp:add` reads from environment and hardcodes values (no `${VAR}` placeholders)

### Adding Custom Servers to Registry

**Use the `/mcp:registry` command to add custom servers:**

```bash
# Add a new server to the registry
/mcp:registry add your-server local npx

# Follow prompts for:
# - Package name: @your-org/your-mcp-server
# - Environment variables: YOUR_API_KEY
# - Description: Your server description
```

**Then add API keys and use your server:**

```bash
# Add API key
/mcp:config edit
# Add: export YOUR_API_KEY="your-key"
source ~/.bashrc

# Add to project
/mcp:add your-server
```

**Or manually edit `~/.claude/mcp-servers-registry.json`** (see complete guide for format)

**📚 Documentation:**
- **Quick Start:** [docs/MCP_QUICK_START.md](docs/MCP_QUICK_START.md)
- **Complete Guide:** `~/.claude/MCP_COMPLETE_GUIDE.md` (run `/docs mcp` to load)

## Project Structure

After `multiagent init`:

```
your-project/
├── .multiagent/              # Core automation system
│   ├── agents/              # Agent coordination infrastructure
│   ├── ai-infrastructure/   # AI cost tracking & orchestration
│   ├── backend/             # Backend development guidance
│   ├── compliance/          # GDPR, CCPA, HIPAA compliance tools
│   ├── core/                # Agent workflows & templates
│   ├── deployment/          # Deployment automation
│   ├── documentation/       # Documentation generation
│   ├── experiment/          # Safe experimentation workflows
│   ├── frontend/            # Frontend development guidance
│   ├── github/              # GitHub integration & PR review
│   ├── iterate/             # Task layering & spec sync
│   ├── mcp/                 # MCP server management
│   ├── observability/       # Monitoring & metrics
│   ├── performance/         # Performance optimization
│   ├── reliability/         # Circuit breakers & resilience
│   ├── security/            # Security scanning & compliance
│   ├── supervisor/          # Agent monitoring
│   ├── testing/             # Test generation & execution
│   └── version-management/  # Semantic versioning
├── .claude/                  # Claude Code configuration
│   ├── agents/              # Specialized agent definitions
│   ├── commands/            # Slash command definitions
│   └── hooks/               # Git hooks & automation
├── .github/workflows/        # CI/CD automation
└── specs/                   # Feature specifications & tasks
```

## Architecture

```
multiagent_core/
├── cli.py              # Main CLI with 15+ commands
├── detector.py         # Tech stack detection
├── analyzer.py         # Environment analysis
├── env_generator.py    # Smart .env generation
├── auto_updater.py     # Auto-update system
├── config.py           # Configuration management
└── templates/          # Deployment templates
```

## Development Workflow

**For Contributors:**

1. **Install in editable mode:**
   ```bash
   pip install -e . --force
   ```

2. **Edit source templates** in root directories (`.multiagent/`, `.claude/`)
   - Build system auto-syncs to `multiagent_core/templates/`

3. **Test changes:**
   ```bash
   cd /tmp && multiagent init test-project
   ```

4. **Build & test distribution:**
   ```bash
   python -m build
   pip install dist/multiagent_core-*.whl --force
   ```

## Automation Systems

Each subsystem is self-contained with its own README:

| System | Path | Purpose |
|--------|------|---------|
| **Agents** | `.multiagent/agents/` | Agent coordination infrastructure & git workflows |
| **AI Infrastructure** | `.multiagent/ai-infrastructure/` | AI cost tracking, model orchestration, prompt management |
| **Backend** | `.multiagent/backend/` | Backend development guidance & API patterns |
| **Compliance** | `.multiagent/compliance/` | GDPR, CCPA, HIPAA compliance tools & PII detection |
| **Core** | `.multiagent/core/` | Agent workflows, templates, coordination |
| **Deployment** | `.multiagent/deployment/` | Multi-platform deployment automation |
| **Documentation** | `.multiagent/documentation/` | Documentation generation & validation |
| **Experiment** | `.multiagent/experiment/` | Safe experimentation & rollback workflows |
| **Frontend** | `.multiagent/frontend/` | Frontend development guidance & UI patterns |
| **GitHub** | `.multiagent/github/` | GitHub integration & PR review automation |
| **Iterate** | `.multiagent/iterate/` | Spec synchronization & task layering |
| **MCP** | `.multiagent/mcp/` | MCP server registry & management |
| **Observability** | `.multiagent/observability/` | Monitoring, metrics, alerting (Prometheus, Grafana, ELK) |
| **Performance** | `.multiagent/performance/` | Performance optimization, caching, rate limiting |
| **Refactoring** | `.multiagent/refactoring/` | Code quality improvement, duplicate extraction, pattern modernization |
| **Reliability** | `.multiagent/reliability/` | Circuit breakers, graceful degradation, health checks |
| **Security** | `.multiagent/security/` | Secret scanning, compliance, auditing |
| **Supervisor** | `.multiagent/supervisor/` | Agent monitoring & compliance |
| **Testing** | `.multiagent/testing/` | Intelligent test generation & execution |
| **Version Management** | `.multiagent/version-management/` | Semantic versioning automation |

## Release & Versioning

- **Semantic Versioning** via conventional commits
- **Automated Releases** on push to main
- **PyPI Publishing** via GitHub Actions
- **Version Management** - `.github/workflows/version-management.yml`

Commit format:
```
feat: Add new command
fix: Resolve deployment issue
docs: Update README
chore: Bump dependencies
```

## Testing

```bash
# Run full test suite
python -m pytest

# GitHub Actions tests:
# - Ubuntu, Windows, macOS
# - Python 3.8-3.12
# - pip, pipx, source installs
```

## Documentation

### User Documentation
- **User Guide**: [`.multiagent/README.md`](multiagent_core/templates/.multiagent/README.md) - Complete framework guide (deployed to projects)
- **AI Infrastructure Summary**: [`AI_INFRASTRUCTURE_BUILD_SUMMARY.md`](AI_INFRASTRUCTURE_BUILD_SUMMARY.md) - 5 production-ready subsystems

### Architecture & Standards
- **Architecture Overview**: [`docs/architecture/01-architecture-overview.md`](docs/architecture/01-architecture-overview.md) - Three-tier system architecture, layered orchestration
- **Development Guide**: [`docs/architecture/02-development-guide.md`](docs/architecture/02-development-guide.md) - Build standards, dependencies & build order
- **Operations Reference**: [`docs/architecture/04-operations-reference.md#subsystem-lifecycle`](docs/architecture/04-operations-reference.md#subsystem-lifecycle) - Subsystem lifecycle including safe deletion

### Workflows & Guides
- **Build Workflow**: [`docs/workflows/BUILD_WORKFLOW.md`](docs/workflows/BUILD_WORKFLOW.md) - Step-by-step guide for building subsystems
- **Template Management**: [`docs/TEMPLATE_MANAGEMENT.md`](docs/TEMPLATE_MANAGEMENT.md) - Template system guide
- **Development Guide**: [`DEVELOPMENT.md`](DEVELOPMENT.md) - Contributor setup

### Reports & Analysis
- **Build Analysis Reports**: `docs/reports/build-analysis/` - Subsystem compliance reports
- **Report Generation Guide**: [`docs/reports/REPORT_GENERATION_GUIDE.md`](docs/reports/REPORT_GENERATION_GUIDE.md) - All report types documented

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with conventional commits
4. Test with `python -m pytest`
5. Submit PR with detailed description

## License

MIT License - see LICENSE file

---

**Install now:** `pip install multiagent-core`

**Documentation:** [.multiagent/README.md](.multiagent/README.md)
# Auto-sync test
