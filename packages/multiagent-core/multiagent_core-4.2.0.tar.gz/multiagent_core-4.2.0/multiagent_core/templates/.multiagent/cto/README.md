# CTO Review

## Purpose

CTO-level architectural review workflow for ongoing project analysis

## What It Does

1. **Architectural Analysis** - Reviews project architecture, specs, enhancements, and refactors for system-wide coherence
2. **Risk Assessment** - Identifies integration gaps, dependency issues, scalability concerns, and security vulnerabilities
3. **Intelligent Review Gating** - Decides what needs review vs. what doesn't based on project phase, complexity, and risk
4. **Continuous Quality Assurance** - Can run at any project phase (beginning, middle, end, or ongoing) to catch issues early

## Agents Used

- **@qwen/cto-reviewer** - CTO-level architectural reviewer analyzing system integration, scalability, performance, security, and maintainability

## Commands

### `/cto:review` - Request CTO-level architectural review
**Usage**: `/cto:review [spec-directory|project-root]`
**Example**: `/cto:review 007-cto-workflow`

Performs comprehensive architectural review of specs, enhancements, refactors, and architecture documentation. Outputs detailed analysis report with risk assessment and actionable recommendations.

**Spawns**: cto-reviewer agent
**Outputs**: `reports/CTO_REVIEW_{timestamp}.md` or `specs/{spec}/reports/CTO_REVIEW.md`

---

## Architecture

```
User runs /cto:review
      ↓
Command orchestrates:
1. Gather context (docs/, specs/, enhancements/, refactors/)
2. Invoke cto-reviewer agent (intelligent analysis)
3. Generate review report from template
4. Assess severity levels (Low/Medium/High/Critical)
5. Display summary with next steps
```

## How It Works

1. **Command Invocation**: User runs `/cto:review [target]` on ANY project (multiagent-core, SpecKit, or any codebase)
2. **Adaptive Context Discovery**: Script intelligently searches for documentation in common locations:
   - Tries multiagent-core conventions (docs/architecture/, specs/)
   - Falls back to common patterns (README.md, ARCHITECTURE.md, ADRs/, wiki/)
   - Detects project type from package managers (package.json, requirements.txt, go.mod, etc.)
   - Searches for API docs (Swagger, OpenAPI), database schemas, infrastructure code
3. **Documentation Level Assessment**: Agent categorizes documentation quality (Minimal → Comprehensive)
4. **Adaptive Analysis**: Review approach adapts to available context:
   - **Minimal docs**: "Initial Architecture Assessment" with project discovery
   - **Basic docs**: Standard review + documentation gap recommendations
   - **Comprehensive docs**: Full architectural analysis across all dimensions
5. **Intelligent Decision Making**: Agent determines what needs review vs. what can skip
6. **Report Generation**: Agent generates appropriate report (CTO_REVIEW.md or INITIAL_ASSESSMENT.md)
7. **Actionable Feedback**: Display summary with findings, severity, and next steps

## Directory Structure

```
.multiagent/cto/
├── README.md              # This file
├── docs/                  # Review guidelines and criteria
│   └── review-criteria.md # What the CTO reviewer evaluates
├── templates/             # Report templates
│   └── CTO_REVIEW.template.md
├── scripts/               # Context gathering utilities
│   └── gather-context.sh  # Collects docs, specs, enhancements, refactors
└── memory/               # Review history (optional)
```

## Templates

Templates in this subsystem:

- `templates/CTO_REVIEW.template.md` - Comprehensive review report with executive summary, architectural analysis, integration points, dependencies, performance, security, maintainability, risks, and recommendations

## Scripts

Mechanical scripts in this subsystem:

- `scripts/gather-context.sh` - Collects all architectural documentation, specs, enhancements, and refactors for agent context

## Outputs

This subsystem generates:

```
reports/
└── CTO_REVIEW_{timestamp}.md

# OR for spec-specific reviews:
specs/{spec}/reports/
└── CTO_REVIEW.md
```

## Usage Example

```bash
# Review entire project architecture
/cto:review

# Review specific spec before implementation
/cto:review 007-cto-workflow

# Review after major enhancement
/cto:review --enhancement 001

# Review before deployment
/cto:review --pre-deploy
```

## Review Scope (Adaptive Discovery)

The CTO reviewer intelligently searches for and analyzes:

### Phase 1: Project Type Detection
- **Node.js**: package.json, package-lock.json
- **Python**: requirements.txt, pyproject.toml, setup.py
- **Go**: go.mod, go.sum
- **Rust**: Cargo.toml
- **PHP**: composer.json
- **Java**: pom.xml, build.gradle

