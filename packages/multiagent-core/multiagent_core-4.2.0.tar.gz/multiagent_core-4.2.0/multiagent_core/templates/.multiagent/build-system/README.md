# Build System - Component Builder for multiagent-core

## Purpose

The build-system subsystem provides **standardized templates, reference documentation, and build commands** for creating all framework components: slash commands, agents, Agent Skills, plugins, and hooks. It ensures consistency and compliance with both framework standards and Claude Code specifications.

## What It Does

1. **Template Library** - Pre-built templates for all component types with `{{VARIABLE}}` placeholders
2. **Reference Documentation** - Official Claude Code docs for accurate builds
3. **Build Commands** - Slash commands to generate components from templates
4. **Validation Scripts** - Automated compliance checking
5. **Integration Bridge** - Connects multiagent-core with Claude Code features (Skills, Plugins)

---

## Architecture Overview

### The Complete Ecosystem

```
multiagent-core Framework
├── Slash Commands (user-invoked)
│   └── Created by: /build:slash-command
│
├── Agents (intelligent analysis)
│   └── Created by: /build:agent
│
├── Claude Code Skills (model-invoked) ⭐ NEW
│   └── Created by: /build:skill
│
├── Claude Code Plugins (distributable bundles) ⭐ NEW
│   └── Created by: /build:plugin
│
└── Hooks (event-triggered)
    └── Created by: /build:hook (to be implemented)
```

### Integration with Claude Code

**multiagent-core** is a framework for building multiagent systems.
**Claude Code** is Anthropic's CLI with support for Skills and Plugins.

**The build-system bridges these worlds:**

- **Framework → Claude Code**: Use `/build:skill` to create Skills that Claude discovers automatically
- **Claude Code → Framework**: Skills can invoke framework commands and agents
- **Distribution**: Use `/build:plugin` to bundle commands+skills+hooks for sharing

---

## Commands

### Core Build Commands

#### `/build:slash-command` - Create Slash Command

**Location**: `~/.claude/commands/build/slash-command.md`

**Usage**:
```bash
/build:slash-command <subsystem> <command-name> "description"
```

**Example**:
```bash
/build:slash-command security scan-secrets "Scan codebase for exposed secrets"
```

**What it does**:
1. Loads **focused context**: `@docs/architecture/02-development-guide.md#slash-command-standards`
2. Loads **Claude Code reference**: `@multiagent_core/templates/.multiagent/build-system/docs/01-claude-code-slash-commands.md`
3. Loads **command template**: `@multiagent_core/templates/.multiagent/build-system/templates/commands/command.md.template`
4. Generates command file with proper frontmatter, @ and ! patterns
5. Validates structure (< 60 lines, no embedded logic)
6. Outputs to: `~/.claude/commands/{subsystem}/{command-name}.md`
7. Registers in `~/.claude/settings.json`

**Creates**: User-invoked orchestrator commands

---

#### `/build:agent` - Create Agent Definition

**Location**: `~/.claude/commands/build/agent.md`

**Usage**:
```bash
/build:agent <agent-name> "description" "tools"
```

**Example**:
```bash
/build:agent secret-scanner "Analyzes code for exposed secrets" "Read,Grep,Write"
```

**What it does**:
1. Loads **focused context**: `@docs/architecture/02-development-guide.md#agent-standards`
2. Loads **agent template**: `@multiagent_core/templates/.multiagent/build-system/templates/agents/agent.md.template`
3. Loads **agent example**: `@multiagent_core/templates/.multiagent/build-system/templates/agents/agent-example.md`
4. Generates agent file with **Step 0 context loading** (CRITICAL)
5. Validates frontmatter, success criteria, output requirements
6. Outputs to: `~/.claude/agents/{agent-name}.md`

**Creates**: Intelligent subagents invoked by commands

---

#### `/build:skill` - Create Agent Skill ⭐ NEW

**Location**: `~/.claude/commands/build/skill.md`

**Usage**:
```bash
/build:skill "Skill Name" "Description with Use when trigger" [--scope=personal|project|plugin]
```

**Example**:
```bash
/build:skill "PDF Processor" "Extract text from PDF files. Use when working with PDF documents." --scope=project
```

