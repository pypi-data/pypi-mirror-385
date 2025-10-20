# Initial Architecture Assessment: {{PROJECT_NAME}}

**Reviewer**: @qwen (CTO-level)
**Date**: {{REVIEW_DATE}}
**Documentation Level**: {{DOC_LEVEL}} (Minimal/Basic)
**Assessment Type**: Initial Project Discovery

---

## Context Found

**Files discovered:**
{{CONTEXT_SUMMARY}}

**Documentation completeness**: {{COMPLETENESS_PERCENT}}%

---

## Project Discovery

### Project Type
{{PROJECT_TYPE}}

### Tech Stack
{{TECH_STACK}}

### Current State
- **Code size**: {{LOC}} lines of code
- **Development phase**: {{DEV_PHASE}}
- **Team size**: {{TEAM_SIZE}}

---

## Inferred Architecture

Based on code structure analysis:

### Components Identified
{{COMPONENTS_IDENTIFIED}}

### Data Layer
{{DATA_LAYER_DESCRIPTION}}

### API Layer (if applicable)
{{API_LAYER_DESCRIPTION}}

### Frontend Layer (if applicable)
{{FRONTEND_LAYER_DESCRIPTION}}

### Infrastructure
{{INFRASTRUCTURE_DESCRIPTION}}

---

## Unclear or Ambiguous

The following architectural aspects are unclear without documentation:

{{UNCLEAR_ASPECTS}}

---

## Initial Observations

### Strengths
{{OBSERVED_STRENGTHS}}

### Concerns
{{OBSERVED_CONCERNS}}

### Risks Identified
{{INITIAL_RISKS}}

---

## Recommended Documentation

To enable comprehensive architectural review, create the following documentation:

### Critical (Must Have)
{{CRITICAL_DOCS}}

### Important (Should Have)
{{IMPORTANT_DOCS}}

### Nice-to-Have
{{NICE_TO_HAVE_DOCS}}

---

## Documentation Templates

Here are suggested templates to get started:

### 1. ARCHITECTURE.md
```markdown
# Architecture Overview

## System Components
- Component 1: Purpose and responsibilities
- Component 2: Purpose and responsibilities

## Data Flow
[Describe how data moves through the system]

## Technology Stack
- Backend: [Framework/Language]
- Frontend: [Framework/Library]
- Database: [Database type]
- Infrastructure: [Cloud provider, containerization]

## Deployment
[How is the system deployed?]
```

### 2. API Documentation
```markdown
# API Endpoints

## Authentication
[How do clients authenticate?]

## Core Endpoints
- GET /api/resource - Description
- POST /api/resource - Description

## Error Handling
[How are errors returned?]
```

### 3. Database Schema
```markdown
# Database Schema

## Tables/Collections
- users: [Fields and relationships]
- resources: [Fields and relationships]

## Indexes
[What indexes exist?]

## Migrations
[How are schema changes managed?]
```

---

## Quick Wins

Immediate improvements you can make without extensive refactoring:

{{QUICK_WINS}}

---

## Next Steps

1. **Create baseline documentation** using templates above
2. **Address any critical concerns** identified in initial observations
3. **Request full CTO review** once architecture documentation is in place

**Estimated effort to create docs**: {{EFFORT_ESTIMATE}}

---

## Follow-Up Review

Once documentation is created, request a full CTO review:

```bash
/cto:review --project
```

This will provide:
- Comprehensive architectural analysis
- Performance and scalability assessment
- Security evaluation
- Detailed risk categorization

---

**Reviewed by**: @qwen
**Assessment Date**: {{REVIEW_DATE}}
**Status**: INITIAL ASSESSMENT - Documentation recommended before full review