### Phase 2: Core Documentation
- **Main docs**: README.md, ARCHITECTURE.md, DESIGN.md, PROJECT_TYPE.md
- **Architecture**: docs/architecture/, architecture/, ADRs/, adr/, docs/design/
- **API docs**: docs/api/, api-docs/, swagger.json, openapi.yaml

### Phase 3: Specifications
- **Multiagent-core**: specs/*/spec.md, specs/*/plan.md
- **Generic**: specs/, spec/, specifications/, docs/specs/, rfcs/, docs/rfcs/

### Phase 4: Enhancements & Plans
- **Multiagent-core**: docs/enhancements/, docs/refactors/
- **Generic**: features/, docs/features/

### Phase 5: Integration & Contracts
- **Integration**: docs/integration/, integrations/
- **Contracts**: contracts/*.json, contracts/*.yaml, schemas/

### Phase 6: Data Models
- **Migrations**: migrations/, db/migrations/, database/migrations/
- **Models**: *models.py, *schema.sql, *schema.prisma

### Phase 7: Infrastructure
- **Containers**: docker-compose.yml, Dockerfile
- **IaC**: *.tf (Terraform), k8s*.yaml (Kubernetes)
- **CI/CD**: .github/workflows/, .gitlab-ci.yml, Jenkinsfile

**Result**: Works on multiagent-core projects, SpecKit projects, legacy codebases, new projects with minimal docs, and everything in between.

## Review Criteria

The cto-reviewer evaluates:

1. **System Architecture** - Component decoupling, separation of concerns, scalability beyond MVP
2. **Dependencies & Interconnections** - Clear dependencies, no circular deps, proper integration points
3. **Data Flow** - Logical data flow, no bottlenecks, appropriate caching, optimized schemas
4. **Performance & Scalability** - Scale performance, async patterns, resource usage
5. **Security & Compliance** - Auth/authz, input validation, secrets management, OWASP compliance
6. **Maintainability** - Code organization, clear contracts, testing strategy, documentation

## Adaptive Review Modes

### Mode 1: Initial Architecture Assessment
**When**: Project has minimal documentation (just README, package.json)
**What happens**:
- Agent performs project discovery (type, tech stack, current state)
- Infers architecture from code structure
- Identifies what's unclear or ambiguous
- Generates INITIAL_ASSESSMENT.md with documentation recommendations
- Provides templates to create baseline docs

**Example output**: `reports/INITIAL_ASSESSMENT_{date}.md`

### Mode 2: Standard Review with Gaps
**When**: Project has basic docs (README + some design docs)
**What happens**:
- Agent reviews documented architecture
- Notes what's missing in "Documentation Gaps" section
- Provides partial analysis based on available context
- Recommends specific docs to create for complete review

**Example output**: `reports/CTO_REVIEW_{date}.md` (with gaps section)

### Mode 3: Comprehensive Review
**When**: Project has good documentation (architecture docs, specs, API docs)
**What happens**:
- Full architectural analysis across all 6 dimensions
- Deep dive into performance, security, scalability
- Detailed risk categorization
- Actionable recommendations

**Example output**: `specs/{spec}/reports/CTO_REVIEW.md` or `reports/CTO_REVIEW_{date}.md`

### Mode 4: Enhanced Multiagent-Core Review
**When**: Project follows multiagent-core conventions
**What happens**:
- All of Mode 3, plus:
- Enhancement and refactor analysis
- Framework compliance assessment
- Integration with specs/ workflow

**Example output**: Full CTO_REVIEW.md with enhancement/refactor sections

## Troubleshooting

### Review says "insufficient context"
**Problem**: Not enough architectural documentation for meaningful review
**Solution**: Agent will automatically perform "Initial Architecture Assessment" instead
- Analyzes what exists
- Recommends documentation to create
- Provides templates to get started

### Agent doesn't understand project type
**Problem**: Cannot detect tech stack from common markers
**Solution**:
```bash
# Add PROJECT_TYPE.md to specify domain
echo "Project Type: SaaS Web Application
Tech Stack: Django + React + PostgreSQL" > PROJECT_TYPE.md

# Then re-run review
/cto:review
```

### Review is too generic
**Problem**: Findings don't feel specific to this project
**Solution**: Create more context:
- Add ARCHITECTURE.md explaining system design
- Document API contracts (OpenAPI/Swagger)
- Add database schema documentation
- Create integration diagrams

## Related Subsystems

- **core**: Integrates with `/core:project-setup` and `/specify` workflows
- **supervisor**: Works with supervisor phases for quality gates
- **docs**: Reads architecture documentation for context

## Future Enhancements

Planned features for this subsystem:

- [ ] Automated review scheduling (weekly, before releases)
- [ ] Trend analysis across multiple reviews
- [ ] Integration with CI/CD for automated quality gates
- [ ] Comparison reports (current vs. previous review)
- [ ] Risk score tracking over time