**What it does**:
1. Loads **Claude Code Skills reference**: `@multiagent_core/templates/.multiagent/build-system/docs/02-claude-code-skills.md`
2. Loads **decision guide**: `@multiagent_core/templates/.multiagent/build-system/docs/04-skills-vs-commands.md`
3. Loads **skill template**: `@multiagent_core/templates/.multiagent/build-system/templates/skills/SKILL.md.template`
4. Creates skill directory with SKILL.md
5. Validates description includes "Use when" trigger context
6. Outputs to:
   - `~/.claude/skills/{skill-slug}/SKILL.md` (personal)
   - `.claude/skills/{skill-slug}/SKILL.md` (project)
   - `.claude/plugins/{plugin}/skills/{skill-slug}/SKILL.md` (plugin)

**Creates**: Model-invoked capabilities that Claude discovers automatically

**Critical Difference from Commands**:
- **Skills**: Claude discovers and uses automatically based on context
- **Commands**: User explicitly invokes with `/command-name`

---

#### `/build:plugin` - Create Plugin ⭐ NEW

**Location**: `~/.claude/commands/build/plugin.md`

**Usage**:
```bash
/build:plugin <plugin-name> "description" [--components=commands,skills,hooks,mcps]
```

**Example**:
```bash
/build:plugin security-tools "Security scanning and detection" --components=commands,skills
```

**What it does**:
1. Loads **Claude Code Plugins reference**: `@multiagent_core/templates/.multiagent/build-system/docs/03-claude-code-plugins.md`
2. Loads **plugin template**: `@multiagent_core/templates/.multiagent/build-system/templates/plugins/plugin.json.template`
3. Creates `.claude-plugin/plugin.json` manifest
4. Creates component directories at plugin root
5. Validates structure (components at root, not in .claude-plugin/)
6. Outputs to: `.claude/plugins/{plugin-name}/`

**Creates**: Distributable bundles of commands, skills, hooks, and MCP servers

**Plugin Structure**:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED: manifest at root
├── commands/                 # Optional: slash commands
│   └── deploy.md
├── skills/                   # Optional: Agent Skills
│   └── code-reviewer/
│       └── SKILL.md
├── hooks/                    # Optional: event hooks
│   └── pre-commit.md
└── mcps/                     # Optional: MCP servers
    └── github-integration/
```

---

#### `/build:subsystem` - Create Subsystem Structure

**Location**: `~/.claude/commands/build/subsystem.md`

**Usage**:
```bash
/build:subsystem <subsystem-name> "purpose statement"
```

**Example**:
```bash
/build:subsystem ai-infrastructure "AI/LLM infrastructure patterns and tooling"
```

**What it does**:
1. Loads focused context on subsystem and dependency standards
2. Creates directory structure: `docs/`, `templates/`, `scripts/`, `memory/`
3. Generates comprehensive README following template
4. Validates structure against framework standards
5. Outputs to: `multiagent_core/templates/.multiagent/{subsystem-name}/`

**Creates**: Foundation structure for new subsystems

---

#### `/build:subsystem-full` - Complete Subsystem Build

**Location**: `~/.claude/commands/build/subsystem-full.md`

**Usage**:
```bash
/build:subsystem-full <subsystem> "<purpose>" \
  --commands="cmd1,cmd2" \
  --agents="agent1,agent2" \
  --scripts="script1,script2"
