# Build System - Comprehensive Testing Checklist

**Version**: 1.0.0
**Date**: 2025-10-19
**Purpose**: Validate all build system components work as intended

---

## 1. File Structure Validation

### Templates Directory
- [ ] `templates/agents/agent.md.template` exists
- [ ] `templates/agents/agent-example.md` exists
- [ ] `templates/commands/command.md.template` exists
- [ ] `templates/commands/command-example.md` exists
- [ ] `templates/skills/SKILL.md.template` exists
- [ ] `templates/skills/skill-example/SKILL.md` exists
- [ ] `templates/plugins/plugin.json.template` exists
- [ ] `templates/plugins/example-plugin/` complete structure

### Reference Documentation
- [ ] `docs/01-claude-code-slash-commands.md` exists
- [ ] `docs/02-claude-code-skills.md` exists
- [ ] `docs/03-claude-code-plugins.md` exists
- [ ] `docs/04-skills-vs-commands.md` exists
- [ ] All docs have proper content (not stubs)

### Validation Scripts
- [ ] `scripts/validate-agent.sh` exists
- [ ] `scripts/validate-command.sh` exists
- [ ] `scripts/validate-skill.sh` exists
- [ ] `scripts/validate-plugin.sh` exists
- [ ] All scripts are executable (`chmod +x`)

### Build Commands
- [ ] `~/.claude/commands/build/slash-command.md` exists
- [ ] `~/.claude/commands/build/agent.md` exists
- [ ] `~/.claude/commands/build/skill.md` exists
- [ ] `~/.claude/commands/build/plugin.md` exists
- [ ] `~/.claude/commands/build/subsystem.md` exists
- [ ] `~/.claude/commands/build/subsystem-full.md` exists
- [ ] `~/.claude/commands/build/analyze.md` exists
- [ ] `~/.claude/commands/build/enhance.md` exists
- [ ] `~/.claude/commands/build/remove.md` exists

### Builder Agents
- [ ] `~/.claude/agents/command-builder.md` exists
- [ ] `~/.claude/agents/agent-builder.md` exists
- [ ] `~/.claude/agents/skill-builder.md` exists
- [ ] `~/.claude/agents/plugin-builder.md` exists
- [ ] `~/.claude/agents/build-dependency-analyzer.md` exists

---

## 2. Content Validation

### Builder Agents - Step 0 Verification
- [ ] `command-builder` has Step 0 context loading
- [ ] `agent-builder` has Step 0 context loading
- [ ] `skill-builder` has Step 0 context loading
- [ ] `plugin-builder` has Step 0 context loading
- [ ] All Step 0 sections load correct templates/docs

### Builder Agents - Infrastructure Analysis
- [ ] `skill-builder` loads existing commands/agents/subsystems (Step 0)
- [ ] `skill-builder` has "Analyze Existing Infrastructure" step
- [ ] `skill-builder` supports `--from-command`, `--from-agent`, `--from-subsystem`
- [ ] `plugin-builder` loads existing commands/agents/skills (Step 0)
- [ ] `plugin-builder` has "Analyze Existing Infrastructure" step
- [ ] `plugin-builder` supports `--from-subsystem`, `--theme` flags

### Build Commands - Context Loading
- [ ] `/build:slash-command` loads focused context (section anchors)
- [ ] `/build:agent` loads focused context (section anchors)
- [ ] `/build:skill` loads Claude Code skills reference
- [ ] `/build:plugin` loads Claude Code plugins reference
- [ ] All commands reference build-system templates with `@` prefix

### Templates - Placeholder Validation
- [ ] Agent template uses `{{VARIABLE}}` format
- [ ] Command template uses `{{VARIABLE}}` format
- [ ] Skill template uses `{{VARIABLE}}` format
- [ ] Plugin template uses `{{VARIABLE}}` format
- [ ] All placeholders documented in comments

---

## 3. Functional Testing

