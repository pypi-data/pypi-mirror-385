# Iterate System - Multi-Phase Spec Ecosystem Management

## Purpose

Transforms sequential tasks into layered structure for parallel agent work. Keeps entire spec ecosystem synchronized as development progresses.

## What It Does

1. **Layers tasks** - Reorganizes tasks.md into parallel layers (Models → Infrastructure → Adapters → Integration)
2. **Assigns agents** - Distributes workload across @claude, @copilot, @qwen, @gemini, @codex
3. **Syncs ecosystem** - Updates all spec files when changes occur
4. **Live adjustments** - Adapts to development changes and new requirements

## Agents Used

- **@claude/task-layering** - Analyzes and layers tasks for parallel work
- **No other dedicated agents** - Uses scripts for file synchronization

## Commands

- **`/iterate:tasks <spec-dir>`** - Transform sequential tasks into layered structure for parallel work
- **`/iterate:sync <spec-dir>`** - Sync entire spec ecosystem to match layered tasks
- **`/iterate:adjust <spec-dir>`** - Live development adjustments with ecosystem sync

## Complete Workflow

### Initial Spec Setup (After Creating Spec)
```bash
# Step 1: Create spec with sequential tasks
# Prerequisite: You have specs/{spec}/tasks.md with sequential task list

# Step 2: Layer tasks for parallel work
/iterate:tasks {spec}
# What this does: Transforms sequential tasks into layered structure
# Expected output: specs/{spec}/agent-tasks/layered-tasks.md created
# Time: 1-2 minutes
# Result: Tasks organized in foundation → parallel → integration layers

# Step 3: Sync entire spec ecosystem
/iterate:sync {spec}
# What this does: Updates plan.md, quickstart.md, creates current-tasks.md symlink
# Expected output: All spec files synchronized to match layered structure
# Time: 30 seconds
# Result: Spec ecosystem coherent and ready for development

# Step 4: Setup worktrees for parallel development
/supervisor:start {spec}
# This validates setup and creates agent worktrees
# Required before agents begin work
```

**Verification**: layered-tasks.md created, spec files synced, worktrees ready

### Multi-Spec Setup (Multiple Specs at Once)
```bash
# Layer tasks for all specs
/iterate:tasks --all
# Or specific specs: /iterate:tasks 001,002,003

# Sync all specs
/iterate:sync --all
# Or specific specs: /iterate:sync 001,002,003

# Setup all worktrees
/supervisor:start --all
```

**Time Savings**: Process multiple specs in parallel vs one-by-one

### Live Development Adjustments (During Development)
```bash
# Step 1: When requirements change during development
# Trigger: PR feedback, new insights, requirement updates

# Step 2: Run adjust to prepare for changes
/iterate:adjust {spec}
# What this does: Backs up current iteration, prepares for updates
# Expected output: Previous iteration saved, adjustment marker created
# Time: 10 seconds
# Result: Ready to incorporate changes

# Step 3: Re-layer tasks with new requirements
/iterate:tasks {spec}
# Updates layered-tasks.md with new structure
# Time: 1-2 minutes

# Step 4: Re-sync ecosystem
/iterate:sync {spec}
# Propagates changes through all spec files
# Time: 30 seconds

# Step 5: Notify agents of changes
# Agents pull latest in their worktrees:
cd ../{project}-{spec#}-{agent-name}/
git merge main
# Review updated task assignments in layered-tasks.md

# Step 6: Continue development with new structure
/supervisor:mid {spec}  # Verify agents aligned
```

**Use Case**: Incorporating PR feedback, scope changes, new requirements