```

**What it does**:
Orchestrates 7 sequential phases:
1. **Structure** - Create directory tree
2. **Commands** - Create all slash commands (ONE AT A TIME)
3. **Agents** - Create all agents (ONE AT A TIME)
4. **Scripts** - Create bash scripts
5. **Templates** - Create generation templates
6. **Documentation** - Generate comprehensive README
7. **Architecture** - Update framework docs

**Creates**: Complete, production-ready subsystem

⚠️ **CRITICAL**: Runs sequentially to avoid API tool pairing errors

---

### Analysis & Maintenance Commands

#### `/build:analyze` - Subsystem Analysis

Analyzes existing or planned subsystems for compliance and integration.

**Modes**:
- `--existing`: Analyze current implementation
- `--new`: Plan architecture for new build
- `--all`: Analyze entire framework

---

#### `/build:enhance` - Targeted Enhancement

Lightweight improvements without full rebuild.

**Use when**: Adding small feature or fixing specific issue

---

#### `/build:remove` - Safe Component Removal

Removes subsystems/commands/agents with dependency checking.

**Agent**: `build-dependency-analyzer`
**Output**: Removal impact report with blast radius

---

## Agents

### Existing Agents

#### `build-dependency-analyzer`

**Location**: `~/.claude/agents/build-dependency-analyzer.md`

**Purpose**: Analyzes dependencies and impact when removing components

**Invoked by**: `/build:remove`

**Tools**: Read, Grep, Glob, Bash, Write

**What it does**:
1. Discovers all files and references to target component
2. Maps dependencies (direct, indirect, reverse)
3. Calculates blast radius (% of framework affected)
4. Assesses risk level (SAFE, CAUTION, DANGEROUS, CRITICAL)
5. Generates removal impact report with recovery plan

**Output**: `docs/reports/build-analysis/{date}/removal-impact-{component}.md`

---

### Missing Agents (Need to Create)

These agents are referenced by build commands but don't exist yet. They need to be created using `/build:agent`:

#### `command-builder` ❌ NOT CREATED

**Should be invoked by**: `/build:slash-command`

**Recommended creation**:
```bash
/build:agent command-builder \
  "Generates slash commands from templates following framework standards" \
  "Read,Write,Edit,Bash"
```

**What it should do**:
- Read command.md.template
- Fill {{PLACEHOLDERS}} with provided values
- Ensure < 60 lines
- Add @ and ! patterns
- Register in settings.json

---

#### `agent-builder` ❌ NOT CREATED

**Should be invoked by**: `/build:agent`

**Recommended creation**:
```bash
/build:agent agent-builder \
  "Generates agents from templates with Step 0 context loading" \
  "Read,Write,Edit,Bash"
```

**What it should do**:
- Read agent.md.template
- Fill {{PLACEHOLDERS}} with provided values
- Ensure Step 0 section exists
- Add success criteria
- Validate tools list

---

#### `skill-builder` ❌ NOT CREATED

**Should be invoked by**: `/build:skill`

**Recommended creation**:
```bash
/build:agent skill-builder \
  "Generates Claude Code Agent Skills with trigger context" \
  "Read,Write,Bash"
```

**What it should do**:
- Read SKILL.md.template
- Ensure "Use when" trigger context in description
- Create skill directory structure
- Add supporting files if needed
- Validate with validate-skill.sh

---

#### `plugin-builder` ❌ NOT CREATED

**Should be invoked by**: `/build:plugin`

**Recommended creation**:
```bash
/build:agent plugin-builder \
  "Generates Claude Code plugin bundles with manifest" \
  "Read,Write,Bash"
```

**What it should do**:
- Read plugin.json.template
- Create .claude-plugin/ directory
- Set up component directories at root
- Generate README.md
- Validate with validate-plugin.sh

---

#### `hook-builder` ❌ NOT CREATED

**Should be invoked by**: `/build:hook` (command not created yet)

**What it should do**:
- Create hook configuration
- Add to hooks.json
- Validate event types

---

## Templates

### Directory Structure

```
multiagent_core/templates/.multiagent/build-system/
├── templates/
│   ├── agents/
│   │   ├── agent.md.template       # Agent template with {{VARIABLES}}
│   │   └── agent-example.md        # Working agent example
│   ├── commands/
│   │   ├── command.md.template     # Slash command template
│   │   └── command-example.md      # Working command example
│   ├── skills/
│   │   ├── SKILL.md.template       # Agent Skill template
│   │   ├── skill-example/
│   │   │   └── SKILL.md            # Working skill example
│   │   └── README.md
│   └── plugins/
│       ├── plugin.json.template    # Plugin manifest template
│       ├── example-plugin/         # Complete working plugin
│       │   ├── .claude-plugin/
│       │   │   └── plugin.json
│       │   ├── commands/
│       │   │   └── greet.md
│       │   └── skills/
│       │       └── hello-skill/
│       │           └── SKILL.md
│       └── README.md
```

### Template Variable Format

All templates use `{{VARIABLE_NAME}}` format:

```markdown
---
name: {{AGENT_NAME}}
description: {{DESCRIPTION}}
tools: {{TOOLS}}
---

