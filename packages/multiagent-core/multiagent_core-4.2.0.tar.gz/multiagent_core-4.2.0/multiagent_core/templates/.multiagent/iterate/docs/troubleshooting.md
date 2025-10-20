# Troubleshooting Guide

## Purpose

This document provides solutions to common issues when using the iterate subsystem.

---

## Quick Diagnosis

### Check System Status

```bash
# Verify iterate scripts exist
ls -la multiagent_core/templates/.multiagent/iterate/scripts/

# Expected files:
# - setup-spec-worktrees.sh
# - setup-worktree-symlinks.sh
# - scaffold-split-structure.sh
# - phase2-ecosystem-sync.sh
# - phase3-development-adjust.sh

# Check spec structure
ls -la specs/{spec-num}/

# Expected:
# - tasks.md
# - agent-tasks/layered-tasks.md (after Phase 1)
# - plan.md
# - quickstart.md
```

---

## Phase 1 Issues (`/iterate:tasks`)

### Issue 1: "Layered tasks not created"

**Symptom**: Command completes but no `layered-tasks.md` file.

**Causes**:
1. Invalid tasks.md format
2. Script execution failure
3. Permission issues

**Solutions**:

```bash
# 1. Verify tasks.md exists and has correct format
cat specs/{spec}/tasks.md

# Expected format:
# - [ ] T001 Task description @agent
# - [ ] T002 Another task @agent

# 2. Check for script errors
bash -x multiagent_core/templates/.multiagent/iterate/scripts/layer-tasks.sh specs/{spec}

# 3. Check permissions
ls -la specs/{spec}/
# Should be writable by current user

# 4. Manually create agent-tasks directory if missing
mkdir -p specs/{spec}/agent-tasks
```

---

### Issue 2: "Task numbering lost"

**Symptom**: Original T001, T002 become T001, T002 in different order.

**Cause**: Task layering should preserve IDs, but agent may have renumbered.

**Solution**:

```bash
# Check original tasks.md for reference
cat specs/{spec}/tasks.md

# Compare with layered-tasks.md
cat specs/{spec}/agent-tasks/layered-tasks.md

# If numbering is wrong, re-run with explicit instruction
/iterate:tasks {spec}
# In the command, emphasize: "PRESERVE original task IDs (T001, T002, etc.)"
```

---

### Issue 3: "Circular dependencies detected"

**Symptom**: Task cannot be placed in any layer due to circular dependency.

**Example**:
```
T001 Service A calls Service B
T002 Service B calls Service A
```

**Solution**:

```bash
# 1. Review tasks.md and identify circular deps
cat specs/{spec}/tasks.md

# 2. Break circular dependency by adding intermediate layer
# Original (circular):
# - T001 Service A → B
# - T002 Service B → A

# Fixed (three layers):
# - T001 Create Service A (no calls)
# - T002 Create Service B (no calls)
# - T003 Integrate A → B

# 3. Update tasks.md manually
# 4. Re-run layering
/iterate:tasks {spec}
```

---

## Phase 2 Issues (`/iterate:sync`)

### Issue 4: "phase2-ecosystem-sync.sh not found"

**Symptom**: Script execution fails with "file not found".

**Cause**: Script missing from iterate scripts directory.

**Solution**:

```bash
# 1. Verify script exists
ls -la multiagent_core/templates/.multiagent/iterate/scripts/phase2-ecosystem-sync.sh

# 2. If missing, script may not be deployed
# Check template source
ls -la ~/.multiagent/iterate/scripts/

# 3. Copy script if needed (should be deployed by framework)
cp ~/.multiagent/iterate/scripts/phase2-ecosystem-sync.sh \
   multiagent_core/templates/.multiagent/iterate/scripts/

# 4. Make executable
chmod +x multiagent_core/templates/.multiagent/iterate/scripts/phase2-ecosystem-sync.sh
```

---

### Issue 5: "current-tasks.md symlink broken"

**Symptom**: Symlink points to non-existent file.

