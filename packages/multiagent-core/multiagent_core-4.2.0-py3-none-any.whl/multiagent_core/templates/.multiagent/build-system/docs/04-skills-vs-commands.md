# Skills vs Slash Commands - Decision Guide

> When should you create a Skill vs a Slash Command? Use this guide to decide.

---

## Purpose

This document helps you decide when to create a Skill vs a Slash Command by understanding:
- Key differences between invocation patterns
- When to use each approach
- How they complement each other
- Decision tree for choosing

**Load this document when**: Deciding component type or creating decision-making agents

---

## Quick Decision Matrix

| If you want... | Use |
|:---------------|:----|
| User explicitly triggers it | **Slash Command** |
| Claude discovers it automatically | **Skill** |
| Simple, quick prompt shortcut | **Slash Command** |
| Complex capability with supporting files | **Skill** |
| Team workflow they invoke manually | **Slash Command** |
| Expert knowledge Claude applies when needed | **Skill** |

---

## Key Differences

| Aspect | Slash Commands | Agent Skills |
|:-------|:---------------|:-------------|
| **Invocation** | User-invoked (`/command`) | Model-invoked (automatic) |
| **Discovery** | Listed in `/help` | Discovered by context |
| **Trigger** | User types `/command` | Claude matches description |
| **Complexity** | Simple (single .md file) | Complex (directory + files) |
| **File Count** | One file only | Multiple files + resources |
| **Structure** | Flat markdown file | Directory with SKILL.md + supporting files |
| **Length** | Target 30-60 lines | No length limit |
| **Supporting Files** | No | Yes (scripts, templates, docs) |

---

## When to Use Slash Commands

### ✅ Use Slash Commands For:

**1. Explicit User Workflows**
```
User wants to manually trigger: "/deploy production"
User wants explicit control: "/review-pr 123"
User repeats frequently: "/commit"
```

**2. Quick Prompt Shortcuts**
- Short, focused instructions
- One file is enough
- No complex supporting resources

**3. Team-Standardized Processes**
```
/testing:test --quick
/deployment:deploy staging
/security:scan-secrets
```
- Team knows to run these commands
- Part of documented workflow
- Explicit steps in processes

**4. Sequential Workflows**
```
/supervisor:start 001    # Step 1: Setup
/supervisor:mid 001      # Step 2: Monitor
/supervisor:end 001      # Step 3: Complete
```
- User controls progression
- Each step explicit
- Order matters

---

## When to Use Skills

### ✅ Use Skills For:

**1. Automatic Expert Knowledge**
```yaml
name: PDF Processing
description: Extract text from PDF files. Use when working with PDF files.
```
- User: "Can you extract text from this PDF?"
- Claude automatically uses PDF Skill
- No explicit invocation needed

**2. Complex Capabilities with Resources**
```
skills/pdf-processor/
├── SKILL.md              # Main instructions
├── FORMS.md             # Form-filling guide
├── REFERENCE.md         # API reference
└── scripts/
    └── extract.py       # Extraction utility
```
- Multiple supporting files
- Scripts and utilities
- Reference documentation
- Progressive disclosure

**3. Context-Dependent Assistance**
```yaml
name: Git Commit Helper
description: Generate commit messages. Use when writing commits.
```
- User: "Help me write a commit message"
- Claude detects context and activates Skill
- Works automatically when appropriate

**4. Domain Expertise**
```yaml
name: Excel Data Analysis
description: Analyze Excel spreadsheets. Use when working with Excel files.
```
- User mentions "Excel" or "spreadsheet"
- Claude applies Skill automatically
- Rich instructions and examples available

---

## Comparison Examples

### Example 1: Code Review

**As Slash Command** (Explicit):
```markdown
# .claude/commands/review.md
---
description: Review code for security and performance
---
Review this code for security, performance, best practices.
```
Usage: `/review` (user explicitly triggers)

**As Skill** (Automatic):
```markdown
# .claude/skills/code-reviewer/SKILL.md
---
name: Code Reviewer
description: Review code for best practices. Use when reviewing code.
---
Includes: SECURITY.md, PERFORMANCE.md, STYLE.md checklists
```
Usage: "Can you review this code?" (automatic)

**Decision**:
- Simple review → **Command**
- Comprehensive review with checklists → **Skill**

---

### Example 2: Documentation

**As Slash Command**:
```markdown
# .claude/commands/docs-update.md
---
description: Update documentation after code changes
---
Update documentation in docs/ based on recent code changes.
```
Usage: `/docs-update`

**As Skill**:
```markdown
# .claude/skills/docs-writer/SKILL.md
---
name: Documentation Writer
description: Write technical documentation. Use when creating docs.
---
Includes: STYLE.md, TEMPLATES.md, EXAMPLES.md
```
Usage: "Can you document this API?"

**Decision**:
- Trigger doc update → **Command**
- Write documentation with style guide → **Skill**

---

## Decision Tree

```
Does user need explicit control?
├─ YES → Slash Command
└─ NO
    │
    Does it need supporting files (scripts, templates, multiple docs)?
    ├─ YES → Skill
    └─ NO
        │
        Should Claude discover it automatically?
        ├─ YES → Skill
        └─ NO → Slash Command
```

---

## Both Can Coexist

You can have both for the same functionality:

**Command** (`/git-commit`):
- Quick commit with provided message
- Explicit user control
- Fast workflow

**Skill** (commit-helper):
- Analyze changes and suggest message
- Automatic when user asks for help
- More comprehensive

Users choose based on their need at the time.

---

## Summary

|  | Slash Commands | Agent Skills |
|:--|:---------------|:-------------|
| **User says** | "I want to..." (explicit) | "Can you help me..." (implicit) |
| **Appears in** | `/help` menu | Discovered automatically |
| **Invoked by** | Typing `/command` | Claude matches context |
| **Best for** | Workflows & shortcuts | Expertise & capabilities |
| **Complexity** | Simple | Complex |
| **Files** | One | Multiple |

**Golden Rule**: If user must explicitly trigger it → Command. If Claude should discover it → Skill.

---

## See Also

- [Slash Commands Documentation](./01-claude-code-slash-commands.md)
- [Skills Documentation](./02-claude-code-skills.md)
- [Plugins Documentation](./03-claude-code-plugins.md)

---

**Purpose**: Decision guide for build system
**Load when**: Deciding between Skills and Commands
