# Testing → Validation → Docs Workflow

**Purpose**: Ensure documentation updates only when code is tested AND validated, not just on file changes.

---

## The Problem

**Current State** (INCORRECT):
```
Code changes → Git detects changes → Docs update
```

**Issue**: Docs update even if:
- Tests haven't run
- Tests failed
- Agent outputs aren't validated
- Work isn't actually complete

---

## The Solution

**New State** (CORRECT):
```
Code changes
  → Tests run (/testing:test)
  → Tests PASS ✅
  → Validation runs (/validation:validate)
  → Validation PASSES ✅
  → Docs update (/docs:update --validated)
  → Docs marked as "Tested & Validated"
```

---

## Three-Phase Workflow

### Phase 1: Testing (Code Execution)

**Subsystem**: `testing`
**Command**: `/testing:test`

**What it does**:
1. Detects project type (frontend/backend)
2. Runs appropriate tests:
   - Backend: `pytest` for API tests
   - Frontend: `vitest` for unit tests, `playwright` for E2E tests
3. Generates test report

**Output**:
```json
{
  "status": "passed" | "failed",
  "tests_run": 47,
  "tests_passed": 47,
  "tests_failed": 0,
  "coverage": 85.3,
  "duration": "12.4s",
  "report_path": "test-results/report.json"
}
```

**Next Step**: If `status == "passed"` → Proceed to Phase 2

---

### Phase 2: Validation (AI Behavior)

**Subsystem**: `validation`
**Command**: `/validation:validate --subsystem <name>`

**What it does**:
1. Validates agent prompts are well-structured
2. Checks command orchestration is pure
3. Tests agent output determinism
4. Verifies template rendering
5. Compares against baselines
6. Generates validation report

**Output**:
```json
{
  "status": "passed" | "failed",
  "score": 92,
  "determinism": 94.2,
  "context_quality": 88.5,
  "tool_accuracy": 95.1,
  "issues": [],
  "report_path": "docs/reports/validation/subsystem-validation-2025-10-19.md"
}
```

**Next Step**: If `status == "passed" && score >= 85` → Proceed to Phase 3

---

### Phase 3: Documentation (Evidence-Based Updates)

**Subsystem**: `documentation`
**Command**: `/docs:update --validated --test-report <path> --validation-report <path>`

**What it does**:
1. Reads test report (Phase 1 output)
2. Reads validation report (Phase 2 output)
3. Updates documentation with:
   - Test results (coverage, pass rate)
   - Validation results (determinism, quality scores)
   - "Tested & Validated" badge
   - Timestamp of validation
4. Creates audit trail

**Output**:
```markdown
# Subsystem Documentation

**Status**: ✅ Tested & Validated
**Last Validated**: 2025-10-19 10:45 UTC
**Test Coverage**: 85.3%
**Validation Score**: 92/100
**Determinism**: 94.2%

[Documentation content...]

---

## Validation History

| Date | Tests | Validation | Status |
|------|-------|------------|--------|
| 2025-10-19 | 47/47 ✅ | 92/100 ✅ | Passed |
| 2025-10-18 | 47/47 ✅ | 88/100 ✅ | Passed |
| 2025-10-17 | 45/47 ❌ | - | Failed Tests |
```

---

## Orchestration Commands

### Option 1: Manual Three-Step

```bash
# Step 1: Run tests
/testing:test

# Step 2: If tests pass, validate
/validation:validate --subsystem implementation

# Step 3: If validation passes, update docs
/docs:update --validated \
  --test-report test-results/report.json \
  --validation-report docs/reports/validation/implementation-validation-2025-10-19.md
```

### Option 2: Automated Workflow

```bash
# Single command that runs all three phases
/validate-and-document --subsystem implementation

# Internally:
# 1. Runs /testing:test
# 2. If pass → /validation:validate
# 3. If pass → /docs:update --validated
```

---

## Git Hook Integration

### Pre-Commit Hook

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit

# Only validate if framework files changed
if git diff --cached --name-only | grep -qE '(agents|commands|templates)'; then
  echo "[Validation] Framework files changed, running validation..."

  # Quick validation check
  /validation:check

  if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Fix issues before committing."
    exit 1
  fi
fi

exit 0
```

### Pre-Push Hook

```bash
#!/usr/bin/env bash
# .git/hooks/pre-push

echo "[Full Validation] Running comprehensive validation before push..."

# 1. Run all tests
/testing:test
if [ $? -ne 0 ]; then
  echo "❌ Tests failed. Fix before pushing."
  exit 1
fi

# 2. Run validation
/validation:validate --all-subsystems
if [ $? -ne 0 ]; then
  echo "❌ Validation failed. Fix before pushing."
  exit 1
fi

# 3. Update docs with validation status
/docs:update --validated \
  --test-report test-results/report.json \
  --validation-report docs/reports/validation/full-validation-$(date +%Y-%m-%d).md

echo "✅ All validations passed. Safe to push."
exit 0
```

---

## Validation Status Badges

Docs should display validation status prominently:

### In README.md

```markdown
# Implementation Subsystem