### Typical Iteration Workflow
```
Initial Pass:
  Create specs/{spec}/tasks.md (sequential)
  /iterate:tasks {spec}           → Layer tasks (2 min)
  /iterate:sync {spec}            → Sync ecosystem (30 sec)
  /supervisor:start {spec}        → Setup worktrees (1 min)

Development Cycle:
  Agents work in parallel
  /supervisor:mid {spec}          → Monitor progress
  /supervisor:end {spec}          → Validate completion
  Create PRs, get feedback

Adjustment (if needed):
  /iterate:adjust {spec}          → Prepare changes (10 sec)
  /iterate:tasks {spec}           → Re-layer (2 min)
  /iterate:sync {spec}            → Re-sync (30 sec)
  Agents continue with updates
```

### Integration with PR Review Workflow
```bash
# After receiving PR feedback:
/github:pr-review {pr-number}    # Analyze feedback
# Review creates feedback/tasks.md with new requirements

# Incorporate feedback into spec:
/iterate:adjust {spec}           # Prepare for changes
/iterate:tasks {spec}            # Re-layer with feedback
/iterate:sync {spec}             # Sync ecosystem
# Agents implement feedback
```

### Iteration Tracking
```bash
# View iteration history
cat specs/{spec}/agent-tasks/iteration-log.md
# Shows: All iterations, what changed, when

# Check current iteration
ls -la specs/{spec}/agent-tasks/current-tasks.md
# Symlink points to latest layered-tasks.md

# View previous iterations
ls specs/{spec}/agent-tasks/iteration-*.md
# Each iteration backed up for audit trail
```

### Typical Session Timeline
```
Hour 0: /iterate:tasks 001        → Layer tasks (2 min)
        /iterate:sync 001         → Sync ecosystem (30 sec)
        /supervisor:start 001     → Setup worktrees (1 min)
Hour 1-8: Agents develop in parallel
Hour 8: /supervisor:end 001       → Validate completion
        Create PRs, submit for review

Day 2: Receive PR feedback
       /iterate:adjust 001        → Prepare changes (10 sec)
       /iterate:tasks 001         → Re-layer (2 min)
       /iterate:sync 001          → Re-sync (30 sec)
       Agents address feedback
```

### Command Relationships
```bash
# Complete workflow integration:
/specify 001                     # Create spec
/iterate:tasks 001               # Layer tasks (ITERATE Phase 1)
/iterate:sync 001                # Sync ecosystem (ITERATE Phase 2)
/supervisor:start 001            # Setup worktrees (SUPERVISOR)
# Development happens...
/supervisor:mid 001              # Monitor progress (SUPERVISOR)
/iterate:adjust 001              # Live changes (ITERATE Phase 3)
/iterate:tasks 001               # Re-layer (ITERATE Phase 1)
/iterate:sync 001                # Re-sync (ITERATE Phase 2)
/supervisor:end 001              # Validate (SUPERVISOR)
# Create PRs...
```

## Overview

The Iterate system solves the core problem of **specification ecosystem coherence** during development. Instead of having docs get out of sync across the project, iterate keeps the entire spec ecosystem aligned through structured phases.

## The Problem We're Solving

### Current Development Chaos
- Change `tasks.md` → `plan.md` gets stale
- Update requirements → `spec.md` and `contracts/` diverge  
- Add new tasks → `data-model.md` becomes inconsistent
- **Result**: Multiple sources of truth, lost context, iteration friction

### Our Solution: Coordinated Ecosystem Updates
- All specs stay synchronized during development
- Changes propagate through the entire ecosystem  
- Single command handles full coherence
- Self-contained system maintains consistency

## Multi-Phase Architecture

### Phase 1: Task Organization (Foundation)
**Purpose**: Analyze tasks and create non-blocking parallel structure

**What it does**:
- Apply intelligent dependency analysis to minimize blocking
- Generate `agent-tasks/layered-tasks.md` with optimized layering
- Organize tasks into Layer 1 (5-10% foundation), Layer 2 (75-85% parallel), Layer 3 (10-15% integration)
- Assign tasks to agents based on specialization and workload distribution
- Prepare structure for worktree creation by supervisor

