# Security System - Preventing $2,300+ API Key Disasters

## Purpose

Prevents accidental secret exposure through 4-layer security: .gitignore protection, git hooks, GitHub Actions scanning, and documentation. Triggered automatically during project setup.

## What It Does

1. **Deploys .gitignore** - Blocks dangerous files (.env, *.key, GEMINI.md, etc.)
2. **Creates .env.example** - Safe-to-commit template with placeholder values
3. **Installs git hooks** - Pre-push secret detection from core
4. **Generates GitHub workflows** - Security scanning on every push (Bandit, Semgrep, Safety)
5. **Scans existing code** - Detects any already-committed secrets
6. **Validates compliance** - Ensures all security measures active
7. **Creates documentation** - Security guides in `security/` directory
8. **Reports status** - Detailed setup report back to @claude

## Agents Used

- **@claude/security-auth-compliance** - Executes complete 8-step security deployment
- **@claude (coordinator)** - Analyzes project, prepares context, invokes security agent

## How It's Triggered

**Automatic via `/core:project-setup <spec-dir>`:**
1. @claude analyzes your project (tech stack, required secrets, current posture)
2. @claude invokes security-auth-compliance subagent with context
3. Subagent executes 8-step deployment
4. @claude validates and reports completion

**Result**: 4-layer security protection with zero manual configuration

## Commands

### `/security:setup` - Complete Security Infrastructure
Security is **automatically triggered** by `/core:project-setup`. No manual security commands needed - it's all orchestrated automatically.

**What it does:**
- Deploys .gitignore protection
- Installs git hooks (pre-push secret scanning)
- Generates GitHub workflows (security-scanning.yml)
- Scans existing code for secrets
- Creates security documentation

**Manual trigger (if needed):**
- Security setup runs automatically via `/core:project-setup`
- Git hooks: Installed at `.git/hooks/pre-push` (blocks secrets)
- GitHub workflows: Generated at `.github/workflows/security-scanning.yml`

### `/security:create-env create` - Environment File Generation
**NEW:** Generates comprehensive .env files by analyzing your entire project structure.

**What it does:**
1. Runs `~/.multiagent/security/scripts/analyze-project-keys.sh` (mechanical file discovery)
2. Invokes `env-generator` agent to analyze ALL discovered files
3. Generates `.env` organized by service type (AI, Communication, Data, Business, Infrastructure)
4. Adds source annotations showing where each key was found
5. Includes dashboard URLs for obtaining keys
6. Updates .gitignore

**Service categories:**
- AI/LLM (anthropic, openai, cohere, etc.)
- Memory Systems (mem0, pinecone, weaviate, etc.)
- Communication (sendgrid, twilio, etc.)
- Data & Storage (airtable, postgresql, redis, etc.)
- Business Services (stripe, signalhire, etc.)
- Infrastructure (vercel, aws, digitalocean, etc.)
- MCP Servers (production only - dev uses ~/.bashrc)

**Usage:**
```bash
/security:create-env create   # Generate initial .env
/security:create-env update   # Add new keys after dependencies change
```

**Agent:** `env-generator` (analyzes specs, docs, code, configs intelligently)
**Script:** `analyze-project-keys.sh` (mechanical file listing only)
**Template:** `~/.multiagent/security/templates/env/.env.template`

---

## 🤖 Agent Workflow Details

### @claude - Strategic Coordinator

**Your Responsibilities**:
1. **Project Analysis**
   - Detect project tech stack (Node.js, Python, etc.)
   - Identify what secrets project needs (API keys, tokens, credentials)
   - Assess existing security posture
   - Determine compliance requirements

2. **Context Preparation**
   - Read project structure with Glob tool
   - Analyze package.json / requirements.txt for dependencies
   - Check if .env or secrets already exist (Read tool)
   - Prepare detailed context for security agent

3. **Subagent Invocation**
   ```
   Task(
       subagent_type="security-auth-compliance",
       description="Setup comprehensive project security",
       prompt="""
       Project: {project_name}
       Tech Stack: {detected_stack}
       Required Secrets: {api_keys_needed}
       Existing Security: {current_state}

       Execute security setup:
       1. Deploy .gitignore from templates/
       2. Create .env.example with project-specific variables
       3. Install git hooks to .git/hooks/
       4. Generate GitHub workflows to .github/workflows/
       5. Scan codebase for existing secrets
       6. Validate all security measures active

       Report: Security status and any issues found
       """
   )
   ```

4. **Post-Work Validation**
   - Verify .gitignore exists in project root
   - Confirm .env.example created
   - Check git hooks installed and executable
   - Validate GitHub workflows present
   - Review agent's security report

