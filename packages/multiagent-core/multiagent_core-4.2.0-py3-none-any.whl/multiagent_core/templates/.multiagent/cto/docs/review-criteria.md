# CTO Review Criteria

This document defines the evaluation criteria used by the cto-reviewer agent when performing architectural reviews.

## Review Dimensions

### 1. System Architecture

**What we evaluate:**
- Component decoupling and separation of concerns
- Adherence to established architectural patterns (MVC, microservices, event-driven, etc.)
- Layer boundaries and responsibilities
- Design pattern consistency across the codebase
- Scalability beyond MVP (can it handle 10x, 100x load?)

**Questions to answer:**
- Are components properly decoupled?
- Is there clear separation of concerns?
- Will this architecture scale beyond the initial launch?
- Are we following consistent design patterns?

**Red flags:**
- God objects or classes
- Tight coupling between unrelated components
- No clear architectural pattern
- Architecture works for MVP but won't scale

---

### 2. Dependencies & Interconnections

**What we evaluate:**
- Dependency graph validation (detect circular dependencies)
- Integration points with existing subsystems
- External service dependencies
- Shared state management
- Module boundaries and contracts

**Questions to answer:**
- Are dependencies clearly identified and documented?
- Are there circular dependencies?
- Do related features properly integrate?
- Are integration points well-defined?

**Red flags:**
- Circular dependency chains (A → B → C → A)
- Unclear or missing integration points
- Features that should connect but don't mention each other
- Shared mutable state across modules

---

### 3. Data Flow

**What we evaluate:**
- Logical data flow from input to output
- Database query patterns (N+1 detection)
- Caching strategy appropriateness
- State management clarity
- Data transformation steps

**Questions to answer:**
- Does data flow make logical sense?
- Are there bottlenecks in data processing?
- Is caching used appropriately?
- Is the database schema optimal?

**Red flags:**
- N+1 query patterns (fetching related data in loops)
- Missing caching for frequently accessed data
- Unclear data transformation logic
- Inefficient database queries

---

### 4. Performance & Scalability

**What we evaluate:**
- Expected load vs. current design capacity
- Async/await usage for I/O-bound operations
- Resource consumption (memory, CPU, network)
- Database indexing strategy
- Rate limiting and throttling

**Questions to answer:**
- Will this perform at expected scale?
- Are async patterns used for I/O operations?
- Is resource usage reasonable?
- Are appropriate indexes defined?

**Red flags:**
- Synchronous blocking calls for I/O
- Missing indexes on frequently queried fields
- No rate limiting on public APIs
- Memory leaks or unbounded growth

---

### 5. Security & Compliance

**What we evaluate:**
- Authentication and authorization patterns
- Input validation and sanitization
- Secrets management (environment variables, not hardcoded)
- OWASP compliance checklist
- Data privacy and PII handling

**Questions to answer:**
- Are auth/authz patterns correct?
- Is input properly validated?
- Are secrets managed securely?
- Does it comply with security standards?

**Red flags:**
- Hardcoded API keys or secrets
- Missing input validation
- SQL injection vulnerabilities
- Exposed sensitive data in logs
- No authentication on sensitive endpoints

---

### 6. Maintainability

**What we evaluate:**
- Code organization and file structure
- API contracts and interface clarity
- Testing strategy completeness
- Documentation quality
- Error handling patterns

**Questions to answer:**
- Is code well-organized?
- Are contracts clear and documented?
- Is testing strategy adequate?
- Is error handling comprehensive?

**Red flags:**
- No tests or very low coverage
- Missing or outdated documentation
- Unclear API contracts
- Inconsistent error handling
- Poor code organization

---

## Risk Severity Levels

### Critical (Blocker)

**Must fix before implementation**

