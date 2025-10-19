# Agent Coordination Infrastructure

## Purpose

Provides the foundational infrastructure for multi-agent coordination, including git worktree management, branching protocols, commit workflows, and agent startup configurations. This subsystem enables multiple AI agents to work in parallel without conflicts.

## What It Does

1. **Agent Configuration** - Defines agent roles, responsibilities, and startup prompts
2. **Git Coordination** - Provides worktree and branching protocols for parallel work
3. **Commit Standards** - Enforces consistent commit formats and co-authorship
4. **Workflow Automation** - Git hooks guide agents through proper workflows

## Key Components

### Agent Definitions

Each AI agent has:
- **Specialization** - Defined role (backend, frontend, optimization, research)
- **Startup Prompt** - Initial instructions loaded when agent begins work
- **Responsibilities** - Specific tasks aligned to agent strengths
- **Coordination Rules** - How to work with other agents

### Git Coordination

**Worktree Management:**
- Isolated workspaces for each agent (e.g., `../project-claude`, `../project-qwen`)
- Independent branches without merge conflicts
- Shared main branch for integration

**Branching Protocol:**
- Branch naming: `agent-{agent-name}-{spec-number}` (e.g., `agent-claude-001`)
- Feature branches from main
- PR-based integration

## Architecture

```
.multiagent/agents/
├── docs/                           # Coordination guides
│   ├── coordination.md           # Multi-agent coordination patterns
│   ├── git-worktree.md          # Worktree setup & management
│   ├── branching.md             # Branching strategy
│   ├── branch-protocol.md       # Branch naming & lifecycle
│   ├── commit-workflow.md       # Commit standards & format
│   └── git-hooks.md             # Hook functionality guide
│
├── hooks/                         # Git hooks
│   └── post-commit              # Post-commit guidance hook
│
├── prompts/                       # Agent startup prompts
│   ├── README.md                # Prompt system overview
│   ├── claude-startup.txt       # @claude initialization
│   ├── copilot-startup.txt      # @copilot initialization
│   ├── qwen-startup.txt         # @qwen initialization
│   ├── gemini-startup.txt       # @gemini initialization
│   └── codex-startup.txt        # @codex initialization
│
└── templates/                     # Configuration templates
    └── agent-responsibilities.yaml  # Agent role definitions
```

## Agent Specializations

### @claude (CTO-level)
- **Role**: Architecture, code review, strategic planning
- **Tasks**: Complex features, integration oversight, quality gates
- **Complexity**: 8-10

### @qwen (Performance Engineer)
- **Role**: Performance optimization, query tuning
- **Tasks**: Algorithm optimization, database queries, caching
- **Complexity**: 6-8

### @gemini (Research & Docs)
- **Role**: Research, documentation, accessibility
- **Tasks**: Technical research, doc writing, design systems
- **Complexity**: 4-7

### @codex (Database Specialist)
- **Role**: Database schema, migrations, data modeling
- **Tasks**: Schema design, complex queries, data integrity
- **Complexity**: 5-8

### @copilot (Implementation)
- **Role**: Simple implementation tasks
- **Tasks**: CRUD operations, basic components, straightforward logic
- **Complexity**: 1-3

## Coordination Workflows

### 1. Worktree Setup

```bash
# Main agent creates worktrees for parallel work
.multiagent/iterate/scripts/setup-spec-worktrees.sh 001

# Creates isolated worktrees:
# ../project-claude  (branch: agent-claude-001)
# ../project-qwen    (branch: agent-qwen-001)
# ../project-codex   (branch: agent-codex-001)
```

### 2. Task Assignment

Agents check layered tasks for their assignments:

```bash
# Each agent in their worktree:
cd ../project-claude
grep "@claude" specs/001-*/agent-tasks/layered-tasks.md

# Implement assigned tasks
# Commit work regularly with proper format
```

### 3. Commit Format

All agents use standardized commit format:

```bash
git commit -m "[WORKING] feat: implement auth system

Related to #123

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: @qwen <noreply@anthropic.com>
Co-Authored-By: @gemini <noreply@anthropic.com>"
```

