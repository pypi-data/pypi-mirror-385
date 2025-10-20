# AI Infrastructure

## Purpose

AI/LLM-specific infrastructure patterns including cost tracking, model orchestration, token management, context window handling, and AI-specific error handling.

## What It Does

1. **Cost & Token Tracking** - Monitor API costs, token usage, and spending across providers (OpenAI, Anthropic, Gemini)
2. **Model Orchestration** - Manage multi-model requests with automatic fallbacks, load balancing, and provider health checks
3. **Context Management** - Handle context window limits, smart truncation, and conversation memory optimization
4. **Prompt Management** - Version control for prompts, A/B testing, and prompt template library
5. **AI Error Handling** - Specialized retry logic, rate limit handling, and graceful degradation patterns

## Agents Used

- **@claude/cost-analyzer** - Analyzes AI costs and token usage patterns across the application
- **@claude/model-orchestrator** - Manages multi-model AI request routing and fallback chains
- **@claude/prompt-manager** - Organizes and versions prompt templates with variable substitution
- **@claude/context-optimizer** - Analyzes and optimizes context window usage for efficient AI calls

## Commands

### `/ai-infrastructure:init` - Initialize AI infrastructure for project
**Usage**: `/ai-infrastructure:init [--project-type]`
**Example**: `/ai-infrastructure:init --project-type=ai-app`

Initializes AI-specific infrastructure including cost tracking database, model configuration files, prompt library structure, and monitoring setup.

**Spawns**: ai-infrastructure-setup agent
**Outputs**:
- `src/ai/cost-tracker.{py|ts}` - Cost tracking module
- `src/ai/model-orchestrator.{py|ts}` - Model routing and fallbacks
- `config/ai-models.yaml` - Model configuration
- `prompts/` - Prompt template directory

---

### `/ai-infrastructure:cost-report` - Generate AI cost usage report
**Usage**: `/ai-infrastructure:cost-report [--timeframe=7d|30d|90d]`
**Example**: `/ai-infrastructure:cost-report --timeframe=30d`

Analyzes token usage logs and generates detailed cost breakdown by model, endpoint, and time period.

**Spawns**: cost-analyzer agent
**Outputs**:
- `.multiagent/reports/ai-cost-report-{date}.md` - Markdown report with charts
- `.multiagent/reports/ai-cost-report-{date}.json` - Raw data export

---

### `/ai-infrastructure:model-health` - Check AI provider health status
**Usage**: `/ai-infrastructure:model-health`
**Example**: `/ai-infrastructure:model-health`

Tests connectivity and response times for all configured AI providers and models.

**Spawns**: model-orchestrator agent
**Outputs**: Health status dashboard displayed in terminal

---

### `/ai-infrastructure:optimize-context` - Analyze and optimize context usage
**Usage**: `/ai-infrastructure:optimize-context [file-or-directory]`
**Example**: `/ai-infrastructure:optimize-context src/ai/`

Scans code for AI API calls and suggests optimizations for context window usage.

**Spawns**: context-optimizer agent
**Outputs**:
- `.multiagent/reports/context-optimization-{date}.md` - Optimization recommendations

---

### `/ai-infrastructure:prompt-library` - Manage prompt templates
**Usage**: `/ai-infrastructure:prompt-library [list|add|test]`
**Example**: `/ai-infrastructure:prompt-library add`

Interactive prompt template management - list existing prompts, add new templates, test with variables.

**Spawns**: prompt-manager agent
**Outputs**: Updates to `prompts/` directory structure

---

## Architecture

```
User runs /ai-infrastructure:{command}
      ↓
Command orchestrates:
1. Run script (gather AI usage data, check configs)
2. Invoke agent (analyze patterns, make recommendations)
3. Generate from templates (cost tracker, model config, prompts)
4. Validate output (test imports, verify syntax)
5. Display summary (costs saved, optimizations found)
```

## How It Works

1. **Command Invocation**: User runs `/ai-infrastructure:{command}` with optional arguments
2. **Script Execution**: Scripts scan logs, check provider APIs, gather token usage metrics
3. **Agent Analysis**: Intelligent agents analyze usage patterns, identify cost savings, recommend optimizations
4. **Template Generation**: Agents generate cost tracking code, model configurations, prompt templates
5. **Output Validation**: System validates generated code compiles and follows best practices
6. **User Feedback**: Display cost summary, health status, optimization recommendations

## Directory Structure

```
.multiagent/ai-infrastructure/
├── README.md              # This file
├── docs/                  # Conceptual documentation
│   ├── cost-management.md
│   ├── model-orchestration.md
│   ├── context-optimization.md
│   └── prompt-versioning.md
├── templates/             # Generation templates
│   ├── cost-tracking/
│   │   ├── cost-tracker.template.py
│   │   ├── cost-tracker.template.ts
│   │   └── cost-db-schema.template.sql
│   ├── model-orchestration/
│   │   ├── model-router.template.py
│   │   ├── model-router.template.ts
│   │   └── fallback-chain.template.yaml
│   ├── context-management/
│   │   ├── context-optimizer.template.py
│   │   └── context-optimizer.template.ts
│   └── prompts/
│       ├── prompt-template.template.md
│       └── prompt-config.template.yaml
├── scripts/               # Mechanical operations only
│   ├── scan-ai-usage.sh
│   ├── test-provider-health.sh
│   └── analyze-token-logs.sh
└── memory/               # Agent state storage
    └── cost-baselines.json
```