### Test 1: Create Slash Command
```bash
# Run this test
/build:slash-command test-subsystem test-command "Test command description"

# Expected results
✓ Command file created at ~/.claude/commands/test-subsystem/test-command.md
✓ File has valid YAML frontmatter
✓ File is under 60 lines
✓ Contains @ and ! prefix patterns
✓ Contains Task() invocation
✓ Registered in ~/.claude/settings.json

# Validation
- [ ] Command file created successfully
- [ ] Frontmatter is valid YAML
- [ ] File length < 60 lines
- [ ] Context loading with @ prefix
- [ ] Agent invocation present
- [ ] Settings.json updated

# Cleanup
rm ~/.claude/commands/test-subsystem/test-command.md
```

### Test 2: Create Agent
```bash
# Run this test
/build:agent test-analyzer "Analyzes test data" "Read,Write,Bash"

# Expected results
✓ Agent file created at ~/.claude/agents/test-analyzer.md
✓ File has valid YAML frontmatter
✓ Step 0: Load Required Context section exists
✓ Success criteria section exists
✓ Tools are comma-separated (no spaces)

# Validation
- [ ] Agent file created successfully
- [ ] Frontmatter is valid YAML
- [ ] Step 0 section exists
- [ ] Success criteria with checkboxes
- [ ] Tools format: "Read,Write,Bash" (no spaces)

# Cleanup
rm ~/.claude/agents/test-analyzer.md
```

### Test 3: Create Skill (New)
```bash
# Run this test
/build:skill "Test Processor" "Process test files. Use when working with test data." --scope=project

# Expected results
✓ Skill directory created at .claude/skills/test-processor/
✓ SKILL.md file created with frontmatter
✓ Description includes "Use when" trigger
✓ Validation script passes

# Validation
- [ ] Skill directory created
- [ ] SKILL.md exists
- [ ] Frontmatter is valid
- [ ] "Use when" in description
- [ ] Validation passes

# Cleanup
rm -rf .claude/skills/test-processor
```

### Test 4: Create Skill (From Existing Command)
**Prerequisites**: Requires existing command to repackage

```bash
# Setup: Check if security:scan-secrets exists
ls ~/.claude/commands/security/scan-secrets.md

# Run this test (if command exists)
/build:skill "Secret Scanner" --from-command security/scan-secrets

# Expected results
✓ skill-builder analyzes existing command
✓ Extracts purpose and arguments
✓ Converts to model-invoked skill
✓ Original command remains for explicit use

# Validation
- [ ] Agent scans existing commands
- [ ] Extracts functionality from command
- [ ] Creates skill with "Use when" context
- [ ] Original command still exists
- [ ] Skill can invoke same agent
```

### Test 5: Create Plugin (Empty Structure)
```bash
# Run this test
/build:plugin test-toolkit "Testing tools" --components=commands,skills

# Expected results
✓ Plugin directory created at .claude/plugins/test-toolkit/
✓ .claude-plugin/plugin.json created at root
✓ commands/ directory at plugin root (not inside .claude-plugin/)
✓ skills/ directory at plugin root
✓ README.md created
✓ Validation script passes

# Validation
- [ ] Plugin directory structure correct
- [ ] .claude-plugin/ at root with plugin.json
- [ ] Component dirs at root (NOT in .claude-plugin/)
- [ ] Manifest is valid JSON
- [ ] README.md exists
- [ ] Validation passes

# Cleanup
rm -rf .claude/plugins/test-toolkit
```

### Test 6: Create Plugin (From Subsystem)
**Prerequisites**: Requires existing subsystem with commands

```bash
# Check if security subsystem exists
ls ~/.claude/commands/security/

# Run this test (if subsystem exists)
/build:plugin security-toolkit "Security tools" --from-subsystem security

# Expected results
✓ plugin-builder analyzes security subsystem
✓ Copies all security/*.md commands to plugin
✓ Lists commands in manifest
✓ Creates complete plugin structure

# Validation
- [ ] Agent scans security commands
- [ ] Copies commands to plugin/commands/
- [ ] Updates manifest with command list
- [ ] Original commands remain
- [ ] Plugin is self-contained
```

