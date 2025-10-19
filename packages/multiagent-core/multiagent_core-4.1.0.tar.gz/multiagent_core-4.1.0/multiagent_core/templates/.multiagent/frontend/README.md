# Frontend Development System

## Purpose

Orchestrates frontend UI/UX development through specialized agents, providing component patterns, state management strategies, design system templates, and end-to-end testing automation for React/Next.js applications.

## What It Does

1. **Development Orchestration** - Routes frontend tasks to appropriate agents based on complexity and specialization
2. **Testing Automation** - Spawns frontend-playwright-tester agent for E2E validation and cross-browser testing
3. **Template Provision** - Provides component specs, state architecture, and design system templates
4. **Quality Enforcement** - Integrates linting, bundle analysis, and build validation

## Agents Used

- **@claude/frontend-developer** - Implements UI components, React/Next.js features, integrates with backend APIs
- **@claude/frontend-playwright-tester** - Writes E2E tests, validates user flows, performs cross-browser testing
- **@gemini** - Design system implementation, accessibility patterns, visual polishing
- **@copilot** - Simple UI tasks (forms, basic components, straightforward layouts)

## Commands

### `/frontend:develop <spec-directory> [--role=agent]` - Execute frontend development tasks

**Usage**: `/frontend:develop <spec-directory> [--role=agent]`
**Example**: `/frontend:develop 001 --role=claude`

Reads layered-tasks.md from spec directory and routes frontend tasks to appropriate agents. Agents implement UI features using templates and docs as guidance.

**Spawns**: frontend-developer agent (or specified agent)
**Outputs**: React/Next.js components, pages, hooks, utilities in `src/` or `app/` directory

---

### `/frontend:test <spec-directory>` - Execute E2E testing workflow

**Usage**: `/frontend:test <spec-directory>`
**Example**: `/frontend:test 001`

Spawns frontend-playwright-tester agent to create and run Playwright tests for implemented UI features. Validates user flows and cross-browser compatibility.

**Spawns**: frontend-playwright-tester agent
**Outputs**: Playwright tests in `tests/frontend/e2e/{spec-dir}/`, test reports in `test-results/`
**Integration**: Works WITH `/testing:test-generate` - checks existing tests, only creates new ones

---

### `/frontend:build [--production|--development]` - Build frontend application

**Usage**: `/frontend:build [--production|--development]`
**Example**: `/frontend:build --production`

Executes build process for frontend application. Production mode includes optimization, minification, and tree-shaking.

**Spawns**: No agent (direct build process)
**Outputs**: Built assets in `dist/` or `.next/` directory

---

### `/frontend:lint [--fix]` - Lint and format frontend code

**Usage**: `/frontend:lint [--fix]`
**Example**: `/frontend:lint --fix`

Runs ESLint and Prettier on frontend codebase. `--fix` flag auto-corrects issues.

**Spawns**: No agent (direct linting process)
**Outputs**: Lint report in terminal, fixed files if `--fix` used

---

### `/frontend:analyze` - Analyze bundle size and dependencies

**Usage**: `/frontend:analyze`
**Example**: `/frontend:analyze`

Analyzes webpack/vite bundle to identify large dependencies and optimization opportunities.

**Spawns**: No agent (direct analysis tool)
**Outputs**: Bundle analysis report in terminal or browser

---

## Architecture

```
User runs /frontend:develop 001
      ↓
Command orchestrates:
1. Read specs/001-*/agent-tasks/layered-tasks.md
2. Filter tasks marked with frontend agents (@claude, @gemini, @copilot)
3. Invoke frontend-developer agent
4. Agent uses templates/ and docs/ for guidance
5. Agent implements components/features
6. Validate build succeeds
7. Display implementation summary
```

```
User runs /frontend:test 001
      ↓
Command orchestrates:
1. Check if tests already exist from /testing:test-generate
2. Read existing tests in tests/frontend/e2e/001/ (if any)
3. Detect implemented frontend features needing NEW tests
4. Invoke frontend-playwright-tester agent
5. Agent writes ONLY NEW E2E tests (skips existing coverage)
6. Save to tests/frontend/e2e/001/ (centralized location)
7. Run all tests (existing + new) across browsers
8. Generate test reports with screenshots
9. Display test summary (existing + new test counts)
```

## How It Works

