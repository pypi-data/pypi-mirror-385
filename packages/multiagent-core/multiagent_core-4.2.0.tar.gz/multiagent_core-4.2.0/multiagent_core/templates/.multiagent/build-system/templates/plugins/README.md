# Plugin Templates

This directory contains templates for creating Claude Code plugins.

## Files

- `plugin.json.template` - Plugin manifest template
- `example-plugin/` - Complete working example plugin

## Template Variables

| Variable | Purpose | Example |
|:---------|:--------|:--------|
| `{{PLUGIN_NAME}}` | Unique identifier (kebab-case) | `deployment-tools` |
| `{{VERSION}}` | Semantic version | `1.0.0` |
| `{{DESCRIPTION}}` | Plugin purpose | `Deployment automation` |
| `{{AUTHOR_NAME}}` | Author name | `Dev Team` |
| `{{AUTHOR_EMAIL}}` | Author email | `dev@company.com` |
| `{{HOMEPAGE_URL}}` | Documentation URL | `https://docs.example.com` |
| `{{REPOSITORY_URL}}` | Source code URL | `https://github.com/org/plugin` |
| `{{LICENSE}}` | License identifier | `MIT`, `Apache-2.0` |
| `{{KEYWORDS}}` | Discovery tags (array) | `["deployment", "ci-cd"]` |

## Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Required manifest
├── commands/                 # Optional slash commands
│   └── deploy.md
├── skills/                   # Optional Agent Skills
│   └── deployment-helper/
│       └── SKILL.md
├── hooks/                    # Optional event hooks
│   └── hooks.json
└── README.md                # Plugin documentation
```

**Critical**: Directories at plugin root, NOT inside `.claude-plugin/`

## Usage

### Creating from Template

```bash
# Create plugin structure
mkdir -p my-plugin/.claude-plugin

# Copy and fill manifest
cp plugin.json.template my-plugin/.claude-plugin/plugin.json
# Edit plugin.json and replace {{VARIABLES}}

# Add components
mkdir my-plugin/commands
mkdir my-plugin/skills
```

### Using Build Command

```bash
# Let build system create it for you
/build:plugin my-plugin "Description" --components=cmd,skill
```

## Best Practices

1. **Use ${CLAUDE_PLUGIN_ROOT}**:
   - For all paths in hooks and MCP servers
   - Ensures portability across installations

2. **Semantic Versioning**:
   - Major: Breaking changes
   - Minor: New features (backwards-compatible)
   - Patch: Bug fixes

3. **Complete Metadata**:
   - Author, repository, license
   - Helps users understand plugin origin

4. **Test Locally**:
   - Use local marketplace for testing
   - Uninstall/reinstall to test updates

---

**Purpose**: Templates for creating plugins
**Used by**: plugin-builder agent
