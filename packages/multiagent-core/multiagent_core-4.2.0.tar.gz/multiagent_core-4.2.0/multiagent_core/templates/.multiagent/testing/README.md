# Testing System - Automated Test Generation

## Purpose

Generates test structure from tasks.md and provides intelligent test execution with automatic project detection (frontend/backend routing).

## What It Does

1. **Generates test files** - Creates test structure from specs/*/tasks.md
2. **Intelligent routing** - Detects project type (React/Next.js frontend, FastAPI/Django backend)
3. **Runs tests** - Executes appropriate test framework (pytest, vitest, playwright)
4. **Production validation** - Ensures no mocks/test data in production code

## Agents Used

- **@claude/test-generator** - Analyzes tasks and generates test structure
- **@claude/backend-tester** - Writes and runs API/backend tests
- **@claude/frontend-playwright-tester** - E2E testing with Playwright

## Commands

### Primary Commands
- `/testing-workflow --generate` - Generate test structure
- `/test --create` - Create tests for specific files
- `/test-generate --unit` - Generate unit tests
- `/test-generate --e2e` - Generate end-to-end tests

### Integration Points
- Called by `/project-setup` during initial setup
- Used by `/test-prod` for production readiness validation

## Complete Workflow

### First-Time Test Generation (New Project)
```bash
# Step 1: Generate test structure from tasks
/testing:test --create
# What this does: Analyzes tasks.md, creates test structure, generates test files
# Expected output: tests/backend/ and/or tests/frontend/ directories created
# Time: 2-5 minutes (uses agents)

# Step 2: Review generated tests
ls -la tests/backend/unit/
ls -la tests/frontend/e2e/
# Verify: Test files created for each feature
# Customize: Update assertions for your specific logic

# Step 3: Run tests to verify setup
/testing:test --quick
# Expected output: Tests run (may have failures needing customization)
# Time: 30-60 seconds
```

**Verification**: Test directories created, tests run without setup errors

### Regular Testing During Development
```bash
# Step 1: Quick test run (every commit)
/testing:test --quick
# What this does: Runs existing tests without creating new ones
# Expected output: Pass/fail results, coverage percentage
# Time: 30-60 seconds

# Step 2: If tests pass (✅ 100% green)
# Proceed with development or deployment
/deployment:deploy-prepare {spec}  # Next step if ready to deploy

# Step 3: If tests fail (❌ Failures detected)
# Fix failing tests
npm test path/to/failing-test.test.js  # Node.js
pytest tests/specific_test.py          # Python
# Then re-run: /testing:test --quick

# Step 4: If coverage low (<80%)
# Generate additional tests
/testing:test --create --unit
# Then re-run: /testing:test --quick
```

**Frequency**: Run before every commit, after every change

### Pre-Deployment Testing
```bash
# Step 1: Run full test suite
/testing:test --quick
# Must show: All tests passing

# Step 2: Validate production readiness
/testing:test-prod
# What this does: Scans for mocks/test data in production paths
# Expected output: No mocks found (or warnings about issues)
# Time: 30 seconds

# Step 3: Check coverage report
npm run test:coverage  # Node.js
pytest --cov=src --cov-report=html  # Python
# Open coverage report in browser
# Target: 80%+ coverage

# Step 4: Proceed with deployment validation
/deployment:deploy-validate
# Tests must pass before deployment
```

**Validation**: All tests green, no mocks in production, 80%+ coverage

### Frontend-Specific Testing
```bash
# Run only frontend tests
/testing:test --frontend
# Includes: Component tests (Jest/Vitest), E2E tests (Playwright)
# Time: 1-3 minutes

# Run E2E tests only
npm run test:e2e
# Or: npx playwright test
# Time: 2-5 minutes
```

### Backend-Specific Testing
```bash
# Run only backend tests
/testing:test --backend
# Includes: Unit tests, integration tests, API tests
# Time: 30-90 seconds

# Run specific test file
pytest tests/backend/unit/test_api.py -v
# Or: npm test tests/backend/unit/api.test.js
```

### Typical Testing Session
```
Initial:
  /testing:test --create        → Generate structure (5 min)
  Customize test assertions
  /testing:test --quick         → Verify setup (1 min)

During Development:
  Write feature code
  /testing:test --quick         → Run tests (30 sec)
  Fix any failures
  /testing:test --quick         → Re-test (30 sec)
  Repeat until green

Pre-PR:
  /testing:test --quick         → Full test run (1 min)
  /testing:test-prod            → Validate production (30 sec)
  Check coverage report
  /supervisor:end {spec}        → Overall validation
```

### Integration with Other Commands
```bash
# Complete feature workflow with testing:
/iterate:tasks 001              # Layer tasks
/supervisor:start 001           # Setup worktrees
# Agents develop features...
/testing:test --create          # Generate tests from tasks
/testing:test --quick           # Run generated tests
# Fix any test failures...
/supervisor:end 001             # Validate (includes test check)
/deployment:deploy-prepare 001  # Deploy (requires tests passing)
```

## Directory Structure

```
.multiagent/testing/
├── scripts/
│   ├── generate-tests.sh          # PRIMARY: Test generation with backend/frontend detection
│   ├── generate-mocks.sh          # Mock creation for dependencies
│   ├── test-coverage.sh           # Coverage reporting
│   └── archive/                   # Archived experimental variants (not used)
├── templates/
│   ├── jest/                      # Jest test templates
│   ├── pytest/                    # Pytest test templates
│   └── mocks/                     # Mock templates
├── memory/                        # Session state (JSON tracking)
└── logs/                          # Generation logs
```

## Outputs

### 1. Test Directory Structure (`tests/`)

Generated based on project type detection:

```
tests/
├── backend/                       # Backend tests (if backend detected)
│   ├── unit/                     # Backend unit tests
│   │   ├── api/                 # API endpoint tests
│   │   ├── services/            # Service layer tests
│   │   ├── models/              # Database model tests
│   │   └── middleware/          # Middleware tests
│   ├── integration/             # Backend integration tests
│   │   ├── database/            # DB integration tests
│   │   └── external/            # External API tests
│   └── e2e/                     # Backend E2E tests
│       └── workflows/           # API workflow tests
├── frontend/                      # Frontend tests (if frontend detected)
│   ├── unit/                     # Frontend unit tests
│   │   ├── components/          # Component tests
│   │   ├── hooks/               # React hooks tests
│   │   └── utils/               # Utility tests
│   ├── integration/             # Frontend integration tests
│   │   └── services/            # Service integration tests
│   └── e2e/                     # Frontend E2E tests (Playwright)
│       ├── flows/               # User flow tests
│       └── scenarios/           # Business scenarios
└── fixtures/                      # Shared test data
```

**Detection Logic**:
- **Backend detected**: Python files (`*.py`), FastAPI, Flask, Django, Express, NestJS
- **Frontend detected**: React, Vue, Angular, Next.js, package.json with UI dependencies
- If only backend → create only `tests/backend/`
- If only frontend → create only `tests/frontend/`
- If both → create both `tests/backend/` and `tests/frontend/`

### 2. Test Files Generated

| Language | Test Framework | File Pattern | Example |
|----------|---------------|--------------|---------|
| JavaScript | Jest | `*.test.js` | `api.test.js` |
| TypeScript | Jest | `*.test.ts` | `service.test.ts` |
| Python | Pytest | `test_*.py` | `test_api.py` |
| Go | Go test | `*_test.go` | `api_test.go` |

### 3. Test Configurations

| File | Purpose | When Created |
|------|---------|--------------|
| `jest.config.js` | Jest configuration | Node.js projects |
| `pytest.ini` | Pytest configuration | Python projects |
| `.coveragerc` | Coverage settings | Python projects |
| `vitest.config.js` | Vitest config | Vite projects |

### 4. Mock Files (`tests/mocks/`)

| Type | Purpose | Example |
|------|---------|---------|
| API mocks | Mock external APIs | `github-api.mock.js` |
| Database mocks | Mock DB operations | `db.mock.py` |
| Service mocks | Mock services | `auth-service.mock.ts` |

## How It Works

### 1. Project Analysis
```bash
# Script analyzes project structure
./scripts/generate-tests.sh specs/001-*
```

### 2. Stack Detection
- Reads `package.json` or `requirements.txt`
- Identifies test framework to use
- Selects appropriate templates

### 3. Test Generation
- Creates test files matching source structure
- Generates assertions based on function signatures
- Adds mock implementations for dependencies

### 4. Configuration
- Sets up test runner config
- Configures coverage thresholds
- Adds test scripts to package.json

## Template Variables

Templates use placeholders:
- `{{MODULE_NAME}}` - Module being tested
- `{{FUNCTION_NAME}}` - Function under test
- `{{TEST_FRAMEWORK}}` - Jest, Pytest, etc.
- `{{MOCK_TYPE}}` - Type of mock needed

## Example Generated Test

### JavaScript (Jest)
```javascript
describe('UserService', () => {
  let userService;
  let mockDatabase;

  beforeEach(() => {
    mockDatabase = createMockDatabase();
    userService = new UserService(mockDatabase);
  });

  describe('createUser', () => {
    it('should create a new user', async () => {
      const userData = { name: 'Test User' };
      const result = await userService.createUser(userData);

      expect(result).toHaveProperty('id');
      expect(mockDatabase.insert).toHaveBeenCalledWith('users', userData);
    });
  });
});
```

### Python (Pytest)
```python
import pytest
from unittest.mock import Mock, patch
from src.services.user_service import UserService

class TestUserService:
    @pytest.fixture
    def mock_database(self):
        return Mock()

    @pytest.fixture
    def user_service(self, mock_database):
        return UserService(database=mock_database)

    def test_create_user(self, user_service, mock_database):
        user_data = {"name": "Test User"}
        result = user_service.create_user(user_data)

        assert "id" in result
        mock_database.insert.assert_called_with("users", user_data)
```

## Integration with CI/CD

Tests are automatically run by GitHub workflows created by the core system:

1. **On Push**: Run unit tests
2. **On PR**: Run all tests + coverage
3. **Pre-deploy**: Run integration tests
4. **Post-deploy**: Run e2e tests

## Coverage Requirements

Default thresholds set in generated configs:
- **Statements**: 80%
- **Branches**: 75%
- **Functions**: 80%
- **Lines**: 80%

## Running Generated Tests

### Node.js Projects
```bash
npm test              # Run all tests
npm run test:unit     # Unit tests only
npm run test:e2e      # E2E tests only
npm run test:coverage # With coverage
```

### Python Projects
```bash
pytest                      # Run all tests
pytest tests/unit          # Unit tests only
pytest tests/integration   # Integration tests
pytest --cov=src           # With coverage
```

## Troubleshooting

### Tests Not Generated
```bash
# Re-run generation with spec
.multiagent/testing/scripts/generate-tests.sh specs/001-*
```

### Missing Mocks
```bash
# Generate mocks for external dependencies
.multiagent/testing/scripts/generate-mocks.sh
```

### Coverage Too Low
```bash
# Check coverage report
npm run test:coverage
# or
pytest --cov=src --cov-report=html
```

## Integration with Frontend Subsystem

The testing and frontend subsystems work together:

1. **Initial Setup** - `/testing:test-generate 001`:
   - Creates `tests/frontend/` structure from specs
   - Generates initial test files based on tasks
   - Sets up unit/, integration/, e2e/ directories

2. **Feature Development** - `/frontend:test 001`:
   - Checks `tests/frontend/e2e/001/` for existing tests
   - Reads existing test files to understand coverage
   - Creates ONLY NEW tests for uncovered features
   - Runs ALL tests (existing + new)
   - No duplication, works additively

3. **Centralized Location**:
   - ALL frontend tests in `tests/frontend/`
   - Organized by spec: `tests/frontend/e2e/{spec-dir}/`
   - Easy discovery for CI/CD
   - No tests scattered in `src/`

## Key Points

- **Testing owns tests/** - All test files in `tests/`
- **Stack-appropriate** - Jest for JS, Pytest for Python
- **Comprehensive** - Unit, integration, and E2E tests
- **Mock-ready** - Generates mocks for external dependencies
- **Coordinates with subsystems** - Frontend checks existing tests before creating new ones
- **CI/CD integrated** - Works with GitHub workflows from core