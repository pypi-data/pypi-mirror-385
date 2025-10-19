# Refactoring Subsystem

## Purpose

Code quality improvement tools for existing codebases, focusing on improving code structure, performance, and maintainability without adding new features.

## What It Does

1. **Code Analysis** - Identifies refactoring opportunities, duplicate code, and technical debt across the codebase
2. **Duplicate Extraction** - DRYs up repeated code by extracting common patterns into shared utilities
3. **Pattern Modernization** - Updates legacy patterns (callbacks → async/await, class → functional components)
4. **Performance Optimization** - Fixes N+1 queries, slow algorithms, and performance bottlenecks
5. **Technical Debt Cleanup** - Removes dead code, updates deprecated APIs, standardizes naming conventions

## Agents Used

- **@claude/refactoring-analyzer** - Analyzes codebase to find refactoring opportunities, duplicate code, and areas needing improvement
- **@claude/code-refactorer** - Performs actual refactoring work across multiple files (existing agent, reused)

## Commands

### `/refactoring:refactor` - Refactor code with multiple operation modes

**Usage**: `/refactoring:refactor [options]`

**Examples**:
```bash
# Analysis modes
/refactoring:refactor --analyze                    # Find all refactoring opportunities
/refactoring:refactor --detect-duplicates          # Scan for duplicate code blocks

# Action modes
/refactoring:refactor --extract-duplicates         # DRY up repeated code
/refactoring:refactor --modernize                  # Update old patterns to modern syntax
/refactoring:refactor --optimize                   # Fix performance issues

# Combined operations
/refactoring:refactor --analyze --extract-duplicates --modernize

# Targeted refactoring
/refactoring:refactor --file="src/api/users.ts" --optimize
/refactoring:refactor --pattern="callbacks" --modernize
```

Main command supporting multiple operation flags. Can analyze code for issues, detect duplicates, extract common patterns, modernize legacy code, optimize performance, and clean up technical debt. Operations can be combined for comprehensive refactoring.

**Spawns**: `refactoring-analyzer` agent (for analysis) or `code-refactorer` agent (for actions)

**Outputs**:
- Analysis: `docs/reports/refactoring-report-{timestamp}.md`
- Changes: Modified source files with improved code quality
- Comparison: `docs/reports/before-after-comparison-{timestamp}.md`

---

## Architecture

```
User runs /refactoring:refactor [--flags]
      ↓
Command orchestrates:
1. Parse flags to determine operations
2. Run analysis scripts (find duplicates, scan deprecated patterns)
3. Invoke appropriate agent:
   - refactoring-analyzer (for --analyze, --detect-*)
   - code-refactorer (for --extract-*, --modernize, --optimize)
4. Generate reports from templates
5. Apply code changes if action flags present
6. Display summary of improvements
```

## How It Works

1. **Command Invocation**: User runs `/refactoring:refactor` with operation flags
2. **Flag Parsing**: Command determines which operations to perform
3. **Script Execution**: Mechanical scripts scan for duplicates, deprecated APIs, complexity
4. **Agent Analysis**: Intelligent agent analyzes findings and creates refactoring plan
5. **Code Changes**: Agent applies refactoring across multiple files (if action flags present)
6. **Report Generation**: Creates analysis reports and before/after comparisons
7. **User Feedback**: Displays summary of changes, metrics, and recommendations

## Directory Structure

```
.multiagent/refactoring/
├── README.md              # This file
├── docs/                  # Refactoring concepts and patterns
├── templates/             # Report and comparison templates
│   ├── refactoring-report.md.template
│   └── before-after-comparison.md.template
├── scripts/               # Mechanical scanning operations
│   ├── find-duplicates.sh
│   ├── scan-deprecated.sh
│   └── analyze-complexity.sh
└── memory/               # Refactoring history (optional)
```

## Templates

Templates in this subsystem:

- `templates/refactoring-report.md.template` - Analysis report showing refactoring opportunities
- `templates/before-after-comparison.md.template` - Side-by-side comparison of code improvements

## Scripts

Mechanical scripts in this subsystem:

- `scripts/find-duplicates.sh` - Scans codebase for duplicate code blocks
- `scripts/scan-deprecated.sh` - Finds usage of deprecated APIs and old patterns
- `scripts/analyze-complexity.sh` - Identifies overly complex functions needing simplification