### security-auth-compliance Subagent - Security Executor

**Built-in Tools** (no scripts needed for most operations):
- **Read** - Read templates from `security/templates/`
- **Write** - Create files in project root and security/ output
- **Edit** - Merge new patterns into existing files
- **MultiEdit** - Bulk updates across multiple files
- **Bash** - Make hooks executable, run scripts, git commands
- **Grep** - Search codebase for secret patterns
- **Glob** - Find all files to scan for secrets

**When Agent Uses Scripts** (minimal - for bulk operations):
- `scripts/scan-secrets.sh` - Pattern matcher for 25+ secret types
- `scripts/validate-compliance.sh` - Checklist validation
- `scripts/generate-github-workflows.sh` - Copy workflow templates

**Complete Agent Workflow** (ALL Steps):

```markdown
### Step 1: Deploy .gitignore Protection
**Purpose**: Block dangerous files from git commits
**Actions**:
- Read: .multiagent/security/templates/.gitignore
- Check: Does project root .gitignore exist?
  - YES: Edit to merge security patterns
  - NO: Write new .gitignore to project root
- Verify: Critical patterns present (.env, *.key, *.pem, GEMINI.md, etc.)

### Step 2: Create .env.example Template
**Purpose**: Safe-to-commit environment variable documentation
**Actions**:
- Read: .multiagent/security/templates/env.template
- Analyze: Project dependencies for required secrets (package.json, requirements.txt)
- Customize: Add project-specific variables
- Write: .env.example to project root with placeholders
- Note: User copies to .env and fills real values

### Step 3: Install Git Hooks
**Purpose**: Pre-push secret scanning, post-commit auto-sync
**Actions**:
- Verify: .git directory exists
- Read: .multiagent/security/hooks/pre-push (security hook)
- Read: .multiagent/agents/hooks/post-commit (agent workflow hook)
- Write: Both hooks to .git/hooks/
- Bash: chmod +x .git/hooks/pre-push .git/hooks/post-commit
- Test: Verify hooks are executable

### Step 4: Generate GitHub Workflows
**Purpose**: CI/CD security scanning on every push
**Actions**:
- Check: .github/workflows/ directory exists (create if needed)
- Bash: scripts/generate-github-workflows.sh
  - Copies security-scan.yml.template → .github/workflows/security-scan.yml
  - Copies security-scanning.yml.template → .github/workflows/security-scanning.yml
  - Replaces {{PROJECT_NAME}}, {{TECH_STACK}} placeholders
- Verify: Both workflow files created

### Step 5: Scan for Existing Secrets
**Purpose**: Detect any already-committed secrets
**Actions**:
- Bash: scripts/scan-secrets.sh
- If secrets found:
  - Report exact file:line locations
  - Mark as CRITICAL issue
  - Block further setup until resolved
  - Provide remediation steps
- If clean: Proceed to validation

### Step 6: Validate Security Compliance
**Purpose**: Verify all security measures active
**Actions**:
- Bash: scripts/validate-compliance.sh
- Check:
  - ✅ .gitignore exists with security patterns
  - ✅ Git hooks installed and executable
  - ✅ .env not committed to git
  - ✅ .env.example present
  - ✅ GitHub workflows generated
- Report: Compliance status

### Step 7: Generate Security Output Directory
**Purpose**: Create documentation, reports, and configuration
**Actions**:
- Create: security/reports/
- Write: security/reports/security-setup-report.md (setup summary)
- Write: security/reports/compliance-check.md (compliance status)
- Write: security/reports/secret-scan-results.md (scan findings)
- Create: security/docs/
- Write: security/docs/SECRET_MANAGEMENT.md (secret handling guide)
- Write: security/docs/SECURITY_CHECKLIST.md (pre-deployment checklist)
- Write: security/docs/INCIDENT_RESPONSE.md (emergency procedures)
- Create: security/configs/
- Write: security/configs/security-config.json (security configuration)

### Step 8: Security Setup Report
**Purpose**: Final status report to @claude
**Actions**:
- TodoWrite: Mark all steps completed
- Return report:
  - ✅ Files created (.gitignore, .env.example, hooks, workflows)
  - ✅ Security patterns deployed
  - ✅ Secrets scanned (clean/issues found)
  - ✅ Compliance validated
  - ✅ Output generated (security/ directory)
  - ⚠️ Any issues requiring user action
  - 📋 Next steps (create .env, test hooks, push to GitHub)
```

---

## 📁 Directory Structure

