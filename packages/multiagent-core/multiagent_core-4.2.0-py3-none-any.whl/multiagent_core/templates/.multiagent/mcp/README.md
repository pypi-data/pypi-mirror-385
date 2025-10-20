# MCP (Model Context Protocol) Subsystem

## Purpose

Manages MCP server configuration and deployment across different AI agents. Provides standardized MCP server setup for AI application development.

## Core Principle

**AGENT-SPECIFIC CONFIGS** - Different agents need different MCP configurations based on their context window sizes and capabilities.

## Architecture

### Agent-Specific Differences

**Claude Code** (Small context window)
- **Config**: `.mcp.json` per-project (minimal, project-specific servers only)
- **Location**: Project root
- **Strategy**: Minimal servers per project to conserve context
- **Managed by**: `/mcp:add`, `/mcp:remove` commands

**Qwen, Gemini** (Large context window)
- **Config**: `settings.json` (can load ALL MCP servers at once)
- **Location**: Agent-specific config directory
- **Strategy**: Load full MCP server registry for maximum capability
- **Managed by**: Global registry sync

**Codex** (Large context window)
- **Config**: `settings.json` or `.toml` (can load ALL MCP servers)
- **Location**: Agent-specific config directory
- **Strategy**: Load full MCP server registry
- **Managed by**: Global registry sync

**VS Code Copilot** (Per-project)
- **Config**: `.vscode/mcp.json` per-project
- **Location**: `.vscode/` directory
- **Strategy**: Project-specific servers like Claude
- **Managed by**: `/mcp:add`, `/mcp:remove` commands

## Structure

```
~/.multiagent/mcp/
├── README.md                    # This file
├── docs/
│   ├── architecture.md          # MCP architecture overview
│   ├── complete-guide.md        # Comprehensive MCP guide
│   └── connector-pattern.md     # MCP connector patterns
├── scripts/                     # Mechanical operations
│   ├── list-servers.sh          # List registry servers
│   ├── validate-config.sh       # Validate JSON configs
│   └── detect-platform.sh       # Detect deployment platform
└── templates/                   # Config templates
    ├── .mcp.json.template       # Claude Code config template
    ├── .vscode-mcp.json.template # VS Code config template
    └── server-definition.json.template # Registry entry template
```

## Command Reference

### `/mcp:add <server> [local|remote]`
**Agent**: mcp-config-generator
**Scripts**:
  - mcp/scripts/list-servers.sh
  - mcp/scripts/detect-platform.sh
**Templates**:
  - mcp/templates/.mcp.json.template
  - mcp/templates/.vscode-mcp.json.template
**Outputs**: Updated .mcp.json and .vscode/mcp.json
**Outcome**: Server added to project configuration from global registry

### `/mcp:remove <server>`
**Agent**: None (direct execution)
**Scripts**:
  - mcp/scripts/validate-config.sh
**Templates**: None
**Outputs**: Updated .mcp.json and .vscode/mcp.json
**Outcome**: Server removed from project configuration

### `/mcp:update <server>`
**Agent**: mcp-config-generator
**Scripts**:
  - mcp/scripts/validate-config.sh
**Templates**: None
**Outputs**: Updated agent CLI configs
**Outcome**: API keys synced from ~/.bashrc to agent configs

### `/mcp:list`
**Agent**: None (direct execution)
**Scripts**:
  - mcp/scripts/list-servers.sh
**Templates**: None
**Outputs**: List of available servers from global registry
**Outcome**: User can see all available MCP servers with descriptions

### `/mcp:status`
**Agent**: None (direct execution)
**Scripts**: None
**Templates**: None
**Outputs**: Current project's MCP configuration
**Outcome**: User can see which servers are active in this project

### `/mcp:setup`
**Agent**: None (interactive)
**Scripts**: None
**Templates**: None
**Outputs**: Configured ~/.bashrc with MCP API keys
**Outcome**: API keys set up for MCP servers

### `/mcp:inventory`
**Agent**: None (direct execution)
**Scripts**: None
**Templates**:
  - mcp/templates/api-keys-inventory.md.template
