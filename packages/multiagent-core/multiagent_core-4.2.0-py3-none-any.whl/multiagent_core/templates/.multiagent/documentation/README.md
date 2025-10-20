# Documentation Management System

**Universal documentation system with layered orchestration - keeps docs synced automatically.**

---

## Core Principle

**UPDATE, DON'T CREATE** - Maintain 2-3 core docs instead of spawning dozens of stale files.

---

## Standard Structure

```
docs/
├── README.md              # Project overview
├── architecture/
│   └── overview.md        # System design
└── DESIGN_SYSTEM.md       # Frontend only (conditional)
```

---

## How It Works

### 1. First-Time Setup

```bash
/docs:init
```

- Reads `.speckit/001-*/spec.md` as source of truth
- Generates `docs/README.md` from spec
- Generates `docs/architecture/overview.md` from spec
- If frontend: Copies `DESIGN_SYSTEM.md` from templates

### 2. Ongoing Maintenance - Layered Orchestration ⭐

```bash
/docs:sync
```

**Three phases with approval gates:**

```
Phase 1: UPDATE
  └─ Loads comprehensive context (13 arch docs, PRs, git history)
  └─ Updates documentation
  └─ Report: docs/reports/docs/{date}/update-summary.md

  ⏸️  GATE 1: "Continue? (y/n)"

Phase 2: VALIDATE
  └─ Checks completeness, consistency, quality
  └─ Quality score: 0-100
  └─ Report: docs/reports/docs/{date}/validation-report.md

  ⏸️  GATE 2: "Auto-fix issues? (y/n)"

Phase 3: FIX
  └─ Applies auto-fixes
  └─ ✅ All synced and validated
```

**Or skip gates:**
```bash
/docs:sync --auto  # CI/CD mode
```

### 3. Individual Commands (Granular Control)

```bash
/docs:update      # Just update (1-2 min)
/docs:validate    # Just validate (30 sec)
/docs:init        # First-time setup
```

---

## Documentation Subsystem Ownership

**The docs subsystem owns:**

1. **Architecture Documentation**
   - All files in `docs/architecture/` (01-05 in consolidated structure)
   - Architecture consolidation and reorganization
   - Cross-reference management via `docs-config.json`

2. **Project Documentation**
   - Main `README.md` (project root)
   - `docs/README.md` (documentation index)
   - All subsystem READMEs (23 subsystems in `.multiagent/*/README.md`)

3. **Reference System**
   - `.multiagent/docs-config.json` (central mappings)
   - `.multiagent/scripts/resolve-doc-reference.sh`
   - `.multiagent/scripts/validate-doc-references.sh`

4. **Standard Workflow**
   - Test → Document → Validate → Commit
   - Automated consolidation
   - Reference updates
   - Quality validation

---

## Commands

### ⭐ Primary Commands

**`/docs:sync [--auto] [--framework]`**
- Full workflow: update → validate → fix
- Default: Interactive with 2 approval gates
- `--auto`: Skip gates (CI/CD)
- `--framework`: Framework docs mode (multiagent-core)

**`/docs:consolidate [--execute] [--dry-run]`** ⭐ NEW
- Consolidate architecture documentation (e.g., 13 → 5 files)
- Intelligent refactoring (not concatenation)
- Automatic reference updates
- Quality validation
- Default: dry-run mode (show plan)
- `--execute`: Perform consolidation

### Individual Commands

**`/docs:update [--check-patterns] [--auto]`**
- Update docs from code changes
- Loads: All 13 architecture docs, PRs, worktrees, git history
- Duration: 1-2 minutes
- Output: `docs/reports/docs/{date}/update-summary.md`

**`/docs:validate [--strict] [--fix]`**
- Validate doc quality
- Quality score: 0-100
- Duration: 30 seconds
- Output: `docs/reports/docs/{date}/validation-report.md`

**`/docs:init [--project-type]`**
- First-time setup from spec
- Creates: README.md, architecture/overview.md
- Frontend: Adds DESIGN_SYSTEM.md

**`/docs:create <type>`**
- Create specific doc (use sparingly)

**`/docs <path>`**
- Load doc for review

---

## Command Reference

### `/docs:sync` - Orchestrator

| Property | Value |
|----------|-------|
| **Agent** | None (orchestrator - calls /docs:update, /docs:validate) |
| **Scripts** | None |
| **Templates** | None |
| **Outputs** | 3 reports: sync-orchestration.md, update-summary.md, validation-report.md |
| **Outcome** | Complete documentation workflow with approval gates |
| **Phases** | Update → Validate → Fix |
| **Duration** | 3-4 min (auto), 5-7 min (interactive) |

### `/docs:update` - Update from Code Changes

| Property | Value |
|----------|-------|
| **Agent** | docs-auto-updater |
| **Context Loaded** | All 13 architecture docs, PRs, worktrees, git history |
| **Outputs** | docs/reports/docs/{date}/update-summary.md |
| **Outcome** | Documentation synchronized with code |
| **Duration** | 1-2 minutes |

### `/docs:validate` - Quality Check

| Property | Value |
|----------|-------|
| **Agent** | docs-validate |
| **Context Loaded** | Current docs, architecture overview, git status |
| **Outputs** | docs/reports/docs/{date}/validation-report.md |
| **Outcome** | Quality score (0-100), categorized issues |
| **Duration** | 30 seconds |

### `/docs:init` - First-Time Setup

| Property | Value |
|----------|-------|
| **Agent** | docs-init |
| **Templates** | frontend/templates/DESIGN_SYSTEM.md (if frontend) |
| **Outputs** | docs/README.md, docs/architecture/overview.md |
| **Outcome** | Complete documentation structure from spec |

