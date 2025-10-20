# MultiAgent Framework

**Intelligent development framework orchestrating specialized AI subagents through slash commands.**

## 🏗️ Architecture: How The Layers Work Together

### The 3-Layer Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: USER & MAIN AGENT (@claude, @qwen, etc.)              │
│ - User provides high-level goals                                │
│ - Main agent plans and coordinates                              │
│ - Executes slash commands to invoke subagents                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: SLASH COMMANDS (Subsystem Orchestrators)              │
│ /docs:init          → Spawns docs-init subagent                │
│ /testing:test       → Spawns backend-tester subagent           │
│ /deployment:prepare → Spawns deployment-prep subagent          │
│ /github:pr-review   → Spawns judge-architect subagent          │
│ /iterate:tasks      → Spawns task-layering subagent            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: SUBAGENTS (Specialized Workers)                       │
│ - docs-init: Reads templates, fills content, writes docs       │
│ - deployment-prep: Analyzes specs, generates configs           │
│ - backend-tester: Writes tests, validates APIs                 │
│ - judge-architect: Reviews PRs, generates feedback             │
│ - test-generator: Creates test structure from tasks            │
│                                                                 │
│ Subagents use subsystem resources:                             │
│ - .multiagent/{subsystem}/templates/                           │
│ - .multiagent/{subsystem}/scripts/                             │
│ - .multiagent/{subsystem}/docs/                                │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principle: Subagents Handle Complexity

**Old Pattern (Deprecated):**
```bash
# Scripts did the work directly
.multiagent/deployment/scripts/generate-deployment.sh
```

**New Pattern (Current):**
```bash
# Main agent runs slash command
/deployment:deploy-prepare 001

# Slash command spawns subagent
→ deployment-prep subagent activated

# Subagent handles complexity
→ Reads .multiagent/deployment/templates/
→ Analyzes specs/001-*/spec.md
→ Generates deployment configs
→ Creates .github/workflows/deploy.yml
→ May call scripts as utilities
```

**Why This Works:**
- Main agent stays focused on coordination
- Subagents have specialized knowledge
- Slash commands provide consistent interface
- Scripts become utilities, not primary logic

## 📋 The 4 Development Phases

MultiAgent organizes work into clear phases, each with specific commands and subagents.

### Phase 1-2: SETUP (Spec Creation)

**Who:** User + Main Agent + Spec-Kit
**Output:** Specification documents

```bash
# 1. Initialize project with SpecKit
specify init --here --ai claude

# 2. Create feature specification
/specify                    # → specs/001-feature-name/spec.md

# 3. Create technical plan
/plan                       # → plan.md, data-model.md

# 4. Generate sequential tasks
/tasks                      # → tasks.md

# ✓ Spec directory ready for MultiAgent
```

### Phase 3: PROJECT SETUP (Infrastructure Deployment)

**Who:** Main Agent + Setup Subagents
**Output:** Project infrastructure and initial configs

#### Step 1: Deploy Framework
```bash
multiagent init
# ✓ Deploys .multiagent/, .claude/, .github/, .vscode/
```

#### Step 2: Initialize Documentation
```bash
/docs:init [--project-type <type>]

# Spawns: docs-init subagent
# Reads templates from:
#   - .multiagent/documentation/templates/
#   - .multiagent/security/templates/docs/
# Writes to: docs/
# Creates: ARCHITECTURE.md, SECURITY.md, README.md, etc.
```

#### Step 3: Generate Deployment Configs
```bash
/deployment:deploy-prepare 001

# Spawns: deployment-prep subagent
# Reads templates from: .multiagent/deployment/templates/
# Analyzes: specs/001-*/spec.md, plan.md
# Writes to: deployment/, .github/workflows/deploy.yml
# Creates: Dockerfile, docker-compose.yml, k8s manifests
```

#### Step 4: Generate Test Structure
```bash
/testing:test-generate 001

# Spawns: test-generator subagent
# Reads templates from: .multiagent/testing/templates/
# Analyzes: specs/001-*/tasks.md
# Writes to: tests/, .github/workflows/ci.yml
# Creates: Test files organized by task complexity
```

