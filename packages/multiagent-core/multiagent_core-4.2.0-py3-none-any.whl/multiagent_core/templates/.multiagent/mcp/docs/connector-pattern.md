# MCP Connector Pattern - Pluggable Architecture

**Version:** 2.0.0
**Last Updated:** 2025-10-10
**Related:** [Complete Guide](complete-guide.md)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Small Server Pattern](#small-server-pattern)
4. [Mounting vs Importing](#mounting-vs-importing)
5. [Tool Limiting Strategy](#tool-limiting-strategy)
6. [Local vs Remote Environments](#local-vs-remote-environments)
7. [Configuration Architecture](#configuration-architecture)
8. [GitHub MCP Registry](#github-mcp-registry)
9. [Implementation Guide](#implementation-guide)

---

## Overview

The **MCP Connector Pattern** is a lightweight plugin architecture for composing multiple small MCP servers instead of building monolithic servers with hundreds of tools.

### The Problem

```
❌ ANTI-PATTERN: Monolithic Server
giant_mcp_server.py
  ├── 50 GitHub tools
  ├── 40 Database tools  
  ├── 30 API tools
  ├── 25 File tools
  └── 55 Utility tools
  = 200 tools → Context explosion, slow, unmaintainable
```

### The Solution

```
✅ CONNECTOR PATTERN: Composed Small Servers
connector.py (lightweight glue)
  ├── github_server.py        (8 tools)
  ├── database_server.py      (10 tools)
  ├── signalhire_server.py    (5 tools)
  ├── email_server.py         (7 tools)
  └── slack_server.py         (5 tools)
  = 35 tools across 5 focused servers
```

---

## Core Principles

### 1. **Small Servers (5-15 tools max)**
Each server focuses on ONE domain with limited tools.

### 2. **Mount, Don't Copy**
Connector delegates to servers at runtime (no tool duplication).

### 3. **Environment Switching**
Same API works with stdio (local dev) and HTTP (production).

### 4. **Tool Filtering**
Limit exposed tools per server and per agent.

### 5. **Plugin Architecture**
Add/remove servers without code changes.

---

## Small Server Pattern

### ✅ Good: Focused Servers

```python
# signalhire_server.py - ONE purpose
from fastmcp import FastMCP

server = FastMCP("SignalHire", max_tools=10)

@server.tool
def search_candidates(query: str):
    """Search for candidates"""
    return search_api(query)

@server.tool
def reveal_contact(candidate_id: str):
    """Get contact information"""
    return reveal_api(candidate_id)

# Only 5 tools total - stays focused!
```

### ❌ Bad: Kitchen Sink Server

```python
# everything_server.py - TOO MANY PURPOSES
server = FastMCP("Everything")

@server.tool
def github_create_issue(): ...

@server.tool  
def send_email(): ...

@server.tool
def query_database(): ...

# 200 tools later... ❌
```

---

## Mounting vs Importing

### Mounting (Recommended for Production)

**Live delegation** - Changes to mounted servers propagate immediately.

```python
from fastmcp import FastMCP

# Create connector (lightweight glue)
connector = FastMCP("MainConnector")

# Mount small servers (live links)
connector.mount(signalhire_server, prefix="sig")
connector.mount(github_server, prefix="gh")

# Tools stay in their servers
# Connector just routes: sig_search → signalhire_server
```

**Benefits:**
- ✅ No tool duplication
- ✅ Hot reload possible
- ✅ Memory efficient
- ✅ Clear namespacing

### Importing (Static Copy)

**One-time copy** - Useful for bundling.

```python
# Copies tools once at startup
await connector.import_server(weather_server, prefix="weather")

# Changes to weather_server won't affect connector
```

---

## Tool Limiting Strategy

### Enforce Limits Per Server

```python
class PluggableMCPServer:
    """Prevents tool explosion"""
    
    def __init__(self, name: str, max_tools: int = 20):
        self.name = name
        self.max_tools = max_tools
        self.tools = {}
        
    def register_tool(self, tool_fn):
        if len(self.tools) >= self.max_tools:
            raise ValueError(
                f"{self.name} reached {self.max_tools} tool limit. "
                "Create a new focused server instead."
            )
        self.tools[tool_fn.__name__] = tool_fn
```

**Result:** Forces architectural discipline - can't build giant servers!

### Tool Configuration Filtering

```json
{
  "servers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "tool_configuration": {
        "enabled": true,
        "allowed_tools": [
          "create_issue",
          "review_pr",
          "list_repos"
        ]
      }
    }
  }
}
```

Even if GitHub server has 50 tools, only expose 3!

---

## Local vs Remote Environments

### The Pattern

**Same API, different transport:**
- **Local (dev)**: stdio - spawn Python process
- **Production**: HTTP - call remote URL

### Configuration

```json
{
  "environment": "local",
  
  "servers": {
    "signalhire": {
      "local": {
        "type": "stdio",
        "command": "python",
        "args": ["./servers/signalhire_server.py"]
      },
      "production": {
        "type": "http",
        "url": "https://mcp.signalhire.com"
      },
      "allowed_tools": ["search_candidates", "reveal_contact"]
    },
    
    "github": {
      "local": {
        "type": "http",
        "url": "https://api.githubcopilot.com/mcp/"
      },
      "production": {
        "type": "http",
        "url": "https://api.githubcopilot.com/mcp/"
      },
      "allowed_tools": ["create_issue", "review_pr"]
    }
  }
}
```

### Environment Switcher

```python
class MCPEnvironment:
    """Automatic environment detection"""
    
    def __init__(self, env: str = None):
        self.env = env or os.getenv("MCP_ENV", "local")
        
    def get_server_config(self, server_name: str):
        """Returns local or production config"""
        config = load_config()
        server = config["servers"][server_name]
        return server[self.env]
        
    async def connect(self, server_name: str):
        """Connects using appropriate transport"""
        config = self.get_server_config(server_name)
        
        if config["type"] == "stdio":
            return await StdioClient(config["command"], config["args"])
        elif config["type"] == "http":
            return HttpClient(config["url"])
```

### Usage

```bash
# Development
export MCP_ENV=local
python main.py  # Uses stdio servers

# Production  
export MCP_ENV=production
python main.py  # Uses HTTP servers

# Same code, different transport!
```

---

## Configuration Architecture

### Server Breakdown by Size

```
Small Servers (Recommended):

✅ signalhire_server.py      5 tools   - Candidate search
✅ github_server.py           8 tools   - GitHub operations
✅ sentry_server.py           6 tools   - Error tracking
✅ database_server.py        10 tools   - DB queries
✅ email_server.py            7 tools   - Email sending
✅ slack_server.py            5 tools   - Notifications
✅ calendar_server.py         6 tools   - Scheduling

Total: 47 tools across 7 focused servers
```

### Agent-Specific Tool Access

```json
{
  "agent_tool_permissions": {
    "orchestrator": {
      "include_servers": ["signalhire", "github", "database"],
      "include_tags": ["sourcing", "development"]
    },
    "sourcing": {
      "include_servers": ["signalhire"],
      "allowed_tools": ["search_candidates", "reveal_contact"]
    },
    "screening": {
      "include_servers": ["database"],
      "allowed_tools": ["query_candidates", "update_status"]
    }
  }
}
```

**Result:** Each agent only sees tools it needs!

---

## GitHub MCP Registry

### Official MCP Endpoints

```bash
# GitHub (Official)
claude mcp add --transport http github \
  https://api.githubcopilot.com/mcp/

# Figma (Official)
claude mcp add --transport http figma \
  https://mcp.figma.com/mcp

# Sentry (Official)
claude mcp add --transport http sentry \
  https://mcp.sentry.dev/mcp

# Notion (Official)
claude mcp add --transport http notion \
  https://mcp.notion.com/mcp
```

### Registry Integration

```python
class MCPRegistry:
    """Connect to external registries"""
    
    REGISTRIES = {
        "github": "https://api.githubcopilot.com/mcp/",
        "anthropic": "https://registry.anthropic.com/mcp/",
        "community": "https://mcp-registry.dev/"
    }
    
    async def discover_servers(self, registry: str = "github"):
        """List available servers"""
        
    async def install_server(self, server_name: str):
        """Add to local config"""
```

### One-Line Server Installation

```bash
# Install from GitHub registry
mcp registry install github

# Install from community
mcp registry install @community/postgres

# List available
mcp registry list --source github
```

---

## Implementation Guide

### 1. Minimal Connector Class (~200 lines)

```python
# multiagent_core/mcp/connector.py

class MCPConnector:
    """Lightweight plugin mounting system"""
    
    def __init__(self, environment: str = "local"):
        self.env = environment
        self.servers = {}  # name -> client
        
    def mount(self, name: str, server, prefix: str = None):
        """Mount small server (live delegation)"""
        prefix = prefix or name
        self.servers[name] = {
            "instance": server,
            "prefix": prefix,
            "type": "mounted"
        }
        
    async def add_remote(self, name: str, url: str, 
                         allowed_tools: list = None):
        """Add remote HTTP server"""
        self.servers[name] = {
            "url": url,
            "type": "remote",
            "allowed_tools": allowed_tools or []
        }
        
    async def call_tool(self, server_name: str, 
                       tool_name: str, args: dict):
        """Delegate to appropriate server"""
        server = self.servers[server_name]
        
        if server["type"] == "mounted":
            return await server["instance"].call_tool(tool_name, args)
        elif server["type"] == "remote":
            return await self._call_remote(server, tool_name, args)
```

### 2. File Structure (Minimal)

```
multiagent_core/
├── mcp/
│   ├── connector.py         # 200 lines - core connector
│   ├── environment.py       # 100 lines - env switching
│   ├── registry.py          # 150 lines - registry client
│   └── servers/             # Small servers
│       ├── signalhire_server.py    (5 tools)
│       ├── github_server.py        (8 tools)
│       └── local_utils_server.py   (10 tools)
└── config/
    └── mcp_config.json      # Environment configs
```

**Total**: ~500 lines for complete system

### 3. Usage Example

```python
# main.py - Works in dev and prod!

# Auto-detect environment
env = os.getenv("MCP_ENV", "local")
connector = MCPConnector(environment=env)

# Load configuration
await connector.load_from_config("config/mcp_config.json")

# Call tools - same API regardless of transport
result = await connector.call_tool(
    server="signalhire",
    tool="search_candidates",
    args={"query": "Python developer"}
)
```

---

## Best Practices

### ✅ DO

1. **Keep servers small** (5-15 tools max)
2. **Use mounting for composition**
3. **Limit tools with allowed_tools**
4. **Switch environments with config**
5. **Namespace tools by server**
6. **Test locally with stdio**
7. **Deploy to HTTP for production**

### ❌ DON'T

1. **Don't build giant servers** (>20 tools)
2. **Don't copy tools between servers**
3. **Don't expose all tools to all agents**
4. **Don't hardcode transport types**
5. **Don't skip tool limits**

---

## Migration Path

### From Monolithic to Connector

```python
# BEFORE: One giant server ❌
giant_server.py (200 tools)

# AFTER: Composed small servers ✅
connector = MCPConnector()
connector.mount(signalhire, prefix="sig")   # 5 tools
connector.mount(github, prefix="gh")        # 8 tools
connector.mount(database, prefix="db")      # 10 tools
# Total: 23 tools, but organized and maintainable!
```

---

## References

- **FastMCP Documentation**: https://gofastmcp.com
- **MCP Specification**: https://modelcontextprotocol.io
- **GitHub MCP Registry**: https://api.githubcopilot.com/mcp/
- **Anthropic MCP Guide**: https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector

---

**Key Takeaway**: Build the glue, not the tools. Keep servers small, mount them together, filter the tools.
