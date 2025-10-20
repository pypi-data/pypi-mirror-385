# Claude Code Agent Skills - Reference Documentation

> Official reference for building Agent Skills in Claude Code. Use this when creating skill templates and builders.

**Reference Link**: https://docs.claude.com/en/docs/claude-code/skills

---

## Purpose

This document provides comprehensive reference for:
- Building Agent Skill templates
- Understanding SKILL.md structure and frontmatter
- Using progressive disclosure with supporting files
- Creating plugin Skills
- Deciding when to use Skills vs commands

**Load this document when**: Creating `/build:skill` templates or skill-builder agents

---

## Overview

Agent Skills are **model-invoked** capabilities that Claude discovers and uses automatically based on context. Unlike slash commands (user-invoked), Skills are chosen by Claude when they match the current task.

**Key Characteristics**:
- **Model-invoked**: Claude decides when to use them
- **Automatic discovery**: No explicit invocation needed
- **Context-dependent**: Activated based on task match
- **Rich resources**: Can include multiple files, scripts, templates
- **Progressive disclosure**: Claude loads only what's needed

---

## Skill Structure

### Required File: SKILL.md

Every Skill must have a `SKILL.md` file with frontmatter and content:

```markdown
---
name: Your Skill Name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
Provide clear, step-by-step guidance for Claude.

## Examples
Show concrete examples of using this Skill.
```

### Directory Structure

```
.claude/skills/my-skill/
├── SKILL.md           (required)
├── reference.md       (optional documentation)
├── examples.md        (optional examples)
├── scripts/
│   └── helper.py      (optional utility)
└── templates/
    └── template.txt   (optional template)
```

---

## Frontmatter Fields

### Required Fields

| Field | Purpose | Example |
|:------|:--------|:--------|
| `name` | Skill display name | `PDF Processing` |
| `description` | What Skill does + when to use | `Extract text from PDFs. Use when working with PDF files` |

### Optional Fields

| Field | Purpose | Example |
|:------|:--------|:--------|
| `allowed-tools` | Restrict tools when Skill active | `Read, Grep, Glob` |

**Note**: `allowed-tools` is only supported in Claude Code Skills.

---

## Critical: The Description Field

The `description` field is **CRITICAL** for Claude to discover when to use your Skill.

**Components of good description**:
1. **What it does** - Core capability
2. **When to use it** - Trigger keywords/contexts
3. **Specific terms** - Words users would mention

**Example - Vague ❌**:
```yaml
description: Helps with documents
```

**Example - Specific ✅**:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

---

## Full Documentation

See complete documentation at: https://docs.claude.com/en/docs/claude-code/skills

---

**Source**: Claude Code Official Documentation
**Purpose**: Reference for build system skill templates
**Load when**: Creating skill templates or `/build:skill`
