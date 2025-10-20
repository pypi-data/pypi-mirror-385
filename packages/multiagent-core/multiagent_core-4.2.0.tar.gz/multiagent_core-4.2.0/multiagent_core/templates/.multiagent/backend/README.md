# Backend Development System

## Purpose

Provides backend API development guidance, database patterns, authentication strategies, and API design templates. Coordinates backend-focused development tasks and testing workflows.

## What It Does

1. **Design Guidance** - Provides patterns for API design, database schemas, authentication
2. **Task Coordination** - Routes backend tasks to appropriate agents via `/backend:develop`
3. **Testing Integration** - Coordinates with backend-tester agent for API validation
4. **Documentation** - Maintains API specifications and architecture patterns

## Agents Used

- **@claude/backend-tester** - Writes backend code, creates API tests, validates functionality, pushes to CI/CD
- **@qwen** - Performance optimization for backend services
- **@codex** - Database schema implementation
- **@copilot** - Simple backend tasks (CRUD operations, basic endpoints)

## Commands

- **`/backend:develop <spec-directory> [--role=agent]`** - Execute backend API tasks from spec layered-tasks.md
- **`/backend:test <spec-directory>`** - Execute backend API testing using backend-tester agent
- **`/backend:migrate [up|down|status|create <name>]`** - Run database migrations
- **`/backend:seed [--development|--test]`** - Seed database with test data
- **`/backend:api-docs [--swagger|--openapi]`** - Generate API documentation

## Architecture

```
.multiagent/backend/
├── docs/                         # Backend design guides
│   ├── authentication.md        # Auth patterns & strategies
│   ├── api-design.md           # REST/GraphQL design principles
│   └── database-patterns.md    # Database schema & query patterns
│
└── templates/                   # Architecture templates
    ├── API_SPEC.md             # API specification template
    ├── DATABASE_SCHEMA.md      # Database schema template
    ├── SERVICE_ARCHITECTURE.md # Service layer patterns
    └── SECURITY_CHECKLIST.md   # Backend security validation
```

## How It Works

### Development Workflow

1. **Command Invocation**: User runs `/backend:develop 001 --role=claude`
2. **Task Assignment**: System reads `specs/001-*/agent-tasks/layered-tasks.md`
3. **Agent Routing**: Routes tasks marked `@claude` to Claude agent
4. **Implementation**: Agent implements backend features using templates/docs as guidance
5. **Testing**: After implementation, use `/backend:test 001` to validate

### Testing Workflow

1. **Test Command**: User runs `/backend:test 001`
2. **Subagent Spawns**: `backend-tester` agent activates
3. **Test Writing**: Agent creates comprehensive API tests
4. **Local Validation**: Runs tests locally to ensure they pass
5. **CI/CD Push**: Pushes changes to trigger CI/CD pipeline

## Provided Templates

### API_SPEC.md
Complete API specification template including:
- Endpoint definitions
- Request/response schemas
- Authentication requirements
- Rate limiting
- Error handling

### DATABASE_SCHEMA.md
Database design template with:
- Entity relationship diagrams
- Table definitions
- Index strategies
- Migration plan

### SERVICE_ARCHITECTURE.md
Service layer patterns including:
- Controller → Service → Repository pattern
- Dependency injection
- Error handling strategies
- Transaction management

### SECURITY_CHECKLIST.md
Backend security validation:
- Input validation
- SQL injection prevention
- Authentication/authorization
- Rate limiting
- CORS configuration

## Design Guides

### authentication.md
Comprehensive authentication patterns:
- JWT vs. session-based auth
- OAuth 2.0 / OpenID Connect
- API key management
- Role-based access control (RBAC)
- Password hashing (bcrypt, Argon2)

### api-design.md
API design principles:
- RESTful conventions
- GraphQL schema design
- Versioning strategies
- Pagination patterns
- Response formatting

### database-patterns.md
Database best practices:
- Schema normalization
- Index optimization
- Query performance
- Connection pooling
- Migration strategies

## Multi-Agent Backend Development

Backend tasks are distributed based on complexity and agent strengths:

**Foundation Layer** (Database & Core):
- `@codex` - Database schema implementation
- `@claude` - Core service architecture

**Implementation Layer** (Business Logic):
- `@claude` - Complex business logic
- `@copilot` - CRUD operations
- `@qwen` - Performance optimization

**Testing Layer**:
- `backend-tester` agent - Comprehensive API testing

## Usage Examples

### Develop Backend Features
```bash
# All agents work on their assigned backend tasks
/backend:develop 001

# Specific agent only
/backend:develop 001 --role=claude
```

### Test Backend APIs
```bash
# Execute backend testing tasks from spec
/backend:test 001

# The backend-tester agent will:
# - Write comprehensive API tests
# - Validate functionality locally
# - Push to trigger CI/CD
```

### Database Operations
```bash
# Create new migration
/backend:migrate create add_users_table

# Run migrations
/backend:migrate up

# Rollback
/backend:migrate down

# Check status
/backend:migrate status
```

### API Documentation
```bash
# Generate Swagger/OpenAPI docs
/backend:api-docs --swagger

# Generate OpenAPI 3.0 spec
/backend:api-docs --openapi
```

## Integration with Other Subsystems

**Testing System:**
- `/backend:test` spawns `backend-tester` agent
- Integrates with `/testing:test --backend`

**Deployment System:**
- Templates used for generating backend deployment configs
- API specs inform container configuration

**Security System:**
- Security checklist enforced during `/security:setup`
- Auth patterns integrated with security scanning

**Documentation System:**
- API specs generate developer documentation
- Architecture templates inform `/docs:init`

## Best Practices

1. **Use Templates** - Start with provided templates for consistency
2. **Follow Guides** - Reference authentication.md and api-design.md
3. **Test Early** - Use `/backend:test` during development
4. **Document APIs** - Generate API docs with `/backend:api-docs`
5. **Secure by Default** - Follow SECURITY_CHECKLIST.md

## Troubleshooting

### Command Not Working
```bash
# Verify spec exists
ls -la specs/001-*/

# Check for layered tasks
cat specs/001-*/agent-tasks/layered-tasks.md
```

### No Backend Tasks Found
```bash
# Ensure tasks are assigned to backend agents
grep "@claude" specs/001-*/agent-tasks/layered-tasks.md
grep "@codex" specs/001-*/agent-tasks/layered-tasks.md
```

### Testing Failures
```bash
# Run tests with verbose output
/backend:test 001 --verbose

# Check test configuration
cat .multiagent/testing/config.yml
```

## Related Documentation

- **Agent Coordination**: `.multiagent/agents/docs/`
- **Testing Strategy**: `.multiagent/testing/README.md`
- **Deployment**: `.multiagent/deployment/README.md`
- **Security**: `.multiagent/security/README.md`

---

🔧 **Backend Development System** - Part of MultiAgent Framework