### Test 7: Validation Scripts
```bash
# Test agent validation
./multiagent_core/templates/.multiagent/build-system/scripts/validate-agent.sh \
  ~/.claude/agents/command-builder.md

# Expected: ✅ PASS

# Test command validation
./multiagent_core/templates/.multiagent/build-system/scripts/validate-command.sh \
  ~/.claude/commands/build/slash-command.md

# Expected: ✅ PASS

# Validation
- [ ] validate-agent.sh executable
- [ ] Checks frontmatter completeness
- [ ] Checks Step 0 exists
- [ ] validate-command.sh executable
- [ ] Checks frontmatter
- [ ] Checks file length
```

---

## 4. Integration Testing

### Integration 1: Command → Agent → Template Flow
```bash
# Test complete build flow
/build:slash-command integration test-flow "Test integration flow"

# Expected flow:
1. /build:slash-command loads templates
2. Invokes command-builder agent
3. command-builder loads template
4. Fills placeholders
5. Writes command file
6. Validates output

# Validation
- [ ] Command invokes correct agent
- [ ] Agent loads correct template
- [ ] Template placeholders filled
- [ ] Output matches standards
```

### Integration 2: Skill Builder Infrastructure Analysis
```bash
# Check skill-builder can scan infrastructure
# This tests Step 0 and Step 1

# Expected:
1. skill-builder loads in Step 0:
   - Claude Code skills reference
   - Existing commands
   - Existing agents
   - Subsystem docs
2. skill-builder analyzes in Step 1:
   - Identifies repackaging opportunities
   - Suggests existing commands to convert

# Validation
- [ ] Agent loads all infrastructure files
- [ ] Agent identifies existing components
- [ ] Agent can convert command to skill
- [ ] Agent can expose agent as skill
```

### Integration 3: Plugin Builder Bundling
```bash
# Check plugin-builder can bundle existing work

# Expected:
1. plugin-builder loads in Step 0:
   - All commands
   - All agents
   - All skills
   - Subsystem docs
2. plugin-builder analyzes in Step 1:
   - Groups by subsystem
   - Groups by theme
   - Identifies bundling opportunities

# Validation
- [ ] Agent scans all components
- [ ] Agent groups by subsystem
- [ ] Agent groups by theme
- [ ] Agent copies files correctly
```

---

## 5. Documentation Testing

### README Completeness
- [ ] build-system/README.md explains all 9 commands
- [ ] README explains all 5 agents
- [ ] README has Skills vs Commands section
- [ ] README has integration patterns
- [ ] README has workflow examples
- [ ] README has troubleshooting guide

### Reference Docs Completeness
- [ ] 01-claude-code-slash-commands.md has full content
- [ ] 02-claude-code-skills.md has SKILL.md structure
- [ ] 03-claude-code-plugins.md has plugin structure
- [ ] 04-skills-vs-commands.md has decision matrix

### Architecture Documentation
- [ ] docs/architecture/02-development-guide.md has agent standards
- [ ] docs/architecture/02-development-guide.md has command standards
- [ ] docs/architecture/build-command-context-requirements.md exists
- [ ] All docs reference build-system templates

---

## 6. Standards Compliance Testing

### Slash Command Standards
For each command in `~/.claude/commands/build/`:
- [ ] Has valid YAML frontmatter
- [ ] Under 60 lines (or documented reason if longer)
- [ ] Uses `@` prefix for file references
- [ ] Uses `!` prefix for bash context
- [ ] Invokes subagent with Task()
- [ ] No embedded complex logic

### Agent Standards
For each agent in `~/.claude/agents/*builder*.md`:
- [ ] Has valid YAML frontmatter
- [ ] Has Step 0: Load Required Context
- [ ] Has numbered process steps
- [ ] Has Success Criteria section
- [ ] Has Output Requirements section
- [ ] Has Error Handling section
- [ ] Has Examples section
- [ ] Tools are comma-separated (no spaces)

### Template Standards
For each template in `templates/`:
- [ ] Uses `{{VARIABLE}}` placeholder format
- [ ] Has PURPOSE comment at top
- [ ] Lists all variables in comment
- [ ] Has example or working version

---

## 7. End-to-End Scenarios