![Tests](https://img.shields.io/badge/tests-47%2F47-brightgreen)
![Validation](https://img.shields.io/badge/validation-92%2F100-green)
![Determinism](https://img.shields.io/badge/determinism-94.2%25-green)

**Status**: ✅ Production Ready
**Last Validated**: 2025-10-19
```

### In Subsystem Docs

```markdown
---
status: validated
test_coverage: 85.3
validation_score: 92
determinism: 94.2
last_validated: 2025-10-19T10:45:00Z
---

# Implementation Subsystem Documentation
```

---

## Integration with CI/CD

### GitHub Actions Workflow

```yaml
name: Validate and Document

on:
  pull_request:
    paths:
      - '~/.claude/agents/**'
      - '~/.claude/commands/**'
      - 'multiagent_core/templates/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Run Tests
        run: /testing:test

      - name: Run Validation
        run: /validation:validate --all-subsystems

      - name: Update Docs
        if: success()
        run: |
          /docs:update --validated \
            --test-report test-results/report.json \
            --validation-report docs/reports/validation/pr-${{ github.event.pull_request.number }}.md

      - name: Commit Updated Docs
        if: success()
        run: |
          git config user.name "Validation Bot"
          git config user.email "validation@multiagent.dev"
          git add docs/
          git commit -m "docs: Update validation status [skip ci]"
          git push
```

---

## Documentation Update Conditions

**Docs SHOULD update when**:
- ✅ All tests pass (100% pass rate)
- ✅ Validation score >= 85/100
- ✅ Determinism >= 85%
- ✅ No critical issues found
- ✅ Context quality >= 70%

**Docs SHOULD NOT update when**:
- ❌ Tests failed
- ❌ Validation score < 85
- ❌ Critical issues found
- ❌ Determinism < 70%
- ❌ Context rot detected

---

## Audit Trail

Every doc update should create an audit entry:

**File**: `docs/.audit/update-log.jsonl`

```json
{"timestamp": "2025-10-19T10:45:00Z", "subsystem": "implementation", "trigger": "validated", "test_status": "passed", "tests_run": 47, "validation_score": 92, "determinism": 94.2, "updated_files": ["README.md", "docs/usage.md"], "commit": "a1b2c3d4"}
{"timestamp": "2025-10-18T14:22:00Z", "subsystem": "enhancement", "trigger": "validated", "test_status": "passed", "tests_run": 23, "validation_score": 88, "determinism": 91.5, "updated_files": ["README.md"], "commit": "e5f6g7h8"}
```

---

## Commands to Implement

### `/validation:validate`
**What**: Run full validation suite
**When**: After tests pass
**Output**: Validation report + score

### `/validation:check`
**What**: Quick validation (structure only)
**When**: Pre-commit
**Output**: Pass/fail + issues

### `/docs:update --validated`
**What**: Update docs with validation status
**When**: After validation passes
**Input**: Test report + validation report
**Output**: Updated docs with badges

### `/validate-and-document`
**What**: Orchestrator for full workflow
**When**: User-triggered or CI/CD
**Flow**: test → validate → document
**Output**: Complete audit trail

---

## Example: Full Workflow

```bash
# User makes changes to implementation subsystem
vim ~/.claude/commands/implementation/implement.md

# Git detects changes, suggests validation
git add -A

# Pre-commit hook runs quick check
# (validates structure only, doesn't run agents)

# User commits
git commit -m "feat: Improve implementation command"

# Before push, user runs full validation
/validate-and-document --subsystem implementation

# Output:
# [1/3] Running tests...
#   ✅ 47/47 tests passed (85.3% coverage)
#
# [2/3] Running validation...
#   ✅ Agent prompts: 95/100
#   ✅ Command structure: 92/100
#   ✅ Determinism: 94.2%
#   ✅ Overall score: 92/100
#
# [3/3] Updating documentation...
#   ✅ Updated README.md with validation status
#   ✅ Updated docs/usage.md with test results
#   ✅ Created audit entry
#
# ✅ Validation complete! Docs updated.
# 📄 Report: docs/reports/validation/implementation-validation-2025-10-19.md

# User pushes with confidence
git push
```

---

## Summary

**Before** (file-based):
- Code changes → Docs update (no validation)

**After** (evidence-based):
- Code changes → Tests PASS → Validation PASS → Docs update (with proof)

**Benefits**:
1. Docs only update when work is complete and validated
2. Audit trail shows test + validation status
3. Badges provide instant status visibility
4. CI/CD enforces validation before merge
5. Git hooks prevent bad commits

**Integration**:
- Testing subsystem: Runs code tests
- Validation subsystem: Validates AI behavior
- Documentation subsystem: Updates with validated status

---

**Next Steps**:
1. Implement `/validation:validate` command
2. Add `--validated` flag to `/docs:update`
3. Create `/validate-and-document` orchestrator
4. Set up git hooks
5. Configure CI/CD workflow
