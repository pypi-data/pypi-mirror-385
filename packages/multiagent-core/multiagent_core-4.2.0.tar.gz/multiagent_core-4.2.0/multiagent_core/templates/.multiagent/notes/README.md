# Notes

## Purpose

Lightweight local tracking system for development observations, TODOs, bugs, questions, and notes with future GitHub integration

## What It Does

1. **Quick Capture** - Zero-friction note creation with `/note "thing I noticed"`
2. **Smart Organization** - Auto-categorizes as bug, todo, observation, question, idea, or refactor
3. **Persistent Tracking** - Stores all notes in `notes.md` markdown file in project root
4. **Flexible Filtering** - List and filter notes by type, priority, file, or status
5. **GitHub Integration** - (Future) Import GitHub Issues as local notes

## Agents Used

- **note-tracker** - Manages local notes database, creates/lists/closes notes in notes.md
- **note-analyzer** - (Future) Analyzes patterns in notes, suggests priorities and groupings

## Commands

### `/note` - Quick capture note

**Usage**: `/note "description" [--type=TYPE] [--priority=PRIORITY] [--file=PATH]`

**Examples**:
```bash
# Simplest - just capture it
/note "Login form doesn't validate email properly"

# With type (bug, todo, observation, question, idea, refactor)
/note --type=bug "API returns 500 on empty request body"
/note --type=todo "Refactor auth middleware"
/note --type=observation "Memory usage seems high after 1000 requests"

# With priority (p1, p2, p3)
/note --priority=p1 "Production deployment failing"

# With file context
/note --file=src/auth.ts "Line 45 needs null check"
```

Zero-friction note creation. If no type specified, defaults to "note". Appends to `notes.md` with timestamp, auto-incrementing ID, and status.

**Spawns**: note-tracker agent
**Outputs**: Appends to `notes.md` in project root

---

### `/note:list` - List and filter notes

**Usage**: `/note:list [--type=TYPE] [--priority=PRIORITY] [--status=STATUS] [--file=PATH]`

**Examples**:
```bash
# Show all open notes
/note:list

# Filter by type
/note:list --type=bug
/note:list --type=todo

# Filter by priority
/note:list --priority=p1

# Filter by file
/note:list --file=src/auth.ts

# Filter by status
/note:list --status=open
/note:list --status=closed
```

Lists notes from `notes.md` with filtering options. Displays in readable table format.

**Spawns**: note-tracker agent
**Outputs**: Formatted list to stdout

---

### `/note:close` - Close/resolve notes

**Usage**: `/note:close <ID> [--reason="REASON"]`

**Examples**:
```bash
# Close specific note
/note:close 5

# Close with reason
/note:close 5 --reason="Fixed in commit abc123"

# Close all notes of a type
/note:close --type=bug --reason="All bugs resolved in sprint"
```

Marks notes as closed in `notes.md`. Adds timestamp and optional reason.

**Spawns**: note-tracker agent
**Outputs**: Updates `notes.md` with closed status

---

### `/note:import` - Import from GitHub Issues (Future)

**Usage**: `/note:import <ISSUE_NUMBER>`

**Example**:
```bash
# Import GitHub Issue #123 as local note
/note:import 123
```

(Future feature) Imports GitHub Issue as local note in `notes.md`. Preserves labels, priority, assignee.

**Spawns**: note-tracker agent
**Outputs**: Appends to `notes.md`

---

## Architecture

```
User runs /note "description"
      ↓
Command orchestrates:
1. Parse arguments (type, priority, file, description)
2. Invoke note-tracker agent
3. Read existing notes.md (if exists)
4. Generate new note entry from template
5. Append to notes.md with auto-incrementing ID
6. Display confirmation
```

## How It Works

1. **Command Invocation**: User runs `/note "description"` with optional flags
2. **Agent Processing**: note-tracker agent reads `notes.md`, determines next ID
3. **Template Generation**: Agent fills note-entry template with data
4. **File Update**: Agent appends new note to `notes.md`
5. **Confirmation**: System displays note ID and details

## Directory Structure

```
.multiagent/notes/
├── README.md              # This file
├── docs/                  # Notes workflow documentation
├── templates/             # Note templates
│   ├── notes.md.template              # Initial notes.md structure
│   ├── note-entry.template.md         # Single note entry format
│   └── notes-summary.md.template      # Summary report format
├── scripts/               # Note management utilities
│   ├── scan-code-notes.sh     # Find TODO/FIXME/BUG comments in code
│   ├── list-notes.sh          # Query notes.md with filters
│   └── validate-note.sh       # Ensure note has required fields
└── memory/               # (Not used for notes subsystem)
```

