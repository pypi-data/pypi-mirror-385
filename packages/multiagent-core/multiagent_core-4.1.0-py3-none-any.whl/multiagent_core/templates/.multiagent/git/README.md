# Git Automation Workflows

## Purpose

Git automation workflows for local development, including worktree management, branch operations, commit automation, and repository maintenance.

## What It Does

1. **Worktree Automation** - Create, manage, and cleanup git worktrees for parallel development
2. **Branch Operations** - Automated branch creation, switching, merging, and cleanup
3. **Commit Helpers** - Smart commit message generation and formatting assistance
4. **Repository Maintenance** - Automated cleanup, pruning, and health checks

## Agents Used

- **@claude/git-worktree-manager** - Manages worktree lifecycle (create, sync, cleanup)
- **@claude/git-commit-helper** - Generates standardized commit messages
- **@claude/git-branch-manager** - Handles branch operations and cleanup

## Commands

### `/git:worktree-create` - Create isolated worktree for parallel development
**Usage**: `/git:worktree-create <branch-name> [base-branch]`
**Example**: `/git:worktree-create feature-auth main`

Creates a new git worktree in an isolated directory, allowing parallel work on multiple branches. Automatically syncs with base branch and sets up proper isolation.

**Spawns**: git-worktree-manager agent
**Outputs**: New worktree directory at `../{branch-name}/`

---

### `/git:worktree-cleanup` - Remove worktree and cleanup branches
**Usage**: `/git:worktree-cleanup <branch-name>`
**Example**: `/git:worktree-cleanup feature-auth`

Safely removes a worktree, cleans up local and remote branches, and prunes references.

**Spawns**: git-worktree-manager agent
**Outputs**: Cleanup report showing removed files and branches

---

### `/git:commit-smart` - Generate standardized commit message
**Usage**: `/git:commit-smart [--type=feat|fix|refactor|docs]`
**Example**: `/git:commit-smart --type=feat`

Analyzes staged changes and generates a properly formatted commit message following project conventions, including co-author tags.

**Spawns**: git-commit-helper agent
**Outputs**: Formatted commit message with `[WORKING]` prefix

---

### `/git:branch-cleanup` - Cleanup merged and stale branches
**Usage**: `/git:branch-cleanup [--dry-run]`
**Example**: `/git:branch-cleanup --dry-run`

Identifies merged or stale branches and offers to remove them locally and remotely.

**Spawns**: git-branch-manager agent
**Outputs**: List of cleaned branches

---

## Architecture

```
User runs /git:{command}
      ↓
Command orchestrates:
1. Run script (git operations)
2. Invoke agent (intelligent analysis)
3. Generate from templates
4. Validate output
5. Display summary
```

## How It Works

1. **Command Invocation**: User runs `/git:{command}` with arguments
2. **Script Execution**: Mechanical git operations (status, list, inspect)
3. **Agent Analysis**: Intelligent agent analyzes git state and makes decisions
4. **Template Generation**: Agent uses templates for commit messages, configs
5. **Output Validation**: System validates git operations succeeded
6. **User Feedback**: Display summary of what was created/modified

## Directory Structure

```
.multiagent/git/
├── README.md              # This file
├── docs/                  # Conceptual documentation
│   ├── worktree-workflow.md
│   ├── commit-standards.md
│   └── branch-strategies.md
├── templates/             # Generation templates
│   ├── commits/          # Commit message templates
│   └── configs/          # Git config templates
├── scripts/               # Mechanical operations only
│   ├── worktree-list.sh
│   ├── branch-status.sh
│   └── cleanup-refs.sh
└── memory/               # Agent state storage (optional)
```

## Templates

Templates in this subsystem:

- `templates/commits/commit-message.template.txt` - Standardized commit message format
- `templates/commits/pr-description.template.md` - Pull request description template
- `templates/configs/worktree-config.template.sh` - Worktree environment setup

## Scripts

Mechanical scripts in this subsystem:

- `scripts/worktree-list.sh` - Lists all active worktrees
- `scripts/branch-status.sh` - Checks branch merge status
- `scripts/cleanup-refs.sh` - Removes stale git references

## Outputs

This subsystem generates:

```
../{worktree-name}/        # Isolated worktree directory
  ├── .git (file)          # Worktree git link
  └── {project-files}      # Full project copy

.git/worktrees/            # Worktree metadata
  └── {worktree-name}/

commit-message.txt         # Generated commit message
cleanup-report.txt         # Branch cleanup report
```

## Usage Example

```bash
# Step 1: Create worktree for new feature
/git:worktree-create feature-payment main

# Step 2: Work in worktree (cd ../feature-payment)
# Make changes, stage files

# Step 3: Generate smart commit message
/git:commit-smart --type=feat

# Step 4: After feature complete, cleanup worktree
/git:worktree-cleanup feature-payment

# Result: Feature developed in isolation, branches cleaned up
```

## Troubleshooting

### Worktree already exists
**Problem**: Trying to create worktree but directory already exists
**Solution**:
```bash
# List existing worktrees
git worktree list

# Remove the conflicting worktree
/git:worktree-cleanup <branch-name>
```

### Cannot remove worktree (uncommitted changes)
**Problem**: Worktree has uncommitted changes preventing cleanup
**Solution**:
```bash
# Commit or stash changes first
cd ../<worktree-name>
git stash
cd -

# Then cleanup
/git:worktree-cleanup <branch-name>
```

### Branch not fully merged
**Problem**: Branch cleanup refuses to delete unmerged branch
**Solution**:
```bash
# Check branch status
git branch -v

# Force delete if intentional
git branch -D <branch-name>

# Or merge the branch first
git checkout main
git merge <branch-name>
```

## Related Subsystems

- **supervisor**: Coordinates multi-agent work using git worktrees
- **github**: Integrates git operations with GitHub (PRs, issues)
- **deployment**: Uses git tags and branches for deployment tracking

## Future Enhancements

Planned features for this subsystem:

- [ ] Automated conflict resolution suggestions
- [ ] Git hook generation and management
- [ ] Commit message linting and validation
- [ ] Branch naming convention enforcement
- [ ] Automated changelog generation from commits
- [ ] Interactive rebase assistance
- [ ] Stash management helper
- [ ] Submodule management automation
