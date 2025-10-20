# Dynamic Documentation Reference System

**Problem Solved**: Avoid manual updates to 21 subsystems, 58 agents, and 101+ commands every time architecture docs change.

**Solution**: Configuration-based documentation references with automatic resolution.

---

## The Problem

When we consolidated 13 architecture files → 5 files:
- ❌ Had to manually update 20+ files with new paths
- ❌ Had to update section anchors (#build-order → #dependencies--build-order)
- ❌ Broke references if we missed any files
- ❌ Will break again on next reorganization

**This doesn't scale.**

---

## The Solution: Three-Tier System

### 1. Central Configuration (`.multiagent/docs-config.json`)

Single source of truth for all documentation paths:

```json
{
  "sections": {
    "build_standards": {
      "file": "docs/architecture/02-development-guide.md",
      "section": "coding-standards",
      "alias": "ARCH_BUILD_STANDARDS",
      "description": "Command, agent, script, template standards"
    }
  }
}
```

### 2. Placeholder References (In Code/Docs)

Use aliases instead of hardcoded paths:

```markdown
❌ OLD (hardcoded):
See [Build Standards](docs/architecture/07-build-standards.md)

✅ NEW (alias):
See {{ARCH_BUILD_STANDARDS}} for coding standards

✅ AGENT CONTEXT (alias):
@{{ARCH_OVERVIEW}} - Load architecture context
```

### 3. Resolution Scripts

Scripts resolve aliases → actual paths:

```bash
# Resolve alias to path
./multiagent/scripts/resolve-doc-reference.sh ARCH_BUILD_STANDARDS
# → docs/architecture/02-development-guide.md#coding-standards

# Validate all references
./.multiagent/scripts/validate-doc-references.sh
# → Scans all subsystems/agents/commands for broken links
```

---

## Usage Examples

### In Subsystem READMEs

```markdown
## Related Documentation

- {{ARCH_ORCHESTRATION}} - Parallel agent spawning pattern
- {{ARCH_BUILD_ORDER}} - Subsystem dependencies
- {{GUIDE_WORKTREE}} - Git worktree setup
```

Resolves to:

```markdown
## Related Documentation

- [Layered Orchestration](docs/architecture/01-architecture-overview.md#layered-orchestration-pattern) - Parallel agent spawning pattern
- [Build Order](docs/architecture/02-development-guide.md#dependencies--build-order) - Subsystem dependencies
- [Worktree Setup](.multiagent/iterate/docs/git-worktree-setup.md) - Git worktree setup
```

### In Agent Prompts

```markdown
## Your Required Process

### Step 0: Load Context

**Read architecture documentation:**

@{{ARCH_OVERVIEW}}
@{{ARCH_BUILD_STANDARDS}}

These provide essential framework knowledge.
```

Resolves to:

```markdown
### Step 0: Load Context

**Read architecture documentation:**

@docs/architecture/01-architecture-overview.md
@docs/architecture/02-development-guide.md#coding-standards

These provide essential framework knowledge.
```

### In Slash Commands

```markdown
---
description: Build new subsystem following framework standards
---

This command builds a complete subsystem structure.

Standards are defined in {{ARCH_BUILD_STANDARDS}}.

For subsystem dependencies, see {{ARCH_BUILD_ORDER}}.
```

---

## Available Aliases

### Architecture Documents

| Alias | Resolves To | Description |
|-------|-------------|-------------|
| `{{ARCH_OVERVIEW}}` | `docs/architecture/01-architecture-overview.md` | Complete system architecture |
| `{{ARCH_DEV_GUIDE}}` | `docs/architecture/02-development-guide.md` | Build standards & dependencies |
| `{{ARCH_SETUP}}` | `docs/architecture/03-system-setup.md` | Installation & configuration |
| `{{ARCH_OPS}}` | `docs/architecture/04-operations-reference.md` | Commands & troubleshooting |
| `{{ARCH_QUICKSTART}}` | `docs/architecture/05-quick-start.md` | 5-minute onboarding |

### Architecture Sections

| Alias | Resolves To | Description |
|-------|-------------|-------------|
| `{{ARCH_ORCHESTRATION}}` | `01-architecture-overview.md#layered-orchestration-pattern` | Parallel agent spawning |
| `{{ARCH_BUILD_ORDER}}` | `02-development-guide.md#dependencies--build-order` | Subsystem build sequence |
| `{{ARCH_BUILD_STANDARDS}}` | `02-development-guide.md#coding-standards` | Coding standards |
| `{{ARCH_WORKFLOWS}}` | `01-architecture-overview.md#integration-workflows` | Cross-subsystem patterns |
| `{{ARCH_TEMPLATES}}` | `03-system-setup.md#template-management-system` | Template swapping |
| `{{ARCH_MCP}}` | `04-operations-reference.md#mcp-registry-management` | MCP management |
| `{{ARCH_PROJECT_TYPES}}` | `04-operations-reference.md#project-type-system` | Project type scaling |
| `{{ARCH_LIFECYCLE}}` | `04-operations-reference.md#subsystem-lifecycle` | Add/update/delete subsystems |
| `{{ARCH_CMD_PATTERNS}}` | `04-operations-reference.md#command-flag-patterns` | Flag consistency |

### Guides

| Alias | Resolves To | Description |
|-------|-------------|-------------|
| `{{GUIDE_AGENT_WORKFLOW}}` | `.multiagent/agents/docs/workflow.md` | Agent coordination |
| `{{GUIDE_WORKTREE}}` | `.multiagent/iterate/docs/git-worktree-setup.md` | Git worktree setup |
| `{{GUIDE_TESTING}}` | `.multiagent/testing/docs/testing-flow.md` | Testing strategy |

---

## When Architecture Changes

### Before (Manual Hell) ❌

```bash
# Consolidate 13 → 5 files
# Manually update:
- docs/README.md
- README.md
- 21 subsystem READMEs
- 58 agent prompts
- 101+ slash commands
- All cross-references
# Total: ~200+ manual edits
```

### After (Config Update) ✅

```bash
# Consolidate 13 → 5 files

# 1. Update ONLY the config file
vim .multiagent/docs-config.json
# Change: "file": "docs/architecture/08-build-order.md"
# To:     "file": "docs/architecture/02-development-guide.md"
#         "section": "dependencies--build-order"

# 2. Validate all references still work
./.multiagent/scripts/validate-doc-references.sh

# 3. Done! All aliases resolve to new locations
```

**Result**: 1 file updated instead of 200+

---

## Build Standards Update

### New Rule: ALWAYS Use Aliases

**In subsystem READMEs:**
```markdown
✅ DO: See {{ARCH_BUILD_STANDARDS}}
❌ DON'T: See docs/architecture/02-development-guide.md
```

**In agent prompts:**
```markdown
✅ DO: @{{ARCH_OVERVIEW}}
❌ DON'T: @docs/architecture/01-architecture-overview.md
```

**In slash commands:**
```markdown
✅ DO: Standards: {{ARCH_BUILD_STANDARDS}}
❌ DON'T: Standards: docs/architecture/02-development-guide.md
```

### Enforcement

**Pre-commit validation:**
```bash
# Add to .git/hooks/pre-commit
./.multiagent/scripts/validate-doc-references.sh
```

**Build standards check:**
```bash
# Subsystem compliance validator checks for hardcoded paths
/testing:subsystem <subsystem-name> --structure
```

---

## Adding New Documentation

### Step 1: Add to Config

```json
{
  "sections": {
    "new_feature": {
      "file": "docs/architecture/02-development-guide.md",
      "section": "new-feature-section",
      "alias": "ARCH_NEW_FEATURE",
      "description": "New feature documentation"
    }
  }
}
```

### Step 2: Use Alias Everywhere

```markdown
See {{ARCH_NEW_FEATURE}} for details.
```

### Step 3: Validate

```bash
./.multiagent/scripts/validate-doc-references.sh
```

---

## Migration Strategy

### For New Code

✅ **Required**: Use aliases from day 1

### For Existing Code

**Phase 1: Critical Files** (Already done in consolidation)
- docs/README.md
- Main README.md
- 2 subsystem READMEs (documentation, iterate)

**Phase 2: Incremental Migration** (As needed)
- Update subsystems when they're modified
- Update agents when they're rebuilt
- Update commands when they're enhanced

**Phase 3: Bulk Migration** (Future)
- Run automated script to replace all hardcoded paths
- Validate with `validate-doc-references.sh`

---

## Benefits

1. **Single Update Point**: Change config, not 200 files
2. **Validation**: Automated checking for broken links
3. **Consistency**: All references use same format
4. **Future-Proof**: Easy to reorganize docs anytime
5. **Self-Documenting**: Aliases describe what they link to
6. **Type Safety**: Validation catches typos immediately

---

## Related Files

- **Config**: `.multiagent/docs-config.json` - Central mappings
- **Resolver**: `.multiagent/scripts/resolve-doc-reference.sh` - Alias → path
- **Validator**: `.multiagent/scripts/validate-doc-references.sh` - Check all refs
- **Standards**: `docs/architecture/02-development-guide.md` - Build standards

---

## Future Enhancements

### Auto-Resolution in Markdown

```bash
# Pre-process markdown files to resolve aliases
./.multiagent/scripts/resolve-all-placeholders.sh README.md
```

### IDE Integration

```json
// .vscode/settings.json
{
  "markdownLinks.resolveAliases": true,
  "markdownLinks.configFile": ".multiagent/docs-config.json"
}
```

### Git Hook Integration

```bash
# Pre-commit: Validate references
# Post-merge: Re-validate references
```

---

**Last Updated**: 2025-10-17
**Version**: 1.0.0
**Status**: ✅ ACTIVE
