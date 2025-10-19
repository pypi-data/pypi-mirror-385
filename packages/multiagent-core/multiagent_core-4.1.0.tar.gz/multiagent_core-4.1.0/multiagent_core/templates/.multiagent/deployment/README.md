# Deployment Preparation System

## Purpose

Generates platform-specific deployment configurations (Docker, Vercel, K8s, Railway, etc.) based on your spec requirements. Handles both config generation and actual deployment to cloud platforms.

## What It Does

1. **Analyzes spec** - Reads tasks.md to determine deployment target
2. **Generates configs** - Creates Dockerfile, docker-compose.yml, vercel.json, etc.
3. **Validates setup** - Ensures all required environment variables and configs exist
4. **Deploys to cloud** - Executes deployment to Vercel, Railway, AWS, etc.

## Agents Used

- **@claude/deployment-prep** - Analyzes spec and generates platform configs
- **@claude/deployment-validator** - Validates deployment readiness
- **@claude/deployment-runner** - Executes local deployments (Docker)

## Commands

- **`/deployment:deploy-prepare <spec-dir>`** - Generate deployment configs (Docker, K8s, etc.)
- **`/deployment:deploy-validate`** - Validate deployment configuration readiness
- **`/deployment:deploy-run [up|down|restart|logs]`** - Execute local deployment with Docker
- **`/deployment:deploy [production|preview]`** - Deploy to cloud platform (Vercel, Railway, AWS)
- **`/deployment:prod-ready [--fix] [--verbose]`** - Comprehensive production readiness scan

## Complete Workflow

### First-Time Deployment Setup
```bash
# Step 1: Ensure all tests passing
/testing:test --quick
# Prerequisite: Tests must be green before deployment
# Expected output: All tests passing, 80%+ coverage

# Step 2: Generate deployment configurations
/deployment:deploy-prepare {spec}
# What this does: Analyzes spec, detects platform, generates configs
# Expected output: deployment/ directory with platform configs
# Time: 1-2 minutes
# Platforms detected: Vercel, AWS, Railway, Docker (local)

# Step 3: Add API keys and environment variables
/security:create-env create
# What this does: Generates .env files based on project analysis
# Expected output: .env.development, .env.production
# Important: Fill in actual API keys after generation

# Step 4: Validate deployment configuration
/deployment:deploy-validate
# What this does: Checks configs, env vars, Docker setup
# Expected output: READY (or issues to fix)
# Time: 30 seconds
```

**Verification**: Configs generated, .env files populated, validation passes

### Local Deployment Testing
```bash
# Step 1: Start local deployment
/deployment:deploy-run up
# What this does: Starts Docker containers locally
# Expected output: Services running, health checks passing
# Time: 1-3 minutes
# Access: http://localhost:3000 (or configured port)

# Step 2: Check service logs
/deployment:deploy-run logs
# Monitor for errors or warnings

# Step 3: Run health checks
curl http://localhost:3000/health
# Expected: {"status": "healthy"}

# Step 4: Stop deployment when done testing
/deployment:deploy-run down
```

**Verification**: Services start successfully, health checks pass, no errors in logs

### Production Readiness Validation
```bash
# Step 1: Run comprehensive production scan
/deployment:prod-ready
# What this does: Checks 50+ production readiness criteria
# Expected output: Detailed readiness report
# Time: 2-3 minutes
# Checks: Security, performance, monitoring, error handling

# Step 2: If issues found, run with --fix
/deployment:prod-ready --fix
# Automatically fixes common issues

# Step 3: Re-validate after fixes
/deployment:prod-ready
# Should show: All checks passing

# Step 4: Review readiness report
cat .multiagent/reports/prod-readiness-{date}.md
```

**Validation**: All production checks green, no critical issues

### Cloud Deployment (Production)
```bash
# Step 1: Verify platform detected correctly
cat deployment/platform.txt
# Shows: vercel, aws, railway, render, fly, heroku, or docker

# Step 2: Sync API keys to GitHub (for CI/CD)
/security:github-secrets
# What this does: Syncs .env keys to GitHub repository secrets
# Expected output: X keys synced to GitHub
# Time: 30 seconds

# Step 3: Deploy to production
/deployment:deploy production
# What this does: Deploys to detected platform
# Expected output: Deployment URL, health check status
# Time: 3-10 minutes (depends on platform)

# Step 4: Verify deployment
curl https://your-app.vercel.app/health
# Expected: {"status": "healthy"}
```

**Verification**: Deployment succeeds, app accessible, health checks pass

### Preview/Staging Deployment
```bash
# Deploy to preview environment first
/deployment:deploy preview
# Test in preview before production

# If preview looks good, deploy to production
/deployment:deploy production
```

**Use Case**: Test in staging before pushing to production