You are a {{ROLE}} that {{ACTION}}.

### Step 0: Load Required Context

Read("{{CONTEXT_FILE_1}}")  # {{CONTEXT_PURPOSE_1}}
```

---

## Reference Documentation

### What's in docs/?

```
docs/
├── 01-claude-code-slash-commands.md    # Official Claude Code command reference
├── 02-claude-code-skills.md            # Official Agent Skills reference
├── 03-claude-code-plugins.md           # Official plugins reference
└── 04-skills-vs-commands.md            # Decision guide
```

### When to Load Each Doc

**Build commands use focused loading:**

- `/build:slash-command` loads:
  - `@docs/architecture/02-development-guide.md#slash-command-standards`
  - `@multiagent_core/templates/.multiagent/build-system/docs/01-claude-code-slash-commands.md`

- `/build:agent` loads:
  - `@docs/architecture/02-development-guide.md#agent-standards`
  - Template and example files

- `/build:skill` loads:
  - `@multiagent_core/templates/.multiagent/build-system/docs/02-claude-code-skills.md`
  - `@multiagent_core/templates/.multiagent/build-system/docs/04-skills-vs-commands.md`

- `/build:plugin` loads:
  - `@multiagent_core/templates/.multiagent/build-system/docs/03-claude-code-plugins.md`

**Why focused loading?**
Loading only relevant sections (30-100 lines) instead of full docs (959 lines) prevents context overload and ensures agents follow correct standards.

---

## Validation Scripts

### Purpose

Automated checking to ensure generated components follow standards.

### Available Scripts

```bash
# Validate agent file
multiagent_core/templates/.multiagent/build-system/scripts/validate-agent.sh \
  ~/.claude/agents/my-agent.md

# Validate command file
multiagent_core/templates/.multiagent/build-system/scripts/validate-command.sh \
  ~/.claude/commands/subsystem/command.md

# Validate skill directory
multiagent_core/templates/.multiagent/build-system/scripts/validate-skill.sh \
  .claude/skills/my-skill/

# Validate plugin directory
multiagent_core/templates/.multiagent/build-system/scripts/validate-plugin.sh \
  .claude/plugins/my-plugin/
```

### What They Check

**validate-agent.sh**:
- ✅ Frontmatter completeness (name, description, tools, model)
- ✅ Step 0 context loading exists
- ✅ Success criteria section exists
- ✅ Read() calls present for context loading

**validate-command.sh**:
- ✅ Frontmatter completeness (allowed-tools, description)
- ✅ File length under 60 lines
- ✅ Agent invocation present ("Invoke the")

**validate-skill.sh**:
- ✅ SKILL.md exists
- ✅ Frontmatter present (name, description)
- ✅ Description includes "Use when" trigger keywords

**validate-plugin.sh**:
- ✅ .claude-plugin/plugin.json exists
- ✅ Valid JSON syntax
- ✅ Required fields (name)
- ✅ Component directories at root (not inside .claude-plugin/)

---

## How It All Works Together

### Workflow 1: Build a New Subsystem with Skills

```bash
# Step 1: Create subsystem structure
/build:subsystem ml-tools "Machine learning helper tools"

# Step 2: Create a slash command (user-invoked)
/build:slash-command ml-tools train-model "Train ML model from dataset"

# Step 3: Create an agent (intelligent analysis)
/build:agent ml-model-trainer "Analyzes dataset and trains model" "Read,Write,Bash"

# Step 4: Create a skill (model-invoked)
/build:skill "Dataset Analyzer" \
  "Analyze ML datasets for quality and feature engineering. Use when working with CSV or pandas DataFrames." \
  --scope=project

# Step 5: Test the integration
# - User runs: /ml-tools:train-model my-dataset.csv
# - Command invokes: ml-model-trainer agent
# - Claude automatically uses: Dataset Analyzer skill (discovers it)
# - Output: Trained model
```

### Workflow 2: Create a Distributable Plugin