**Cause**: layered-tasks.md not created in Phase 1.

**Solution**:

```bash
# 1. Check if layered-tasks.md exists
ls -la specs/{spec}/agent-tasks/layered-tasks.md

# 2. If missing, re-run Phase 1
/iterate:tasks {spec}

# 3. Then re-run Phase 2
/iterate:sync {spec}

# 4. Verify symlink
ls -la specs/{spec}/agent-tasks/current-tasks.md
# Should point to → layered-tasks.md
```

---

### Issue 6: "plan.md not updated"

**Symptom**: plan.md doesn't show iteration reference.

**Cause**: plan.md doesn't exist or is read-only.

**Solution**:

```bash
# 1. Check if plan.md exists
ls -la specs/{spec}/plan.md

# 2. If missing, create it
touch specs/{spec}/plan.md

# 3. Check permissions
ls -l specs/{spec}/plan.md
# Should be writable

# 4. Re-run sync
/iterate:sync {spec}
```

---

## Phase 3 Issues (`/iterate:adjust`)

### Issue 7: "No previous iteration to backup"

**Symptom**: Warning about missing iteration file to backup.

**Cause**: First iteration - no previous layered-tasks.md exists.

**Solution**:

```bash
# This is normal for first adjustment
# Script will create iteration-1 without backup

# Verify iteration log
cat specs/{spec}/agent-tasks/iteration-log.md

# Should show:
# ## Iteration 1 - {date}
# **Status**: Adjustment Needed
```

---

### Issue 8: "Adjustment doesn't trigger re-layering"

**Symptom**: adjust.md runs but tasks not re-layered.

**Cause**: Phase 3 only prepares for adjustment. You must manually re-run Phase 1 + 2.

**Solution**:

```bash
# Phase 3 creates marker and backs up
/iterate:adjust {spec}

# Then manually run Phase 1 + 2
/iterate:tasks {spec}
/iterate:sync {spec}

# This is by design - allows you to review before re-layering
```

---

## Worktree Issues

### Issue 9: "Worktree already exists for different spec"

**Symptom**: Agent worktree points to old spec.

**Solution**:

```bash
# 1. List all worktrees
git worktree list

# 2. Remove old worktree
git worktree remove ../project-{agent} --force

# 3. Delete old branch
git branch -D agent-{agent}-{old-spec-num}

# 4. Re-run Phase 2 to recreate
/iterate:sync {spec}
```

---

### Issue 10: "Cannot create worktree - not on main"

**Symptom**: setup-spec-worktrees.sh fails with branch error.

**Cause**: Must be on main/master branch to create worktrees.

**Solution**:

```bash
# 1. Check current branch
git branch --show-current

# 2. Switch to main
git checkout main

# 3. Pull latest
git pull

# 4. Re-run sync
/iterate:sync {spec}
```

---

### Issue 11: "Worktree symlink not working"

**Symptom**: Agents can't see layered-tasks-main.md in worktree.

**Solution**:

```bash
# 1. Check symlink in worktree
cd ../project-{agent}
ls -la specs/{spec}/layered-tasks-main.md

# 2. If missing, manually create
cd specs/{spec}/
ln -sf ../../../../multiagent-core/specs/{spec}/agent-tasks/layered-tasks.md \
       layered-tasks-main.md

# 3. Or re-run symlink script
bash ~/.multiagent/iterate/scripts/setup-worktree-symlinks.sh {spec}
```

---

## File Format Issues

### Issue 12: "Tasks not recognized"

**Symptom**: Layering agent ignores some tasks.

**Cause**: Invalid markdown checkbox format.

**Solution**:

```bash
# Valid formats:
- [ ] T001 Task description
- [ ] T002 Another task @claude

# Invalid formats (won't be recognized):
- T001 Task description (missing checkbox)
* [ ] T001 Task description (wrong bullet)
- [x] T001 Task description (marked complete)

# Fix tasks.md
vim specs/{spec}/tasks.md

# Ensure all tasks use: - [ ] TXXX format
```

