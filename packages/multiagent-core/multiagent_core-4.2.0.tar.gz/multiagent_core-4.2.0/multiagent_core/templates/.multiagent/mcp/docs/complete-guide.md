# MCP System - Complete Guide

**Version:** 1.2.0
**Last Updated:** 2025-10-09

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Key Management](#key-management)
4. [Registry System](#registry-system)
5. [Custom MCP Server Development](#custom-mcp-server-development)
6. [Slash Commands Reference](#slash-commands-reference)
7. [Complete Workflow](#complete-workflow)
8. [Local vs Remote Servers](#local-vs-remote-servers)
9. [Multi-CLI Support](#multi-cli-support)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

The MCP (Model Context Protocol) system manages AI assistant server configurations across multiple tools (Claude Code, VS Code Copilot, Gemini CLI, Qwen CLI, Codex CLI).

### Key Design Principles

1. **Single Source of Truth**: All API keys stored in `~/.bashrc`
2. **Hardcoded Values**: No placeholder variables (`${VAR}`) in configs
3. **Dual Config Support**: Claude Code + VS Code Copilot
4. **On-Demand Loading**: Add servers only when needed
5. **Token Optimization**: Empty configs = maximum context window

### Why This Architecture?

**Problem**: Claude Code and VS Code don't support environment variable substitution
**Solution**: Read from `~/.bashrc`, hardcode into JSON configs
**Benefit**: Single place to manage keys, automatic propagation to all configs

---

## Architecture

### Directory Structure

```
~/.bashrc                              # Single source of truth for API keys
~/.claude/
├── MCP_COMPLETE_GUIDE.md              # This guide
├── mcp-servers-registry.json          # Server definitions (with placeholders)
└── commands/mcp/                      # Slash commands
    ├── add.md                         # Add server to project
    ├── remove.md                      # Remove server from project
    ├── config.md                      # Manage API keys in ~/.bashrc
    ├── list.md                        # List available servers
    ├── status.md                      # Show current project config
    ├── check.md                       # Validate environment variables
    ├── registry.md                    # Manage server definitions
    └── update.md                      # Update keys in configs

/your-project/
├── .mcp.json                          # Claude Code config (hardcoded keys)
├── .vscode/mcp.json                   # VS Code Copilot config (hardcoded keys)
└── .gitignore                         # Both configs are gitignored
```

### The Three Layers Architecture

**CRITICAL: Where actual values live vs where references live**

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: ~/.bashrc (ACTUAL VALUES - NEVER COMMITTED)       │
├─────────────────────────────────────────────────────────────┤
│ export POSTMAN_API_KEY="PMAK-68a819ab04b03100014ed381..."   │
│ export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxxxx..."          │
│ export OPENAI_API_KEY="sk-proj-xxxxx..."                    │
│                                                              │
│ ✅ This is the SOURCE OF TRUTH for all API keys             │
│ ✅ This is NEVER committed to git                           │
│ ✅ This is user-specific (each dev has their own)           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (environment inherited)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: ~/.claude/mcp-servers-registry.json (REFERENCES)  │
├─────────────────────────────────────────────────────────────┤
│ {                                                            │
│   "servers": {                                               │
│     "postman": {                                             │
│       "env": {                                               │
│         "POSTMAN_API_KEY": "${POSTMAN_API_KEY}"  ← REFERENCE│
│       }                                                      │
│     }                                                        │
│   }                                                          │
│ }                                                            │
│                                                              │
│ ✅ Contains ONLY ${PLACEHOLDER} syntax                      │
│ ✅ Can be committed to git (no actual secrets)              │
│ ✅ Same for all users (references work everywhere)          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (/mcp:add reads & replaces)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: .mcp.json (HARDCODED VALUES - GITIGNORED)         │
├─────────────────────────────────────────────────────────────┤
│ {                                                            │
│   "mcpServers": {                                            │
│     "postman": {                                             │
│       "env": {                                               │
│         "POSTMAN_API_KEY": "PMAK-68a819ab..."  ← ACTUAL VALUE│
│       }                                                      │
│     }                                                        │
│   }                                                          │
│ }                                                            │
│                                                              │
│ ✅ Contains ACTUAL hardcoded values (from Layer 1)          │
│ ✅ Gitignored (cannot be committed)                          │
│ ✅ Claude Code/VS Code reads this directly                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (runtime execution)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ RUNTIME: MCP Server Process (VALUES IN MEMORY)              │
├─────────────────────────────────────────────────────────────┤
│ Claude Code:                                                 │
│   1. Reads .mcp.json                                         │
│   2. Sees: "POSTMAN_API_KEY": "PMAK-68a819ab..."            │
│   3. Passes actual value to MCP server process              │
│                                                              │
│ MCP Server receives:                                         │
│   process.env.POSTMAN_API_KEY = "PMAK-68a819ab04b03100..."  │
│                                                              │
│ ✅ Actual value exists in memory only                        │
│ ✅ Secure - no secrets on disk except in ~/.bashrc          │
└─────────────────────────────────────────────────────────────┘
```

**Why This Architecture?**

- **Security:** Actual secrets only in ~/.bashrc (user-specific, not committed). Everything else uses references or gitignored hardcoded values.
- **Portability:** Registry uses ${VAR} placeholders - same for all users. Each developer has their own keys in ~/.bashrc.
- **Simplicity:** Claude Code and VS Code don't support ${VAR} substitution, so /mcp:add hardcodes values from environment.

### Data Flow Quick Reference

```
1. Store API keys:
   ~/.bashrc (export KEY="value")

2. Define servers:
   ~/.claude/mcp-servers-registry.json (with ${VAR} placeholders)

3. Add to project:
   /mcp:add <server>
   → Reads KEY from environment
   → Replaces ${VAR} with actual value
   → Writes hardcoded value to .mcp.json and .vscode/mcp.json

4. Update keys:
   Edit ~/.bashrc → source ~/.bashrc → /mcp:update <server> all
```

---

## Key Management

### Storage Location: ~/.bashrc

All API keys are stored as shell exports:

```bash
# ============================================================
# MCP SERVER API KEYS (for /mcp:add to hardcode into configs)
# ============================================================
# Postman - API testing
export POSTMAN_API_KEY="PMAK-your-key-here"

# OpenAI - Language models
export OPENAI_API_KEY="sk-proj-your-key-here"

# GitHub - Repository access
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_your-token-here"

# SignalHire - Talent search
export SIGNALHIRE_API_KEY="your-key-here"

# Remote server authentication (for HTTP servers)
export MCP_AUTH_TOKEN="your-remote-auth-token"

# Remote server URLs (auto-detected or manually set)
export SIGNALHIRE_REMOTE_URL="http://142.93.123.456:8080/mcp"
export AIRTABLE_REMOTE_URL="https://airtable-mcp.railway.app"
```

### Key Management Commands

#### View Keys
```bash
/mcp:config view
```
Shows all MCP API keys currently exported in ~/.bashrc

#### Add/Update Keys
```bash
/mcp:config edit
```
Prompts for key name and value, adds to ~/.bashrc

#### Manual Edit
```bash
nano ~/.bashrc
# Add: export KEY_NAME="value"
source ~/.bashrc  # Apply changes
```

#### Validate Keys
```bash
/mcp:check
```
Shows which keys are set (✅) and which are missing (❌)

---

## Registry System

### What is the Registry?

The registry (`~/.claude/mcp-servers-registry.json`) stores server definitions with placeholder variables. It's the template for all servers you can add to projects.

### Registry Structure

#### Simple Server (no variants)
```json
"postman": {
  "type": "stdio",
  "command": "npx",
  "args": ["@postman/postman-mcp-server"],
  "env": {
    "POSTMAN_API_KEY": "${POSTMAN_API_KEY}"
  },
  "description": "API testing and collection management",
  "category": "standard"
}
```

#### Server with Variants (local + remote)
```json
"signalhire": {
  "variants": {
    "local": {
      "type": "stdio",
      "command": "node",
      "args": ["./mcp-servers/signalhire/index.js"],
      "env": {
        "SIGNALHIRE_API_KEY": "${SIGNALHIRE_API_KEY}"
      },
      "description": "SignalHire talent search (local development)"
    },
    "remote": {
      "type": "http",
      "url": "${SIGNALHIRE_REMOTE_URL}",
      "headers": {
        "Authorization": "Bearer ${MCP_AUTH_TOKEN}"
      },
      "description": "SignalHire talent search (remote server)"
    }
  },
  "category": "custom",
  "description": "SignalHire talent search and recruitment API"
}
```

### Registry Management Commands

#### List All Servers
```bash
/mcp:registry list
```
Shows all servers with variants and required keys

#### Add New Server
```bash
/mcp:registry add <server-name> <local|remote|both> [npx|node]
```
Examples:
- `/mcp:registry add twilio local npx` → Add stdio server with npx
- `/mcp:registry add calendly local node` → Add stdio server with local script
- `/mcp:registry add myserver both` → Add both local and remote variants

#### Remove Server
```bash
/mcp:registry remove <server-name>
```

#### Update Server
```bash
/mcp:registry update <server-name>
```
Prompts which field to update

---

## Custom MCP Server Development

Build and deploy your own MCP servers for use across all your projects.

### Development Structure

**Recommended Location:** `~/mcp-servers/`

```
~/mcp-servers/
├── cats/                          # TypeScript MCP server
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   └── index.ts
│   └── dist/
│       └── index.js
├── signalhire/                    # Python MCP server
│   ├── setup.py
│   ├── src/
│   │   └── server.py
│   └── requirements.txt
└── another-server/
```

### Deployment Options

#### Option 1: Local Development (Testing)

**Best for:** Development, testing, iteration

**Registry Entry:**
```json
"cats": {
  "type": "stdio",
  "command": "node",
  "args": ["~/mcp-servers/cats/dist/index.js"],
  "env": {
    "CATS_API_KEY": "${CATS_API_KEY}"
  },
  "description": "Custom CATS server (local)",
  "category": "custom"
}
```

**Usage:**
```bash
/mcp:add cats  # Points to local files
```

---

#### Option 2: Published NPM Package (Production)

**Best for:** Sharing across projects, team collaboration

**Publish:**
```bash
cd ~/mcp-servers/cats
npm publish @yourorg/cats-mcp
```

**Registry Entry:**
```json
"cats": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@yourorg/cats-mcp"],
  "env": {
    "CATS_API_KEY": "${CATS_API_KEY}"
  },
  "description": "Custom CATS server (npm)",
  "category": "custom"
}
```

**Usage:**
```bash
/mcp:add cats  # Downloads from npm
```

---

#### Option 3: Git Repository (Private Servers)

**Best for:** Private servers, not ready for public npm

**Registry Entry:**
```json
"cats": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "github:yourorg/cats-mcp"],
  "env": {
    "CATS_API_KEY": "${CATS_API_KEY}"
  },
  "description": "Custom CATS server (git)",
  "category": "custom"
}
```

**Usage:**
```bash
/mcp:add cats  # Clones from GitHub
```

---

#### Option 4: Remote HTTP Server (Cloud Deployment)

**Best for:** Production, multi-project shared instance

**Deploy to Droplet:**
```bash
ssh your-droplet
cd /var/mcp-servers
pm2 start cats-server.js
# Server running at http://your-droplet:8080/mcp
```

**Registry Entry (with variants):**
```json
"cats": {
  "variants": {
    "local": {
      "type": "stdio",
      "command": "node",
      "args": ["~/mcp-servers/cats/dist/index.js"],
      "env": {
        "CATS_API_KEY": "${CATS_API_KEY}"
      },
      "description": "Custom CATS server (local)"
    },
    "remote": {
      "type": "http",
      "url": "${CATS_REMOTE_URL}",
      "headers": {
        "Authorization": "Bearer ${MCP_AUTH_TOKEN}"
      },
      "description": "Custom CATS server (remote)"
    }
  },
  "category": "custom",
  "description": "Custom CATS server with local/remote variants"
}
```

**Setup Remote:**
```bash
# Add URL to bashrc
echo 'export CATS_REMOTE_URL="http://your-droplet:8080/mcp"' >> ~/.bashrc
source ~/.bashrc

# Use remote version
/mcp:add cats remote
```

---

### Complete Development Workflow

**1. Build Custom Server**
```bash
# Create directory
mkdir -p ~/mcp-servers/cats
cd ~/mcp-servers/cats

# Initialize project
npm init -y
# or for Python: touch setup.py
```

**2. Add to Registry (Local for Testing)**
```bash
/mcp:registry add cats local node
# Prompts:
# - Path: ~/mcp-servers/cats/dist/index.js
# - Env vars: CATS_API_KEY
# - Description: Custom CATS server
```

**3. Add API Keys**
```bash
/mcp:config edit
# Add: CATS_API_KEY=your-key-here
source ~/.bashrc
```

**4. Test in Project**
```bash
cd ~/your-project
/mcp:add cats
# Restart Claude Code / VS Code
# Test the server
```

**5. Iterate**
```bash
# Make changes to server code
cd ~/mcp-servers/cats
npm run build  # or python build

# Restart Claude Code to reload
```

**6. Publish (When Ready)**
```bash
# Option A: Publish to npm
npm publish @yourorg/cats-mcp

# Option B: Push to GitHub
git push origin main

# Option C: Deploy to droplet
scp -r dist/ your-droplet:/var/mcp-servers/cats/
ssh your-droplet "pm2 restart cats-server"
```

**7. Update Registry**
```bash
# Change from local path to published package
/mcp:registry update cats
# Update command to: npx -y @yourorg/cats-mcp
```

**8. Use in All Projects**
```bash
cd ~/project-a && /mcp:add cats
cd ~/project-b && /mcp:add cats
cd ~/project-c && /mcp:add cats
# All projects now use published version
```

---

### Best Practices

**Development:**
- Use local path during development (`~/mcp-servers/cats/`)
- Test thoroughly before publishing
- Version your servers (use semver)

**Production:**
- Publish stable versions to npm
- Use remote HTTP for shared team instances
- Keep registry updated with correct package names

**Multi-Project Usage:**
- One registry entry works everywhere
- Update registry once, use in all projects
- Local for dev, remote/npm for production

---

## Slash Commands Reference

### /mcp:config - Key Management
```bash
/mcp:config view       # Show keys in ~/.bashrc
/mcp:config edit       # Add/update keys
```

### /mcp:check - Validate Environment
```bash
/mcp:check             # Show which keys are set
```
Output example:
```
✅ POSTMAN_API_KEY: PMAK-68d***
✅ OPENAI_API_KEY: sk-proj-***
❌ GITHUB_PERSONAL_ACCESS_TOKEN: Not set
```

### /mcp:list - Show Available Servers
```bash
/mcp:list              # List all servers from registry
```

### /mcp:status - Current Project Status
```bash
/mcp:status            # Show servers in .mcp.json and .vscode/mcp.json
```

### /mcp:add - Add Server(s) to Project
```bash
/mcp:add <server-name(s)> [local|remote] [platform]
```

**Single Server:**
- `/mcp:add postman` → Add Postman
- `/mcp:add github` → Add GitHub
- `/mcp:add signalhire local` → Add SignalHire (local)
- `/mcp:add signalhire remote vercel` → Add SignalHire (Vercel deployment)

**Multiple Servers:**
- `/mcp:add context7 postman github` → Add 3 servers at once
- `/mcp:add memory playwright filesystem` → Add utility servers
- Shows summary: ✅ added, ⏭️ skipped, ❌ failed

**What it does:**
1. Reads server definitions from registry
2. Gets API keys from environment (exported in ~/.bashrc)
3. Replaces `${VAR}` placeholders with actual hardcoded values
4. Writes to `.mcp.json` (Claude Code)
5. Writes to `.vscode/mcp.json` (VS Code Copilot)
6. Shows summary of successes/failures for batch adds

### /mcp:remove - Remove Server from Project
```bash
/mcp:remove <server-name>
```
Removes from both `.mcp.json` and `.vscode/mcp.json`

### /mcp:update - Update Keys in Configs
```bash
/mcp:update <server-name> [claude|vscode|gemini|qwen|codex|all]
```
Examples:
- `/mcp:update postman` → Updates all CLIs (default)
- `/mcp:update postman claude` → Updates only Claude Code
- `/mcp:update github vscode` → Updates only VS Code

**When to use:**
After updating keys in ~/.bashrc, use this to propagate changes to config files.

### /mcp:registry - Manage Server Definitions
```bash
/mcp:registry list                              # List all servers
/mcp:registry add <name> <local|remote|both>    # Add new server
/mcp:registry remove <name>                     # Remove server
/mcp:registry update <name>                     # Update server
```

---

## Complete Workflow

### First-Time Setup

1. **Add API keys to ~/.bashrc:**
```bash
/mcp:config edit
# Or manually:
nano ~/.bashrc
# Add: export POSTMAN_API_KEY="your-key-here"
source ~/.bashrc
```

2. **Verify keys are set:**
```bash
/mcp:check
# Should show: ✅ POSTMAN_API_KEY: PMAK-***
```

3. **See available servers:**
```bash
/mcp:list
```

4. **Add server to project:**
```bash
/mcp:add postman
```

5. **Restart Claude Code / VS Code**
```bash
# Claude Code: Restart session
# VS Code: Ctrl+Shift+P → "Reload Window"
```

6. **Verify:**
```bash
/mcp:status
# Should show: 1 server active (postman)
```

### Daily Usage

**Add a server when needed:**
```bash
/mcp:add github
```

**Remove when done:**
```bash
/mcp:remove github
```

**Check what's active:**
```bash
/mcp:status
```

### Updating API Keys

1. **Update in ~/.bashrc:**
```bash
nano ~/.bashrc
# Change: export POSTMAN_API_KEY="new-key-here"
source ~/.bashrc
```

2. **Update configs:**
```bash
/mcp:update postman all
```

3. **Restart tools**

### Adding Custom Servers

1. **Add to registry:**
```bash
/mcp:registry add myserver local node
# Follow prompts for command, env vars, description
```

2. **Add keys to ~/.bashrc:**
```bash
/mcp:config edit
# Add required keys
source ~/.bashrc
```

3. **Add to project:**
```bash
/mcp:add myserver
```

---

## Local vs Remote Servers

### Local Servers (stdio)

**Type:** `stdio`
**Connection:** Spawns local process
**Format:**
```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["@postman/postman-mcp-server"],
  "env": {
    "POSTMAN_API_KEY": "hardcoded-key-here"
  }
}
```

**Use Cases:**
- Development and testing
- Pre-built npm packages
- Local scripts

**Examples:**
- `postman` → npx package
- `github` → npx package
- `memory` → npx package
- `signalhire local` → local node script

### Remote Servers (http)

**Type:** `http`
**Connection:** HTTP requests to remote URL
**Format:**
```json
{
  "type": "http",
  "url": "http://142.93.123.456:8080/mcp",
  "headers": {
    "Authorization": "Bearer hardcoded-token-here"
  }
}
```

**Use Cases:**
- Production deployments
- Shared team servers
- Cloud-hosted services

**Examples:**
- `signalhire remote vercel` → Vercel deployment
- `signalhire remote railway` → Railway deployment
- `signalhire remote docker` → Local Docker container

### Platform Auto-Detection

When adding remote servers, specify the platform to auto-detect URLs:

```bash
/mcp:add signalhire remote vercel
# Runs: vercel inspect
# Extracts: deployment URL
# Adds to ~/.bashrc: export SIGNALHIRE_REMOTE_URL="https://..."
```

**Supported Platforms:**
- `vercel` → Uses `vercel inspect`
- `railway` → Uses `railway status`
- `digitalocean` → Uses `doctl compute droplet list`
- `docker` → Uses `docker ps` + `docker inspect`

---

## Multi-CLI Support

### Supported CLI Tools

| CLI | Config Location | Command Format |
|-----|----------------|----------------|
| **Claude Code** | `.mcp.json` | `/mcp:add <server>` |
| **VS Code Copilot** | `.vscode/mcp.json` | Same as Claude |
| **Gemini CLI** | `~/.config/gemini/settings.json` | `/mcp:update <server> gemini` |
| **Qwen CLI** | `~/.config/qwen/settings.json` | `/mcp:update <server> qwen` |
| **Codex CLI** | `~/.config/codex/settings.json` | `/mcp:update <server> codex` |

### Update Specific CLI

```bash
# Update only Gemini
/mcp:update postman gemini

# Update only VS Code
/mcp:update github vscode

# Update all CLIs
/mcp:update postman all
```

### Project-Specific vs Global

**Project-Specific** (`.mcp.json`, `.vscode/mcp.json`):
- Servers needed for this project only
- Different servers per project
- Managed with `/mcp:add` and `/mcp:remove`

**Global** (`~/.config/gemini/settings.json`, etc.):
- Servers available in all projects
- Updated with `/mcp:update <server> gemini`

---

## Troubleshooting

### API Key Not Working

**Problem:** Server added but tools can't authenticate

**Solution:**
```bash
# 1. Verify key is in environment
/mcp:check

# 2. If missing, add to ~/.bashrc
/mcp:config edit

# 3. Reload environment
source ~/.bashrc

# 4. Update configs
/mcp:update <server> all

# 5. Restart tools
```

### Placeholder Not Replaced

**Problem:** Config shows `${VAR}` instead of actual value

**Cause:** Claude Code and VS Code don't support placeholders

**Solution:**
```bash
# Our system automatically replaces placeholders
# If you see ${VAR}, it means:
# 1. Key not in environment when /mcp:add was run
# 2. Need to re-run /mcp:add after adding key

/mcp:config edit      # Add key
source ~/.bashrc      # Reload
/mcp:remove <server>  # Remove old config
/mcp:add <server>     # Re-add with actual value
```

### Server Not Loading

**Problem:** Added server but tools don't see it

**Solution:**
```bash
# 1. Check config files
/mcp:status

# 2. Verify format
cat .mcp.json
cat .vscode/mcp.json

# 3. Restart tools
# Claude Code: Restart session
# VS Code: Ctrl+Shift+P → "Reload Window"
```

### Registry Server Not Found

**Problem:** `/mcp:add <server>` says server not found

**Solution:**
```bash
# 1. Check registry
/mcp:registry list

# 2. If missing, add it
/mcp:registry add <server-name> local npx

# 3. Then add to project
/mcp:add <server-name>
```

### Remote URL Not Detected

**Problem:** Platform auto-detection fails

**Solution:**
```bash
# 1. Manually add URL to ~/.bashrc
nano ~/.bashrc
# Add: export SERVERNAME_REMOTE_URL="http://your-url-here"
source ~/.bashrc

# 2. Then add server
/mcp:add <server> remote
```

### Too Many Tokens Used

**Problem:** Context window filling up

**Solution:**
```bash
# Remove unused servers
/mcp:status              # See what's active
/mcp:remove <server>     # Remove what you don't need

# Each server adds ~10K-20K tokens
# Empty config = maximum ~200K context available
```

### Keys in Git

**Problem:** Accidentally committed API keys

**Solution:**
```bash
# 1. Verify .gitignore
cat .gitignore
# Should contain:
# .mcp.json
# .vscode/mcp.json

# 2. If already committed
git rm --cached .mcp.json
git rm --cached .vscode/mcp.json
git commit -m "Remove API keys from git"

# 3. Rotate compromised keys immediately
```

---

## Quick Reference Card

### Essential Commands
```bash
/mcp:config view           # Show API keys
/mcp:check                 # Validate keys
/mcp:list                  # Available servers
/mcp:status                # Current config
/mcp:add <server>          # Add server
/mcp:remove <server>       # Remove server
/mcp:update <server> all   # Update keys
```

### Common Workflows
```bash
# Setup
/mcp:config edit → source ~/.bashrc → /mcp:add postman

# Change key
nano ~/.bashrc → source ~/.bashrc → /mcp:update postman all

# Add custom server
/mcp:registry add myserver local → /mcp:config edit → /mcp:add myserver

# Remote deployment
/mcp:add signalhire remote docker
```

### File Locations
```bash
~/.bashrc                              # API keys
~/.claude/mcp-servers-registry.json    # Server definitions
.mcp.json                              # Claude Code config
.vscode/mcp.json                       # VS Code config
```

---

## Support

**Documentation:** `~/.claude/MCP_COMPLETE_GUIDE.md` (this file)
**Load in session:** `/docs` (loads this guide for review)
**Commands:** `~/.claude/commands/mcp/*.md`
**Registry:** `~/.claude/mcp-servers-registry.json`

---

**Last Updated:** 2025-10-09
**Version:** 1.2.0

## Changelog

**v1.2.0** (2025-10-09):
- Added "The Three Layers Architecture" visual diagram
- Enhanced architecture explanation with clear security model
- Improved understanding of hardcoded values vs placeholders

**v1.1.0** (2025-10-09):
- Added "Custom MCP Server Development" section
- Updated `/mcp:add` to support multiple servers at once
- Added complete workflows for local development to production deployment
- Added examples for npm publishing, git repos, and remote HTTP servers

---

## 🔗 See Also

### Related Guides

- **[MCP Connector Pattern](connector-pattern.md)** - NEW! Pluggable architecture for composing small MCP servers
  - Small server pattern (5-15 tools max)
  - Mounting vs importing servers
  - Local (stdio) vs Remote (HTTP) environments
  - Tool limiting strategies
  - GitHub MCP Registry integration

### Quick Links

- Complete Guide: [complete-guide.md](complete-guide.md) - Full MCP system documentation
- Connector Pattern: [connector-pattern.md](connector-pattern.md) - Pluggable architecture guide

---

**Updated:** 2025-10-10 - Added Connector Pattern documentation
