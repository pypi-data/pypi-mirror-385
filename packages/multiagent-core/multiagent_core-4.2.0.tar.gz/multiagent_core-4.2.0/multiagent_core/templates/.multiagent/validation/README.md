# Validation Subsystem

**Purpose**: Test AI agent behavior, context engineering quality, and framework consistency - NOT user application code.

**Status**: ✅ Structure Complete, ⏳ Commands Needed

---

## What This Subsystem Does

Validates the **multiagent framework itself** (agents, commands, templates):

- ✅ Agent prompts are well-structured (Anthropic principles)
- ✅ Commands orchestrate properly (<80 lines, no embedded bash)
- ✅ Templates render without errors
- ✅ Agents produce consistent outputs (determinism >85%)
- ✅ Context quality meets benchmarks (>85% task completion)
- ✅ No regressions from baselines

**This is NOT traditional testing** (pytest, vitest) - that's the `testing/` subsystem.

---

## Directory Structure

```
multiagent_core/templates/.multiagent/validation/
├── README.md                           # This file
├── scripts/                            # ✅ 6 mechanical validation scripts (26KB)
│   ├── validate-agent-prompt.sh        # Check agent definition structure
│   ├── validate-command-structure.sh   # Verify command orchestration
│   ├── validate-template-vars.sh       # Check template placeholders
│   ├── validate-frontmatter.sh         # Verify YAML frontmatter
│   ├── run-determinism-test.sh         # Execute agent multiple times
│   └── compare-outputs.sh              # Calculate output similarity
├── templates/                          # ✅ 2 templates
│   ├── checklist.md.template           # Template for creating checklists
│   └── validation-report.md.template   # Validation report format
├── checklists/                         # ✅ 5 subsystem checklists (116KB, 3,473 lines)
│   ├── implementation-subsystem.md     # 706 lines - Idea/enhancement/refactor workflows
│   ├── enhancement-subsystem.md        # 739 lines - Enhancement lifecycle
│   ├── refactoring-subsystem.md        # 630 lines - Code refactoring validation
│   ├── core-subsystem.md               # 666 lines - Project setup & specs
│   └── documentation-subsystem.md      # 732 lines - Docs sync & validation
├── baselines/                          # ✅ Golden outputs for regression testing
│   ├── core/
│   ├── implementation/
│   ├── enhancement/
│   ├── refactoring/
│   └── documentation/
└── docs/                               # ✅ Workflow documentation
    └── TEST-VALIDATION-DOCS-WORKFLOW.md  # Testing → Validation → Docs flow
```

---

## Mechanical Scripts (100% Non-Intelligent)

All scripts do **ZERO intelligence** - only file I/O, string matching, arithmetic:

### 1. `validate-agent-prompt.sh`
**What it checks** (mechanical only):
- ✅ YAML frontmatter exists
- ✅ `model:` field present (checks for `claude-sonnet-4-5-20250929`)
- ✅ `tools:` array present
- ✅ File length <200 lines
- ✅ No hardcoded paths (`/home/`, `/Users/`)
- ✅ Structured sections present (`<background>`, `<instructions>`)

**What it DOES NOT do**:
- ❌ Evaluate prompt quality
- ❌ Judge if instructions are clear
- ❌ Decide if context is appropriate

**Usage**:
```bash
./validate-agent-prompt.sh ~/.claude/agents/backend-tester.md /tmp/validation.json
```

### 2. `validate-command-structure.sh`
**What it checks**:
- ✅ YAML frontmatter exists
- ✅ File length <80 lines (or warns if <120)
- ✅ Embedded bash detection (counts `if`, `for`, `while`, etc.)
- ✅ SlashCommand() or Task() usage
- ✅ Step numbering present
- ✅ No hardcoded paths
- ✅ Error handling present
- ✅ Script delegation (calls to `.sh` files)

**What it DOES NOT do**:
- ❌ Evaluate orchestration quality
- ❌ Judge workflow logic

**Usage**:
```bash
./validate-command-structure.sh ~/.claude/commands/testing/test.md /tmp/validation.json
```

### 3. `validate-template-vars.sh`
**What it checks**:
- ✅ PURPOSE comment header
- ✅ Finds all `{{PLACEHOLDERS}}`
- ✅ Variables documented in header
- ✅ Agent attribution present
- ✅ Template location documented
- ✅ No unfilled markers (`{{UNFILLED}}`, `{{TODO}}`)
- ✅ Valid YAML frontmatter (if present)
- ✅ Placeholder format consistency