**Command**: `/iterate:tasks [spec-directory]`
**Agent**: `task-layering`
**Output**:
- `specs/[session]/agent-tasks/layered-tasks.md` with agent assignments

**Next step**: Run `/supervisor:start [spec-directory]` to create worktrees and symlinks

### Phase 2: Spec Ecosystem Sync (Coherence)
**Purpose**: Update the entire spec ecosystem to match the organized tasks

**What it does**:
- Read the layered tasks from Phase 1
- Update `plan.md` to reflect new task structure
- Sync `spec.md` with any new requirements discovered
- Update `contracts/` to match new agent assignments
- Refresh `data-model.md` for any new data needs
- Ensure `quickstart.md` reflects current workflow

**Command**: `/iterate sync [spec-directory]`  
**Script**: `.multiagent/iterate/scripts/phase2-ecosystem-sync.sh`
**Output**: Updated spec files across the entire directory

### Phase 3: Development Adjustments (Live Updates)
**Purpose**: Handle live changes during development while maintaining coherence

**What it does**:
- Accept new requirements or task changes
- Re-run Phase 1 + Phase 2 automatically
- Track what changed and why
- Maintain development audit trail
- Keep everything synchronized

**Command**: `/iterate adjust [spec-directory]`
**Script**: `.multiagent/iterate/scripts/phase3-development-adjust.sh`
**Output**: Updated ecosystem + change log

## Command Patterns

### Individual Phases
```bash
/iterate tasks 002-system-context-we           # Phase 1 only
/iterate sync 002-system-context-we            # Phase 2 only  
/iterate adjust 002-system-context-we          # Phase 3
```

### Command Usage
```bash
# Run phases sequentially as needed
/iterate tasks 002-system-context-we           # Phase 1 first
/iterate sync 002-system-context-we            # Then Phase 2
/iterate adjust 002-system-context-we          # Phase 3 when needed
```

## System Structure

```
.multiagent/iterate/
├── README.md                           # This file
├── scripts/
│   ├── phase1-task-layering.sh         # Task organization 
│   ├── phase2-ecosystem-sync.sh        # Spec synchronization
│   ├── phase3-development-adjust.sh    # Live adjustments
│   └── coherence-check.sh              # Validation utilities
└── templates/
    └── task-layering.template.md       # Task layering template (placeholder format)
```

## Integration with Existing Systems

### Works With
- **PR Review System** (`.multiagent/github/pr-review/`): Uses iterate to update specs based on feedback
- **Agent Tasks**: Agents read from `agent-tasks/layered-tasks.md` generated by Phase 1
- **SpecKit Pattern**: Follows Command → Script → Output like other systems

### Command Integration
- **After `/judge`**: Run `/iterate adjust` to incorporate feedback into specs
- **After `/plan`**: Run `/iterate tasks` then `/iterate sync` to structure and organize everything
- **During development**: Use `/iterate adjust` when requirements change

## Success Criteria

### ✅ Phase 1 Success
- `agent-tasks/layered-tasks.md` generated with proper layering
- Tasks organized into foundation → parallel → integration structure
- Agent assignments clear and non-conflicting

### ✅ Phase 2 Success  
- All spec files updated to reflect task structure
- No contradictions between `plan.md`, `spec.md`, `tasks.md`
- Contracts match agent assignments from layered tasks

### ✅ Phase 3 Success
- Changes propagated through entire ecosystem
- Change log tracks what updated and why
- Development audit trail maintained

### ✅ Overall System Success
- Single source of truth maintained across all specs
- No manual sync required between documents
- Development iterations don't break coherence
- Clear workflow for making changes

## Implementation Status

### ✅ Completed
- **Phase 1**: Task layering using proven `layer-tasks.sh` script
- **Phase 2**: Spec ecosystem sync script with iteration tracking
- **Command Structure**: Multi-phase argument parsing and auto-detection
- **Integration**: Works with existing PR review and agent systems