#### Step 5: Generate Environment Configuration
```bash
/security:create-env create

# Spawns: env-generator subagent
# Script: ~/.multiagent/security/scripts/analyze-project-keys.sh (file discovery)
# Template: ~/.multiagent/security/templates/env/.env.template (structure)
# Analyzes: specs/, docs/, configs, MCP servers
# Writes to: .env (in current project)
# Categorizes: AI, Communication, Data, Business, Infrastructure
# Includes: Source annotations, dashboard URLs
```

#### Step 6: Layer Tasks for Parallel Work
```bash
/iterate:tasks 001

# Spawns: task-layering subagent
# Reads: specs/001-*/tasks.md
# Analyzes: Dependencies, complexity, agent skills
# Writes to: specs/001-*/agent-tasks/layered-tasks.md
# Organizes: Foundation → Implementation → Testing layers
# Assigns: Tasks to specific agents (@claude, @qwen, etc.)
```

#### Step 7: Setup Agent Worktrees (Optional)
```bash
.multiagent/iterate/scripts/setup-spec-worktrees.sh 001

# Creates isolated worktrees for each assigned agent
# ✓ ../project-claude (agent-claude-001)
# ✓ ../project-codex (agent-codex-001)
# ✓ ../project-qwen (agent-qwen-001)
```

**✓ Project Setup Complete** - Ready for development

---

### Phase 4: DEVELOPMENT (Feature Implementation)

**Who:** Multiple Agents Working in Parallel
**Output:** Feature implementation in isolated branches

#### Continuous Development Commands

```bash
# Update documentation automatically (queue-based)
/docs:auto-update
# Spawns: docs-auto-updater subagent
# Processes queued updates from post-commit hooks
# Batch processes multiple commits at once

# OR manual targeted update
/docs:update [--check-patterns]
# Spawns: docs-update subagent
# Manual updates based on current code state

# Run tests during development
/testing:test [--quick|--create|--backend|--frontend]
# Spawns: backend-tester or frontend-playwright-tester subagent
# Intelligently routes to correct test framework

# Sync spec ecosystem after changes
/iterate:sync 001
# Spawns: ecosystem-sync subagent
# Propagates spec changes to related files

# Adjust tasks during development
/iterate:adjust 001
# Spawns: live-adjust subagent
# Updates task assignments based on progress
```

#### Agent Workflow in Development
```bash
# Each agent in their worktree:
1. cd ../project-[agent]
2. grep "@[agent]" specs/001-*/agent-tasks/layered-tasks.md
3. Implement assigned tasks
4. Commit work regularly
5. Push to branch when complete
6. Create PR
```

#### Progress Monitoring
```bash
# Check mid-development compliance
/supervisor:mid 001

# Spawns: supervisor-mid subagent
# Validates: Task completion, code quality, standards
# Reports: Progress, blockers, recommendations
```

**✓ Development Phase** - Agents work in parallel, main agent coordinates

---

### Phase 4.5: PR REVIEW & FEEDBACK (Quality Gates)

**Who:** Main Agent + Judge Subagent
**Output:** PR analysis, feedback tasks, approval decisions

```bash
# 1. Agent creates PR from worktree
gh pr create --title "feat: implement auth system"

# 2. Analyze PR review feedback
/github:pr-review 123

# Spawns: judge-architect subagent
# Reads: GitHub PR #123 review comments
# Analyzes: Against specs/001-*/spec.md requirements
# Writes to: specs/001-*/feedback/
# Creates:
#   - judge-summary.md (APPROVE/DEFER/REJECT decision)
#   - tasks.md (actionable feedback items)
#   - future-enhancements.md
#   - plan.md (if architecture changes needed)

# 3. Create GitHub issues from feedback
/github:create-issue --feature "title"

# Spawns: github-issue subagent
# Creates properly formatted issues with templates

# 4. Pre-PR completion check
/supervisor:end 001

# Spawns: supervisor-end subagent
# Validates: All tasks complete, tests pass, ready for merge
# Blocks: If requirements not met
```

**Human Decision Point:**
- **APPROVE** → `gh pr merge 123`
- **DEFER** → Implement feedback tasks, iterate
- **REJECT** → Major changes needed, create new tasks

**✓ PR Review Complete** - Quality gates passed

---

### Phase 5: DEPLOYMENT (Production Readiness & Launch)

**Who:** Main Agent + Production Subagents
**Output:** Validated, secure, production-ready deployment

#### Pre-Deployment Validation

