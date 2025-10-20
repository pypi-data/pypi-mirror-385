# Implementation Subsystem

## Purpose

Orchestrate idea/enhancement/refactor to spec implementation workflow with AI-powered plan and task generation. This subsystem bridges the gap between proposals (ideas, enhancements, refactors) and ready-to-implement specs by coordinating mechanical file operations and intelligent AI-powered planning.

## What It Does

1. **Workflow Orchestration** - Coordinates the entire journey from proposal to implementation-ready spec
2. **Auto-Promotion** - Automatically promotes ideas to enhancements when implementation is requested
3. **Intelligent Planning** - Delegates to specialized agents to generate detailed implementation plans and tasks
4. **Spec Management** - Creates new specs or adds proposals to existing specs based on context
5. **Integration Hub** - Connects enhancement, refactoring, idea, and supervisor subsystems into unified workflow

## Architecture

The implementation subsystem acts as the **orchestrator** that coordinates between:

```
┌─────────────────────────────────────────────────────────────────┐
│                   IMPLEMENTATION SUBSYSTEM                      │
│                         (Orchestrator)                          │
└─────────────────────────────────────────────────────────────────┘
                               ↓
        ┌──────────────────────┼──────────────────────┐
        ↓                      ↓                      ↓
┌───────────────┐    ┌─────────────────┐    ┌────────────────┐
│  Enhancement  │    │   Refactoring   │    │      Idea      │
│   Subsystem   │    │    Subsystem    │    │   Subsystem    │
│               │    │                 │    │                │
│ /enhancement: │    │  /refactoring:  │    │   /idea:       │
│    spec       │    │      spec       │    │   promote      │
│ (mechanical)  │    │  (mechanical)   │    │ (mechanical)   │
└───────────────┘    └─────────────────┘    └────────────────┘
        ↓                      ↓
┌───────────────────────────────────────────────────────────────┐
│                      AGENTS (Intelligence)                     │
│                                                                │
│  enhancement-spec-creator  |  refactor-spec-creator           │
│  (generates plan + tasks)  |  (generates plan + tasks)        │
└────────────────────────────────────────────────────────────────┘
```

## Agents Used

- **enhancement-spec-creator** - Reads enhancement proposals and generates comprehensive implementation plans with phased approach, technical decisions, and actionable task lists
- **refactor-spec-creator** - Reads refactor proposals and generates implementation plans focused on code improvement, technical debt reduction, and refactoring strategies

## Commands

### `/implementation:implement` - Orchestrate proposal to spec implementation

**Usage**:
```bash
/implementation:implement --idea <slug>
/implementation:implement --enhancement <id>
/implementation:implement --refactor <id>
/implementation:implement --spec <id>
```

**Examples**:
```bash
/implementation:implement --idea redis-caching-layer
/implementation:implement --enhancement 001
/implementation:implement --refactor 001
```

This command coordinates the entire workflow from proposal to implementation-ready spec. It handles auto-promotion, spec creation/selection, mechanical file operations, and AI-powered plan generation.

**Workflow**:
1. Parse source type (idea/enhancement/refactor/spec)
2. Auto-promote ideas to enhancements if needed
3. Find proposal file
4. Determine spec location (create new or add to existing)
5. Call `/enhancement:spec` or `/refactoring:spec` for mechanical operations
6. Invoke appropriate agent to generate plan.md and tasks.md
7. Validate outputs
8. Display summary and next steps

**Spawns**:
- `enhancement-spec-creator` agent (for enhancements)
- `refactor-spec-creator` agent (for refactors)

**Outputs**:
- `specs/{id}/enhancements/{id}-{slug}/plan.md` (for enhancements)
- `specs/{id}/enhancements/{id}-{slug}/tasks.md` (for enhancements)
- `specs/{id}/refactors/{id}-{slug}/plan.md` (for refactors)
- `specs/{id}/refactors/{id}-{slug}/tasks.md` (for refactors)

---

## How It Works

### The Problem

Before this subsystem existed, implementing proposals required multiple manual steps:

```
OLD WORKFLOW (Manual):
1. Idea created → User must manually promote to enhancement
2. Enhancement created → User must manually determine which spec
3. User runs /enhancement:spec → Only copies file mechanically
4. User must manually generate plan.md and tasks.md
5. User runs /iterate:tasks → Layer tasks
6. User runs /supervisor:start → Begin implementation
```