**What it DOES NOT do**:
- ❌ Evaluate template content quality
- ❌ Judge if placeholders are appropriate

**Usage**:
```bash
./validate-template-vars.sh multiagent_core/templates/.multiagent/testing/templates/unit_template.test.js
```

### 4. `validate-frontmatter.sh`
**What it checks**:
- ✅ Frontmatter starts with `---`
- ✅ Frontmatter is closed (second `---`)
- ✅ Expected fields present (customizable)
- ✅ No duplicate keys
- ✅ No tabs (YAML requires spaces)
- ✅ No empty values
- ✅ Reasonable length (<50 lines)

**What it DOES NOT do**:
- ❌ Evaluate field value quality
- ❌ Parse complex YAML structures

**Usage**:
```bash
./validate-frontmatter.sh ~/.claude/agents/backend-tester.md "model,tools"
```

### 5. `run-determinism-test.sh`
**What it does**:
- ✅ Creates directory structure for N runs (default 5)
- ✅ Prepares run directories (`run-1/`, `run-2/`, etc.)
- ✅ Creates metadata files
- ✅ Generates summary JSON

**What it DOES NOT do**:
- ❌ Actually run agents (that's done by `/validation:validate`)
- ❌ Evaluate output quality
- ❌ Decide if outputs are correct

**Usage**:
```bash
./run-determinism-test.sh backend-tester "Create API test" 5 /tmp/determinism-test
```

### 6. `compare-outputs.sh`
**What it does**:
- ✅ Counts files in each run directory
- ✅ Diffs file contents
- ✅ Calculates similarity percentage (arithmetic only)
- ✅ Flags >15% variation
- ✅ Compares all pairs (when using `--all`)
- ✅ Calculates average similarity

**What it DOES NOT do**:
- ❌ Evaluate if differences matter
- ❌ Judge output quality
- ❌ Decide if variation is acceptable

**Usage**:
```bash
# Compare two runs
./compare-outputs.sh /tmp/determinism/run-1 /tmp/determinism/run-2

# Compare all runs
./compare-outputs.sh --all /tmp/determinism-test-123456
```

---

## Intelligence = Agents (Not Scripts)

**validation-analyzer agent** provides the intelligence:
- Reads Anthropic context engineering reports
- Evaluates what mechanical checks mean
- Decides if 20% variation is acceptable for this task
- Suggests improvements based on failures
- Applies context engineering principles

**Separation of Concerns**:
```
Scripts (mechanical) → Data
  ↓
Agent (intelligent) → Analysis
  ↓
Report → Recommendations
```

---

## Checklists (5 Subsystems)

Each checklist has **300+ test items** across 14 sections:

1. **Pre-Validation Setup** - Files exist, settings configured
2. **Mechanical Scripts** - Each script tested individually
3. **Agent Prompts** - Structure + Anthropic principles
4. **Commands** - Pure orchestration validation
5. **Templates** - Placeholder filling verified
6. **Determinism** - 5-run consistency (>85%)
7. **Integration** - Cross-subsystem validation
8. **Workflows** - End-to-end user flows
9. **Context Engineering** - Anthropic benchmarks
10. **Documentation** - Complete and accurate
11. **Performance** - <30s commands, <1s scripts
12. **Security** - No injection vulnerabilities
13. **Architecture** - Separation of concerns
14. **Production Ready** - All checks pass

**Subsystems covered**:
- `implementation-subsystem.md` - Idea/enhancement/refactor → spec workflows
- `enhancement-subsystem.md` - Enhancement lifecycle management
- `refactoring-subsystem.md` - Code refactoring validation
- `core-subsystem.md` - Project setup & spec creation
- `documentation-subsystem.md` - Docs sync & validation

---

## Testing → Validation → Docs Workflow

**Problem**: Docs currently update on file changes, not on validation success.

**Solution**: Three-phase workflow

```
Phase 1: Testing (/testing:test)
  → Run pytest, vitest, playwright
  → Test APPLICATION code
  → Output: test-report.json
  ↓ Tests PASS ✅

Phase 2: Validation (/validation:validate)
  → Run validation scripts
  → Test AI AGENTS
  → Output: validation-report.md
  ↓ Validation PASS ✅ (score >= 85)

Phase 3: Documentation (/docs:update --validated)
  → Update docs with PROOF
  → Add badges, timestamps, scores
  → Create audit trail
  → Output: Updated docs with validation status
```

**Commands to implement**:
1. `/validation:validate --subsystem <name>` - Full validation suite
2. `/validation:check` - Quick pre-commit check
3. `/docs:update --validated` - Update with validation proof
4. `/validate-and-document` - Orchestrator for full workflow

**See**: `docs/TEST-VALIDATION-DOCS-WORKFLOW.md` for complete details

---

## Anthropic Context Engineering Principles

Validation is based on 6 Anthropic articles synthesized in:
`docs/reports/2025-10-18/context-engineering/00-SYNTHESIS-context-engineering-validation-framework.md`

**Key principles**:
1. **Tools > Prompts** - Focus on command quality
2. **Context is Finite** - Measure degradation at varying lengths
3. **Evaluation-Driven** - Can't improve what you don't measure
4. **Multi-agent coordination** - 90%+ improvements when done right
5. **What Agents Omit** - Analyze raw transcripts, look for silent failures
6. **Simple, composable patterns** - Add complexity only when justified

**Target metrics** (from research):
- Task completion: >85%
- Tool selection accuracy: >90%
- Determinism: >85%
- Context efficiency: >70%
- Multi-agent improvement: >50% vs single-agent

---

## Usage Examples

### Validate an Agent
```bash
cd multiagent_core/templates/.multiagent/validation/scripts
./validate-agent-prompt.sh ~/.claude/agents/backend-tester.md

# Output: JSON report with score, issues, warnings
```

### Validate a Command
```bash
./validate-command-structure.sh ~/.claude/commands/testing/test.md

# Output: Checks orchestration purity, embedded bash, length
```

### Test Determinism
```bash
# 1. Prepare test structure
./run-determinism-test.sh backend-tester "Create API test" 5 /tmp/det-test

# 2. Run /validation:validate to execute agent and populate runs

# 3. Compare outputs
./compare-outputs.sh --all /tmp/det-test

# Output: Average similarity, variation percentage, status
```

### Validate Template
```bash
./validate-template-vars.sh ~/.multiagent/testing/templates/unit_template.test.js

# Output: Finds all {{PLACEHOLDERS}}, checks documentation
```

---

## Next Steps

**Still need to implement**:
- [ ] `/validation:validate` command - Orchestrates all scripts + agent analysis
- [ ] `/validation:check` command - Quick pre-commit validation
- [ ] `/validation:baseline` command - Store golden outputs
- [ ] `/docs:update --validated` flag - Update docs with validation proof
- [ ] `/validate-and-document` - Full workflow orchestrator
- [ ] Git hooks integration (pre-commit, pre-push)
- [ ] CI/CD workflow integration

**Already complete**:
- [x] Directory structure
- [x] 6 mechanical validation scripts (26KB)
- [x] 5 subsystem checklists (116KB, 3,473 lines)
- [x] 2 templates (checklist, validation-report)
- [x] Baselines directory structure
- [x] Workflow documentation

---

## Integration Points

### With Testing Subsystem
- Testing validates application code → Validation validates AI agents
- Both must pass before docs update
- Testing outputs test-report.json → Validation reads it

### With Documentation Subsystem
- Docs update only when validation passes
- Validation report becomes part of docs
- Audit trail tracks validation history

### With All Subsystems
- Each subsystem has a validation checklist
- Validates agents, commands, scripts, templates
- Ensures framework quality and consistency

---

## Files Created

**Total**: 142KB across 14 files

### Scripts (6 files, 26KB)
- `validate-agent-prompt.sh` (4.4KB)
- `validate-command-structure.sh` (4.3KB)
- `validate-template-vars.sh` (4.6KB)
- `validate-frontmatter.sh` (4.9KB)
- `run-determinism-test.sh` (2.9KB)
- `compare-outputs.sh` (5.6KB)

### Checklists (5 files, 116KB)
- `implementation-subsystem.md` (25KB, 706 lines)
- `enhancement-subsystem.md` (25KB, 739 lines)
- `refactoring-subsystem.md` (21KB, 630 lines)
- `core-subsystem.md` (21KB, 666 lines)
- `documentation-subsystem.md` (24KB, 732 lines)

### Templates (2 files)
- `checklist.md.template`
- `validation-report.md.template`

### Documentation (2 files)
- `TEST-VALIDATION-DOCS-WORKFLOW.md`
- `README.md` (this file)

---

**Last Updated**: 2025-10-19
**Status**: Structure complete, commands needed
**Integration**: Testing → Validation → Docs workflow documented