```bash
# 1. Validate production test coverage
/testing:test-prod [--fix] [--verbose]

# Spawns: production-test-validator subagent
# Scans: All code for remaining mocks
# Validates: Production APIs configured
# Reports: Mock locations, replacement suggestions
# Optionally: Auto-generates production replacements

# 2. Comprehensive production readiness scan
/deployment:prod-ready [--fix] [--verbose]

# Spawns: production-specialist subagent
# Checks:
#   - Security vulnerabilities (secrets, dependencies)
#   - Environment variables configured
#   - Production configs valid
#   - Build processes work
#   - Health checks pass
# Generates: Detailed readiness report
# Optionally: Auto-fixes common issues

# 3. Validate deployment configuration
/deployment:deploy-validate

# Spawns: deployment-validator subagent
# Validates:
#   - Dockerfile syntax
#   - docker-compose configuration
#   - Environment files complete
#   - K8s manifests valid
# Reports: Configuration issues

# 4. Validate documentation completeness
/docs:validate [--strict]

# Spawns: docs-validator subagent
# Checks:
#   - All placeholders filled
#   - Cross-document consistency
#   - Required sections present
# Reports: Documentation gaps
```

#### Local Deployment Testing

```bash
# 5. Test deployment locally
/deployment:deploy-run up

# Spawns: deployment-runner subagent
# Actions:
#   - Builds Docker images
#   - Starts containers via docker-compose
#   - Runs health checks
#   - Validates services running
# Commands: up, down, restart, logs, status

# Check deployment logs
/deployment:deploy-run logs

# Stop local deployment
/deployment:deploy-run down
```

#### Cloud Deployment

```bash
# 6. Deploy to preview environment
/deployment:deploy preview [--platform=vercel|aws|railway]

# Spawns: cloud-deployer subagent
# Actions:
#   - Builds production bundle
#   - Configures platform
#   - Deploys to preview URL
#   - Runs smoke tests
# Reports: Preview URL, deployment status

# 7. Deploy to production
/deployment:deploy production [--platform=vercel|aws|railway]

# Spawns: cloud-deployer subagent
# Requires: All validation checks passed
# Actions:
#   - Final security scan
#   - Production build
#   - Deploy to production
#   - Run health checks
#   - Monitor initial metrics
# Reports: Production URL, deployment summary
```

**✓ Deployment Complete** - Live in production

---

### Phase 6: END (Cleanup & Maintenance)

**Who:** Main Agent + Cleanup Utilities
**Output:** Clean workspace, archived work

```bash
# After PR merge - Clean up worktrees
cd /path/to/main/project
git checkout main && git pull

# Remove agent worktrees
git worktree remove ../project-claude
git worktree remove ../project-codex
git worktree remove ../project-qwen

# Delete branches
git branch -d agent-claude-001
git branch -d agent-codex-001
git branch -d agent-qwen-001

# Verify cleanup
git worktree list  # Should show only main project

# Continue monitoring
/deployment:prod-ready  # Periodic production health checks
/docs:auto-update       # Process queued doc updates from commits
```

**✓ Cycle Complete** - Ready for next feature

---

## 🎯 Subsystem Overview

MultiAgent has 25 specialized subsystems. Each owns its templates, scripts, and documentation.

**Framework Statistics:**
- **25 subsystems** in `.multiagent/`
- **120+ slash commands** across 25 command namespaces
- **70+ specialized agents** for autonomous work
- **103+ templates** for code generation