**Issues with old workflow:**
- Too many manual steps
- Easy to forget steps
- Inconsistent plan/task quality
- Proposals sit unimplemented

### The Solution

The implementation subsystem provides a **single entry point** that orchestrates everything:

```
NEW WORKFLOW (Automated):
/implement --idea redis-caching
  ↓ Auto-promotes to enhancement
  ↓ Determines spec (new or existing)
  ↓ Copies files mechanically
  ↓ Generates plan + tasks with AI
  ↓ Ready for /supervisor:start
```

### Workflow Details

**1. Source Detection**
- Accepts `--idea`, `--enhancement`, `--refactor`, or `--spec` flags
- Finds proposal files in `docs/ideas/`, `docs/enhancements/`, or `docs/refactors/`
- Auto-promotes ideas to enhancements (ideas are not implementation-ready)

**2. Spec Location Logic**

```bash
if proposal already in a spec:
  Use that spec
else:
  Show available specs
  Prompt: "Create new spec or add to existing?"

  if create new:
    Generate next spec ID (e.g., 008)
    Create specs/008-{name}/ directory
    Create placeholder spec.md

  if add to existing:
    User selects spec ID
    Use that spec
```

**3. Mechanical Operations (Delegation)**

Calls existing subsystem commands:
- `/enhancement:spec {spec-id} --from-enhancement {name}` - Copies enhancement.md
- `/refactoring:spec {spec-id} --from-refactor {name}` - Copies refactor.md

These commands are **purely mechanical**:
- Create subdirectory: `specs/{id}/enhancements/{id}-{slug}/`
- Copy proposal file: `enhancement.md` or `refactor.md`
- Move proposal: `02-approved/` → `03-in-progress/`
- No AI, no intelligence, just file operations

**4. Intelligent Planning (Agents)**

After mechanical operations, invokes specialized agents:

```javascript
Task(
  subagent_type: "general-purpose",
  description: "Generate plan and tasks from enhancement",
  prompt: "You are the enhancement-spec-creator agent.

  Read: specs/{id}/enhancements/{id}-{slug}/enhancement.md

  Generate:
  1. plan.md - Implementation strategy with phases, decisions, risks
  2. tasks.md - Actionable tasks (T001, T002, ...) with dependencies

  Follow structure in ~/.claude/agents/enhancement-spec-creator.md"
)
```

Agents are **100% intelligence**:
- Read proposal and understand requirements
- Break down into implementation phases
- Make technical decisions
- Generate detailed task list with dependencies
- Include acceptance criteria and file paths

**5. Validation & Summary**

- Checks plan.md and tasks.md were created
- Displays summary with file locations
- Prompts next steps: `/iterate:tasks`, `/supervisor:start`

## Directory Structure

```
.multiagent/implementation/
├── README.md              # This file - explains subsystem
├── docs/                  # Conceptual documentation
├── templates/             # (None needed - delegates to other subsystems)
├── scripts/               # (None needed - uses bash in command)
└── memory/               # Agent state storage (future)
```

**Why minimal?**

This subsystem is an **orchestrator**, not a generator. It:
- Delegates mechanical operations to enhancement/refactoring subsystems
- Delegates intelligent operations to specialized agents
- Coordinates workflow between subsystems

No custom templates or scripts needed - it uses what already exists.

## Integration with Other Subsystems

### Enhancement Subsystem
**Relationship**: Implementation subsystem **delegates to** enhancement subsystem

- `/implementation:implement --enhancement X` calls `/enhancement:spec`
- Enhancement subsystem handles mechanical file copying
- Implementation subsystem handles AI planning

**Files touched**:
- Enhancement: `docs/enhancements/02-approved/{area}-{slug}.md`
- Spec: `specs/{id}/enhancements/{id}-{slug}/enhancement.md` (copied by enhancement subsystem)
- Spec: `specs/{id}/enhancements/{id}-{slug}/plan.md` (generated by implementation agent)
- Spec: `specs/{id}/enhancements/{id}-{slug}/tasks.md` (generated by implementation agent)

### Refactoring Subsystem
**Relationship**: Implementation subsystem **delegates to** refactoring subsystem

- `/implementation:implement --refactor X` calls `/refactoring:spec`
- Refactoring subsystem handles mechanical file copying
- Implementation subsystem handles AI planning

