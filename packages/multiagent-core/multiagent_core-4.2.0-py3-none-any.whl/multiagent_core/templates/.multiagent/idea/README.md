# Idea System

## Purpose

Lightweight brainstorming system for capturing early-stage concepts before they become formal enhancement proposals.

## What It Does

1. **Quick Capture** - Create idea documents with minimal metadata (complexity, value, category)
2. **Browse & Filter** - List ideas by category, value, or complexity for review
3. **Promotion** - Convert promising ideas to formal enhancement proposals with full template

## Agents Used

- **@claude/general-purpose** - Expands lightweight ideas into formal enhancement templates during promotion

## Commands

### `/idea:create` - Create new lightweight idea document
**Usage**: `/idea:create "Title here"`
**Example**: `/idea:create "Add Redis caching layer"`

Creates a minimal idea document in `docs/ideas/` with basic metadata (complexity, value, category). Ideas are flat - no status folders or formal tracking until promoted.

**Spawns**: None (bash-only operation)
**Outputs**: `docs/ideas/{slug}.md`

---

### `/idea:list` - List all ideas with filtering
**Usage**: `/idea:list [--category=<category>] [--value=<value>]`
**Example**: `/idea:list --value=high`

Displays all ideas grouped by category with metadata. Supports filtering by category (feature, improvement, infrastructure, integration) or value (low, medium, high).

**Spawns**: None (bash-only operation)
**Outputs**: Formatted list to console

---

### `/idea:promote` - Convert idea to formal enhancement
**Usage**: `/idea:promote <slug>`
**Example**: `/idea:promote redis-caching-layer`

Prompts for area selection, then invokes agent to expand lightweight idea into full enhancement template. Original idea moved to `.archive/`.

**Spawns**: general-purpose agent
**Outputs**:
- `docs/enhancements/01-proposed/{date}/{area}-{slug}.md`
- `docs/ideas/.archive/{slug}.md`

---

## Architecture

```
User runs /idea:create "Title"
      ↓
Command orchestrates:
1. Generate slug from title
2. Prompt for metadata (complexity, value, category)
3. Create idea file in docs/ideas/
4. Display summary

User runs /idea:list
      ↓
Command orchestrates:
1. Scan docs/ideas/ for all *.md files
2. Extract metadata from each file
3. Apply filters if specified
4. Group by category and display

User runs /idea:promote <slug>
      ↓
Command orchestrates:
1. Locate idea file
2. Prompt for area selection
3. Invoke agent to expand → enhancement
4. Move idea to .archive/
5. Display next steps
```

## How It Works

1. **Command Invocation**: User runs `/idea:create "Title"`
2. **Metadata Collection**: Command prompts for complexity, value, category
3. **File Creation**: Bash creates minimal markdown file in `docs/ideas/`
4. **User Feedback**: Display location and next steps

**Promotion Flow:**
1. User runs `/idea:promote <slug>` when idea is mature
2. System prompts for area (core, backend, frontend, etc.)
3. Agent reads lightweight idea and expands to full enhancement template
4. Enhancement created in `docs/enhancements/01-proposed/{date}/`
5. Original idea archived to `docs/ideas/.archive/`

## Directory Structure

```
.multiagent/idea/
├── README.md              # This file
├── docs/                  # Conceptual documentation
├── templates/             # Idea template
│   └── idea.md.template  # Lightweight idea format
├── scripts/               # Validation scripts
│   └── validate-idea.sh  # Validates idea file structure
└── memory/               # (Not used - ideas are stateless)
```

## Templates

Templates in this subsystem:

- `templates/idea.md.template` - Lightweight idea document format with minimal metadata

## Scripts

Mechanical scripts in this subsystem:

- `scripts/validate-idea.sh` - Validates idea file has required sections and proper metadata

## Outputs

This subsystem generates:

```
docs/ideas/
├── {idea-slug}.md         # Active ideas
├── {another-slug}.md
└── .archive/              # Promoted ideas
    └── {archived}.md
```

When promoted, creates:
```
docs/enhancements/01-proposed/
└── {date}/
    └── {area}-{slug}.md   # Full enhancement template
```

## Usage Example

```bash
# Step 1: Capture initial thought
/idea:create "Add Redis caching layer"
# Prompts for: complexity (medium), value (high), category (feature)
# Creates: docs/ideas/redis-caching-layer.md

# Step 2: Add more ideas
/idea:create "Extract database utilities"
/idea:create "Modernize callbacks to async/await"

# Step 3: Review high-value ideas
/idea:list --value=high

# Step 4: When ready, promote to enhancement
/idea:promote redis-caching-layer
# Prompts for: area (backend)
# Agent expands to full template
# Creates: docs/enhancements/01-proposed/2025-10-18/backend-redis-caching-layer.md
# Archives: docs/ideas/.archive/redis-caching-layer.md

# Step 5: Continue enhancement workflow
# Manual: mv to 02-approved/ when reviewed
# /enhancement:spec 007 --from-enhancement backend-redis-caching-layer
```

## Troubleshooting

### Idea file validation fails
**Problem**: Idea file missing required sections or metadata
**Solution**:
```bash
# Validate idea structure
~/.multiagent/idea/scripts/validate-idea.sh docs/ideas/{slug}.md

# Check for required sections: Problem, Proposed Solution, Rough Notes
# Check for metadata: Created, Complexity, Value, Category
```

### Promotion fails - template not found
**Problem**: Enhancement template missing during promotion
**Solution**:
```bash
# Verify template exists
ls -la multiagent_core/templates/.multiagent/enhancement/templates/enhancement.md.template

# Template should exist - if not, rebuild enhancement subsystem
```

### Ideas directory doesn't exist
**Problem**: First-time use, directory not created
**Solution**:
```bash
# Directory is created automatically on first /idea:create
# If needed manually:
mkdir -p docs/ideas/.archive
```

## Related Subsystems

- **enhancement**: Ideas get promoted to enhancement proposals when mature
- **refactoring**: Similar lightweight capture, but for post-implementation cleanup
- **documentation**: Ideas may reference or generate documentation needs

## Future Enhancements

Planned features for this subsystem:

- [ ] `/idea:merge` - Combine related ideas into single enhancement
- [ ] `/idea:tag` - Add custom tags beyond complexity/value/category
- [ ] `/idea:search` - Full-text search across all ideas
- [ ] Automatic expiration: Archive old ideas after N months
- [ ] Idea voting/ranking system for teams