```bash
# Step 1: Create plugin structure
/build:plugin devops-toolkit "DevOps automation tools" --components=commands,skills

# Step 2: Create commands for the plugin
/build:slash-command devops-toolkit deploy "Deploy application to cloud"
# Then move: ~/.claude/commands/devops-toolkit/deploy.md
#       to: .claude/plugins/devops-toolkit/commands/deploy.md

# Step 3: Create skills for the plugin
/build:skill "Dockerfile Generator" \
  "Generate optimized Dockerfiles. Use when creating container configurations." \
  --scope=plugin

# Step 4: Update plugin.json
# Add commands and skills to manifest

# Step 5: Distribute
# Push to Git repo, share with team
# Others install with: /plugins:install {repo-url}
```

### Workflow 3: Framework Development

```bash
# Analyze existing subsystem
/build:analyze backend --existing

# Fix issues found in analysis
/build:enhance backend "Add validation to API endpoints"

# Check removal impact before deleting
/build:remove subsystem example-old

# Review impact report, then force remove if safe
/build:remove subsystem example-old --force
```

---

## Claude Code Integration

### Skills vs Commands

**Use Skill when:**
- Claude should discover it automatically
- Context-dependent activation
- Complex capability with supporting files
- Progressive disclosure needed
- **Example**: Code review, PDF processing, data analysis

**Use Command when:**
- User explicitly triggers it
- Appears in /help menu
- Simple orchestration workflow
- User decides when to run
- **Example**: Deploy app, run tests, generate report

### Decision Matrix

| Scenario | Use |
|----------|-----|
| User types `/deploy` | **Command** |
| Claude sees PDF file and offers to extract text | **Skill** |
| User wants to scan for secrets on demand | **Command** |
| Claude automatically detects code quality issues | **Skill** |
| Orchestrate 5-step deployment workflow | **Command** |
| Parse configuration files intelligently | **Skill** |

### How Skills Work with Agents

**Skills can invoke agents:**

```markdown
# In SKILL.md

## Instructions

1. Analyze the PDF structure
2. Invoke the pdf-extractor agent to extract text
3. Format the output as markdown
```

**Agents can't invoke skills directly** (skills are model-invoked)

### Plugin Distribution

**Plugins bundle everything:**
- Commands (user-invoked)
- Skills (model-invoked)
- Hooks (event-triggered)
- MCP servers (external tools)

**Install a plugin:**
```bash
/plugins:install github.com/username/security-toolkit
```

**Result**: All commands, skills, hooks available in your project

---

## Integration with multiagent-core Framework

### Framework Layers

```
Layer 1: COMMANDS (orchestration)
         └─ Created by /build:slash-command
         └─ Examples: /deploy:prepare, /testing:test

Layer 2: AGENTS (intelligent analysis)
         └─ Created by /build:agent
         └─ Examples: deployment-validator, test-generator

Layer 3: SKILLS (model-invoked capabilities) ⭐ NEW
         └─ Created by /build:skill
         └─ Examples: "Code Reviewer", "Docker Generator"

Layer 4: SCRIPTS (mechanical operations)
         └─ Created manually
         └─ Examples: list-files.sh, validate.sh

Layer 5: TEMPLATES (structure)
         └─ Created by build-system templates
         └─ Examples: deployment.yml.template
```

### How Layers Interact

```
User: /deploy:prepare production

1. COMMAND (deploy:prepare) executes
2. Loads context with @ references
3. Runs mechanical SCRIPT (check-env.sh)
4. Invokes AGENT (deployment-prep)
5. AGENT loads context from templates
6. AGENT may trigger SKILLS automatically
7. AGENT generates from TEMPLATES
8. Output validated and displayed
```

### Skills Enhance Framework

**Before Skills:**
- Agent needs explicit instructions for every context
- Can't adapt to new file types automatically
- Limited to what command tells it

**With Skills:**
- Claude discovers relevant capabilities
- Adapts to context (PDF → PDF skill, Docker → Docker skill)
- Progressive disclosure (loads supporting files when needed)

---

## Best Practices

### For Commands
- ✅ Keep under 60 lines
- ✅ Load focused context with section anchors
- ✅ Use @ prefix for file references
- ✅ Use ! prefix for bash context
- ✅ Invoke subagents for intelligence
- ❌ Don't embed complex logic

