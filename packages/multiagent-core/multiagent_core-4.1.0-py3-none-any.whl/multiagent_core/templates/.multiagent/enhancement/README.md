# Enhancement Subsystem

**Full lifecycle management from capture to completion**

## Purpose

Manages enhancements from idea through implementation:
- Captures future improvements from PR reviews or manual creation
- Analyzes architecture fit, complexity, and business value
- Generates analysis reports for decision-making
- Tracks status from idea to completion
- Provides git safety during implementation
- Promotes complex enhancements to full specs

## What It Does

1. **Capture Enhancements** - From PR reviews or manual creation
2. **Analyze Fit** - Architecture impact, complexity, effort estimation
3. **Generate Reports** - Analysis reports with recommendations
4. **Track Status** - `not-started` → `analyzed` → `ready` → `in-progress` → `completed`
5. **Safe Implementation** - Git tagging and rollback protection
6. **Lifecycle Management** - Complete workflow from idea to production

---

## Commands

### Capture Phase

#### `/enhancement:create "<title>"`
Create new enhancement manually

**Example**:
```bash
/enhancement:create "Add Redis caching layer"
```

**Outputs**: `enhancements/NNN-title/enhancement.md`

#### `/enhancement:create --from-pr <pr-number>`
Capture enhancements from PR review feedback

**Example**:
```bash
/enhancement:create --from-pr 123
```

**Outputs**: Multiple enhancement folders from PR feedback

**Note**: Usually invoked automatically by `/github:pr-review`

---

### Analysis Phase

#### `/enhancement:analyze [id]` or `/enhancement:analyze --all`
Analyze one or all enhancements for architecture fit and complexity

**Example**:
```bash
/enhancement:analyze --all
```

**Spawns**: `enhancement-analyzer` agent

**Outputs**:
- `enhancements/NNN/analysis.md` - Detailed individual analysis
- `docs/reports/enhancement-analysis-YYYY-MM-DD.md` - Consolidated report

**What It Analyzes**:
- Architecture fit (affected subsystems, integration points)
- Technical complexity (1-5 scale)
- Implementation effort (hours/days)
- Business value (LOW/MEDIUM/HIGH/CRITICAL)
- Recommendation (🟢 implement / 🟡 defer / 🔴 reject)
- Priority score (0-10)

#### `/enhancement:list [--status=<status>] [--priority=<priority>]`
List all enhancements with status

**Example**:
```bash
/enhancement:list
/enhancement:list --status=ready
/enhancement:list --priority=high
```

**Outputs**: Formatted table grouped by status:
- 🔴 Not Started
- ✅ Analyzed
- 🟢 Ready to Implement
- 🔵 In Progress
- ⚠️  Blocked
- ✅ Completed
- 🟡 Deferred
- ❌ Rejected

---

### Decision Phase

#### `/enhancement:status <id> <new-status>`
Update enhancement status

**Example**:
```bash
/enhancement:status 001 ready
```

**Valid Statuses**:
- `not-started` - Captured, not analyzed yet
- `analyzed` - Analysis complete, awaiting decision
- `ready` - Approved for implementation
- `in-progress` - Currently being implemented
- `blocked` - Cannot proceed (dependencies, conflicts)
- `completed` - Implemented and merged
- `rejected` - Decision made not to implement
- `deferred` - Postponed to future date

**Updates**:
- `enhancements/NNN/status.json` - Machine-readable
- `enhancements/NNN/enhancement.md` - Human-readable

---

### Implementation Phase

#### `/enhancement:start <id>`
Begin implementation with git safety measures

**Example**:
```bash
/enhancement:start 001
```

**Actions**:
- Creates safety tag: `pre-enhancement/001-timestamp`
- Creates branch: `enhancement/001-title`
- Updates status: `ready` → `in-progress`