**Outputs**: ~/.api-keys-inventory.md
**Outcome**: Global tracking file for API keys across all projects

### `/mcp:check`
**Agent**: None (direct execution)
**Scripts**: None
**Templates**: None
**Outputs**: List of configured MCP_* API keys
**Outcome**: User can verify which MCP keys are set in ~/.bashrc

### `/mcp:clear`
**Agent**: None (direct execution)
**Scripts**: None
**Templates**: None
**Outputs**: Empty .mcp.json and .vscode/mcp.json
**Outcome**: All servers removed from project (maximize context window)

### `/mcp:registry <add|remove|list|update>`
**Agent**: mcp-registry-manager
**Scripts**: None
**Templates**:
  - mcp/templates/server-definition.json.template
**Outputs**: Updated ~/.multiagent/config/mcp-servers-registry.json
**Outcome**: Global registry updated with new server definitions

## Agents

**mcp-registry-manager** (`~/.claude/agents/mcp-registry-manager.md`)
- Manages MCP server registry CRUD operations
- Validates server definitions
- Handles local/remote variants
- Tools: Read, Write, Edit

**mcp-config-generator** (`~/.claude/agents/mcp-config-generator.md`)
- Generates .mcp.json and .vscode/mcp.json files
- Replaces API key placeholders with actual values from ~/.bashrc
- Handles hardcoded key requirement (Claude/VS Code limitation)
- Tools: Read, Write, Bash

## Scripts

**list-servers.sh**
- Lists all servers in global registry
- Outputs JSON array with server metadata
- Used by: `/mcp:list`

**validate-config.sh**
- Validates MCP config file syntax
- Checks required fields
- Detects hardcoded keys vs placeholders
- Used by: `/mcp:add`, `/mcp:update`

**detect-platform.sh**
- Detects deployment platform from git remote
- Supports: Vercel, AWS, Railway, Render, Heroku
- Falls back to config file detection
- Used by: `/mcp:add` (for remote variants)

## Templates

**`.mcp.json.template`**
- Template for Claude Code configuration
- Placeholders: `{{SERVER_NAME}}`, `{{COMMAND}}`, `{{ARGS}}`, `{{ENV_KEY}}`, `{{ENV_VALUE}}`
- Used by: `mcp-config-generator` agent

**`.vscode-mcp.json.template`**
- Template for VS Code configuration
- Same placeholder format as Claude Code template
- Used by: `mcp-config-generator` agent

**`server-definition.json.template`**
- Template for registry entries
- Supports both local and remote variants
- Used by: `mcp-registry-manager` agent

## MCP Registry

**Central Registry**: `~/.claude/mcp-servers-registry.json`

Contains all available MCP servers with:
- Server command and args
- Required environment variables (using `${MCP_*}` pattern)
- Server description and category
- Variants (local/remote) for deployment-aware servers

## API Key Management

**Three-Tier Architecture** (managed by Security subsystem):

**Tier 1: MCP Keys** (`MCP_*` prefix in `~/.bashrc`)
- Used BY agents through MCP servers ONLY
- Example: `MCP_GITHUB_TOKEN`, `MCP_POSTMAN_API_KEY`
- Managed by: `/security:bashrc add-mcp <service>`

**Tier 2: Direct API Keys** (in `~/.bashrc`)
- Used in YOUR application code for direct API calls
- Example: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- Managed by: `/security:bashrc add-direct <service>`

**Tier 3: Platform Keys** (in `~/.bashrc`)
- Infrastructure and deployment platforms
- Example: `VERCEL_TOKEN`, `DIGITALOCEAN_API_KEY`
- Managed by: `/security:bashrc add-platform <service>`

**Why separate MCP keys?**
- Track agent MCP tool costs separately from application API usage
- Rotate one tier without affecting others
- Agents ONLY use Tier 1 keys through MCP servers

## Commands

### Server Management
- `/mcp:add <server>` - Add MCP server to project (Claude, VS Code)
- `/mcp:remove <server>` - Remove MCP server from project
- `/mcp:list` - List available MCP servers from registry
- `/mcp:status` - Show current MCP configuration
- `/mcp:clear` - Remove all MCP servers from project

