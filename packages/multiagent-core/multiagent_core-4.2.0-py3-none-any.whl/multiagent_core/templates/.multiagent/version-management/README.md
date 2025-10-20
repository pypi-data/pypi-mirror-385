# Version Management Subsystem

Automated semantic versioning and release management for Python and TypeScript projects using intelligent agents and mechanical scripts.

## Overview

The version-management subsystem provides:
- **Intelligent version analysis** - Analyzes commits and recommends version bumps
- **Configuration validation** - Ensures version management is properly configured
- **Changelog generation** - Creates human-readable changelogs from commits
- **Release validation** - Pre-release checks for production readiness
- **Automated workflows** - GitHub Actions integration for seamless releases

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  /version:setup     /version:status     /version:validate       │
│  (orchestration)    (orchestration)     (orchestration)          │
└──────────┬──────────────────┬──────────────────┬────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Intelligent Agent Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  version-validator  version-analyzer   changelog-generator      │
│  release-validator                                               │
│  (AI-powered analysis and decision making)                       │
└──────────┬──────────────────┬──────────────────┬────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Mechanical Script Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  check-version-sync.sh    list-unpushed-commits.sh              │
│  validate-conventional-commits.sh                                │
│  (Pure mechanical operations, no intelligence)                   │
└──────────┬──────────────────┬──────────────────┬────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│  JSON Reports        User Summaries        Version Updates       │
│  (Structured data)   (Human readable)      (VERSION file)        │
└─────────────────────────────────────────────────────────────────┘
```

## Slash Commands

### `/version:setup [python|typescript]`
Setup semantic versioning with validation and templates.
- **Invokes**: `version-validator` agent
- **Creates**: VERSION file, GitHub Actions workflow
- **Output**: Setup summary with manual configuration steps

### `/version:status`
Check version status with intelligent analysis.
- **Invokes**: `version-analyzer` agent
- **Uses**: `check-version-sync.sh`, `list-unpushed-commits.sh`
- **Output**: Version analysis with bump recommendation

### `/version:validate`
Validate version configuration and readiness.
- **Invokes**: `version-validator` agent
- **Uses**: `check-version-sync.sh`, `validate-conventional-commits.sh`
- **Output**: Comprehensive validation report

## Intelligent Agents

### `version-analyzer`
Analyzes commit history and determines version bump type (major/minor/patch).
- **Tools**: Read, Bash, Write, Grep
- **Input**: Commit data from scripts
- **Output**: Version analysis with recommendations

### `version-validator`
Validates VERSION files and configuration.
- **Tools**: Read, Bash, Write, Grep
- **Input**: Project files and configuration
- **Output**: Validation report with issues and recommendations

### `changelog-generator`
Generates intelligent changelog from commits.
- **Tools**: Read, Bash, Write, Grep
- **Input**: Commit history
- **Output**: CHANGELOG.md with grouped entries

### `release-validator`
Validates release readiness and prerequisites.
- **Tools**: Read, Bash, Write, Grep
- **Input**: Tests, builds, version data
- **Output**: Go/no-go release decision

## Mechanical Scripts

### `check-version-sync.sh`
**Purpose**: Verify VERSION matches pyproject.toml/package.json
**Input**: Project directory, output file path
**Output**: JSON with sync status
**Exit Codes**: 0=synced, 1=out_of_sync, 2=missing/error

### `list-unpushed-commits.sh`
**Purpose**: List unpushed commits for analysis
**Input**: Project directory, output file, branch name
**Output**: JSON with commit list and metadata
**Exit Codes**: 0=success

### `validate-conventional-commits.sh`
**Purpose**: Validate commit messages follow Conventional Commits
**Input**: Project directory, output file, commit range
**Output**: JSON with validation results and violations
**Exit Codes**: 0=all valid, 1=violations found

## Workflow Templates

### Python Projects
**Location**: `templates/python/github-workflows/version-management.yml`
- Automated semantic-release workflow
- Publishes to PyPI
- Updates VERSION file and pyproject.toml
- Creates GitHub releases

**Variables**:
- `{{PROJECT_NAME}}` - Display name for workflow
- `{{PACKAGE_NAME}}` - PyPI package name
- `{{PYTHON_VERSION}}` - Python version (default: 3.9)
- `{{NODE_VERSION}}` - Node version for semantic-release (default: 20)
- `{{BRANCH_NAME}}` - Release branch (default: main)

### TypeScript/Node.js Projects
**Location**: `templates/typescript/github-workflows/version-management.yml`
- Automated semantic-release workflow
- Publishes to npm
- Updates VERSION file and package.json
- Creates GitHub releases

**Variables**:
- `{{PROJECT_NAME}}` - Display name for workflow
- `{{PACKAGE_NAME}}` - npm package name
- `{{NODE_VERSION}}` - Node version (default: lts/*)
- `{{BRANCH_NAME}}` - Release branch (default: main)

## Directory Structure

```
version-management/
├── README.md                          # This file
├── docs/
│   └── OVERVIEW.md                    # Complete documentation
├── templates/
│   ├── python/
│   │   └── github-workflows/
│   │       └── version-management.yml # Python workflow template
│   └── typescript/
│       └── github-workflows/
│           └── version-management.yml # TypeScript workflow template
├── scripts/
│   ├── check-version-sync.sh         # Version synchronization check
│   ├── list-unpushed-commits.sh      # Commit listing
│   └── validate-conventional-commits.sh # Format validation
└── memory/                            # Release history tracking
```

## Quick Start

### Setup Version Management

```bash
# For Python project
/version:setup python

