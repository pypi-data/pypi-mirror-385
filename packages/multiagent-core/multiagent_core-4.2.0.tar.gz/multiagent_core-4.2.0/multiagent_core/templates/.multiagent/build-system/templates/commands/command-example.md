---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Read(*), Task(*)
argument-hint: [message]
description: Create standardized git commit with analysis and proper format
---

# Smart Commit Command

User input: $ARGUMENTS

## Context

- Staged changes: !`git diff --staged`
- Recent commits: !`git log --oneline -5`
- Current branch: !`git branch --show-current`

## Reference Files

- Commit standards: @docs/commit-standards.md
- Co-author format: @.multiagent/agents/docs/commit-workflow.md

## Task

Invoke the git-commit-helper subagent to create standardized commit

**Arguments**:
- Message: ${1:-"Auto-generated commit message"}

**Task**:
1. Analyze staged changes
2. Generate commit message following standards
3. Create commit with proper format
4. Include co-author attribution

**Success Criteria**:
- Summary under 50 characters
- Body explains what and why (not how)
- Includes co-author attribution
- Follows conventional commit format

**Output**: Git commit created in current repository

---

**Generated from**: multiagent_core/templates/.multiagent/build-system/templates/commands/command.md.template
**Template Version**: 1.0.0
**Example**: Complete working command following all standards (under 60 lines)
