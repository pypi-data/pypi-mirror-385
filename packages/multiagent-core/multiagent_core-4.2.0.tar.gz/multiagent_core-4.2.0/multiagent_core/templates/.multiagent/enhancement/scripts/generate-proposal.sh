#!/bin/bash
set -euo pipefail

# Generate enhancement proposal from template
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

# Check for duplicate/similar enhancements
echo "🔍 Checking for similar enhancements..."

# Extract key words from title (lowercase, split on spaces/dashes)
TITLE_WORDS=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr '-' ' ' | tr '/' ' ')

# Search existing enhancements
SIMILAR_FILES=$(find docs/enhancements -name "*.md" -type f ! -name "*-ANALYSIS.md" ! -name "ANALYSIS_REPORT.md" \
  -exec grep -l "$(echo "$TITLE_WORDS" | awk '{print $1}')\|$(echo "$TITLE_WORDS" | awk '{print $2}')\|$(echo "$TITLE_WORDS" | awk '{print $3}')" {} \; 2>/dev/null | head -5)

if [[ -n "$SIMILAR_FILES" ]]; then
  echo ""
  echo "⚠️  Found potentially similar enhancements:"
  echo ""
  for file in $SIMILAR_FILES; do
    # Extract title from file
    EXISTING_TITLE=$(grep "^# Enhancement:" "$file" 2>/dev/null | sed 's/# Enhancement: //' || basename "$file" .md)
    EXISTING_STATUS=$(grep "^status:" "$file" 2>/dev/null | awk '{print $2}' || echo "unknown")
    EXISTING_AREA=$(grep "^area:" "$file" 2>/dev/null | awk '{print $2}' || echo "unknown")

    echo "  📄 $EXISTING_TITLE"
    echo "     Status: $EXISTING_STATUS | Area: $EXISTING_AREA"
    echo "     Path: $file"
    echo ""
  done

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Options:"
  echo "  1. Continue creating new enhancement"
  echo "  2. Cancel and consolidate with existing"
  echo "  3. Show details of existing enhancement"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  read -p "Choice (1/2/3): " CHOICE

  case "$CHOICE" in
    1)
      echo "✓ Continuing with new enhancement..."
      ;;
    2)
      echo "❌ Cancelled. Please consolidate with existing enhancement."
      echo ""
      echo "To consolidate:"
      echo "1. Edit the existing file"
      echo "2. Add your proposed changes to the appropriate sections"
      echo "3. Update the 'updated' date in frontmatter"
      exit 0
      ;;
    3)
      echo ""
      for file in $SIMILAR_FILES; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "File: $file"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        head -50 "$file"
        echo ""
        echo "(Showing first 50 lines)"
        echo ""
      done
      echo "Re-run script after reviewing."
      exit 0
      ;;
    *)
      echo "Invalid choice. Exiting."
      exit 1
      ;;
  esac
else
  echo "✓ No similar enhancements found"
fi
echo ""

# Get dates
CREATION_DATE=$(date +%Y-%m-%d)
UPDATED_DATE=$(date +%Y-%m-%d)

# Determine source
if [[ -n "$SOURCE_REPORT" ]]; then
  SOURCE="analysis-report"
else
  SOURCE="manual"
fi

# Read template - find it relative to script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_PATH="${SCRIPT_DIR}/../templates/enhancement.md.template"

# Fallback: try from current project root
if [[ ! -f "$TEMPLATE_PATH" ]]; then
  TEMPLATE_PATH=".multiagent/enhancement/templates/enhancement.md.template"
fi

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "❌ Error: Template not found"
  echo "Tried:"
  echo "  - ${SCRIPT_DIR}/../templates/enhancement.md.template"
  echo "  - .multiagent/enhancement/templates/enhancement.md.template"
  echo ""
  echo "Make sure you're in a project with multiagent framework initialized."
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

# Enhancement: ${TITLE}

**ID**: ${ID}
**Related Area**: ${AREA}
**Status**: proposed
**Priority**: medium (critical | high | medium | low)
**Source**: ${SOURCE}
**Estimated Effort**: TBD (hours/days/weeks)

---

## Description

[Provide a clear description of what this enhancement adds or improves]

---

## Problem Statement

**Current State:**
- What exists today
- What's missing or broken
- Why it matters

**User Impact:**
- Who is affected
- How they're affected
- Severity of impact

---

## Proposed Solution

[High-level overview of the enhancement]

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

**Components Affected:**
- Component 1 - How it's affected
- Component 2 - How it's affected

### Implementation Approach

1. Step 1: ...
2. Step 2: ...
3. Step 3: ...

---

## Integration

**Primary Area**: ${AREA}

**Related Areas:**
- area-name - How they interact
- another-area - Integration points

**Dependencies:**
- Depends on: [other enhancements or features]
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

### Breaking Changes
- [ ] No breaking changes
- [ ] Breaking changes (describe below)

[If breaking changes, describe and provide migration path]

---

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] Documentation updated
- [ ] Tests passing
- [ ] No regressions

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

**Validation:**
- [ ] All tests pass
- [ ] No performance regression
- [ ] Documentation reviewed

---

## Documentation Updates

**Files to Update:**
- \`docs/path/to/doc1.md\` - What to add
- \`docs/path/to/doc2.md\` - What to change

**New Documentation:**
- \`docs/path/to/new-doc.md\` - Purpose

---

## Original Feedback Context

EOF

# If source report provided, add reference
if [[ -n "$SOURCE_REPORT" ]]; then
  cat >> "$OUTPUT" << EOF
**Analysis Report**: \`${SOURCE_REPORT}\`

This enhancement was identified through feature analysis. See the full analysis report for detailed recommendations and priorities.

EOF
fi

cat >> "$OUTPUT" << EOF
---

## References

**Related Enhancements:**
- enhancement-name.md - How related

**External References:**
- [Link to docs](url)
- [Link to issue](url)

**Prior Art:**
- Similar implementation 1
- Similar implementation 2

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

**Area Examples:**
- **For multiagent-core framework:** deployment, testing, supervisor, version-management, etc.
- **For web apps:** authentication, user-management, payments, analytics, etc.
- **For APIs:** endpoints, middleware, rate-limiting, caching, etc.
- **For CLI tools:** commands, configuration, plugins, output-formatting, etc.

Adapt the "Area" field and "Project Context" checkboxes to match your project's structure.
EOF

echo "✅ Proposal generated: $OUTPUT"
