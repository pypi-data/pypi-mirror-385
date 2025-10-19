# MCP Documentation

**Last Updated:** 2025-10-10

---

## 📚 Available Guides

### [Complete Guide](complete-guide.md) - 1058 lines
**Full system documentation** covering:
- System architecture & key management
- Registry system
- Custom MCP server development
- Slash commands reference
- Local vs remote servers
- Multi-CLI support (Claude Code, VS Code, Gemini, Qwen, Codex)
- Troubleshooting

**Use when:** Setting up MCP from scratch, managing API keys, troubleshooting

---

### [Connector Pattern](connector-pattern.md) - 519 lines ⭐ NEW
**Pluggable architecture** for production MCP systems:
- Small server pattern (5-15 tools max)
- Mounting vs importing servers
- Local (stdio) vs Remote (HTTP) environments  
- Tool limiting strategies
- GitHub MCP Registry integration
- Agent-specific tool permissions

**Use when:** Building production MCP systems, composing multiple servers, preventing tool explosion

---

## 🚀 Quick Start

### For Development
```bash
# 1. Add connector pattern to your project
cp ~/.claude/docs/mcp/connector-pattern.md docs/

# 2. Start with small focused servers
multiagent_core/mcp/servers/
  ├── signalhire_server.py    (5 tools)
  ├── github_server.py        (8 tools)
  └── database_server.py      (10 tools)

# 3. Use local stdio for testing
export MCP_ENV=local
```

### For Production
```bash
# Use remote HTTP servers
export MCP_ENV=production

# Connect to registries
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

---

## 🎯 Key Concepts

### Small Servers (Connector Pattern)
✅ **DO:** 5-15 tools per server
❌ **DON'T:** 200 tools in one server

### Mounting (Connector Pattern)
```python
connector.mount(signalhire, prefix="sig")  # Live delegation
```

### Environment Switching
```json
{
  "signalhire": {
    "local": {"type": "stdio", "command": "python", ...},
    "production": {"type": "http", "url": "https://..."}
  }
}
```

---

## 📖 Documentation Map

```
MCP Docs/
├── README.md (you are here)
├── complete-guide.md
│   ├── System architecture
│   ├── Key management (~/.bashrc)
│   ├── Registry system
│   └── Troubleshooting
└── connector-pattern.md ⭐ NEW
    ├── Pluggable architecture
    ├── Small server pattern
    ├── Environment switching
    └── GitHub registry
```

---

## 🔗 External Resources

- **FastMCP Documentation**: https://gofastmcp.com
- **MCP Specification**: https://modelcontextprotocol.io  
- **GitHub MCP Registry**: https://api.githubcopilot.com/mcp/
- **Anthropic MCP Guide**: https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector

---

**Choose Your Path:**
- New to MCP? → Start with [Complete Guide](complete-guide.md)
- Building production system? → Read [Connector Pattern](connector-pattern.md)
- Both? → Read Complete Guide first, then Connector Pattern
