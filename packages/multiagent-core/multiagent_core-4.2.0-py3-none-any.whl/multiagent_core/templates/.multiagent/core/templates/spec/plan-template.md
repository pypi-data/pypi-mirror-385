# Implementation Plan: {{FEATURE_NAME}}

**Spec**: `{{SPEC_NUMBER}}-{{FEATURE_SLUG}}`
**Created**: {{DATE}}
**Branch**: {{BRANCH}}
**Prerequisites**: `spec.md` (read requirements and scenarios)

---

## Summary

{{DESCRIPTION}}

[Brief technical approach to implement the requirements from spec.md]

---

## Technical Context

**Language/Stack**: [e.g., Python 3.11, TypeScript/Next.js, Rust, etc.]
**Key Dependencies**: [e.g., FastAPI, React, tokio, etc.]
**Storage** (if applicable): [e.g., PostgreSQL, MongoDB, Redis, file-based, none]
**Testing Framework**: [e.g., pytest, vitest, cargo test]
**Deployment Target**: [e.g., Docker, serverless, native binary, browser]

**Project Type**:
- [ ] Framework/Subsystem (multiagent-core itself)
- [ ] Web App (frontend + backend)
- [ ] API Platform (backend only)
- [ ] CLI Tool (command-line)
- [ ] Integration (webhooks, workflows)
- [ ] Other: [specify]

---

## Architecture Approach

### High-Level Design
[Describe the overall approach - what components/modules/services are needed]

### Key Components
1. **[Component 1]**: [Purpose and responsibility]
2. **[Component 2]**: [Purpose and responsibility]
3. **[Component 3]**: [Purpose and responsibility]

### Data Flow (if applicable)
```
[User/System] → [Component A] → [Component B] → [Storage/Output]
```

---

## Project Structure

### For Framework/Subsystem Work
```
multiagent_core/templates/.multiagent/{{FEATURE_SLUG}}/
├── commands/           # Slash commands
├── agents/             # Agent definitions
├── scripts/            # Bash scripts
├── templates/          # File templates
└── docs/               # Documentation
```

### For Application Work
```
src/                    # Source code
├── [components/modules based on architecture]
└── ...

tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── e2e/               # End-to-end tests (if applicable)
```

---

## Implementation Strategy

### Phase 1: Foundation
[What needs to be set up first - structure, dependencies, core models]

### Phase 2: Core Implementation
[Main functionality implementation]

### Phase 3: Integration
[Connecting components, middleware, error handling]

### Phase 4: Testing & Polish
[Tests, documentation, performance optimization]

---

## Testing Strategy

### Test Types Needed
- [ ] Unit tests for [specific components]
- [ ] Integration tests for [workflows]
- [ ] Contract tests for [APIs/interfaces]
- [ ] E2E tests for [user scenarios]

### Test-First Approach
- Write failing tests before implementation
- Each requirement from spec.md should have corresponding test
- Tests validate acceptance scenarios

---

## Dependencies & Prerequisites

### Technical Dependencies
- [Dependency 1]: [Why needed]
- [Dependency 2]: [Why needed]

### External Requirements
- [API access, credentials, etc.]

### Assumptions
- [Any assumptions made in this plan]

---

## Risks & Considerations

### Technical Risks
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]

### Complexity Notes
- [Any areas of high complexity]
- [Areas requiring special attention]

---

## Next Steps

1. Review this plan for completeness
2. Create task breakdown: `tasks.md`
3. Optional: `/iterate:tasks {{SPEC_NUMBER}}-{{FEATURE_SLUG}}` to create layered-tasks.md for multi-agent work
4. Start implementation: `/supervisor:start {{SPEC_NUMBER}}-{{FEATURE_SLUG}}`
