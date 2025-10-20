#!/bin/bash

# gather-context.sh
# Intelligently collects architectural context from ANY project structure
# Usage: ./gather-context.sh [spec-directory|--all]

set -e

REVIEW_SCOPE="${1:-all}"

echo "📋 Discovering project structure and gathering context..."
echo ""

# Create temporary context file
CONTEXT_FILE=$(mktemp)
echo "Context gathered at: $(date)" > "$CONTEXT_FILE"
echo "Review scope: $REVIEW_SCOPE" >> "$CONTEXT_FILE"
echo "" >> "$CONTEXT_FILE"

# Function to safely append file content
append_file() {
    local filepath="$1"
    local label="$2"

    if [ -f "$filepath" ]; then
        echo "=== $label ===" >> "$CONTEXT_FILE"
        cat "$filepath" >> "$CONTEXT_FILE"
        echo "" >> "$CONTEXT_FILE"
        echo "✓ $label"
        return 0
    fi
    return 1
}

# Function to safely append directory contents
append_directory() {
    local dirpath="$1"
    local label="$2"
    local pattern="$3"

    if [ -d "$dirpath" ]; then
        echo "=== $label ===" >> "$CONTEXT_FILE"
        find "$dirpath" -name "$pattern" -type f 2>/dev/null | while read -r file; do
            echo "--- File: $file ---" >> "$CONTEXT_FILE"
            cat "$file" >> "$CONTEXT_FILE"
            echo "" >> "$CONTEXT_FILE"
        done
        echo "✓ $label"
        return 0
    fi
    return 1
}

# Function to search for files by pattern anywhere in project
find_and_append() {
    local pattern="$1"
    local label="$2"
    local max_depth="${3:-5}"

    local found=0
    find . -maxdepth "$max_depth" -name "$pattern" -type f 2>/dev/null | while read -r file; do
        if [ $found -eq 0 ]; then
            echo "=== $label ===" >> "$CONTEXT_FILE"
            found=1
        fi
        echo "--- File: $file ---" >> "$CONTEXT_FILE"
        cat "$file" >> "$CONTEXT_FILE"
        echo "" >> "$CONTEXT_FILE"
    done

    if [ $found -eq 1 ]; then
        echo "✓ $label"
        return 0
    fi
    return 1
}

# Function to detect project type
detect_project_type() {
    echo "=== PROJECT TYPE DETECTION ===" >> "$CONTEXT_FILE"

    # Check for common project markers
    if [ -f "package.json" ]; then
        echo "Detected: Node.js/JavaScript project" >> "$CONTEXT_FILE"
        cat package.json >> "$CONTEXT_FILE"
    fi

    if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
        echo "Detected: Python project" >> "$CONTEXT_FILE"
        [ -f "requirements.txt" ] && cat requirements.txt >> "$CONTEXT_FILE"
        [ -f "pyproject.toml" ] && cat pyproject.toml >> "$CONTEXT_FILE"
    fi

    if [ -f "go.mod" ]; then
        echo "Detected: Go project" >> "$CONTEXT_FILE"
        cat go.mod >> "$CONTEXT_FILE"
    fi

    if [ -f "Cargo.toml" ]; then
        echo "Detected: Rust project" >> "$CONTEXT_FILE"
        cat Cargo.toml >> "$CONTEXT_FILE"
    fi

    if [ -f "composer.json" ]; then
        echo "Detected: PHP project" >> "$CONTEXT_FILE"
        cat composer.json >> "$CONTEXT_FILE"
    fi

    if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
        echo "Detected: Java project" >> "$CONTEXT_FILE"
    fi

    echo "" >> "$CONTEXT_FILE"
    echo "✓ Project type detection"
}

echo "Phase 1: Detecting project structure..."
detect_project_type

echo ""
echo "Phase 2: Collecting core documentation..."

# 1. Main README (always start here)
append_file "README.md" "Main README" || echo "⚠️  No README.md found"

# 2. Try common documentation locations
append_file "PROJECT_TYPE.md" "Project Type" || true
append_file "ARCHITECTURE.md" "Architecture Overview" || true
append_file "DESIGN.md" "Design Document" || true

# 3. Search for architecture documentation in common locations
append_directory "docs/architecture" "Architecture Documentation" "*.md" || \
append_directory "docs/design" "Design Documentation" "*.md" || \
append_directory "architecture" "Architecture Documentation" "*.md" || \
append_directory "design" "Design Documentation" "*.md" || \
append_directory "ADRs" "Architecture Decision Records" "*.md" || \
append_directory "adr" "Architecture Decision Records" "*.md" || \
echo "⚠️  No architecture documentation directories found"