**State Markers:**
- `[STABLE]` - Production ready
- `[WORKING]` - Functional, needs testing
- `[WIP]` - Work in progress
- `[HOTFIX]` - Emergency fix

### 4. Integration via PRs

```bash
# Agent completes work in worktree
cd ../project-claude
git push -u origin agent-claude-001

# Create PR for review
gh pr create --title "feat: implement auth system"

# Main agent reviews and merges
# Other agents rebase on updated main
```

## Git Hooks

### post-commit Hook

Automatically provides guidance after each commit:

**Triggers:**
- After every `git commit`

**Actions:**
- Reminds agent of next steps
- Suggests relevant commands
- Provides coordination tips

**Example Output:**
```
✅ Commit successful!

Next steps:
- Continue with assigned tasks from layered-tasks.md
- Run tests: /testing:test --quick
- Update docs if needed: /docs:update
- Coordinate with other agents via PR comments
```

## Agent Startup Prompts

Each agent loads context-specific prompts when starting work:

**claude-startup.txt:**
- CTO-level responsibilities
- Architecture decision-making guidance
- Code review standards
- Quality gate enforcement

**qwen-startup.txt:**
- Performance optimization focus
- Benchmarking guidelines
- Query optimization patterns

**gemini-startup.txt:**
- Research methodologies
- Documentation standards
- Accessibility guidelines

**codex-startup.txt:**
- Database design patterns
- Schema normalization rules
- Migration best practices

**copilot-startup.txt:**
- Simple task implementation
- Code consistency rules
- Common patterns library

## Coordination Patterns

### Task Handoffs

Tasks flow between agents based on dependencies:

```markdown
- [x] T025 @claude Database schema design complete ✅
- [ ] T026 @codex Implement schema (depends on T025)
- [ ] T027 @qwen Optimize queries (depends on T026)
```

### Parallel Execution

Independent tasks run concurrently:

```markdown
# Foundation Layer (Parallel)
- [ ] T001 @claude API architecture
- [ ] T002 @codex Database schema
- [ ] T003 @gemini Design system

# Implementation Layer (After foundation)
- [ ] T010 @claude Core business logic (depends on T001)
- [ ] T011 @qwen Performance optimization (depends on T002)
```

### Communication

Agents coordinate via:
- **Task comments** in layered-tasks.md
- **PR comments** during code review
- **Commit messages** with context
- **Branch naming** for clarity

## Best Practices

1. **Pull Before Starting** - Always `git pull` before beginning work
2. **Check Dependencies** - Verify prerequisite tasks are complete
3. **Small Commits** - Commit frequently with clear messages
4. **Test Early** - Run tests after significant changes
5. **Document Changes** - Update docs for new patterns
6. **Coordinate** - Use task comments to communicate blockers

## Troubleshooting

### Worktree Conflicts

```bash
# List all worktrees
git worktree list

# Remove stale worktree
git worktree remove ../project-agent

# Prune invalid references
git worktree prune
```

### Branch Issues

```bash
# Check branch status
git status

# Sync with main
git checkout main
git pull origin main
git checkout agent-claude-001
git rebase main
```

### Commit Format Errors

```bash
# Amend last commit message
git commit --amend

# Use proper format with state marker and co-authors
```

## Integration with Other Subsystems

**Iterate System:**
- Uses agent definitions for task assignment
- Creates worktrees for parallel work
- Manages agent branches

**Supervisor System:**
- Monitors agent compliance with protocols
- Validates commit formats
- Checks coordination patterns

**Testing System:**
- Agents run tests in their worktrees
- Test results inform handoffs

**Documentation System:**
- Agent responsibilities guide doc assignment
- Prompts enforce documentation standards

## Related Documentation

- **Git Worktree Guide**: `docs/git-worktree.md`
- **Coordination Patterns**: `docs/coordination.md`
- **Commit Workflow**: `docs/commit-workflow.md`
- **Branching Strategy**: `docs/branching.md`

---

🤝 **Agent Coordination Infrastructure** - Enabling Parallel Multi-Agent Development