```
.multiagent/security/
├── README.md                           # This file
├── WORKFLOW.md                         # Detailed security workflow
├── scripts/
│   ├── scan-secrets.sh                # Tool: Secret pattern matcher
│   ├── validate-compliance.sh         # Tool: Security checklist
│   └── generate-github-workflows.sh   # Tool: Workflow template copier
├── templates/
│   ├── .gitignore                     # Comprehensive gitignore (7,985 bytes)
│   ├── env.template                   # Environment variables template
│   ├── .env.example                   # Safe-to-commit example
│   └── github-workflows/
│       ├── security-scan.yml.template         # Security scanning workflow
│       └── security-scanning.yml.template     # Comprehensive checks (Bandit, Semgrep, Safety)
└── docs/
    ├── AGENT_INSTRUCTIONS.md          # Security agent detailed guide
    ├── SECRET_MANAGEMENT.md           # How to handle secrets
    └── COMPLIANCE_CHECKLIST.md        # Security requirements

Git Hooks (organized by concern):
Security hooks:
.multiagent/security/hooks/
└── pre-push                           # Secret scanning before push

Agent workflow hooks:
.multiagent/agents/hooks/
└── post-commit                        # Agent workflow guidance
```

---

## 🛡️ Security Layers

### Layer 1: .gitignore Protection
**File**: `templates/.gitignore` (7,985 bytes)
**Blocks**:
```gitignore
# SECURITY & SECRETS
.env
.env.*
!.env.template
!.env.example
*.key
*.pem
*.p12
*.pfx
secrets/
GEMINI.md          # The $2,300 disaster file!
api_keys.*
*_key
*_secret
*_token
```

**Deployed To**: Project root `.gitignore`
**Agent Action**: Read template → Write/Edit to project root

---

### Layer 2: Pre-Push Hook (from core)
**File**: `../core/scripts/hooks/pre-push`
**Purpose**: Block pushes containing secrets
**Patterns Detected**: 25+ including:
- Google API keys: `AIzaSy[0-9A-Za-z_-]{33}`
- OpenAI keys: `sk-[0-9A-Za-z]{48}`
- GitHub tokens: `ghp_[0-9A-Za-z]{36}`
- AWS credentials: `AKIA[0-9A-Z]{16}`
- Private keys: `-----BEGIN RSA PRIVATE KEY-----`
- GEMINI.md files (the $2,300 disaster!)

**Deployed To**: `.git/hooks/pre-push` (executable)
**Agent Action**: Read from core → Write to .git/hooks/ → Bash: chmod +x

---

### Layer 3: Post-Commit Hook (from core)
**File**: `../core/scripts/hooks/post-commit`
**Purpose**: Auto-sync templates on meaningful commits
**Features**:
- Triggers template sync to all registered projects
- Ensures security updates propagate automatically

**Deployed To**: `.git/hooks/post-commit` (executable)
**Agent Action**: Read from core → Write to .git/hooks/ → Bash: chmod +x

---

### Layer 4: GitHub Actions Security Scanning
**Files**:
- `templates/github-workflows/security-scan.yml.template`
- `templates/github-workflows/security-scanning.yml.template`

**Purpose**: CI/CD security validation on every push
**Capabilities**:
- Secret pattern detection (same 25+ patterns as hooks)
- Python dependency vulnerability scanning (Safety)
- Static security analysis (Bandit, Semgrep)
- Weekly automated scans
- Pull request security validation

**Deployed To**: `.github/workflows/security-scan.yml` (project-specific)
**Agent Action**: Bash: scripts/generate-github-workflows.sh

**Key Point**: Templates stay in `security/templates/github-workflows/` - they are NOT synced from repo `.github/`. Each project gets customized workflows generated by the security agent.

---

## 🔧 Minimal Script Set (Tools Only)

### 1. scan-secrets.sh
**Purpose**: Pattern-based secret detection utility
**Usage**: `scripts/scan-secrets.sh [directory]`
**Returns**: List of files with secrets (file:line format)
**Called By**: Security agent during validation

### 2. validate-compliance.sh
**Purpose**: Security checklist validator
**Checks**:
- .gitignore exists with security patterns
- Git hooks installed and executable
- .env not committed
- GitHub workflows present
**Called By**: Security agent post-setup

### 3. generate-github-workflows.sh
**Purpose**: Copy and customize workflow templates
**Actions**:
- Copy security-scan.yml.template → .github/workflows/
- Copy security-scanning.yml.template → .github/workflows/
- Replace {{PROJECT_NAME}} with actual project name
- Replace {{TECH_STACK}} with detected stack
**Called By**: Security agent during setup

---

## 📋 Integration with /project-setup

### Command Flow