**Files touched**:
- Refactor: `docs/refactors/02-approved/{area}-{slug}.md`
- Spec: `specs/{id}/refactors/{id}-{slug}/refactor.md` (copied by refactoring subsystem)
- Spec: `specs/{id}/refactors/{id}-{slug}/plan.md` (generated by implementation agent)
- Spec: `specs/{id}/refactors/{id}-{slug}/tasks.md` (generated by implementation agent)

### Idea Subsystem
**Relationship**: Implementation subsystem **uses** idea subsystem

- `/implementation:implement --idea X` calls `/idea:promote`
- Idea subsystem promotes idea to enhancement
- Then implementation continues with enhancement workflow

### Supervisor Subsystem
**Relationship**: Implementation subsystem **feeds into** supervisor subsystem

- Implementation generates plan.md and tasks.md
- Supervisor reads these files to set up worktrees
- User runs: `/implement --enhancement X` then `/supervisor:start {spec}`

### Iterate Subsystem
**Relationship**: Implementation subsystem **optionally feeds into** iterate subsystem

- Implementation generates tasks.md
- User can optionally run `/iterate:tasks {spec}` to layer tasks
- Creates `layered-tasks.md` for parallel agent work

## Outputs

This subsystem generates:

```
specs/{id}/enhancements/{enhancement-id}-{slug}/
├── enhancement.md         # (copied by /enhancement:spec)
├── plan.md               # (generated by enhancement-spec-creator agent)
└── tasks.md              # (generated by enhancement-spec-creator agent)

specs/{id}/refactors/{refactor-id}-{slug}/
├── refactor.md           # (copied by /refactoring:spec)
├── plan.md               # (generated by refactor-spec-creator agent)
└── tasks.md              # (generated by refactor-spec-creator agent)
```

## Usage Example

### Example 1: Implement from Idea

```bash
# User has idea: docs/ideas/redis-caching-layer.md
/implementation:implement --idea redis-caching-layer

# System does:
# 1. Auto-promotes to enhancement (calls /idea:promote)
# 2. Creates new spec: specs/008-redis-caching/
# 3. Copies enhancement file (calls /enhancement:spec)
# 4. Generates plan.md and tasks.md (agent)
# 5. Displays summary

# User proceeds:
/supervisor:start 008
```

### Example 2: Implement from Enhancement

```bash
# User has approved enhancement in docs/enhancements/02-approved/
/implementation:implement --enhancement 001

# System prompts:
# "Create new spec or add to existing? (1 or spec ID): "

# User chooses existing spec 007
# System does:
# 1. Copies enhancement to specs/007/enhancements/001-name/
# 2. Generates plan.md and tasks.md
# 3. Displays summary

# User proceeds:
/supervisor:start 007
```

### Example 3: Implement from Refactor

```bash
# User has approved refactor in docs/refactors/02-approved/
/implementation:implement --refactor 001

# System does:
# 1. Finds refactor file
# 2. Determines it belongs to existing spec 005
# 3. Copies refactor to specs/005/refactors/001-name/
# 4. Generates plan.md and tasks.md
# 5. Displays summary

# User proceeds:
/supervisor:start 005
```

## Troubleshooting

### Issue: "Enhancement not found"
**Problem**: Can't find enhancement file matching provided ID
**Solution**:
```bash
# List all enhancements
/enhancement:list

# Check if enhancement exists
find docs/enhancements -name "*001*.md"

# Ensure enhancement is in 02-approved/ or 03-in-progress/
ls docs/enhancements/02-approved/
```

### Issue: "Agent didn't generate plan.md"
**Problem**: Agent invocation failed or agent couldn't read proposal
**Solution**:
```bash
# Check if proposal file exists
ls specs/{id}/enhancements/{id}-{slug}/enhancement.md

# Manually read proposal to verify it's valid
cat specs/{id}/enhancements/{id}-{slug}/enhancement.md

# Re-run just the agent part (manual workaround)
# The agent should read the proposal and generate plan.md + tasks.md
```

### Issue: "Don't know if I should create new spec or add to existing"
**Problem**: Uncertainty about spec organization
**Solution**:

**Create new spec when:**
- Enhancement introduces entirely new feature/component
- No existing spec covers this domain
- Represents new product capability