# 4. Search for API documentation
append_directory "docs/api" "API Documentation" "*.md" || \
append_directory "api-docs" "API Documentation" "*.md" || \
find_and_append "swagger.json" "Swagger/OpenAPI Specification" || \
find_and_append "openapi.yaml" "OpenAPI Specification" || \
find_and_append "openapi.yml" "OpenAPI Specification" || \
echo "⚠️  No API documentation found"

echo ""
echo "Phase 3: Collecting specs and plans..."

# 5. Multiagent-core style specs (if they exist)
if [ "$REVIEW_SCOPE" = "all" ]; then
    if [ -d "specs" ]; then
        echo "Collecting all specs..."
        append_directory "specs" "All Specifications" "spec.md"
        append_directory "specs" "All Implementation Plans" "plan.md"
    fi
elif [ -d "specs/$REVIEW_SCOPE" ]; then
    echo "Collecting spec: $REVIEW_SCOPE"
    append_file "specs/$REVIEW_SCOPE/spec.md" "Spec: $REVIEW_SCOPE"
    append_file "specs/$REVIEW_SCOPE/plan.md" "Plan: $REVIEW_SCOPE"
    append_file "specs/$REVIEW_SCOPE/data-model.md" "Data Model: $REVIEW_SCOPE"
fi

# 6. Other common spec/design locations
append_directory "specs" "Specifications" "*.md" || \
append_directory "spec" "Specifications" "*.md" || \
append_directory "specifications" "Specifications" "*.md" || \
append_directory "docs/specs" "Specifications" "*.md" || \
echo "⚠️  No specs directory found"

echo ""
echo "Phase 4: Collecting enhancements and technical plans..."

# 7. Enhancements (multiagent-core style)
if [ -d "docs/enhancements" ]; then
    append_directory "docs/enhancements/01-proposed" "Proposed Enhancements" "*.md" || true
    append_directory "docs/enhancements/02-approved" "Approved Enhancements" "*.md" || true
    append_directory "docs/enhancements/03-in-progress" "In-Progress Enhancements" "*.md" || true
fi

# 8. Refactors (multiagent-core style)
if [ -d "docs/refactors" ]; then
    append_directory "docs/refactors/01-proposed" "Proposed Refactors" "*.md" || true
    append_directory "docs/refactors/02-approved" "Approved Refactors" "*.md" || true
fi

# 9. Other enhancement/feature documentation
append_directory "features" "Feature Documentation" "*.md" || \
append_directory "docs/features" "Feature Documentation" "*.md" || \
append_directory "rfcs" "RFCs (Request for Comments)" "*.md" || \
append_directory "docs/rfcs" "RFCs" "*.md" || \
echo "⚠️  No feature/enhancement documentation found"

echo ""
echo "Phase 5: Collecting integration and contract documentation..."

# 10. Integration documentation
append_directory "docs/integration" "Integration Documentation" "*.md" || \
append_directory "integrations" "Integration Documentation" "*.md" || \
echo "⚠️  No integration documentation found"

# 11. API contracts
append_directory "contracts" "API Contracts" "*.json" || true
append_directory "contracts" "API Contracts" "*.yaml" || true
append_directory "schemas" "API Schemas" "*.json" || true
append_directory "schemas" "API Schemas" "*.yaml" || true

echo ""
echo "Phase 6: Collecting database and data models..."

# 12. Database schemas and migrations
append_directory "migrations" "Database Migrations" "*.sql" || \
append_directory "db/migrations" "Database Migrations" "*.sql" || \
append_directory "database/migrations" "Database Migrations" "*.sql" || \
echo "⚠️  No database migrations found"

find_and_append "*models.py" "Python Models" 3 || true
find_and_append "*schema.sql" "SQL Schemas" 3 || true
find_and_append "*schema.prisma" "Prisma Schema" 3 || true

echo ""
echo "Phase 7: Collecting configuration and infrastructure..."

# 13. Infrastructure as code
find_and_append "docker-compose.yml" "Docker Compose Configuration" 2 || \
find_and_append "docker-compose.yaml" "Docker Compose Configuration" 2 || true

find_and_append "Dockerfile" "Dockerfile" 2 || true
find_and_append "*.tf" "Terraform Configuration" 3 || true
find_and_append "k8s*.yaml" "Kubernetes Configuration" 3 || true

# 14. CI/CD configuration
append_directory ".github/workflows" "GitHub Actions Workflows" "*.yml" || true
append_file ".gitlab-ci.yml" "GitLab CI Configuration" || true
append_file "Jenkinsfile" "Jenkins Pipeline" || true

echo ""
echo "✅ Context gathering complete"
echo ""
echo "Summary:"
echo "--------"
wc -l "$CONTEXT_FILE" | awk '{print "Total lines collected: " $1}'
echo "Context file: $CONTEXT_FILE"
echo ""

# Output the context file path for the command to use
echo "$CONTEXT_FILE"