```
User: /project-setup specs/001-my-project

@claude:
1. Read specs/001-my-project/ to understand project
2. Detect tech stack (Node.js, Python, etc.)
3. Identify required secrets (API keys from package.json, requirements.txt)
4. Check existing security measures

@claude invokes security-auth-compliance:
  - Context: Project analysis results
  - Task: Execute comprehensive security setup
  - Expected: All 6 security steps completed

security-auth-compliance:
1. Deploy .gitignore (Read + Write/Edit)
2. Create .env.example (Read + Write)
3. Install git hooks (Read + Write + Bash)
4. Generate GitHub workflows (Bash: script)
5. Scan for secrets (Bash: script)
6. Validate compliance (Bash: script)
7. Report results (TodoWrite + return)

@claude:
- Validate security agent's work
- Verify all files created
- Report success/issues to user
```

---

## 🚀 What Gets Created in Projects

### Project Root Output
**Location**: `project-root/`
**Purpose**: All security infrastructure and documentation

```
project-root/
├── .gitignore                        # Already exists, moves from template to root
├── .env.example                      # Created/filled from config
├── .github/workflows/                # Workflows automatically moved here
│   ├── security-scan.yml
│   └── security-scanning.yml
├── .git/hooks/                       # Already initialized by core
│   ├── pre-push                      # Already exists from core
│   └── post-commit                   # Already exists from core
└── security/                         # NEW - Security system output
    ├── reports/
    │   ├── security-setup-report.md      # Initial setup results
    │   ├── compliance-check.md           # Compliance validation
    │   └── secret-scan-results.md        # Scan findings (if any)
    ├── docs/
    │   ├── SECRET_MANAGEMENT.md          # How to manage secrets
    │   ├── SECURITY_CHECKLIST.md         # Pre-deployment checklist
    │   └── INCIDENT_RESPONSE.md          # Emergency procedures
    └── configs/
        └── security-config.json          # Security configuration
```

### User Creates (NOT committed)
```
project-root/
└── .env                 # Real secrets (blocked by .gitignore)
```

---

## ✅ Success Criteria

### Automated Checks
- ✅ .gitignore exists with all security patterns
- ✅ .env.example created (safe to commit)
- ✅ .env blocked by .gitignore (if created)
- ✅ Git hooks installed at .git/hooks/
- ✅ Hooks are executable (chmod +x)
- ✅ GitHub workflows generated in .github/workflows/
- ✅ No secrets detected in codebase

### Manual Validation
- ✅ Security agent completes all steps successfully
- ✅ /project-setup integrates security seamlessly
- ✅ New projects have full security from day one
- ✅ Existing projects can opt-in without conflicts

---

## 📚 Related Documentation

- **Security Overview**: `docs/core/SECURITY.md` ($2,300 incident context)
- **Agent Instructions**: `security/docs/AGENT_INSTRUCTIONS.md` (detailed setup guide)
- **Secret Management**: `security/docs/SECRET_MANAGEMENT.md` (handling secrets)
- **Compliance Checklist**: `security/docs/COMPLIANCE_CHECKLIST.md` (requirements)
- **System Workflow Pattern**: `.multiagent/core/docs/architecture/SYSTEM_WORKFLOW_PATTERN.md`
- **Project Setup**: `.claude/commands/core/project-setup.md` (integration point)

---

## 🔒 Security Benefits

### Prevents Financial Disasters
- **$2,300+ API overcharge protection** (Google Gemini incident)
- Blocks unauthorized access to paid services
- Prevents account compromise

### Protects Sensitive Data
- Customer data access prevention
- Internal system credential protection
- Development environment isolation

### Compliance & Governance
- Industry security best practices
- Audit trail of blocked attempts
- Consistent protection across all projects

---

## ⚠️ Critical Architecture Notes

### 1. Templates vs Live Files
- **Templates**: `.multiagent/security/templates/` (source, never executed)
- **Live Files**: Project root (deployed by agent, actively protect)

### 2. GitHub Workflows NOT Synced
- **Repo .github/**: Only repo-specific workflows
- **Project .github/**: Generated per-project by security agent
- **Why**: Each project needs customized workflows (project name, tech stack)

### 3. Hooks Organized by Concern
- **Security**: `.multiagent/security/hooks/pre-push` (secret scanning)
- **Agents**: `.multiagent/agents/hooks/post-commit` (workflow guidance)
- **Why**: Each subsystem owns its hooks based on primary purpose

### 4. Scripts Are Tools
- NOT orchestrators - agents do the work
- ONLY used for complex validation/pattern matching
- Agents call scripts, scripts don't call agents

---

**Remember**: This system exists because of a $2,300 mistake. Every security layer is designed to ensure that never happens again to any project using this framework.