---

## Components

### Agents (in `~/.claude/agents/`)

| Agent | Purpose | Key Feature |
|-------|---------|-------------|
| `docs-init` | First-time setup | Reads spec, generates docs |
| `docs-auto-updater` | Update from changes | **Step 0**: Loads ALL 13 arch docs, PRs, git history |
| `docs-validate` | Quality validation | Quality score 0-100, categorized issues |

### Scripts (in `scripts/`)

| Script | Purpose | Called By |
|--------|---------|-----------|
| `detect-doc-drift.sh` | Detect code→docs drift | Post-commit hook |
| `detect-docs-sprawl.sh` | Detect misplaced docs | Post-commit hook |

### Reports (`docs/reports/docs/`)

**Structure:** `docs/reports/docs/{YYYY-MM-DD}/{operation}-{descriptor}.md`

**All reports include YAML frontmatter:**
```yaml
---
status: COMPLETED | IN_PROGRESS | FAILED
subsystem: docs
operation: sync
date: 2025-10-14
started: 2025-10-14T14:23:15Z
completed: 2025-10-14T14:28:42Z
duration: 5m 27s
quality_score: 95
---
```

**Benefits:**
- ✅ Git tracked (historical record)
- ✅ Timeline navigation: `ls docs/reports/docs/2025-10-14/`
- ✅ Searchable: `grep "status: IN_PROGRESS" docs/reports/`

---

## Workflows

### Day-to-Day Development

```bash
# Make code changes
vim src/config.py

# Commit
git commit -m "feat: add new config option"

# Sync everything
/docs:sync

# Review and push
git show
git push
```

### Granular Control

```bash
# Just update
/docs:update

# Just validate
/docs:validate

# Auto-fix if issues
/docs:validate --fix
```

### Before Release

```bash
# Full sync with strict validation
/docs:sync --validate

# Or manually
/docs:validate --strict
/docs:validate --fix
```

---

## Integration Points

**Depends on:**
- agents/ (post-commit hook)
- core/ (project setup calls /docs:init)

**Used by:**
- All subsystems (documentation is universal)
- testing/ (test docs)
- deployment/ (deployment docs)

**Integrates with:**
- Git hooks → detect drift
- /core:project-setup → calls /docs:init

---

## Design Principles

1. **Spec is Source of Truth** - Read spec first, generate from it
2. **Minimal by Default** - 2-3 docs, expand only if needed
3. **Update Over Create** - Always prefer updating
4. **Layered Orchestration** - Phase 1 → Phase 2 → Phase 3
5. **Comprehensive Context** - Agents see EVERYTHING (all arch docs, PRs, etc.)
6. **Approval Gates** - User control at critical points

---

## Agent Context Intelligence

**Every agent has Step 0: Load Required Context**

**docs-auto-updater loads:**
- ALL 13 architecture docs (complete system understanding)
- Open PRs (work by other agents)
- Worktrees (work in progress)
- Git history (last 30 commits)
- Current branch and status

**Why this matters:**
- ✅ Understands integration between 23 subsystems
- ✅ Sees layered orchestration pattern
- ✅ Recognizes PR work (doesn't interfere)
- ✅ Maintains consistency across all docs
- ❌ **Without context:** Falls off rails, generates wrong format

**This solves the "isolated context window problem" documented in:**
`docs/architecture/02-development-guide.md` → Agent Context Requirements

---

## Report Management

See: `docs/reports/README.md`

**Structure:** `docs/reports/{subsystem}/{YYYY-MM-DD}/{operation}-{descriptor}.md`

**Finding reports:**
```bash
# Today
ls docs/reports/*/$(date +%Y-%m-%d)/

# In progress
grep -r "status: IN_PROGRESS" docs/reports/

# All sync operations
find docs/reports -name "sync-*.md"
```

---

## Key Features

### Comprehensive Context Loading
Agents see the full system before making changes - all architecture docs, open PRs, work by other agents.

### Layered Orchestration
Phase 1 generates report → Phase 2 reads report → Phase 3 fixes issues. Clear audit trail.

### Approval Gates
User reviews changes at critical points (after update, before auto-fix). Can skip with `--auto`.

### Timeline-Centric Reports
All Oct 14 activity in one folder. Git-tracked for historical record.

### Universal Design
Works for ANY project type - landing pages to SaaS platforms.

---

## Roadmap

### Phase 1: Foundation ✅
- [x] Spec-aware `/docs:init`
- [x] Auto-detection scripts
- [x] Post-commit hook integration

### Phase 2: Layered Orchestration ✅ **COMPLETE**
- [x] `/docs:sync` orchestrator with approval gates
- [x] `/docs:update` with comprehensive context
- [x] `/docs:validate` with quality scoring
- [x] Agent Step 0 context loading
- [x] Timeline-centric report structure

### Phase 3: Intelligence 🔮
- [ ] Auto-detect when to create vs update
- [ ] Auto-consolidate redundant docs
- [ ] Suggest improvements based on code
- [ ] Multi-agent config sync

---

## Related Documentation

- **Layered Orchestration Pattern**: `docs/architecture/01-architecture-overview.md#layered-orchestration-pattern`
- **Agent Context Requirements**: `docs/architecture/02-development-guide.md`
- **Report Management**: `docs/reports/README.md`
- **Build Standards**: `docs/architecture/02-development-guide.md`

---

**Philosophy:** The spec is the blueprint, docs are the map. Keep them in sync with layered orchestration.

**Last Updated:** 2025-10-14
**Version:** 2.0 (Layered Orchestration)
