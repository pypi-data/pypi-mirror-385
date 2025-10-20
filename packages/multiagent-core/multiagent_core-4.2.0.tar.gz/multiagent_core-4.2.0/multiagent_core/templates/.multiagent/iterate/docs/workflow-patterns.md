# Workflow Patterns

## Purpose

This document provides detailed workflow patterns for using the iterate subsystem's three-phase process (tasks → sync → adjust).

---

## The Three-Phase Workflow

### Overview

```
Spec Creation → Phase 1 → Phase 2 → Agent Work → Phase 3 (if needed)
     ↓            ↓          ↓           ↓              ↓
  /specify   /iterate:  /iterate:   Parallel     /iterate:
             tasks      sync        Implementation  adjust
```

---

## Phase 1: Task Layering (`/iterate:tasks`)

**Purpose**: Transform sequential tasks into non-blocking parallel structure.

### When to Use

- After creating new spec with `/specify`
- After planning tasks with `/plan`
- When task structure changes significantly

### Input

- `specs/{spec-num}/tasks.md` - Sequential task list

### Process

1. Read tasks.md
2. Analyze dependencies
3. Apply layering rules (Infrastructure First, Use Before Build)
4. Assign tasks to agents based on complexity
5. Create layered-tasks.md with numbered layers

### Output

- `specs/{spec-num}/agent-tasks/layered-tasks.md`

### Example Usage

```bash
# Single spec
/iterate:tasks 005

# Multiple specs
/iterate:tasks 005,007,009

# All specs in project
/iterate:tasks --all
```

### Success Criteria

✅ layered-tasks.md created
✅ Tasks organized into clear layers
✅ Agent assignments match complexity
✅ Original task IDs preserved
✅ No circular dependencies

---

## Phase 2: Ecosystem Sync (`/iterate:sync`)

**Purpose**: Update entire spec ecosystem to match layered structure.

### When to Use

- Immediately after `/iterate:tasks`
- Before agents begin work
- After major spec reorganization

### Input

- `specs/{spec-num}/agent-tasks/layered-tasks.md`

### Process

1. Create `current-tasks.md` symlink
2. Update `plan.md` with iteration reference
3. Update `quickstart.md` with agent workflow
4. Create/update `iteration-log.md` for tracking

### Output

- `agent-tasks/current-tasks.md` (symlink)
- Updated `plan.md`
- Updated `quickstart.md`
- `agent-tasks/iteration-log.md`

### Example Usage

```bash
/iterate:sync 005
```

### Success Criteria

✅ current-tasks.md symlink created
✅ plan.md updated
✅ quickstart.md updated
✅ iteration-log.md tracking started
✅ All files consistent

---

## Phase 3: Live Adjustments (`/iterate:adjust`)

**Purpose**: Handle changes during active development.

### When to Use

- After PR review feedback (`/github:pr-review`)
- When requirements change mid-development
- After `/judge` provides new guidance

### Input

- Updated `specs/{spec-num}/tasks.md`

### Process

1. Backup current `layered-tasks.md` to `iteration-N-tasks.md`
2. Mark adjustment needed in log
3. Instruct to re-run Phase 1 + 2

### Output

- `agent-tasks/iteration-N-tasks.md` (backup)
- Updated `iteration-log.md`
- `.adjustment-needed` marker

### Example Usage

```bash
/iterate:adjust 005

# Then follow the workflow:
/iterate:tasks 005
/iterate:sync 005
```

### Success Criteria

✅ Previous iteration backed up
✅ iteration-log.md updated
✅ Clear next steps provided
✅ Agents notified of changes

---

## Complete Workflows

### Workflow 1: New Spec Development

```bash
# 1. Create spec
/specify "Build user authentication system"

# 2. Plan tasks
/plan 010

# 3. Layer tasks for parallel work
/iterate:tasks 010

# 4. Sync ecosystem
/iterate:sync 010

# 5. Verify setup
/supervisor:start 010

# 6. Begin agent work (in parallel worktrees)
# Agents work on their assigned tasks

# 7. Monitor progress
/supervisor:mid 010

# 8. Complete and verify
/supervisor:end 010
```

---

### Workflow 2: Handle PR Feedback

```bash
# 1. Review PR feedback
/github:pr-review 42

# 2. Update tasks.md based on feedback
# (Manual or via /judge)

# 3. Trigger adjustment
/iterate:adjust 010

# 4. Re-layer tasks
/iterate:tasks 010

# 5. Re-sync ecosystem
/iterate:sync 010

# 6. Agents continue work with updated structure
```