### Typical Deployment Session
```
Pre-Deployment:
  /testing:test --quick             → Verify tests (1 min)
  /deployment:prod-ready            → Check readiness (3 min)
  Fix any issues found
  /deployment:prod-ready            → Re-validate (3 min)

Local Testing:
  /deployment:deploy-prepare 001    → Generate configs (2 min)
  /security:create-env create       → Create .env files (1 min)
  Fill in actual API keys
  /deployment:deploy-validate       → Validate setup (30 sec)
  /deployment:deploy-run up         → Start locally (2 min)
  Test application manually
  /deployment:deploy-run down       → Stop local (30 sec)

Production Deployment:
  /security:github-secrets          → Sync keys (30 sec)
  /deployment:deploy production     → Deploy (5-10 min)
  Verify deployment URL
  Monitor logs for issues
```

### Integration with Other Commands
```bash
# Complete development to deployment workflow:
/iterate:tasks 001                 # Layer tasks
/supervisor:start 001              # Setup development
# Development...
/supervisor:end 001                # Validate completion
/testing:test --quick              # Run tests
/deployment:prod-ready             # Check readiness
/deployment:deploy-prepare 001     # Generate configs
/deployment:deploy-validate        # Validate
/deployment:deploy production      # Deploy
```

## Architecture

```
.claude/
├── agents/deployment/        # Deployment subagents
│   ├── deployment-prep.md   # Main prep agent
│   └── deployment-analyzer.md # Stack analyzer
└── commands/deployment/     # Commands
    └── deploy-prepare.md    # Main command

.multiagent/deployment/
├── scripts/                 # Generation scripts
│   └── generate-deployment.sh
├── templates/              # Deployment templates
│   ├── docker/            # Dockerfile templates
│   ├── compose/           # docker-compose templates
│   ├── k8s/              # Kubernetes manifests
│   ├── env/              # Environment configs
│   ├── nginx/            # Nginx configs
│   └── scripts/          # Deployment scripts
├── memory/                # Session memory
└── logs/                  # Generation logs
```

## How It Works

1. **Command Invocation**: User runs deployment preparation command
2. **Subagent Analysis**: deployment-prep agent analyzes tasks and project
3. **Stack Detection**: Automatically detects tech stack (Python, Node, etc.)
4. **Template Selection**: Chooses appropriate templates based on analysis
5. **Generation**: Creates deployment artifacts in `/deployment` directory

## Generated Output Structure

```
deployment/
├── docker/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── configs/
│   ├── .env.example
│   ├── .env.development
│   └── nginx.conf
└── scripts/
    ├── deploy.sh
    └── health-check.sh
```

## Intelligent Detection

The system automatically detects:
- **Language**: Python, JavaScript, Java, Go, etc.
- **Framework**: FastAPI, Express, React, Django, etc.
- **Services**: PostgreSQL, Redis, MongoDB, etc.
- **Architecture**: Monolith, microservices, serverless

## Usage

```bash
# Generate deployment configurations
multiagent deploy-prepare

# Generate for specific spec
multiagent deploy-prepare specs/001-build-a-complete
```

## Templates

Templates use placeholders that get replaced based on project analysis:
- `{{APP_NAME}}` - Application name from project
- `{{PORT}}` - Detected or default port
- `{{STACK}}` - Technology stack
- `{{SERVICES}}` - Required services

## Complements GitHub Actions

This system prepares artifacts that GitHub Actions uses but doesn't duplicate CI/CD logic:
- **We Generate**: Dockerfiles, configs, manifests
- **GitHub Does**: Build, test, deploy, validate

## Post-Generation Steps

After generation, you need to:

### 1. Update `.env` files with real values:
```bash
# Edit deployment/configs/.env.development
DATABASE_URL=      # Add your actual database URL
JWT_SECRET=        # Generate a secure secret
API_KEYS=          # Add actual API keys
WEBHOOK_SECRETS=   # Add webhook secrets from integrations
```

### 2. Adjust ports if needed:
- Check `docker-compose.yml` for port conflicts
- Update exposed ports based on your setup

### 3. Add secrets for production:
```bash
# Never commit these!
cp deployment/configs/.env.production .env.production.local
# Edit .env.production.local with real production values
```

### 4. Customize for your infrastructure:
- Update K8s namespace
- Adjust resource limits
- Configure ingress rules

## Session Memory

Each generation session is logged with:
- Timestamp
- Spec analyzed
- Stack detected
- Files generated
- Decisions made

This allows for consistent regeneration and debugging.

## Troubleshooting

Having deployment issues? Check our comprehensive guides:

- 📚 [Troubleshooting Index](docs/TROUBLESHOOTING_INDEX.md) - Start here!
- 🌊 [DigitalOcean Issues](docs/troubleshooting/digitalocean-droplet.md)
- ☁️ [AWS Issues](docs/troubleshooting/aws-common-issues.md)
- 🐳 [Docker Issues](docs/troubleshooting/docker-common-issues.md)
- ☸️ [Kubernetes Issues](docs/troubleshooting/kubernetes-common-issues.md)

Most common issues:
1. **Firewall blocking ports** - Check UFW and cloud firewall
2. **Binding to localhost** - Use 0.0.0.0 instead
3. **Missing env variables** - Check .env file loaded
4. **Health check failing** - Verify /health endpoint