# For TypeScript project
/version:setup typescript
```

### Check Version Status

```bash
/version:status
```

Output:
```
📊 Version Analysis Summary

Current Version: 1.2.3
Recommended: 1.3.0 (MINOR bump)

📈 Commit Breakdown:
- 3 features (feat:)
- 1 fix (fix:)
- 0 breaking changes

✅ Conventional Commits: 100% valid

🎯 Recommendation: Bump to 1.3.0 before release
```

### Validate Configuration

```bash
/version:validate
```

## Conventional Commits Format

The subsystem uses [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope?): subject

[optional body]

[optional footer]
```

**Types**:
- `feat:` - New feature (MINOR bump)
- `fix:` - Bug fix (PATCH bump)
- `BREAKING CHANGE:` or `type!:` - Breaking change (MAJOR bump)
- `docs:`, `style:`, `refactor:`, `test:`, `chore:` - No version bump

**Examples**:
```bash
feat: add user authentication
fix(api): resolve token expiry bug
feat!: redesign authentication system
```

## Integration with Other Subsystems

**Depends On**:
- `core` - Git hooks (pre-push reminder)
- `github` - GitHub Actions workflows

**Used By**:
- `deployment` - Version checking before deploy
- `ai-infrastructure` - Version tracking in reports
- `docs` - Version documentation updates

## Troubleshooting

### Version Mismatch

**Problem**: VERSION file and pyproject.toml/package.json don't match

**Solution**:
```bash
# Check sync status
/version:validate

# Manually sync if needed
# For Python: Update pyproject.toml version field
# For TypeScript: Update package.json version field
```

### Commit Format Violations

**Problem**: Commits don't follow Conventional Commits format

**Solution**:
```bash
# Check violations
/version:validate

# Fix recent commits
git commit --amend -m "feat: proper commit message"

# Or add conventional format going forward
```

### Workflow Not Triggering

**Problem**: GitHub Actions workflow doesn't run

**Solution**:
1. Check workflow file exists: `.github/workflows/version-management.yml`
2. Verify secrets are configured: PYPI_TOKEN or NPM_TOKEN
3. Ensure pushing to main branch
4. Check workflow permissions in repository settings

## Further Documentation

See `docs/OVERVIEW.md` for:
- Complete setup guide
- Detailed conventional commits explanation
- Python vs npm comparison
- Advanced configuration
- Troubleshooting guide