| Subsystem | Subagents | Primary Commands | Templates Location |
|-----------|-----------|------------------|-------------------|
| **Agents** | N/A | Coordination infrastructure | `.multiagent/agents/templates/` |
| **AI Infrastructure** | cost-tracker, model-orchestrator | `/ai-infrastructure:*` | `.multiagent/ai-infrastructure/templates/` |
| **Backend** | backend-tester | `/backend:develop`, `/backend:test` | `.multiagent/backend/templates/` |
| **Compliance** | pii-scanner, gdpr-tools | `/compliance:*` | `.multiagent/compliance/templates/` |
| **Core** | project-analyzer, project-setup-orchestrator, upgrade-orchestrator | `/core:project-setup`, `/core:upgrade-to`, `/core:build` | `.multiagent/core/` |
| **CTO** | cto-reviewer, architecture-auditor | `/cto:review`, `/cto:audit` | `.multiagent/cto/templates/` |
| **Deployment** | deployment-prep, deployment-validator, deployment-runner, production-specialist | `/deployment:*` | `.multiagent/deployment/templates/` |
| **Documentation** | docs-init, docs-auto-updater, docs-update, docs-validator, docs-fix | `/docs:*` | `.multiagent/documentation/templates/` |
| **Enhancement** | enhancement-analyzer | `/enhancement:create`, `/enhancement:analyze`, `/enhancement:list`, `/enhancement:status`, `/enhancement:start`, `/enhancement:promote` | `.multiagent/enhancement/` |
| **Frontend** | frontend-developer, frontend-playwright-tester | `/frontend:develop`, `/frontend:test` | `.multiagent/frontend/templates/` |
| **Git** | N/A | `/git:*` (6 commands) | `.multiagent/git/templates/` |
| **GitHub** | judge-architect, issue-reviewer | `/github:*` | `.multiagent/github/pr-review/templates/` |
| **Idea** | idea-capture | `/idea:capture`, `/idea:list` | `.multiagent/idea/templates/` |
| **Implementation** | implementation-tracker | `/implementation:track`, `/implementation:validate` | `.multiagent/implementation/templates/` |
| **Iterate** | task-layering, ecosystem-sync, live-adjust | `/iterate:*` | `.multiagent/iterate/templates/` |
| **MCP** | N/A | `/mcp:add`, `/mcp:remove`, `/mcp:status`, `/mcp:clear` | `.claude/commands/mcp/` |
| **Notes** | note-tracker, note-analyzer | `/note`, `/note:list`, `/note:close`, `/note:import` | `.multiagent/notes/templates/` |
| **Observability** | metrics-collector, alert-manager | `/observability:*` | `.multiagent/observability/templates/` |
| **Performance** | performance-analyzer, cache-optimizer | `/performance:*` | `.multiagent/performance/templates/` |
| **Refactoring** | code-refactorer | `/refactoring:refactor` | `.multiagent/refactoring/templates/` |
| **Reliability** | circuit-breaker, health-checker | `/reliability:*` | `.multiagent/reliability/templates/` |
| **Security** | env-generator, security-scanner, compliance-checker | `/security:*` | `.multiagent/security/templates/` |
| **Supervisor** | supervisor-start, supervisor-mid, supervisor-end | `/supervisor:*` | `.multiagent/supervisor/templates/` |
| **Testing** | test-generator, backend-tester, frontend-tester | `/testing:*` | `.multiagent/testing/templates/` |
| **Version Management** | version-bumper | `/version:*` | `.multiagent/version-management/` |

## 📚 Complete Directory Structure