---

### Issue 13: "Agent assignments not applied"

**Symptom**: All tasks show @claude or no agent.

**Cause**: Agent assignment happens during layering, not in original tasks.md.

**Solution**:

```bash
# This is expected behavior:
# - tasks.md: No agent assignments (optional)
# - layered-tasks.md: Has agent assignments

# Check layered-tasks.md for assignments
grep "@" specs/{spec}/agent-tasks/layered-tasks.md

# Should show:
# - [ ] T001 Task @claude
# - [ ] T002 Task @copilot

# If missing, agent failed to assign. Re-run:
/iterate:tasks {spec}
```

---

## Integration Issues

### Issue 14: "Supervisor can't find layered tasks"

**Symptom**: `/supervisor:start` reports missing layered-tasks.md.

**Cause**: Phase 1 not completed before supervision.

**Solution**:

```bash
# Always run iterate before supervisor
/iterate:tasks {spec}
/iterate:sync {spec}
/supervisor:start {spec}  # Now works
```

---

### Issue 15: "GitHub PR review doesn't trigger adjust"

**Symptom**: PR review feedback doesn't update iteration.

**Cause**: Manual integration required - `/iterate:adjust` not auto-triggered.

**Solution**:

```bash
# After PR review:
/github:pr-review {pr-num}

# Manually update tasks.md based on feedback

# Then trigger adjustment
/iterate:adjust {spec}
/iterate:tasks {spec}
/iterate:sync {spec}
```

---

## Performance Issues

### Issue 16: "Layering takes too long"

**Symptom**: `/iterate:tasks` hangs or takes >5 minutes.

**Cause**: Very large task list (>100 tasks).

**Solution**:

```bash
# 1. Check task count
wc -l specs/{spec}/tasks.md

# 2. If >100 tasks, consider splitting spec
# Use /iterate:split for guidance

# 3. Or simplify tasks (combine related items)

# 4. Increase timeout for agent
# (This is a framework setting - see agent configuration)
```

---

## Common Error Messages

### Error: "Spec directory not found"

```bash
# Cause: Invalid spec number or path
# Fix: Use correct spec number
/iterate:tasks 005  # ✅ Correct
/iterate:tasks 5    # ❌ Wrong (must be zero-padded)
```

---

### Error: "Could not extract spec number"

```bash
# Cause: Spec directory name doesn't start with number
# Fix: Rename to standard format
# Bad:  specs/auth-system/
# Good: specs/010-auth-system/
```

---

### Error: "Permission denied"

```bash
# Cause: Script not executable
# Fix: Make scripts executable
chmod +x multiagent_core/templates/.multiagent/iterate/scripts/*.sh
```

---

## Debugging Tips

### Enable Debug Mode

```bash
# Run scripts with debug output
bash -x multiagent_core/templates/.multiagent/iterate/scripts/phase2-ecosystem-sync.sh specs/005
```

---

### Check Script Logs

```bash
# Scripts output to /tmp/
ls -la /tmp/phase2-sync-*.json
ls -la /tmp/phase3-adjust-*.json

# Review JSON output
cat /tmp/phase2-sync-005.json
```

---

### Verify File Permissions

```bash
# All specs should be writable
find specs/ -type f ! -perm -u+w

# If any files shown, fix permissions
chmod -R u+w specs/
```

---

## Getting Help

If issues persist:

1. **Check iteration-log.md**: `cat specs/{spec}/agent-tasks/iteration-log.md`
2. **Review script output**: Check `/tmp/phase*.json` files
3. **Verify file structure**: Use tree command: `tree specs/{spec}/`
4. **Check git status**: Ensure clean working directory
5. **Report issue**: Include error messages and script output

---

## References

- **Layering Philosophy**: `docs/layering-philosophy.md`
- **Workflow Patterns**: `docs/workflow-patterns.md`
- **Main README**: `multiagent_core/templates/.multiagent/iterate/README.md`
- **Build Standards**: `docs/architecture/02-development-guide.md`
