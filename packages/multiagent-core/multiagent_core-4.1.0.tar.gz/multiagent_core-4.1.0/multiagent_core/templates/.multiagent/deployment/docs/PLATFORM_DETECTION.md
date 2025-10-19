# Platform Detection & Auto-Configuration

## Overview

The deployment system now automatically detects deployment platforms mentioned in specs and configures environment variables accordingly.

## Flow

### 1. Platform Detection (`/deployment:deploy-prepare`)

**Step 5** searches all spec files for platform keywords:

| Keyword | Platform |
|---------|----------|
| "Vercel" | vercel |
| "AWS", "Amazon Web Services" | aws |
| "DigitalOcean", "Digital Ocean" | digitalocean |
| "Railway" | railway |
| "Render" | render |
| "Fly.io", "Fly" | fly |
| "Heroku" | heroku |

**Selection logic:**
- Multiple platforms → Choose most frequently mentioned
- No platform → Default to "docker" (self-hosted)

### 2. Configuration Generation

**deployment-prep agent** creates:

```
deployment/
├── platform.txt           # Single line: "digitalocean"
├── env-required.txt       # Platform-specific env vars needed
├── docker-compose.yml     # For local testing
└── [platform configs]     # vercel.json, Dockerfile, etc.
```

**Example `deployment/platform.txt`:**
```
digitalocean
```

**Example `deployment/env-required.txt`:**
```
# Required environment variables for digitalocean deployment

DIGITALOCEAN_TOKEN=your-digitalocean-token-here
DIGITALOCEAN_SPACES_KEY=your-spaces-key-here
DIGITALOCEAN_SPACES_SECRET=your-spaces-secret-here
```

### 3. Environment Setup (`/config:env create`)

**Step 3** reads `deployment/platform.txt` and syncs platform keys:

```bash
# If platform.txt contains "digitalocean"
# /config:env adds to .env:
DIGITALOCEAN_TOKEN=<from ~/.bashrc>
DIGITALOCEAN_SPACES_KEY=<from ~/.bashrc>
DIGITALOCEAN_SPACES_SECRET=<from ~/.bashrc>
```

### 4. Deployment Execution (`/deployment:deploy`)

Reads `deployment/platform.txt` to determine deployment target:

```bash
# Auto-detects platform from deployment/platform.txt
/deployment:deploy production

# Or override:
/deployment:deploy production --platform=aws
```

## Platform-Specific Keys

### Vercel
```bash
VERCEL_TOKEN=
VERCEL_ORG_ID=
VERCEL_PROJECT_ID=
```

### AWS
```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

### DigitalOcean
```bash
DIGITALOCEAN_TOKEN=
DIGITALOCEAN_SPACES_KEY=
DIGITALOCEAN_SPACES_SECRET=
```

### Railway
```bash
RAILWAY_TOKEN=
```

### Render
```bash
RENDER_API_KEY=
```

### Fly.io
```bash
FLY_API_TOKEN=
```

### Heroku
```bash
HEROKU_API_KEY=
HEROKU_APP_NAME=
```

## Full Workflow Example

**1. Spec mentions platform:**
```markdown
# spec.md
Deploy to DigitalOcean droplet with Spaces for static assets.
```

**2. Run deployment preparation:**
```bash
/deployment:deploy-prepare specs/001-my-app
# Detects: digitalocean
# Creates: deployment/platform.txt with "digitalocean"
# Creates: deployment/env-required.txt with DO keys
```

**3. Configure environment:**
```bash
/config:env create backend
# Reads: deployment/platform.txt
# Adds DIGITALOCEAN_* keys from ~/.bashrc to .env
```

**4. Validate and deploy:**
```bash
/deployment:deploy-validate
/deployment:deploy production
# Uses platform from deployment/platform.txt
```

## Templates

### platform.txt.template
```
{{PLATFORM}}
```

### env-required.txt.template
```
# Required environment variables for {{PLATFORM}} deployment

{{#IF_VERCEL}}
VERCEL_TOKEN=your-vercel-token-here
...
{{/IF_VERCEL}}

{{#IF_DIGITALOCEAN}}
DIGITALOCEAN_TOKEN=your-digitalocean-token-here
...
{{/IF_DIGITALOCEAN}}
```

## Integration with Project Setup

`/core:project-setup` workflow:
1. Runs `/deployment:deploy-prepare` (detects platform)
2. Runs `/deployment:deploy-validate` (checks configs)
3. Runs `/config:env create [preset]` (syncs platform keys)
4. Installs dependencies
5. Ready to deploy!

---

**Last Updated:** 2025-10-10