```
.multiagent/
│
├── agents/                         # Agent Coordination Infrastructure
│   ├── docs/                       # Agent workflow guides
│   ├── templates/                  # Agent behavior templates (CLAUDE.md, etc.)
│   ├── prompts/                    # User prompt templates
│   └── hooks/                      # Git hooks (post-commit guidance)
│
├── core/                           # Project Setup Orchestrator (3-Phase Intelligent Setup)
│   ├── scripts/                    # Analysis & orchestration utilities
│   │   ├── detect-project-type.sh      # Infer type from spec keywords
│   │   ├── analyze-project-structure.sh # Scan stack and dependencies
│   │   ├── validate-prerequisites.sh    # Check required tools
│   │   └── backup-configuration.sh      # Backup before upgrades
│   ├── templates/                  # GitHub workflows, config templates
│   │   ├── github-workflows/      # CI/CD templates
│   │   └── github-config/         # Issue templates, labels
│   └── docs/                       # Setup documentation
│
├── deployment/                     # Deployment Configuration
│   ├── templates/                  # Dockerfile, K8s, compose templates
│   │   └── workflows/             # deploy.yml.template
│   ├── scripts/                   # Deployment utilities
│   └── logs/                      # Deployment execution logs
│
├── documentation/                  # Documentation Generation
│   ├── templates/                  # ARCHITECTURE.md, README.md templates
│   ├── scripts/                   # Doc generation utilities
│   └── memory/                    # Doc state tracking
│
├── enhancement/                    # Enhancement Lifecycle Management
│   ├── docs/                      # Enhancement workflow documentation
│   ├── memory/                    # Enhancement tracking state
│   ├── scripts/                   # Enhancement utilities
│   │   ├── get-next-id.sh         # Calculate next enhancement ID
│   │   ├── list-enhancements.sh   # List with status filtering
│   │   ├── update-status.sh       # Update status.json files
│   │   ├── start-enhancement.sh   # Create git safety tag
│   │   ├── rollback-enhancement.sh # Reset to safety tag
│   │   ├── cleanup-enhancement.sh  # Remove branch and tag
│   │   └── full-reset.sh          # Complete rollback sequence
│   └── templates/                 # Enhancement templates
│       ├── enhancement.md.template         # Enhancement description
│       ├── enhancement-metadata-schema.md  # Metadata format
│       ├── enhancement-status-schema.json  # Status tracking schema
│       └── enhancement-analysis-EXAMPLE.md # Analysis report example
│
├── iterate/                        # Task Organization
│   ├── templates/                  # layered-tasks.md.template
│   ├── scripts/                   # Task layering utilities
│   └── logs/                      # Task layering logs
│
├── github/                         # GitHub Integration & PR Review
│   ├── pr-review/                 # PR Review Subsystem (SHIPS TO USERS)
│   │   ├── templates/             # PR feedback templates (8 standardized)
│   │   │   ├── judge-output-review.md       # Judge agent execution flow
│   │   │   ├── pr-analysis.template.md      # PR technical analysis
│   │   │   └── pr-feedback-tasks.template.md # Task breakdown
│   │   └── scripts/               # PR processing scripts
│   │       └── process-pr-feedback.sh       # Extract PR data from GitHub API
│   └── issue-review/              # Issue Review Subsystem (CONTRIBUTOR-ONLY)
│       ├── templates/             # Issue analysis templates (3 standardized)
│       │   ├── issue-analysis.md        # Comprehensive analysis report
│       │   ├── issue-summary.md         # Quick reference
│       │   └── spec-from-issue.md       # Spec generation
│       └── scripts/               # Issue processing scripts (TBD)
│
├── security/                       # Security Enforcement
│   ├── templates/
│   │   ├── env/                   # .env.template (environment file generation)
│   │   ├── docs/                  # SECURITY.md.template
│   │   └── github-workflows/     # security-scan.yml.template
│   ├── hooks/                     # pre-push (secret scanning)
│   └── scripts/                   # analyze-project-keys.sh, scan-secrets.sh
│
├── supervisor/                     # Agent Compliance Monitoring
│   ├── templates/                  # compliance-report.md.template
│   ├── scripts/                   # Compliance validation
│   └── memory/                    # Compliance rules
│
└── testing/                        # Test Generation & Execution
    ├── templates/                  # Test file templates
    │   └── workflows/             # ci.yml.template
    ├── scripts/                   # Test generation utilities
    └── logs/                      # Test execution logs
```

## 🔌 MCP Server Registry System - Universal Server Management

> 📚 **Full Documentation**: See [MCP_USAGE_GUIDE.md](./MCP_USAGE_GUIDE.md) for comprehensive usage guide including:
> - Detailed command reference with examples
> - Security best practices (never hardcode keys!)
> - API key organization in `~/.mcp-keys/`
> - Troubleshooting and common workflows
> - **VS Code Copilot integration** (unified `.mcp.json` + `.vscode/mcp.json` system)

### The Problem: Managing MCP Servers Across Projects

**Before:** Hardcoded server lists per-project, no central management
**Now:** Global registry of all available servers, add to any project on-demand
**Result:** 43-48% more context (no auto-loading), universal server library

### The Registry Architecture

**Global Server Registry (`~/.multiagent/config/mcp-servers-registry.json`):**
- Master list of ALL available MCP servers
- Standard servers (npm packages)
- Custom servers (your droplets, local development)
- Supports both local (stdio) and remote (HTTP) variants
- **Update Protection**: User registry never overwritten by framework upgrades
- **Auto-Migration**: Automatically migrates from old location (`~/.claude/`) on first init

**Per-Project Config (`.mcp.json`):**
- Empty by default: `{"mcpServers": {}}`
- Populated via `/mcp:add` from global registry
- Only loads what THIS project needs

### Registry Structure

