# Layering Philosophy

## Purpose

This document explains the core principles behind the iterate subsystem's task layering approach - transforming sequential task lists into parallel, non-blocking agent workflows.

---

## Core Principles

### 1. Infrastructure First

**Principle**: Build foundational components before dependent features.

**Why**: Prevents rework when dependencies change. Creates stable base for parallel development.

**Example**:
```
❌ Bad:
Layer 1: @claude Build user dashboard
Layer 2: @codex Create authentication system

✅ Good:
Layer 1: @codex Create authentication system
Layer 2: @claude Build user dashboard (depends on auth)
```

---

### 2. Use Before Build

**Principle**: Implement consumers after providers are complete.

**Why**: Ensures APIs and interfaces exist before code tries to use them.

**Example**:
```
❌ Bad:
Layer 1: @claude Call API endpoint /users
Layer 2: @codex Implement /users endpoint

✅ Good:
Layer 1: @codex Implement /users endpoint
Layer 2: @claude Call API endpoint /users
```

---

### 3. Non-Blocking Parallelism

**Principle**: Tasks in the same layer can be worked on simultaneously without conflicts.

**Why**: Maximizes agent productivity. Reduces waiting time.

**Example**:
```
Layer 1 (Parallel):
  - @claude Setup database schema
  - @qwen Configure Redis cache
  - @gemini Initialize API routing

All three can work simultaneously - no dependencies between them.
```

---

### 4. Complexity-Based Assignment

**Principle**: Match task complexity to agent capabilities.

**Agent Capabilities**:
- **@claude** (45%): Complex architecture, integration, system design
- **@copilot** (30%): Standard implementation, boilerplate
- **@qwen** (15%): Performance optimization, efficiency
- **@gemini** (10%): Research, documentation, analysis
- **@codex** (0%): Interactive TDD, special cases only

**Why**: Ensures efficient resource allocation and quality outcomes.

---

## Layering Rules

### Rule 1: Same-Layer Independence

Tasks in the same layer MUST NOT depend on each other.

```
✅ Valid Layer:
  - T001 @claude Create user model
  - T002 @codex Create product model
  - T003 @qwen Create order model

(All independent database models)

❌ Invalid Layer:
  - T004 @claude Create user service
  - T005 @codex Call user service from controller

(T005 depends on T004 - must be in later layer)
```

---

### Rule 2: Cross-Layer Dependencies

Tasks in later layers CAN depend on earlier layers.

```
Layer 1:
  - T001 @claude Create API client

Layer 2:
  - T002 @codex Use API client in service ✅
  (Depends on T001 from Layer 1)
```

---

### Rule 3: Preserve Task Numbers

**CRITICAL**: Original task numbers (T001, T002, etc.) MUST be preserved during layering.

**Why**: Traceability, audit trail, issue tracking.

```
❌ Wrong:
Original: T015 Create authentication
Layered:  T001 Create authentication  (renumbered!)

✅ Correct:
Original: T015 Create authentication
Layered:  T015 Create authentication  (preserved!)
```

---

## Workflow Patterns

### Pattern 1: Three-Phase Workflow

```
Phase 1: /iterate:tasks
  → Analyze tasks.md
  → Apply layering rules
  → Create agent-tasks/layered-tasks.md

Phase 2: /iterate:sync
  → Update plan.md
  → Update quickstart.md
  → Create current-tasks.md symlink

Phase 3: /iterate:adjust
  → Handle live changes
  → Backup previous iteration
  → Re-run Phase 1 + 2
```

---

### Pattern 2: Multi-Spec Support

```bash
# Single spec
/iterate:tasks 005

# Multiple specs
/iterate:tasks 005,007,009

# All specs
/iterate:tasks --all
```

---

### Pattern 3: Iteration Tracking

```
First iteration:
  agent-tasks/layered-tasks.md

After adjustment:
  agent-tasks/iteration-1-tasks.md (backup)
  agent-tasks/layered-tasks.md (new version)

After another adjustment:
  agent-tasks/iteration-1-tasks.md
  agent-tasks/iteration-2-tasks.md (backup)
  agent-tasks/layered-tasks.md (new version)
```

---

## Common Anti-Patterns

### Anti-Pattern 1: Front-End First

```
❌ Wrong:
Layer 1: Build UI components
Layer 2: Create API endpoints

Problem: UI built before backend exists. Will need rework.

✅ Right:
Layer 1: Create API endpoints
Layer 2: Build UI components

Benefit: UI built against stable API.
```

---

### Anti-Pattern 2: Monolithic Layers

```
❌ Wrong:
Layer 1: 45 tasks (all agents)

Problem: No parallelism benefit. Bottleneck.

✅ Right:
Layer 1: 15 tasks (foundation)
Layer 2: 20 tasks (implementation)
Layer 3: 10 tasks (integration)

Benefit: Staged progress. Clear milestones.
```

---

### Anti-Pattern 3: Circular Dependencies

```
❌ Wrong:
Layer 1: T001 Service A calls Service B
Layer 2: T002 Service B calls Service A

Problem: Circular dependency. Cannot complete either.

✅ Right:
Layer 1: T001 Create Service A
Layer 2: T002 Create Service B
Layer 3: T003 Integrate A → B

Benefit: Clear dependency flow.
```

---

## Success Criteria

A well-layered spec has:

1. ✅ **Clear layer boundaries** - Each layer has distinct purpose
2. ✅ **Balanced distribution** - No single agent overloaded
3. ✅ **No circular dependencies** - Clean dependency graph
4. ✅ **Preserved task IDs** - Original numbering maintained
5. ✅ **Realistic workload** - Agent assignments match complexity
6. ✅ **Maximum parallelism** - Tasks in same layer are independent

---

## Examples

### Example 1: API Development

```markdown
## Layer 1: Foundation (Parallel - No dependencies)
- T001 @claude Database schema design
- T002 @qwen Redis caching setup
- T003 @codex API routing configuration

## Layer 2: Implementation (Depends on Layer 1)
- T004 @claude User authentication service
- T005 @copilot Product catalog service
- T006 @qwen Order processing service

## Layer 3: Integration (Depends on Layer 2)
- T007 @claude Integrate auth across services
- T008 @codex End-to-end API tests
```

---

### Example 2: Frontend Development

```markdown
## Layer 1: Foundation (Parallel - No dependencies)
- T010 @claude Component library setup
- T011 @qwen State management (Redux/Zustand)
- T012 @copilot API client generation

## Layer 2: Core Components (Depends on Layer 1)
- T013 @claude Authentication flow UI
- T014 @copilot Dashboard layout
- T015 @codex Form components

## Layer 3: Features (Depends on Layer 2)
- T016 @claude User profile page
- T017 @copilot Settings page
- T018 @qwen Performance optimization
```

---

## References

- **Main README**: `multiagent_core/templates/.multiagent/iterate/README.md`
- **Workflow Patterns**: `docs/workflow-patterns.md`
- **Integration Guide**: `docs/integration-guide.md`
- **Build Standards**: `docs/architecture/02-development-guide.md`