Examples:
- Security vulnerabilities (SQL injection, XSS, hardcoded secrets)
- Circular dependencies that cause deadlocks
- Data loss scenarios
- Scalability showstoppers (won't handle expected load)

**Action**: Block implementation until fixed

---

### High (Important)

**Should fix soon, can proceed with caution**

Examples:
- Performance bottlenecks (N+1 queries)
- Missing integration points
- Insufficient error handling
- Inadequate testing coverage

**Action**: Can proceed but must be addressed in next iteration

---

### Medium (Nice-to-have)

**Future enhancement, doesn't block**

Examples:
- Code organization improvements
- Additional caching layers
- Documentation gaps
- Minor refactoring opportunities

**Action**: Document for future iteration, proceed with implementation

---

### Low (Optional)

**Consider if time permits**

Examples:
- Style consistency improvements
- Comment improvements
- Nice-to-have features
- Minor optimization opportunities

**Action**: Optional improvements, no action required

---

## Decision Matrix: Does This Need Review?

### ✅ MUST REVIEW

- Major features (>50 tasks)
- New architectural patterns not used before
- Cross-subsystem integrations
- Security-sensitive features (auth, payments, PII handling)
- Performance-critical systems (real-time, high-throughput)
- Data model changes (schema migrations)
- External service integrations
- API contract changes

### ⚠️ SHOULD REVIEW

- Medium features (20-50 tasks)
- New external dependencies
- Significant refactors
- State management changes
- New database tables/collections

### ❌ SKIP REVIEW

- Trivial bug fixes (<5 tasks)
- Documentation-only changes
- UI-only changes (no backend impact)
- Prototype/POC work (will be rewritten)
- Configuration changes
- Simple CRUD operations using established patterns

---

## Review Output Standards

Every CTO review MUST include:

1. **Executive Summary** - 2-3 paragraphs high-level assessment
2. **Architectural Analysis** - Strengths, concerns, recommendations
3. **Integration Points** - What connects to what
4. **Dependency Assessment** - Dependency graph and issues
5. **Data Flow Review** - How data moves through the system
6. **Performance & Scalability** - Can it handle expected load?
7. **Security Assessment** - Security posture evaluation
8. **Maintainability Assessment** - Can we maintain this long-term?
9. **Identified Risks** - Categorized by severity
10. **Required Changes** - Specific, actionable recommendations
11. **Approval Decision** - Clear decision with conditions

---

## Review Philosophy

### Think System-Wide

Don't just review the spec in isolation. Consider:
- How does this fit into the overall system architecture?
- What other features does this affect?
- Are there ripple effects we need to consider?

### Be Pragmatic

Balance ideal architecture with practical constraints:
- MVP constraints vs. long-term scalability
- Time-to-market vs. perfect solution
- Technical debt vs. feature delivery

### Be Specific

Bad: "Improve performance"
Good: "Add Redis caching for user session lookups to reduce database load from 1000 queries/sec to ~50 queries/sec"

Bad: "Add tests"
Good: "Add integration tests for the payment flow covering successful charges, failed charges, and refunds"

### Focus on Risk

Not every decision needs to be perfect. Focus on:
- High-risk areas (security, data loss, scalability)
- Critical paths (user flows, core functionality)
- Integration points (where systems connect)

### Enable, Don't Block

Your job is to:
- Catch critical issues early (cheap to fix)
- Provide actionable guidance
- Enable better decisions

NOT to:
- Block progress unnecessarily
- Demand perfection
- Nitpick implementation details

### Teach, Don't Just Judge

Explain WHY something is a concern:
- "This creates a circular dependency because..."
- "This won't scale because..."
- "This is a security risk because..."

Not just THAT it's a concern:
- "This is wrong"
- "Don't do it this way"

---

## Common Review Patterns

### Pattern: Missing Integration

**Symptom**: Feature A and Feature B should connect but don't mention each other

**Analysis**:
- Read both specs
- Identify logical connection points
- Document missing integration

**Recommendation**: Add integration section to both specs

---

### Pattern: N+1 Query

**Symptom**: Fetching related data in a loop

**Analysis**:
- Review data access patterns
- Estimate query count at scale
- Calculate performance impact

**Recommendation**: Use eager loading or batch fetching

---

### Pattern: Hardcoded Configuration

**Symptom**: API keys, URLs, or config in code

**Analysis**:
- Security risk assessment
- Environment-specific values in code
- No way to change without redeployment

**Recommendation**: Move to environment variables or config files

---

### Pattern: No Error Handling

**Symptom**: Happy path only, no error cases

**Analysis**:
- What happens when API call fails?
- What happens when database is down?
- What happens with invalid input?

**Recommendation**: Add comprehensive error handling and recovery

---

## Anti-Patterns to Avoid

❌ **Generic reviews** - Could apply to any project
✅ **Specific reviews** - Reference actual files and decisions

❌ **Perfectionism** - Demand gold-plating
✅ **Pragmatism** - Distinguish must-fix from nice-to-have

❌ **Implementation focus** - Review code style
✅ **Architecture focus** - Review design patterns and system integration

❌ **Incomplete specs** - Review vague or missing sections
✅ **Complete specs** - Require sufficient detail before review

❌ **Blocking trivial changes** - Review everything
✅ **Intelligent filtering** - Skip trivial, review important