---

### Workflow 3: Multi-Spec Update

```bash
# Update multiple specs at once
/iterate:tasks 005,007,009

# Sync all
/iterate:sync 005
/iterate:sync 007
/iterate:sync 009

# Or use loop
for spec in 005 007 009; do
  /iterate:sync $spec
done
```

---

## Integration Patterns

### Pattern 1: Spec-Kit Integration

```
Spec Creation Flow:
  /specify → Creates specs/{spec}/
    ↓
  /plan → Creates tasks.md
    ↓
  /iterate:tasks → Creates layered-tasks.md
    ↓
  /iterate:sync → Updates ecosystem
    ↓
  Agent work begins
```

---

### Pattern 2: Supervisor Integration

```
Supervision Flow:
  /supervisor:start {spec} → Verifies layered-tasks.md exists
    ↓
  Agents work on tasks
    ↓
  /supervisor:mid {spec} → Checks progress via layered-tasks.md
    ↓
  /supervisor:end {spec} → Validates all tasks complete
```

---

### Pattern 3: GitHub Integration

```
PR Review Flow:
  /github:pr-review {pr-num}
    ↓
  Creates feedback in specs/{spec}/feedback/
    ↓
  /iterate:adjust {spec}
    ↓
  /iterate:tasks {spec} (re-layer)
    ↓
  /iterate:sync {spec} (re-sync)
    ↓
  Agents address feedback
```

---

## Troubleshooting Workflows

### Issue 1: Tasks Not Layered

**Symptom**: `/iterate:tasks` completes but no layered-tasks.md

**Solution**:
```bash
# Check tasks.md exists
ls specs/{spec}/tasks.md

# Verify task format
cat specs/{spec}/tasks.md

# Expected format:
# - [ ] T001 Task description
# - [ ] T002 Another task
```

---

### Issue 2: Sync Fails

**Symptom**: `/iterate:sync` reports missing files

**Solution**:
```bash
# Ensure Phase 1 completed
ls specs/{spec}/agent-tasks/layered-tasks.md

# If missing, re-run Phase 1
/iterate:tasks {spec}

# Then retry sync
/iterate:sync {spec}
```

---

### Issue 3: Worktrees Conflict

**Symptom**: Agent worktrees show wrong spec

**Solution**:
```bash
# List all worktrees
git worktree list

# Remove conflicting worktrees
git worktree remove ../project-{agent}

# Re-run setup
/iterate:sync {spec}

# Worktrees will be recreated with correct branches
```

---

## Best Practices

### 1. Always Run in Order

```bash
✅ Correct:
/iterate:tasks 005
/iterate:sync 005

❌ Wrong:
/iterate:sync 005  # Fails - no layered-tasks.md yet
```

---

### 2. Adjust Before Re-layering

```bash
✅ Correct:
# Edit tasks.md first
/iterate:adjust 005
/iterate:tasks 005
/iterate:sync 005

❌ Wrong:
/iterate:tasks 005  # Overwrites without backup!
```

---

### 3. Verify Before Agent Work

```bash
✅ Correct:
/iterate:tasks 005
/iterate:sync 005
/supervisor:start 005  # Verify setup
# Then agents begin

❌ Wrong:
/iterate:tasks 005
# Agents start immediately - may miss sync issues
```

---

## Advanced Patterns

### Pattern 1: Partial Re-layering

```bash
# When only some tasks change:
# 1. Edit tasks.md (add/remove specific tasks)
# 2. Run adjustment
/iterate:adjust 005

# 3. Re-layer (preserves task IDs)
/iterate:tasks 005

# 4. Re-sync
/iterate:sync 005
```

---

### Pattern 2: Conditional Layering

```bash
# Layer only if tasks.md changed
if [[ specs/005/tasks.md -nt specs/005/agent-tasks/layered-tasks.md ]]; then
  /iterate:tasks 005
  /iterate:sync 005
fi
```

---

### Pattern 3: Batch Operations

```bash
# Find all specs needing re-layering
for spec_dir in specs/*/; do
  spec=$(basename "$spec_dir")
  if [[ -f "$spec_dir/tasks.md" ]]; then
    /iterate:tasks "$spec"
    /iterate:sync "$spec"
  fi
done
```

---

## References

- **Layering Philosophy**: `docs/layering-philosophy.md`
- **Integration Guide**: `docs/integration-guide.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **Main README**: `multiagent_core/templates/.multiagent/iterate/README.md`
