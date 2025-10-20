# Tasks: {{FEATURE_NAME}}

**Spec**: `{{SPEC_NUMBER}}-{{FEATURE_SLUG}}`
**Generated**: {{DATE}}
**Prerequisites**: `plan.md` (read technical approach and architecture)

---

## Task Format

Tasks use the format: `[ID] [P?] Description with file path`
- **[P]**: Task can run in parallel (different files, no dependencies)
- File paths should be specific (e.g., `src/models/user.py`, not just "user model")

---

## Phase 1: Setup & Foundation

- [ ] T001 Create project structure per plan.md
- [ ] T002 Initialize dependencies and configuration
- [ ] T003 [P] Set up linting and formatting tools
- [ ] T004 [P] Set up testing framework

## Phase 2: Core Implementation

### Tests First (if following TDD)
- [ ] T005 [P] Write test for [feature/component] in tests/
- [ ] T006 [P] Write test for [feature/component] in tests/
- [ ] T007 [P] Write integration test for [workflow] in tests/

### Implementation
- [ ] T008 [P] Implement [component] in src/[path]
- [ ] T009 [P] Implement [component] in src/[path]
- [ ] T010 Implement [feature that depends on T008/T009]
- [ ] T011 Add input validation
- [ ] T012 Add error handling

## Phase 3: Integration & Polish

- [ ] T013 Connect [component A] to [component B]
- [ ] T014 Add logging and monitoring
- [ ] T015 [P] Write additional unit tests in tests/unit/
- [ ] T016 [P] Update documentation in docs/ or README.md
- [ ] T017 Performance optimization (if needed)
- [ ] T018 Manual testing and validation

---

## Dependencies

Document task dependencies:
- T010 depends on T008, T009
- Tests (T005-T007) should pass after T008-T012
- T013 requires completed T008-T012

---

## Notes

### Working Solo
Work through tasks sequentially. Commit after each task completion.

### Working with Multi-Agent
Run `/iterate:tasks {{SPEC_NUMBER}}-{{FEATURE_SLUG}}` to convert this into `layered-tasks.md` with:
- Tasks organized into non-blocking layers
- Agent assignments (@claude, @copilot, @qwen, etc.)
- Parallel execution strategy

Then run `/supervisor:start {{SPEC_NUMBER}}-{{FEATURE_SLUG}}` to begin multi-agent work.

---

## Task Generation Guidelines

When filling in tasks:
1. Be specific about file paths
2. Mark [P] only if truly independent (different files, no shared state)
3. Tests before implementation (TDD approach)
4. Each task should be completable in one sitting
5. Break down large tasks into smaller ones

---

## Next Steps

1. Fill in specific tasks based on plan.md
2. Choose workflow:
   - **Solo**: Work through tasks sequentially
   - **Multi-agent**: Run `/iterate:tasks {{SPEC_NUMBER}}-{{FEATURE_SLUG}}`
3. Start work: `/supervisor:start {{SPEC_NUMBER}}-{{FEATURE_SLUG}}`