**Add to existing spec when:**
- Enhancement extends existing feature
- Refines/improves existing component
- Part of same feature area

**Example:**
- New spec: "Add Redis caching" (new infrastructure)
- Existing spec: "Add caching headers to API responses" (extends existing spec 003-api-endpoints)

## Related Subsystems

- **Enhancement**: Handles enhancement lifecycle (proposal → approved → in-progress → completed)
- **Refactoring**: Handles refactor lifecycle and analysis
- **Idea**: Handles lightweight brainstorming before commitment
- **Supervisor**: Orchestrates multi-agent implementation
- **Iterate**: Organizes tasks into parallel layers
- **Core**: Provides spec creation and project setup

## Workflow Diagram

```
┌──────────────┐
│     IDEA     │
│ (lightweight │
│ brainstorm)  │
└──────┬───────┘
       │
       │ /idea:promote
       │ (manual or auto via /implement)
       ↓
┌──────────────┐     ┌──────────────┐
│ ENHANCEMENT  │     │   REFACTOR   │
│  (approved)  │     │  (approved)  │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    │
       └────────┬───────────┘
                │
                │ /implementation:implement
                │ (ORCHESTRATOR)
                ↓
       ┌────────────────────┐
       │ Mechanical Ops:    │
       │ /enhancement:spec  │
       │ /refactoring:spec  │
       │ (copy files)       │
       └────────┬───────────┘
                │
                ↓
       ┌────────────────────┐
       │ Intelligent Ops:   │
       │ enhancement-spec-  │
       │ creator agent      │
       │ (generate plan +   │
       │ tasks)             │
       └────────┬───────────┘
                │
                ↓
       ┌────────────────────┐
       │   SPEC READY       │
       │   plan.md          │
       │   tasks.md         │
       └────────┬───────────┘
                │
                │ Optional: /iterate:tasks
                ↓
       ┌────────────────────┐
       │ layered-tasks.md   │
       │ (parallel work)    │
       └────────┬───────────┘
                │
                │ /supervisor:start
                ↓
       ┌────────────────────┐
       │ IMPLEMENTATION     │
       │ (multi-agent work) │
       └────────────────────┘
```

## Design Decisions

### Why separate mechanical and intelligent operations?

**Mechanical operations** (file copying, directory creation):
- Should be 100% consistent
- Should be scriptable and repeatable
- Should never vary based on content
- Handled by `/enhancement:spec` and `/refactoring:spec`

**Intelligent operations** (planning, task breakdown):
- Requires understanding proposal content
- Needs to make technical decisions
- Should adapt to proposal complexity
- Handled by `enhancement-spec-creator` and `refactor-spec-creator` agents

**Benefits of separation:**
- Clear responsibilities
- Easy to test mechanical parts in isolation
- Easy to improve AI planning without touching file operations
- Reusable - other commands can use mechanical operations

### Why auto-promote ideas?

Ideas are **lightweight brainstorming** - no commitment. When you run `/implement --idea X`, you're saying "I want to actually build this", which is commitment. At that point, it should be an enhancement.

Auto-promotion saves a manual step and makes the workflow seamless.

### Why interactive prompts for spec selection?

The system can't always determine if a proposal should be a new spec or added to existing spec. This is a **strategic decision** that requires human judgment:

- Does this belong with existing work?
- Is this a new feature area?
- Should we keep specs focused or broad?

Interactive prompts give users control while still automating everything else.

## Future Enhancements

Planned features for this subsystem:

- [ ] **AI-powered spec matching** - Use AI to suggest which existing spec a proposal belongs to
- [ ] **Batch implementation** - `/implement --enhancement 001,002,003` to process multiple at once
- [ ] **Template selection** - Choose between minimal vs comprehensive plan templates
- [ ] **Direct implementation** - `--no-prompt` flag to skip confirmations
- [ ] **Status tracking** - Track which proposals have been implemented
- [ ] **Rollback** - `/implement:undo` to reverse an implementation
- [ ] **Dry run** - `--dry-run` to preview without creating files
- [ ] **CI/CD integration** - Auto-implement approved proposals via GitHub Actions

## Version History

- **v1.0.0** (2025-10-18) - Initial implementation subsystem
  - `/implementation:implement` command
  - Integration with enhancement and refactoring subsystems
  - Agent delegation for intelligent planning
  - Interactive spec selection