### For Agents
- ✅ Always include Step 0 context loading
- ✅ Use @ symbol for file references
- ✅ Define clear success criteria
- ✅ Specify exact output requirements
- ❌ Don't skip context loading

### For Skills
- ✅ Include "Use when" trigger keywords
- ✅ Make descriptions context-specific
- ✅ Provide concrete examples
- ✅ Use progressive disclosure
- ❌ Don't make descriptions vague

### For Plugins
- ✅ Use semantic versioning
- ✅ Use ${CLAUDE_PLUGIN_ROOT} for paths
- ✅ Complete manifest metadata
- ✅ Validate structure with script
- ❌ Don't hardcode absolute paths

---

## Current Status

### ✅ Complete

- [x] Build command templates
- [x] Reference documentation (Claude Code)
- [x] Validation scripts
- [x] Command: `/build:slash-command`
- [x] Command: `/build:agent`
- [x] Command: `/build:skill` ⭐ NEW
- [x] Command: `/build:plugin` ⭐ NEW
- [x] Command: `/build:subsystem`
- [x] Command: `/build:subsystem-full`
- [x] Command: `/build:analyze`
- [x] Command: `/build:enhance`
- [x] Command: `/build:remove`
- [x] Agent: `build-dependency-analyzer`

### ❌ To Do

- [ ] Agent: `command-builder`
- [ ] Agent: `agent-builder`
- [ ] Agent: `skill-builder` ⭐
- [ ] Agent: `plugin-builder` ⭐
- [ ] Agent: `hook-builder`
- [ ] Command: `/build:hook`
- [ ] Update `/build:subsystem` to reference templates
- [ ] Update `/build:subsystem-full` to use focused context
- [ ] Fix `/build:remove` script paths

---

## Next Steps

### 1. Create Missing Builder Agents

```bash
# Create command-builder
/build:agent command-builder \
  "Generates slash commands from templates" \
  "Read,Write,Edit,Bash"

# Create agent-builder
/build:agent agent-builder \
  "Generates agents with Step 0 context loading" \
  "Read,Write,Edit,Bash"

# Create skill-builder
/build:agent skill-builder \
  "Generates Claude Code Skills with trigger context" \
  "Read,Write,Bash"

# Create plugin-builder
/build:agent plugin-builder \
  "Generates Claude Code plugin bundles" \
  "Read,Write,Bash"
```

### 2. Update Existing Commands

- Update `/build:subsystem` to reference build-system templates
- Update `/build:subsystem-full` to use focused context loading
- Fix `/build:remove` to use correct script paths

### 3. Test Integration

- Build a sample skill and verify Claude discovers it
- Build a sample plugin and test distribution
- Validate all builder agents work correctly

---

## Troubleshooting

### Skill Not Discovered by Claude

**Problem**: Created skill but Claude doesn't use it

**Solutions**:
1. Check description includes "Use when" trigger keywords
2. Verify SKILL.md is in correct location
3. Make trigger context more specific
4. Test with exact scenario matching trigger

### Plugin Components Not Loading

**Problem**: Installed plugin but commands/skills missing

**Solutions**:
1. Verify `.claude-plugin/plugin.json` exists
2. Check components are at plugin root (not inside .claude-plugin/)
3. Run validation script
4. Restart Claude Code

### Builder Agent Not Found

**Problem**: Build command says agent doesn't exist

**Solutions**:
1. Check if agent was created (see "To Do" list above)
2. Create the missing agent using `/build:agent`
3. Update command to reference correct agent name

### Template Variables Not Replaced

**Problem**: Output contains {{VARIABLE_NAME}}

**Solutions**:
1. Verify builder agent loads correct template
2. Check agent fills all required variables
3. Review template for missing placeholders

---

## Related Documentation

- [Framework Development Guide](../../docs/architecture/02-development-guide.md)
- [Slash Command Standards](../../docs/architecture/02-development-guide.md#slash-command-standards)
- [Agent Standards](../../docs/architecture/02-development-guide.md#agent-standards)
- [Build Command Context Requirements](../../docs/architecture/build-command-context-requirements.md)
- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [Claude Code Plugins Documentation](https://docs.claude.com/en/docs/claude-code/plugins)

---

🏗️ **Build System** - Standardized component creation for multiagent-core + Claude Code integration