1. **Command Invocation**: User runs `/frontend:develop 001` to start frontend development
2. **Task Filtering**: Command reads layered-tasks.md and filters for frontend tasks
3. **Agent Invocation**: Spawns appropriate agent (claude/gemini/copilot) based on task complexity
4. **Template Usage**: Agent references templates (COMPONENT_SPEC, STATE_ARCHITECTURE, etc.)
5. **Implementation**: Agent writes React/Next.js code following templates and patterns
6. **Testing**: After implementation, `/frontend:test 001` spawns playwright-tester for validation
7. **Validation**: Build process confirms code compiles, linting passes

## Directory Structure

```
.multiagent/frontend/
├── README.md                      # This file
├── docs/                          # Frontend design guides
│   ├── component-patterns.md     # Component architecture patterns
│   ├── state-management.md       # State management strategies
│   ├── routing-architecture.md   # Next.js/React Router patterns
│   └── design-system-setup.md    # Design system implementation
│
└── templates/                     # Generation templates
    ├── COMPONENT_SPEC.md         # Component specification template
    ├── STATE_ARCHITECTURE.md     # State management template
    ├── DESIGN_SPECS.md           # Design system template
    └── API_CLIENT.md             # API client integration template
```

## Templates

Templates in this subsystem:

- `templates/COMPONENT_SPEC.md` - Component API definition (props, events, composition)
- `templates/STATE_ARCHITECTURE.md` - Global/local state patterns (Redux, Zustand, Context)
- `templates/DESIGN_SPECS.md` - Design system structure (typography, colors, spacing)
- `templates/API_CLIENT.md` - HTTP client setup (Axios/Fetch, interceptors, error handling)

## Scripts

This subsystem has no mechanical scripts - all operations are agent-driven or direct tool invocations (build, lint, analyze).

## Outputs

This subsystem generates:

```
src/ (or app/)
├── components/
│   ├── ui/                       # Reusable UI components
│   └── features/                 # Feature-specific components
├── hooks/                        # Custom React hooks
├── lib/                          # Utilities and API client
├── styles/                       # Global styles and theme
└── pages/ (or app/)              # Pages/routes

tests/frontend/
├── unit/                          # Unit tests for components/hooks
├── integration/                   # Integration tests for services
└── e2e/                          # E2E tests organized by spec
    ├── 001-auth/                 # Spec 001 E2E tests
    │   ├── login.spec.ts
    │   └── signup.spec.ts
    ├── 002-dashboard/            # Spec 002 E2E tests
    │   └── user-flow.spec.ts
    └── 003-checkout/             # Spec 003 E2E tests
        └── purchase-flow.spec.ts
```

## Usage Example

```bash
# Step 1: Develop frontend features
/frontend:develop 001 --role=claude
# → Implements complex interactive components

/frontend:develop 001 --role=copilot
# → Implements forms and basic UI elements

# Step 2: Test implemented features
/frontend:test 001
# → Writes and runs E2E tests for user flows

# Step 3: Validate build
/frontend:build --production
# → Confirms production build succeeds

# Step 4: Check code quality
/frontend:lint --fix
# → Auto-fixes linting issues

# Step 5: Analyze bundle
/frontend:analyze
# → Identifies optimization opportunities
```

## Troubleshooting

### Command Not Working
**Problem**: `/frontend:develop 001` returns no tasks
**Solution**:
```bash
# Verify spec exists
ls -la specs/001-*/

# Check for layered tasks with frontend assignments
grep "@claude\|@gemini\|@copilot" specs/001-*/agent-tasks/layered-tasks.md
```

### Build Failures
**Problem**: Build fails with module errors
**Solution**:
```bash
# Check dependencies installed
npm install  # or pnpm install

# Verify configuration
cat package.json
cat next.config.js  # or vite.config.ts

# Run with verbose output
/frontend:build --production --verbose
```

### Test Failures
**Problem**: E2E tests fail
**Solution**:
```bash
# Install Playwright browsers
npx playwright install

# Run with debugging
/frontend:test 001 --debug

# Check Playwright configuration
cat playwright.config.ts
```

## Related Subsystems

- **Backend**: API_CLIENT.md templates integrate with backend API specs
- **Testing**:
  - `/testing:test-generate` creates initial test structure in `tests/frontend/`
  - `/frontend:test` works WITH existing tests, only creates new ones for uncovered features
  - Both use centralized `tests/frontend/` directory (NOT scattered in src/)
- **Deployment**: Build output feeds into deployment pipeline
- **Documentation**: Component specs inform developer docs

---

🎨 **Frontend Development System** - Part of MultiAgent Framework