```json
{
  "servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"},
      "description": "GitHub API integration",
      "category": "standard"
    },
    "signalhire": {
      "variants": {
        "local": {
          "type": "stdio",
          "command": "node",
          "args": ["./mcp-servers/signalhire/index.js"],
          "description": "SignalHire (local development)"
        },
        "remote": {
          "type": "http",
          "url": "http://${DROPLET_IP}:8080/mcp",
          "headers": {"Authorization": "Bearer ${MCP_AUTH_TOKEN}"},
          "description": "SignalHire (remote droplet)"
        }
      },
      "category": "custom"
    }
  }
}
```

### Slash Commands for Registry-Based MCP Management

```bash
# Browse available servers in registry
/mcp:list

# Check current project's active servers
/mcp:status

# Add server from registry to project
/mcp:add github                    # Standard server (auto-adds)
/mcp:add signalhire                # Prompts: local or remote?
/mcp:add signalhire remote         # Explicit variant

# Remove server from current project
/mcp:remove signalhire

# Clear all servers from project
/mcp:clear

# API key tracking and organization
/mcp:inventory   # Generate/update ~/.api-keys-inventory.md
```

### Available Servers in Registry

**Standard Servers (npm packages):**
- **github** - GitHub API integration, PRs, issues
- **postman** - API testing and collections
- **memory** - Persistent conversation memory (local)
- **playwright** - Browser automation, E2E testing
- **filesystem** - File/directory operations
- **supabase** - Supabase backend operations

**Custom Servers (local + remote variants):**
- **signalhire** - Talent search (local dev or droplet)
- **airtable** - Database operations (local dev or droplet)
- **twilio** - SMS/voice communications (local dev or droplet)
- **calendly** - Appointment scheduling (local dev or droplet)

### How It Works

#### 1. Global Setup (ONE TIME)
```bash
# API keys in ~/.bashrc or ~/.zshrc
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxxx"
export POSTMAN_API_KEY="PMAK_xxxx"
export DROPLET_IP="142.93.123.456"
export MCP_AUTH_TOKEN="your_token"

# Registry created automatically on first 'multiagent init'
# Located at: ~/.multiagent/config/mcp-servers-registry.json
# Old location (~/.claude/) automatically migrated with backup
```

**Why global API keys?**
- ✅ One place to manage keys across ALL projects
- ✅ Never commit secrets to git
- ✅ Works everywhere automatically

#### 2. Per-Project Usage
```bash
# In any project directory:
/mcp:list                  # Browse available servers
/mcp:add signalhire remote # Add remote droplet server
/mcp:add github            # Add standard server

# .mcp.json is populated:
{
  "mcpServers": {
    "signalhire": {
      "type": "http",
      "url": "http://142.93.123.456:8080/mcp",
      "headers": {"Authorization": "Bearer your_token"}
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxx"}
    }
  }
}
```

#### 3. Local vs Remote Servers

**Local (stdio):**
- Server runs on your machine
- Faster (no network latency)
- Works offline
- Good for development/debugging

**Remote (HTTP):**
- Server runs on droplet
- Accessible from anywhere
- Shared across team
- Production-ready

**Same server, both modes:**
```bash
/mcp:add signalhire local   # Use local for debugging
/mcp:add signalhire remote  # Use remote for production
```

### Recommended Combinations by Project Type

```bash
# Web Development
/mcp:add github memory playwright

# API Development
/mcp:add github memory postman

# Full Stack
/mcp:add github memory playwright postman

# Automation/Scripts
/mcp:add filesystem playwright

# Basic Development
/mcp:add github memory
```

### Important: Works Beyond Just Droplets

**This strategy applies to ANY project type:**
- ✅ Web apps (React, Vue, Angular)
- ✅ Backend APIs (Node.js, Python, Go)
- ✅ CLI tools and automation scripts
- ✅ Documentation projects
- ✅ DevOps configurations
- ✅ ANY codebase where you use Claude Code

**Not limited to droplets/deployment** - use this pattern everywhere to save context.

### API Key Organization & Tracking

Use `/mcp:inventory` to maintain a global tracking file:

```bash
# In any multiagent project:
/mcp:inventory

# Creates/updates: ~/.api-keys-inventory.md
```

**What it tracks:**
- Which projects use which API keys
- Purpose: MCP infrastructure vs application code
- Billing impact per project
- Key rotation schedule
- Usage monitoring dashboards