#### `/enhancement:rollback`
Rollback to safety tag (if experiment didn't work)

**Example**:
```bash
/enhancement:rollback
```

**Actions**: Resets to pre-enhancement tag (destructive, prompts for confirmation)

#### `/enhancement:cleanup <id>`
Clean up after successful completion

**Example**:
```bash
/enhancement:cleanup 001
```

**Actions**:
- Deletes branch: `enhancement/001-title`
- Deletes safety tag: `pre-enhancement/001-*`
- Archives tracking files

#### `/enhancement:full-reset <id>`
Rollback + cleanup in one command (for failed experiments)

**Example**:
```bash
/enhancement:full-reset 001
```

**Actions**: Sequential rollback → switch to main → cleanup

---

### Promotion Phase

#### `/enhancement:promote <id>`
Promote enhancement to full spec (for complex enhancements)

**Example**:
```bash
/enhancement:promote 001
```

**When to Use**:
- Enhancement is larger than expected (> 2 days)
- Requires detailed task breakdown
- Needs comprehensive planning
- Should be tracked as major feature

**Actions**: Creates `specs/NNN-title/` from enhancement analysis

---

## Command Reference

### `/enhancement:create "<title>"` or `/enhancement:create --from-pr <pr-number>`
**Agent**: None (direct execution)
**Scripts**:
  - enhancement/scripts/get-next-id.sh
**Templates**:
  - enhancement/templates/enhancement.md.template
  - enhancement/templates/enhancement-metadata-schema.md
**Outputs**: enhancements/ENH-XXX-title/enhancement.md
**Outcome**: New enhancement created with unique ID and metadata

### `/enhancement:list [--status=<status>] [--priority=<priority>]`
**Agent**: None (direct execution)
**Scripts**:
  - enhancement/scripts/list-enhancements.sh
**Templates**: None
**Outputs**: Filtered list of enhancements
**Outcome**: User can see all enhancements with optional filtering

### `/enhancement:status <id> <new-status>`
**Agent**: None (direct execution)
**Scripts**:
  - enhancement/scripts/update-status.sh
**Templates**:
  - enhancement/templates/enhancement-status-schema.json
**Outputs**: Updated enhancements/ENH-XXX-*/status.json
**Outcome**: Enhancement status updated (not-started/analyzed/ready/in-progress/blocked/completed/rejected/deferred)

### `/enhancement:start <id>`
**Agent**: None (direct execution)
**Scripts**:
  - enhancement/scripts/start-enhancement.sh
**Templates**: None
**Outputs**: Git safety tag + new branch
**Outcome**: Safe rollback point created before making changes

### `/enhancement:analyze [id]` or `/enhancement:analyze --all`
**Agent**: enhancement-analyzer
**Scripts**: None
**Templates**:
  - enhancement/templates/enhancement-analysis-EXAMPLE.md
**Outputs**: enhancements/ENH-XXX-*/analysis.md
**Outcome**: Architecture fit analysis with complexity and effort estimates

### `/enhancement:promote <id>`
**Agent**: None (direct execution)
**Scripts**: None
**Templates**: None
**Outputs**: New spec directory created from enhancement
**Outcome**: Enhancement promoted to full specification for implementation

### `/enhancement:rollback`
**Agent**: None (direct execution)
**Scripts**:
  - enhancement/scripts/rollback-enhancement.sh
**Templates**: None
**Outputs**: Git reset to safety tag
**Outcome**: Code reverted to pre-enhancement state (destructive)

### `/enhancement:cleanup <enhancement-name>`
**Agent**: None (direct execution)
**Scripts**:
  - enhancement/scripts/cleanup-enhancement.sh
**Templates**: None
**Outputs**: Branch and tag deleted
**Outcome**: Git artifacts cleaned up (destructive)

### `/enhancement:full-reset <enhancement-name>`
**Agent**: None (direct execution)
**Scripts**:
  - enhancement/scripts/full-reset.sh
**Templates**: None
**Outputs**: Complete rollback (reset + cleanup + return to main)
**Outcome**: Enhancement completely undone (destructive)

---

## Integration with GitHub PR Review

When you run `/github:pr-review 123`:

1. `judge-architect` agent analyzes feedback
2. Future enhancements auto-created in `enhancements/`
3. Each enhancement gets folder with `enhancement.md`
4. Status automatically set to `not-started`

**Then**:
```bash
/enhancement:analyze --all     # Analyze all captured enhancements
# Review report
/enhancement:status 001 ready  # Approve what to implement
/enhancement:start 001         # Begin implementation
```

---

## Typical Workflow

### Workflow 1: From PR Review

```bash
# 1. PR review captures enhancements
/github:pr-review 123
# → Creates enhancements/001/, 002/, 003/

# 2. Analyze all
/enhancement:analyze --all
# → Generates analysis.md for each
# → Creates consolidated report with recommendations

# 3. Review report and approve
cat docs/reports/enhancement-analysis-2025-10-13.md
/enhancement:status 001 ready
/enhancement:status 002 ready

# 4. Implement (one at a time)
/enhancement:start 001
# work on implementation...
git add . && git commit -m "feat: add Redis caching"

# 5. Complete or rollback
# Option A: Success
/enhancement:cleanup 001

# Option B: Failure
/enhancement:full-reset 001
```

### Workflow 2: Manual Enhancement

```bash
# 1. Create enhancement manually
/enhancement:create "Add Redis caching layer"

# 2. Analyze
/enhancement:analyze 001

# 3. Review and approve
cat enhancements/001-add-redis-caching-layer/analysis.md
/enhancement:status 001 ready

# 4. Start implementation
/enhancement:start 001

# 5. Complete
/enhancement:status 001 completed
/enhancement:cleanup 001
```

### Workflow 3: Promote to Full Spec

```bash
# If enhancement turns out to be complex...
/enhancement:promote 001
# → Creates specs/010-add-redis-caching-layer/

# Continue with spec workflow
/iterate:tasks 010
/iterate:adjust 010
```

---

## File Structure

```
enhancements/
├── 001-redis-caching/
│   ├── enhancement.md       # Human-readable description
│   ├── analysis.md          # Auto-generated analysis
│   ├── status.json          # Machine-readable status
│   └── notes.md             # Optional manual notes
├── 002-circuit-breaker/
│   ├── enhancement.md
│   ├── analysis.md
│   ├── status.json
│   └── notes.md
└── ...

docs/reports/
└── enhancement-analysis-YYYY-MM-DD.md  # Consolidated analysis report
```

---

## Agents Used

### `enhancement-analyzer`
Analyzes enhancements for architecture fit, complexity, and business value

**Invoked by**: `/enhancement:analyze`

**Responsibilities**:
1. Read enhancement proposals from `enhancements/*/enhancement.md`
2. Load current architecture context
3. Analyze affected subsystems and integration points
4. Assess technical complexity (1-5 scale)
5. Estimate implementation effort (hours/LOC)
6. Evaluate business value and strategic alignment
7. Generate recommendation (implement/defer/reject)
8. Calculate priority score (0-10)
9. Create individual `analysis.md` files
10. Update `status.json` tracking files
11. Generate consolidated analysis report

**Tools**: Read, Write, Glob, Grep, Bash
**Model**: claude-sonnet-4-5-20250929

---

## Templates

### `enhancement.md.template`
Template for creating new enhancement descriptions

**Variables**:
- `{{ID}}` - Enhancement ID (001, 042, etc.)
- `{{TITLE}}` - Short descriptive title
- `{{PRIORITY}}` - critical, high, medium, low
- `{{SOURCE}}` - Where it came from (PR review, manual, etc.)
- `{{CREATED_DATE}}` - YYYY-MM-DD
- `{{DESCRIPTION}}` - 1-3 paragraph description
- `{{EXPECTED_OUTCOMES}}` - Bulleted list
- `{{SUCCESS_CRITERIA}}` - How to know it's done

### `analysis.md.template`
Template for enhancement analysis output

**Variables**: Architecture fit, complexity scores, effort estimates, business value, recommendations

### `status.json.template`
Template for machine-readable status tracking

**Schema**: See `enhancement-status-schema.json` for full specification

---

## Scripts

### `get-next-id.sh`
Calculate next available enhancement ID

**Usage**: `bash get-next-id.sh [project-dir]`
**Output**: Next ID (e.g., "001", "042")

### `list-enhancements.sh`
List all enhancements with status in formatted table

**Usage**: `bash list-enhancements.sh [project-dir] [filter-status] [filter-priority]`
**Output**: Formatted table grouped by status

### `update-status.sh`
Update enhancement status.json file

**Usage**: `bash update-status.sh <project-dir> <id> <new-status>`
**Output**: Updated status.json with timestamp

### Git Safety Scripts

#### `start-enhancement.sh`
Create git safety tag and branch

**Usage**: `bash start-enhancement.sh <enhancement-name>`
**Creates**:
- Tag: `pre-enhancement/<name>-<timestamp>`
- Branch: `enhancement/<name>`

#### `rollback-enhancement.sh`
Reset to safety tag

**Usage**: `bash rollback-enhancement.sh`
**Action**: `git reset --hard` to safety tag

#### `cleanup-enhancement.sh`
Delete branch and tag after completion

**Usage**: `bash cleanup-enhancement.sh <enhancement-name>`
**Removes**: Branch, tag, tracking files

#### `full-reset.sh`
Orchestrator: rollback → switch to main → cleanup

**Usage**: `bash full-reset.sh <enhancement-name>`
**Action**: Complete cleanup sequence

---

## Status Lifecycle

```
not-started
    ↓ (after /enhancement:analyze)
analyzed
    ↓ (human approval)
ready
    ↓ (after /enhancement:start)
in-progress
    ↓ (after merge)
completed
    ↓ (cleanup)
[archived]

Alternative Paths:
- analyzed → deferred (postpone)
- analyzed → rejected (don't implement)
- in-progress → blocked (dependency issue)
- blocked → ready (unblocked)
- ready → promote (escalate to full spec)
```

---

## Examples

### Example 1: High-Value, Low-Effort Enhancement

**Analysis Output**:
```
Enhancement: 001 - Add Redis Caching Layer
Recommendation: 🟢 IMPLEMENT NOW
Priority Score: 8.5/10

Effort: 4-6 hours
Complexity: Medium (3/5)
Business Value: HIGH

Benefits:
- 60-80% reduction in DB queries
- 200-500ms improvement in response time
- Better scalability under load
```

### Example 2: Low-Value, High-Effort Enhancement

**Analysis Output**:
```
Enhancement: 005 - Migrate to Microservices
Recommendation: 🔴 REJECT
Priority Score: 1.2/10

Effort: 3-6 months
Complexity: Extreme (5/5)
Business Value: NEGATIVE (at current scale)

Reasoning:
- Team too small (< 20 engineers)
- No scaling bottlenecks yet
- Premature optimization
- Maintenance overhead > benefit
```

---

## Architecture

### Three-Tier Enhancement System

```
Tier 1: Capture (Lightweight)
├── Manual: /enhancement:create "Title"
└── Automated: /github:pr-review 123

Tier 2: Analysis (Intelligent)
├── enhancement-analyzer agent
├── Architecture fit assessment
├── Complexity scoring (1-5)
├── Effort estimation (hours/LOC)
├── Business value evaluation
├── Priority calculation (0-10)
└── Recommendation generation

Tier 3: Execution (Safe)
├── Git safety (tags + branches)
├── Status tracking (JSON + markdown)
├── Lifecycle management
└── Promotion to specs (if complex)
```

### Integration Points

**Input Sources**:
- `/github:pr-review` → Captures future enhancements
- `/enhancement:create` → Manual creation
- User ideas and feedback

**Output Destinations**:
- `enhancements/*/` → Enhancement tracking
- `docs/reports/` → Analysis reports
- `specs/*/` → Promoted to full specs (if complex)

**Dependencies**:
- GitHub subsystem (PR review feedback)
- Iterate subsystem (if promoted to spec)
- Build subsystem (for analysis of existing architecture)

---

## Troubleshooting

### Enhancement not found
```bash
# Check available enhancements
ls -d enhancements/*/

# Create if needed
/enhancement:create "Enhancement title"
```

### Analysis failed
```bash
# Check if enhancement.md exists
cat enhancements/001-*/enhancement.md

# Re-run analysis
/enhancement:analyze 001
```

### Status not updating
```bash
# Check status.json format
cat enhancements/001-*/status.json | jq .

# Manually update if needed
/enhancement:status 001 ready
```

### Git safety not working
```bash
# Check if tag exists
git tag | grep pre-enhancement

# Check if branch exists
git branch | grep enhancement

# Recreate if needed
/enhancement:start 001
```

---

## Best Practices

### When to Use Enhancements

**Use enhancements for**:
- Quick fixes (< 2 days)
- Simple, focused changes
- Ideas from PR reviews
- Exploratory work
- Low-medium complexity

**Promote to specs for**:
- Complex features (> 2 days)
- Major architectural changes
- Multi-agent coordination needed
- Requires detailed task breakdown

### Workflow Tips

1. **Always analyze before implementing**
   ```bash
   /enhancement:analyze 001  # Don't skip this!
   ```

2. **Review analysis reports before approval**
   ```bash
   cat enhancements/001-*/analysis.md  # Read the recommendation
   ```

3. **Use git safety for risky changes**
   ```bash
   /enhancement:start 001  # Create safety tag first
   ```

4. **One enhancement at a time**
   - Complete or rollback before starting next
   - Prevents conflicts and confusion

5. **Clean up after completion**
   ```bash
   /enhancement:cleanup 001  # Remove git artifacts
   ```

### Analysis Interpretation

**Priority Score Ranges**:
- **8-10**: Must implement (high value, low effort)
- **5-7**: Should implement (good balance)
- **3-4**: Consider deferring (medium value/effort)
- **0-2**: Likely reject (low value or high cost)

**Confidence Scores**:
- **0.9-1.0**: High confidence (act on recommendation)
- **0.7-0.9**: Medium confidence (human judgment needed)
- **0.0-0.7**: Low confidence (needs more research)

---

## Metrics

Track enhancement system effectiveness:

```bash
# Total enhancements over time
find enhancements/ -type d -maxdepth 1 | wc -l

# By status
/enhancement:list | grep -A 1 "Analyzed"
/enhancement:list | grep -A 1 "Completed"

# Average time to implement (from status.json)
# started → completed timestamps
```

---

## Summary

The Enhancement subsystem provides:

✅ **Capture** - From PR reviews or manual creation
✅ **Analyze** - Architecture fit, complexity, business value
✅ **Decide** - Human-reviewed recommendations
✅ **Track** - Status lifecycle from idea to completion
✅ **Implement** - Git safety with rollback protection
✅ **Promote** - Escalate complex enhancements to full specs

**Result**: Systematic management of improvements from capture through completion, with data-driven analysis and safe implementation practices.
