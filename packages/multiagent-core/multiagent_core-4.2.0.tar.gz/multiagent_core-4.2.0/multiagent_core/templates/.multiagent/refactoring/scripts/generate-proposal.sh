#!/bin/bash
set -euo pipefail

# Generate refactoring proposal from template
# Usage: generate-proposal.sh --id ID --area AREA --title TITLE --output PATH [--source-report PATH]

# Parse arguments
ID=""
AREA=""
TITLE=""
OUTPUT=""
SOURCE_REPORT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id)
      ID="$2"
      shift 2
      ;;
    --area)
      AREA="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --source-report)
      SOURCE_REPORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Validate required arguments
if [[ -z "$ID" || -z "$AREA" || -z "$TITLE" || -z "$OUTPUT" ]]; then
  echo "❌ Error: Missing required arguments"
  echo "Usage: generate-proposal.sh --id ID --area AREA --title TITLE --output PATH [--source-report PATH]"
  exit 1
fi

# Get dates
CREATION_DATE=$(date +%Y-%m-%d)
UPDATED_DATE=$(date +%Y-%m-%d)

# Determine source
if [[ -n "$SOURCE_REPORT" ]]; then
  SOURCE="analysis-report"
else
  SOURCE="manual"
fi

# Read template
TEMPLATE_PATH="$HOME/Projects/multiagent-core/multiagent_core/templates/.multiagent/refactoring/templates/refactoring.md.template"

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "❌ Error: Template not found at $TEMPLATE_PATH"
  exit 1
fi

# Generate proposal from template
cat > "$OUTPUT" << EOF
---
id: ${ID}
area: ${AREA}
status: proposed
priority: medium
source: ${SOURCE}
effort: TBD
created: ${CREATION_DATE}
updated: ${UPDATED_DATE}
---

# Refactoring: ${TITLE}

**ID**: ${ID}
**Related Area**: ${AREA}
**Status**: proposed
**Priority**: medium (critical | high | medium | low)
**Source**: ${SOURCE}
**Estimated Effort**: TBD (hours/days/weeks)

---

## Description

[Provide a clear description of what this refactoring improves or cleans up]

---

## Problem Statement

**Current State:**
- What code patterns exist today
- What's problematic or inefficient
- Why it needs refactoring

**Technical Impact:**
- Performance implications
- Maintainability concerns
- Code quality issues

---

## Proposed Refactoring

[High-level overview of the refactoring approach]

### Expected Outcomes

- Outcome 1
- Outcome 2
- Outcome 3

### Changes Required

**Files Modified:**
1. \`path/to/file1\` - What changes
2. \`path/to/file2\` - What changes

**Files Created:**
1. \`path/to/new-file\` - Purpose

**Files Deleted:**
1. \`path/to/old-file\` - Reason for removal

**Components Affected:**
- Component 1 - How it's affected
- Component 2 - How it's affected

### Refactoring Approach

1. Step 1: ...
2. Step 2: ...
3. Step 3: ...

---

## Code Examples

### Before (Current Code)

\`\`\`javascript
// Problematic code pattern
// Example code showing current state
\`\`\`

**Issues:**
- Issue 1
- Issue 2
- Issue 3

### After (Refactored Code)

\`\`\`javascript
// Improved code pattern
// Example code showing desired state
\`\`\`

**Improvements:**
- Improvement 1
- Improvement 2
- Improvement 3

---

## Integration

**Primary Area**: ${AREA}

**Related Areas:**
- area-name - How they interact
- another-area - Integration points

**Dependencies:**
- Depends on: [other refactorings or features]
- Blocks: [what's waiting for this]

**Project Context:**
- [ ] Backend / API
- [ ] Frontend / UI
- [ ] Infrastructure / DevOps
- [ ] Database / Data Layer
- [ ] Authentication / Security
- [ ] Testing / QA
- [ ] Documentation
- [ ] [Custom area for your project]

---

## Impact Analysis

### Benefits
- Benefit 1
- Benefit 2
- Benefit 3

### Risks
- Risk 1 - Mitigation strategy
- Risk 2 - Mitigation strategy

### Performance Impact
- Expected performance change: [+X% faster | no change | careful monitoring needed]
- Benchmarks to run: [list specific benchmarks]

### Breaking Changes
- [ ] No breaking changes
- [ ] Breaking changes (describe below)

[If breaking changes, describe and provide migration path]

---

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] All tests passing
- [ ] No performance regression
- [ ] Code quality metrics improved
- [ ] Documentation updated
- [ ] No new linting/type errors

---

## Implementation Plan

### Phase 1: [Name]
**Duration**: [estimate]

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Phase 2: [Name]
**Duration**: [estimate]

- [ ] Task 4
- [ ] Task 5
- [ ] Task 6

---

## Testing Strategy

**Unit Tests:**
- Test scenario 1
- Test scenario 2

**Integration Tests:**
- Integration scenario 1
- Integration scenario 2

**Regression Tests:**
- Ensure no functionality broken
- Verify performance maintained/improved

**Validation:**
- [ ] All tests pass
- [ ] No performance regression
- [ ] Code coverage maintained or improved
- [ ] Manual testing completed

---

## Rollback Plan

**If issues are discovered:**

\`\`\`bash
# Rollback changes
git revert {{COMMIT_HASH}}

# Or restore specific files
git checkout {{BEFORE_COMMIT}} -- file1 file2
\`\`\`

**Monitoring:**
- Watch for errors in logs
- Monitor performance metrics
- Check user reports

---

## Documentation Updates

**Files to Update:**
- \`docs/path/to/doc1.md\` - What to add
- \`docs/path/to/doc2.md\` - What to change

**New Documentation:**
- \`docs/path/to/new-doc.md\` - Purpose

---

## Original Context

EOF

# If source report provided, add reference
if [[ -n "$SOURCE_REPORT" ]]; then
  cat >> "$OUTPUT" << EOF
**Analysis Report**: \`${SOURCE_REPORT}\`

This refactoring was identified through automated code analysis. See the full analysis report for detailed findings and metrics.

EOF
fi

cat >> "$OUTPUT" << EOF
---

## References

**Related Refactorings:**
- refactoring-name.md - How related

**External References:**
- [Link to docs](url)
- [Link to issue](url)

**Similar Refactorings:**
- Similar refactoring 1
- Similar refactoring 2

---

## Timeline

**Proposed Start**: TBD
**Estimated Completion**: TBD
**Actual Completion**: TBD

---

## Approval

**Proposed By**: [Your name]
**Reviewed By**: TBD
**Approved By**: TBD
**Approval Date**: TBD

---

**Document Location**: \`${OUTPUT}\`
**Last Updated**: ${UPDATED_DATE}

---

## Usage Notes

**Refactoring Types:**
- **Code Duplication**: Extract duplicated code into shared utilities
- **Legacy Patterns**: Modernize callbacks to async/await, update deprecated APIs
- **Performance**: Optimize algorithms, reduce N+1 queries, add caching
- **Complexity**: Simplify nested logic, break down large functions
- **Technical Debt**: Remove dead code, clean up TODOs, update documentation

Adapt the "Area" field and "Project Context" checkboxes to match your project's structure.
EOF

echo "✅ Proposal generated: $OUTPUT"