## Templates

Templates in this subsystem:

- `templates/notes.md.template` - Initial structure for notes.md file
- `templates/note-entry.template.md` - Format for individual note entries
- `templates/notes-summary.md.template` - Summary report of all notes

## Scripts

Mechanical scripts in this subsystem:

- `scripts/scan-code-notes.sh` - Scans codebase for TODO/FIXME/BUG/NOTE comments
- `scripts/list-notes.sh` - Queries notes.md with filters (type, priority, status)
- `scripts/validate-note.sh` - Validates note has required fields (ID, date, description)

## Outputs

This subsystem generates:

```
project-root/
└── notes.md              # Persistent notes file (markdown)
```

## Notes File Format

The `notes.md` file uses this structure:

```markdown
# Development Notes

Last updated: 2025-10-18

## Open Notes (5)

### #1 - [BUG] [P1] Login form validation
**Created:** 2025-10-18 14:23:45
**File:** src/auth.ts
**Status:** open
**Description:** Login form doesn't validate email properly

---

### #2 - [TODO] [P2] Refactor auth middleware
**Created:** 2025-10-18 14:25:12
**Status:** open
**Description:** Auth middleware should use new JWT library

---

## Closed Notes (3)

### #3 - [BUG] [P1] API 500 error
**Created:** 2025-10-17 09:15:33
**Closed:** 2025-10-18 10:30:22
**Reason:** Fixed in commit abc123
**Status:** closed
**Description:** API returns 500 on empty request body

---
```

## Usage Example

```bash
# Step 1: Create some notes during development
/note "Login form doesn't validate email properly" --type=bug --priority=p1 --file=src/auth.ts
/note "Refactor auth middleware" --type=todo
/note "Memory usage seems high after 1000 requests" --type=observation

# Step 2: List all open notes
/note:list

# Step 3: List only bugs
/note:list --type=bug

# Step 4: Close a note when fixed
/note:close 1 --reason="Fixed in commit abc123"

# Step 5: View all notes (including closed)
/note:list --status=all

# Step 6: Scan code for inline TODO comments
.multiagent/notes/scripts/scan-code-notes.sh
```

## Note Types

- **bug** - Something broken that needs fixing
- **todo** - Task to complete
- **observation** - Something noticed (performance, pattern, etc.)
- **question** - Something that needs clarification
- **idea** - Feature or improvement to consider
- **refactor** - Code quality improvement needed

## Priority Levels

- **p1** - Critical/urgent (blocks work, production issue)
- **p2** - Important (should fix soon)
- **p3** - Nice to have (low priority)

## Troubleshooting

### Notes not showing in list
**Problem**: Created note but `/note:list` doesn't show it
**Solution**:
```bash
# Verify notes.md exists and is not empty
cat notes.md

# Check file format matches template
.multiagent/notes/scripts/validate-note.sh
```

### Duplicate note IDs
**Problem**: Multiple notes with same ID
**Solution**:
```bash
# The note-tracker agent auto-increments IDs
# If you manually edited notes.md and created duplicates:
# 1. Backup notes.md
cp notes.md notes.md.backup

# 2. Let agent rebuild IDs
/note:list --rebuild-ids
```

### Can't close note
**Problem**: Note won't close with `/note:close`
**Solution**:
```bash
# Verify note ID exists
/note:list | grep "#5"

# Try with explicit ID
/note:close 5
```

## Related Subsystems

- **testing**: Link bugs to failing tests
- **github**: Future integration with GitHub Issues
- **supervisor**: Include notes in compliance reports
- **documentation**: Reference notes in docs/bugs/

## Future Enhancements

Planned features for this subsystem:

- [ ] Auto-scan code for TODO/FIXME comments and create notes
- [ ] Import GitHub Issues as local notes
- [ ] Export notes to GitHub Issues
- [ ] Link notes to commits (git hooks)
- [ ] Generate weekly notes summary report
- [ ] Search notes by keyword/description
- [ ] Assign notes to team members
- [ ] Note templates for common issue types
- [ ] Integration with `/testing:test` to link bugs to tests
- [ ] Auto-close notes when related commits pushed