### Configuration Management
- `/mcp:setup` - Interactive MCP server setup wizard
- `/mcp:update <server>` - Sync MCP keys from ~/.bashrc to configs
- `/mcp:check` - Verify which MCP keys are configured
- `/mcp:inventory` - Generate API keys inventory tracking

### Registry Management
- `/mcp:registry add <server>` - Add server to registry
- `/mcp:registry remove <server>` - Remove server from registry
- `/mcp:registry list` - List all servers in registry
- `/mcp:registry update` - Update server definitions

## Workflow Examples

### Adding MCP Server (Claude/VS Code)
```bash
# 1. Add MCP key to ~/.bashrc
/security:bashrc add-mcp postman
# Prompts for API key value
# Adds: export MCP_POSTMAN_API_KEY="..."

# 2. Reload environment
source ~/.bashrc

# 3. Add server to project
cd ~/my-project
/mcp:add postman
# Adds to .mcp.json and .vscode/mcp.json with hardcoded key

# 4. Restart Claude Code or VS Code
```

### Setting Up Full MCP for Qwen/Gemini
```bash
# 1. Add all necessary MCP keys to ~/.bashrc
/security:bashrc add-mcp github
/security:bashrc add-mcp postman
/security:bashrc add-mcp context7

# 2. Reload environment
source ~/.bashrc

# 3. Sync to Qwen/Gemini settings.json
# (Future: /mcp:sync qwen)
# Loads ALL servers from registry into settings.json
```

### Checking MCP Configuration
```bash
# View current setup
/mcp:status
# Shows:
# - Servers configured in project
# - Which keys are set in ~/.bashrc
# - Missing keys that need to be added

# Check which keys exist
/mcp:check
# Shows all MCP_* keys in ~/.bashrc
```

## Config File Formats

### Claude Code (`.mcp.json`)
```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_actual_hardcoded_key_here"
      }
    }
  }
}
```

### VS Code Copilot (`.vscode/mcp.json`)
```json
{
  "servers": {
    "postman": {
      "type": "stdio",
      "command": "npx",
      "args": ["@postman/postman-mcp-server"],
      "env": {
        "POSTMAN_API_KEY": "PMAK-actual_hardcoded_key_here"
      }
    }
  }
}
```

### Qwen/Gemini (`settings.json`)
```json
{
  "mcpServers": {
    "github": { /* full registry definition */ },
    "postman": { /* full registry definition */ },
    "context7": { /* full registry definition */ },
    "memory": { /* full registry definition */ },
    "playwright": { /* full registry definition */ }
    /* ... all available servers ... */
  }
}
```

## Design Principles

1. **Agent-Appropriate** - Different configs for different agents
2. **Minimal for Claude** - Small context requires minimal servers per-project
3. **Full for Large Context** - Qwen/Gemini can load all servers
4. **Central Registry** - Single source of truth for server definitions
5. **Hardcoded Keys** - No `${VAR}` placeholders (Claude/VS Code don't support)
6. **Security Separation** - MCP keys (Tier 1) separate from app keys (Tier 2/3)

## Integration Points

### With Security Subsystem
- MCP keys stored in `~/.bashrc` (Tier 1 with `MCP_*` prefix)
- Managed by `/security:bashrc` commands
- Separate from application API keys

### With Project Init
- Claude/VS Code: Minimal `.mcp.json` and `.vscode/mcp.json` created per-project
- Qwen/Gemini: Global `settings.json` with full registry

### With Deployment
- Remote MCP server variants for deployment platforms
- Auto-detect deployment URLs (Vercel, Railway, etc.)

## Related Systems

- **Security Subsystem** (`~/.multiagent/security/`) - Three-tier API key management
- **Slash Commands** (`~/.claude/commands/mcp/`) - MCP server management
- **MCP Registry** (`~/.claude/mcp-servers-registry.json`) - Central server definitions

---

**Remember: MCP is foundational for AI development. Choose configs appropriate for each agent's capabilities.**