**Example inventory entry:**
```markdown
### StaffHive
**Location:** /home/user/Projects/StaffHive
**MCP Keys:** GITHUB_PERSONAL_ACCESS_TOKEN, POSTMAN_API_KEY
**App Keys:** OPENAI_API_KEY_APP (AI features), STRIPE_API_KEY (payments)
**Billing:** OpenAI $50/month, Stripe per-transaction
```

**Why this matters:**
- 🎯 **Clear separation**: MCP infrastructure vs app business logic
- 💰 **Billing tracking**: Know which project costs what
- 🔐 **Security**: Audit which keys are used where
- 📊 **Usage monitoring**: Track API consumption per project

### Benefits

1. **Massive token savings** - 43-48% more context available
2. **Faster responses** - Less data to process per conversation
3. **Project-specific** - Only load what you need
4. **Easy management** - Simple slash commands, no manual JSON editing
5. **Zero globals** - Each project isolated from others
6. **Key tracking** - Global inventory for billing & security

### Implementation Files

Slash commands are stored in `.claude/commands/mcp/`:
- `add.md` - Add server from library
- `remove.md` - Remove server
- `status.md` - Show current configuration
- `clear.md` - Remove all servers
- `local.md` - Enable local dev preset
- `remote.md` - Enable remote droplet preset
- `inventory.md` - Generate/update API keys tracking file

Template files:
- `.env.example` - API key organization guide (per-project)
- `.api-keys-inventory.example.md` - Global tracking template

**Current Approach:** Commands deployed per-project via `multiagent init`
**Future Consideration:** May move to global `~/.claude/commands/mcp/` in home directory since this strategy is so universally useful across ALL projects, not just multiagent projects.

---

## 🔧 Installation

### Quick Start (Recommended: pipx)

```bash
# Install pipx if you haven't already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install MultiAgent Core
pipx install multiagent-core

# Verify installation
multiagent --version
```

### Alternative: pip Installation

```bash
# Global installation (may require sudo)
pip install multiagent-core

# Or user installation
pip install --user multiagent-core
```

## 📐 Project Type System

**The framework scales from landing pages (10 min) to AI SaaS (days)**

### Choose Your Starting Point

```bash
# Simple landing page
/core:project-setup 001 --type=landing-page
# → Frontend + Vercel (10 min)

# Marketing website
/core:project-setup 001 --type=website
# → Multi-page + CMS (30 min)

# Full-stack web app
/core:project-setup 001 --type=web-app
# → Frontend + Backend + DB (2-4 hrs)

# AI application
/core:project-setup 001 --type=ai-app
# → Full stack + AI infrastructure (6-8 hrs)
```

### Grow Incrementally

```bash
# Start simple
/core:project-setup 001 --type=landing-page

# Later: Add backend
/core:upgrade-to web-app

# Later: Add AI
/core:upgrade-to ai-app
```

**Same path, different depth** - Every project gets security, testing, docs. Simple projects get less, complex projects get more.

---

## 🚀 Quick Start Guide

### Full Workflow Example (Web App)

```bash
# PHASE 1-2: SETUP (Spec Creation)
specify init --here --ai claude
/specify                              # Create spec
/plan                                 # Create plan
/tasks                                # Generate tasks

# PHASE 3: PROJECT SETUP (Type-Aware)
multiagent init                       # Deploy framework
/core:project-setup 001 --type=web-app # Configure for web app
/docs:init                            # Initialize docs
/deployment:deploy-prepare 001        # Generate deployment
/testing:test-generate 001            # Generate tests
/security:setup                       # Security infrastructure
/iterate:tasks 001                    # Layer tasks

# PHASE 4: DEVELOPMENT
# Agents work in parallel on assigned tasks
/testing:test --quick                 # Run tests during dev
/docs:auto-update                     # Process queued doc updates (from commits)
/supervisor:mid 001                   # Check progress

# PHASE 4.5: PR REVIEW
gh pr create                          # Create PR
/github:pr-review 123                 # Analyze feedback
/supervisor:end 001                   # Pre-merge validation

# PHASE 5: DEPLOYMENT
/testing:test-prod                    # Validate production tests
/deployment:prod-ready                # Comprehensive checks
/deployment:deploy-run up             # Test locally
/deployment:deploy preview            # Deploy to preview
/deployment:deploy production         # Deploy to prod

# PHASE 6: END (Cleanup)
git worktree remove ../project-*      # Clean up worktrees
```