### Scenario 1: Build a New Subsystem with Skills
```bash
# Complete workflow test

# 1. Create subsystem
/build:subsystem ml-tools "Machine learning tools"

# 2. Create command
/build:slash-command ml-tools train "Train ML model"

# 3. Create agent
/build:agent ml-trainer "Trains ML models" "Read,Write,Bash"

# 4. Create skill from agent
/build:skill "ML Model Trainer" --from-agent ml-trainer

# Validation
- [ ] Subsystem created with structure
- [ ] Command invokes ml-trainer
- [ ] Agent has Step 0
- [ ] Skill wraps agent capability
- [ ] Claude can discover skill
```

### Scenario 2: Bundle Subsystem into Plugin
```bash
# Complete bundling workflow

# Assuming security subsystem exists
/build:plugin security-toolkit "Security tools" --from-subsystem security

# Validation
- [ ] Plugin created with all security commands
- [ ] Manifest lists all components
- [ ] Plugin is distributable
- [ ] Original commands remain
```

### Scenario 3: Repackage Command as Skill
```bash
# Conversion workflow

# Assuming /backend:test command exists
/build:skill "API Tester" --from-command backend/test

# Validation
- [ ] Agent analyzes backend/test
- [ ] Converts workflow to skill instructions
- [ ] Skill has proper trigger context
- [ ] Original command still works
```

---

## 8. Error Handling Testing

### Test Error: Agent Already Exists
```bash
# Try to create duplicate
/build:agent command-builder "Duplicate" "Read,Write"

# Expected:
⚠️  WARNING: Agent 'command-builder' already exists
Do you want to OVERWRITE? (yes/no):

# Validation
- [ ] Warning displayed
- [ ] Prompts for confirmation
- [ ] Cancels if 'no'
- [ ] Overwrites if 'yes' (backs up first)
```

### Test Error: Invalid Tool Name
```bash
# Try invalid tool
/build:agent test-agent "Test" "Read,InvalidTool,Write"

# Expected:
❌ ERROR: Invalid tool: InvalidTool
Valid tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite

# Validation
- [ ] Error message shown
- [ ] Lists valid tools
- [ ] Exits with error code 1
```

### Test Error: Missing "Use when" in Skill
```bash
# Try skill without trigger
/build:skill "Vague Skill" "Does something useful"

# Expected:
❌ ERROR: Description MUST include 'Use when' trigger context
Example: 'Extract PDFs. Use when working with PDF files.'

# Validation
- [ ] Error caught
- [ ] Example provided
- [ ] Skill creation rejected
```

---

## 9. Performance Testing

### Build Time Testing
- [ ] `/build:slash-command` completes in < 10 seconds
- [ ] `/build:agent` completes in < 15 seconds
- [ ] `/build:skill` with analysis completes in < 20 seconds
- [ ] `/build:plugin --from-subsystem` completes in < 30 seconds

### Context Loading Testing
- [ ] Commands load focused context (not full 959-line guide)
- [ ] Agents load only required templates
- [ ] No context overload warnings
- [ ] Token usage reasonable

---

## 10. Final Checklist

### Pre-Commit Validation
- [ ] All tests above pass
- [ ] No broken file references
- [ ] All documentation updated
- [ ] README.md comprehensive
- [ ] Testing checklist itself is complete
- [ ] Git status clean (all files committed)

### Documentation Updates Needed
- [ ] Main README updated with build system
- [ ] Architecture docs reference build-system
- [ ] Workflow docs include build examples
- [ ] Troubleshooting guide updated

### Known Issues to Document
- [ ] List any failing tests
- [ ] List any incomplete features
- [ ] List any workarounds needed
- [ ] List any future enhancements

---

## Test Results Summary

**Date Tested**: _____________
**Tester**: _____________
**Total Tests**: 100+
**Passed**: _____ / _____
**Failed**: _____ / _____
**Skipped**: _____ / _____

### Critical Failures (Must Fix Before Commit)
1. _____________
2. _____________
3. _____________

### Non-Critical Issues (Can Fix Later)
1. _____________
2. _____________
3. _____________

### Notes
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

---

## Sign-Off

- [ ] All critical tests pass
- [ ] Documentation complete
- [ ] Ready to commit
- [ ] Ready to push
- [ ] Ready for production use

**Signed**: _____________
**Date**: _____________