## Templates

Templates in this subsystem:

- `templates/cost-tracking/cost-tracker.template.py` - Python cost tracking implementation
- `templates/cost-tracking/cost-tracker.template.ts` - TypeScript cost tracking implementation
- `templates/cost-tracking/cost-db-schema.template.sql` - Database schema for cost data
- `templates/model-orchestration/model-router.template.py` - Python model routing logic
- `templates/model-orchestration/model-router.template.ts` - TypeScript model routing logic
- `templates/model-orchestration/fallback-chain.template.yaml` - Model fallback configuration
- `templates/context-management/context-optimizer.template.py` - Python context optimization
- `templates/context-management/context-optimizer.template.ts` - TypeScript context optimization
- `templates/prompts/prompt-template.template.md` - Prompt template with variables
- `templates/prompts/prompt-config.template.yaml` - Prompt metadata and versioning

## Scripts

Mechanical scripts in this subsystem:

- `scripts/scan-ai-usage.sh` - Scans codebase for AI API calls and token usage
- `scripts/test-provider-health.sh` - Tests API endpoints for all configured providers
- `scripts/analyze-token-logs.sh` - Parses logs to extract token usage statistics

## Outputs

This subsystem generates:

```
src/ai/
├── cost-tracker.{py|ts}        # Cost tracking module
├── model-orchestrator.{py|ts}  # Model routing and fallbacks
├── context-manager.{py|ts}     # Context window optimization
└── __init__.{py|ts}

config/
├── ai-models.yaml              # Model configurations
└── prompt-library.yaml         # Prompt metadata

prompts/
├── system/                     # System prompts
├── user/                       # User-facing prompts
└── templates/                  # Reusable templates

.multiagent/reports/
├── ai-cost-report-*.md         # Cost analysis reports
└── context-optimization-*.md   # Optimization recommendations
```

## Usage Example

```bash
# Step 1: Initialize AI infrastructure for new project
/ai-infrastructure:init --project-type=ai-app

# Step 2: Check that all AI providers are healthy
/ai-infrastructure:model-health

# Step 3: Generate cost report after first week
/ai-infrastructure:cost-report --timeframe=7d

# Step 4: Optimize context usage in main AI module
/ai-infrastructure:optimize-context src/ai/

# Step 5: Add new prompt template
/ai-infrastructure:prompt-library add

# Result: Project has cost tracking, optimized AI calls, and organized prompts
```

## Troubleshooting

### Cost tracking shows $0 despite API usage
**Problem**: Cost tracker not capturing API calls
**Solution**:
```bash
# Check if cost tracker is initialized
cat src/ai/cost-tracker.{py,ts}

# Verify cost tracker is imported in AI modules
grep -r "from.*cost.tracker import" src/

# Run usage scan to find uninstrumented calls
~/.multiagent/ai-infrastructure/scripts/scan-ai-usage.sh
```

### Model fallback not triggering on errors
**Problem**: Primary model fails but fallback chain doesn't activate
**Solution**:
```bash
# Check fallback configuration
cat config/ai-models.yaml

# Test provider health to see which models are down
/ai-infrastructure:model-health

# Review model orchestrator error handling
cat src/ai/model-orchestrator.{py,ts} | grep -A 10 "except"
```

### Context window errors still occurring
**Problem**: Requests exceeding context limits despite optimizer
**Solution**:
```bash
# Run context analysis on problematic module
/ai-infrastructure:optimize-context src/problematic-module.{py,ts}

# Check if context manager is being used
grep -r "context.*manager" src/

# Review context limits in model config
cat config/ai-models.yaml | grep context_window
```

## Related Subsystems

- **observability**: Provides metrics collection and dashboards for AI cost/performance monitoring
- **performance**: Implements caching strategies that reduce redundant AI API calls
- **reliability**: Circuit breakers protect against AI provider outages
- **security**: Manages AI API keys and prevents secret exposure

## Future Enhancements

Planned features for this subsystem:

- [ ] Real-time cost alerts when spending exceeds thresholds
- [ ] Automatic prompt optimization using A/B testing results
- [ ] Multi-tenant cost tracking and billing
- [ ] Smart caching based on semantic similarity
- [ ] Model performance benchmarking and auto-selection
- [ ] Integration with LangSmith/LangFuse for advanced tracing
- [ ] Prompt injection detection and sanitization
- [ ] Token budget allocation per user/feature
- [ ] Cost forecasting and budget planning tools
- [ ] Integration with popular AI frameworks (LangChain, LlamaIndex)