## 🎓 Key Concepts

### 1. Slash Commands Spawn Subagents
Slash commands don't run scripts directly - they spawn specialized subagents:
```
/docs:init → docs-init subagent → reads templates → writes docs
```

### 2. Subagents Handle Complexity
Subagents have specialized knowledge and use subsystem resources:
- Read templates from `.multiagent/{subsystem}/templates/`
- May call utility scripts from `.multiagent/{subsystem}/scripts/`
- Write output to project locations (`docs/`, `tests/`, etc.)

### 3. Layered Task Organization
Tasks are organized by dependency layers, not sequence:
- **Foundation** - Database models, core infrastructure
- **Implementation** - Business logic, adapters
- **Testing** - Test suites, validation

### 4. Parallel Agent Workflows
Multiple agents work simultaneously in isolated worktrees:
- No merge conflicts
- Independent progress
- Coordinated integration via PRs

### 5. Phase-Based Development
Commands are organized by development phase:
- **Setup** - Infrastructure deployment
- **Development** - Feature implementation
- **PR Review** - Quality gates
- **Deployment** - Production launch
- **End** - Cleanup and maintenance

## 🔍 Common Workflows

### Workflow: Adding a New Feature

```bash
# 1. Create spec (Spec-Kit)
/specify
/plan
/tasks

# 2. Setup infrastructure (MultiAgent)
/iterate:tasks 001
/testing:test-generate 001
/deployment:deploy-prepare 001

# 3. Implement (Agents)
# Agents work in parallel on layered tasks

# 4. Review & merge (Judge)
/github:pr-review 123
gh pr merge 123

# 5. Deploy (Production)
/deployment:prod-ready
/deployment:deploy production
```

### Workflow: Updating Documentation

```bash
# Initial setup
/docs:init

# During development (automatic)
# After commits, hooks create queue files
/docs:auto-update       # Process all queued doc updates

# OR manual update
/docs:update --check-patterns

# Before release
/docs:validate --strict # Ensure completeness
```

### Workflow: Testing Strategy

```bash
# Generate test structure
/testing:test-generate 001

# During development
/testing:test --quick         # Fast feedback
/testing:test --backend       # API tests
/testing:test --frontend      # UI tests

# Before production
/testing:test-prod --verbose  # Validate prod readiness
```

### Workflow: Environment Configuration

```bash
# Generate .env file from project analysis
/security:create-env create

# Spawns: env-generator subagent
# Actions:
#   - Runs ~/.multiagent/security/scripts/analyze-project-keys.sh
#   - Analyzes specs, docs, configs, MCP servers
#   - Uses ~/.multiagent/security/templates/env/.env.template
#   - Categorizes by service type (AI, Communication, Data, etc.)
#   - Adds source annotations and dashboard URLs
# Creates: .env with all required keys

# After adding new dependencies
/security:create-env update    # Re-analyze and add new keys

# Related commands
/security:bashrc view          # View global dev MCP keys
/security:github-secrets       # Sync .env to GitHub (after testing)
```

## 📖 Additional Resources

- **Agent Workflows**: `.multiagent/agents/docs/`
- **Subsystem Documentation**: Each subsystem has `README.md`
- **Archived Scripts**: `.archive/` (root level)

## 🐛 Troubleshooting

### Command Not Found

```bash
# For pipx installation
python3 -m pipx ensurepath
source ~/.bashrc  # or ~/.zshrc

# For pip installation
export PATH="$PATH:$HOME/.local/bin"
```

### Slash Command Errors

Check that spec exists:
```bash
ls -la specs/001-*/
```

Check that subsystem is deployed:
```bash
ls -la .multiagent/deployment/
ls -la .multiagent/testing/
```

### Subagent Not Activating

Verify agent configuration:
```bash
ls -la .claude/agents/
cat .claude/agents/backend-tester.md
```

## 📞 Getting Help

- **Documentation**: https://github.com/vanman2024/multiagent-core
- **Issues**: https://github.com/vanman2024/multiagent-core/issues

## 🤝 Contributing

See [DEVELOPMENT.md](../DEVELOPMENT.md) for contributor guide.

## 📄 License

MIT License - see [LICENSE](https://github.com/vanman2024/multiagent-core/blob/main/LICENSE).

---

🤖 **Powered by MultiAgent Framework**

Version: `multiagent --version`