### 🔄 In Progress  
- **Phase 3**: Development adjustment script (final piece)
- **Testing**: End-to-end validation with real specs

### 📋 Ready for Testing
The system is ready for testing with:
```bash
/iterate tasks 002-system-context-we    # Test Phase 1
/iterate sync 002-system-context-we     # Test Phase 2  
# Run phases individually as needed
```

## The Iterative Development Workflow

### Initial Pass (Foundation)
```
tasks.md → /iterate tasks → layered-tasks.md
↓ (manual review and refinements)
/iterate adjust → iteration-1-tasks.md
```

### Development Cycle
```
iteration-N-tasks.md → Agents implement → PRs created
↓
/judge PR → feedback/tasks.md
↓
/iterate sync → iteration-N+1-tasks.md (incorporates feedback)
↓
Agents implement → New PRs → Cycle continues
```

### Output Evolution
```
specs/002-system-context-we/agent-tasks/
├── layered-tasks.md        # Initial layering
├── iteration-1-tasks.md    # Manual refinements  
├── iteration-2-tasks.md    # Post-PR feedback
├── current-tasks.md        # → symlink to latest
└── iteration-log.md        # Change tracking
```

---

## Troubleshooting

### Common Issues

#### Issue: "Layered tasks file not found"

**Cause**: Phase 1 (`/iterate:tasks`) not completed successfully.

**Solution**:
```bash
# Verify tasks.md exists
cat specs/{spec}/tasks.md

# Re-run Phase 1
/iterate:tasks {spec}

# Check output
ls specs/{spec}/agent-tasks/layered-tasks.md
```

---

#### Issue: "Worktree creation failed"

**Cause**: Not on main/master branch or worktree already exists.

**Solution**:
```bash
# Check current branch
git branch --show-current

# Switch to main
git checkout main

# Remove conflicting worktrees
git worktree list
git worktree remove ../project-{agent} --force

# Re-run Phase 2
/iterate:sync {spec}
```

---

#### Issue: "Phase scripts not found"

**Cause**: Scripts not deployed to project.

**Solution**:
```bash
# Verify scripts exist
ls -la multiagent_core/templates/.multiagent/iterate/scripts/

# Expected files:
# - setup-spec-worktrees.sh
# - setup-worktree-symlinks.sh
# - scaffold-split-structure.sh
# - phase2-ecosystem-sync.sh
# - phase3-development-adjust.sh

# Check permissions
ls -l multiagent_core/templates/.multiagent/iterate/scripts/*.sh
# All should be executable (chmod +x if not)
```

---

#### Issue: "current-tasks.md symlink broken"

**Cause**: layered-tasks.md missing or Phase 2 not completed.

**Solution**:
```bash
# Check if layered-tasks.md exists
ls -la specs/{spec}/agent-tasks/layered-tasks.md

# If missing, run Phase 1 first
/iterate:tasks {spec}

# Then run Phase 2
/iterate:sync {spec}

# Verify symlink
ls -la specs/{spec}/agent-tasks/current-tasks.md
```

---

#### Issue: "Tasks not properly layered"

**Cause**: Invalid task format or circular dependencies.

**Solution**:
```bash
# Check task format in tasks.md
cat specs/{spec}/tasks.md

# Expected format:
# - [ ] T001 Task description
# - [ ] T002 Another task

# Invalid formats:
# - T001 Missing checkbox
# * [ ] T001 Wrong bullet
# - [x] T001 Already completed

# Fix format and re-run
/iterate:tasks {spec}
```

---

### Getting More Help

For detailed troubleshooting, see:
- **Troubleshooting Guide**: `docs/troubleshooting.md`
- **Workflow Patterns**: `docs/workflow-patterns.md`
- **Layering Philosophy**: `docs/layering-philosophy.md`

---

*This system maintains the proven SpecKit pattern while solving the multi-document coherence problem that slows down iterative development.*