## Available Flags

### Analysis Flags
- `--analyze` - Find refactoring opportunities across entire codebase
- `--detect-duplicates` - Scan for duplicate code blocks
- `--detect-smells` - Identify code smells and anti-patterns (future)

### Action Flags
- `--extract-duplicates` - Extract repeated code into shared utilities
- `--modernize` - Update legacy patterns (callbacks → async/await, class → functional)
- `--optimize` - Fix performance issues (N+1 queries, inefficient algorithms)
- `--clean-debt` - Remove dead code and update deprecated APIs

### Target Flags
- `--file="path"` - Target specific file for refactoring
- `--pattern="name"` - Target specific pattern (e.g., "callbacks", "class-components")
- `--scope="directory"` - Limit operations to specific directory (future)

## Outputs

This subsystem generates:

```
docs/reports/
├── refactoring-report-{timestamp}.md        # Analysis results
└── before-after-comparison-{timestamp}.md   # Code improvements

src/ (modified files)
├── {refactored-files}                       # Updated with improvements
└── utils/ (new shared code)
    └── {extracted-utilities}.ts             # Extracted common patterns
```

## Usage Example

```bash
# Step 1: Analyze codebase for refactoring opportunities
/refactoring:refactor --analyze

# Review: Check docs/reports/refactoring-report-{timestamp}.md

# Step 2: Extract duplicate code found during analysis
/refactoring:refactor --extract-duplicates

# Step 3: Modernize legacy callback patterns
/refactoring:refactor --modernize --pattern="callbacks"

# Step 4: Optimize performance issues
/refactoring:refactor --optimize

# Combined: Comprehensive refactoring in one command
/refactoring:refactor --analyze --extract-duplicates --modernize --optimize

# Targeted: Refactor specific file
/refactoring:refactor --file="src/api/legacy.ts" --modernize --optimize
```

## Troubleshooting

### Duplicate detection finds false positives
**Problem**: Script flags similar-looking code that isn't actually duplicated
**Solution**:
```bash
# Use --file flag to target specific areas with known duplicates
/refactoring:refactor --file="src/services/" --detect-duplicates
```

### Refactoring breaks tests
**Problem**: Automated refactoring changes behavior unexpectedly
**Solution**:
```bash
# 1. Rollback changes
git checkout .

# 2. Run with --analyze first to review proposed changes
/refactoring:refactor --analyze

# 3. Apply changes incrementally with specific flags
/refactoring:refactor --extract-duplicates  # Test after this
/refactoring:refactor --modernize           # Then test this
```

### Pattern not recognized for modernization
**Problem**: `--pattern` flag doesn't find expected legacy patterns
**Solution**:
```bash
# Check available patterns in analysis report first
/refactoring:refactor --analyze

# Review docs/reports/refactoring-report-*.md for pattern names
# Use exact pattern name from report
```

## Related Subsystems

- **Enhancement**: Handles adding NEW features with lifecycle tracking (refactoring improves EXISTING code)
- **Testing**: Validates that refactored code maintains functionality
- **Documentation**: Updates docs to reflect refactored code structure
- **Performance**: Monitors performance improvements from optimization refactoring
- **Git**: Manages branches and commits for refactoring work

## Key Differences from Enhancement Subsystem

**Refactoring** (this subsystem):
- Improves EXISTING code without adding features
- Maintains same functionality with better structure/performance
- No lifecycle tracking needed (apply and done)
- Focus: Code quality, performance, maintainability

**Enhancement**:
- Adds NEW features or capabilities
- Changes functionality
- Has lifecycle (analyze → approve → implement → rollback if needed)
- Focus: Feature additions, user-facing changes

## Future Enhancements

Planned features for this subsystem:

- [ ] `--detect-smells` flag for automatic code smell detection
- [ ] `--scope` flag to limit refactoring to specific directories
- [ ] Integration with code coverage tools to prioritize high-impact refactoring
- [ ] Automatic test generation for refactored code
- [ ] Rollback mechanism for failed refactoring attempts
- [ ] Performance benchmarking before/after refactoring
- [ ] Team collaboration features (suggest refactoring to other developers)
