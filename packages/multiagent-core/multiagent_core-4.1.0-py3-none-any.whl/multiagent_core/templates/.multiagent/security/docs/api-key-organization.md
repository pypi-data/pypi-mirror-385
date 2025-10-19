# API Key Organization Pattern

**Problem:** When API keys are used for both MCP server tool access AND direct API calls in code, billing/usage tracking becomes confused and security management becomes complex.

**Solution:** Separate API keys by usage context with clear naming conventions.

---

## Organization Strategy

### Three-Tier Key Structure

```bash
# ~/.bashrc

# ============================================================================
# TIER 1: MCP SERVER KEYS (Tool Access)
# ============================================================================
# Used by MCP servers for tool calls in Claude Code, VS Code, etc.
# Prefix: MCP_*

export MCP_OPENAI_API_KEY="sk-..."           # OpenAI MCP server
export MCP_ANTHROPIC_API_KEY="sk-ant-..."   # Anthropic MCP server
export MCP_CATS_API_KEY="..."               # CATS ATS MCP server
export MCP_GITHUB_TOKEN="ghp_..."            # GitHub MCP server
export MCP_SUPABASE_URL="https://..."       # Supabase MCP server
export MCP_SUPABASE_KEY="..."               # Supabase MCP server

# ============================================================================
# TIER 2: DIRECT API KEYS (Code & Scripts)
# ============================================================================
# Used for direct API calls in your application code and agent scripts
# No prefix - standard naming

export OPENAI_API_KEY="sk-..."              # Direct OpenAI API calls
export ANTHROPIC_API_KEY="sk-ant-..."       # Direct Anthropic API calls
export GEMINI_API_KEY="..."                 # Direct Gemini API calls
export CODEX_API_KEY="..."                  # Direct Codex API calls
export QWEN_API_KEY="..."                   # Direct Qwen API calls

# ============================================================================
# TIER 3: PLATFORM KEYS (Infrastructure & Services)
# ============================================================================
# Deployment, infrastructure, and third-party service integration

export VERCEL_TOKEN="..."                   # Vercel deployment
export AWS_ACCESS_KEY_ID="..."              # AWS services
export AWS_SECRET_ACCESS_KEY="..."          # AWS services
export RAILWAY_TOKEN="..."                  # Railway deployment
export RENDER_API_KEY="..."                 # Render deployment
export SUPABASE_SERVICE_ROLE_KEY="..."      # Direct Supabase calls
export STRIPE_SECRET_KEY="..."              # Payment processing
export SENDGRID_API_KEY="..."               # Email service
```

---

## Benefits

### 1. Clear Billing Separation
- Track MCP tool usage costs separately from direct API usage
- Understand which context is consuming what resources
- Set different rate limits per context

### 2. Security Isolation
- Rotate MCP keys without affecting production code
- Rotate production keys without reconfiguring MCP servers
- Limit blast radius of key exposure

### 3. Development Flexibility
- Use free tier/testing keys for MCP servers
- Use production keys for application code
- Mix and match key tiers per environment

### 4. Usage Clarity
- Immediately understand key purpose from name
- Easier auditing of API usage patterns
- Clear documentation of key responsibilities

---

## MCP Server Configuration

### ~/.claude/mcp-library.json

Reference MCP-prefixed keys in your server configurations:

```json
{
  "openai": {
    "command": "npx",
    "args": ["-y", "@anthropics/mcp-server-openai"],
    "env": {
      "OPENAI_API_KEY": "${MCP_OPENAI_API_KEY}"
    }
  },
  "github": {
    "command": "npx",
    "args": ["-y", "@anthropics/mcp-server-github"],
    "env": {
      "GITHUB_TOKEN": "${MCP_GITHUB_TOKEN}"
    }
  },
  "cats-ats": {
    "command": "node",
    "args": ["/path/to/cats-mcp-server/index.js"],
    "env": {
      "CATS_API_KEY": "${MCP_CATS_API_KEY}"
    }
  },
  "supabase": {
    "command": "npx",
    "args": ["-y", "@supabase/mcp-server"],
    "env": {
      "SUPABASE_URL": "${MCP_SUPABASE_URL}",
      "SUPABASE_ANON_KEY": "${MCP_SUPABASE_KEY}"
    }
  }
}
```

---

## Code Usage Patterns

### Python Example

```python
# Direct API usage in application code
import os
from openai import OpenAI
from anthropic import Anthropic

# Uses OPENAI_API_KEY (no MCP_ prefix)
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Uses ANTHROPIC_API_KEY (no MCP_ prefix)
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# MCP servers automatically use MCP_OPENAI_API_KEY for their tools
# No code changes needed - separation is environment-level
```

### TypeScript/Node.js Example

```typescript
// Direct API usage in application code
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';

// Uses OPENAI_API_KEY (no MCP_ prefix)
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Uses ANTHROPIC_API_KEY (no MCP_ prefix)
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// MCP servers automatically use MCP_OPENAI_API_KEY for their tools
```

### Environment File Pattern

```bash
# .env (for application code)
OPENAI_API_KEY=sk-direct-usage-key
ANTHROPIC_API_KEY=sk-ant-direct-usage-key
STRIPE_SECRET_KEY=sk_live_...

# ~/.bashrc (for MCP servers)
export MCP_OPENAI_API_KEY="sk-mcp-tool-key"
export MCP_ANTHROPIC_API_KEY="sk-ant-mcp-tool-key"
```

---

## Key Rotation Strategy

### When to Rotate MCP Keys
- After MCP server compromise or exposure
- Periodic security audits (quarterly recommended)
- When changing MCP server configurations
- After removing team member access

### When to Rotate Direct API Keys
- After code repository exposure
- Production security incident
- Periodic rotation (monthly for sensitive apps)
- After removing developer access

### When to Rotate Platform Keys
- After infrastructure compromise
- Major deployment changes
- Team member offboarding
- Compliance requirements (90-day rotation common)

### Rotation Process

```bash
# 1. Generate new key from provider
# 2. Update ~/.bashrc
nano ~/.bashrc  # Update the relevant MCP_* or regular key

# 3. Reload environment
source ~/.bashrc

# 4. Test the new key
# For MCP: Restart Claude Code and test MCP tool
# For Direct: Run application tests
# For Platform: Test deployment pipeline

# 5. Revoke old key from provider dashboard
# 6. Document the rotation in your security log
```

---

## Security Best Practices

### 1. Never Commit Keys
```bash
# .gitignore (MANDATORY)
.env
.env.*
!.env.example
*.key
*.pem
config/secrets.yml
```

### 2. Use Different Keys Per Environment
```bash
# Development
export MCP_OPENAI_API_KEY="sk-dev-..."
export OPENAI_API_KEY="sk-dev-..."

# Staging
export MCP_OPENAI_API_KEY="sk-staging-..."
export OPENAI_API_KEY="sk-staging-..."

# Production
export MCP_OPENAI_API_KEY="sk-prod-..."
export OPENAI_API_KEY="sk-prod-..."
```

### 3. Monitor Usage Per Key
- Set up billing alerts per key
- Review usage dashboards weekly
- Investigate anomalous spikes
- Track costs by context (MCP vs Direct vs Platform)

### 4. Principle of Least Privilege
- MCP keys: Read-only or minimal permissions where possible
- Direct API keys: Scoped to necessary operations only
- Platform keys: Environment-specific permissions

### 5. Key Validation
```python
# Validate keys are properly separated
import os

def validate_key_separation():
    """Ensure MCP and Direct keys are different"""
    mcp_key = os.getenv('MCP_OPENAI_API_KEY')
    direct_key = os.getenv('OPENAI_API_KEY')

    if mcp_key == direct_key:
        raise ValueError("MCP and Direct keys should be different!")

    if not mcp_key or not direct_key:
        raise ValueError("Missing required API keys!")

    print("✅ Key separation validated")

validate_key_separation()
```

---

## Migration from Single Key Setup

### Before (Single Key)
```bash
# ~/.bashrc
export OPENAI_API_KEY="sk-..."  # Used for EVERYTHING
```

### After (Separated Keys)
```bash
# ~/.bashrc
export MCP_OPENAI_API_KEY="sk-mcp-..."     # MCP tools only
export OPENAI_API_KEY="sk-direct-..."      # Application code only
```

### Migration Steps

1. **Generate New MCP Key**
   - Go to provider dashboard
   - Create new API key labeled "MCP Tools"
   - Copy key to clipboard

2. **Update ~/.bashrc**
   ```bash
   nano ~/.bashrc
   # Add: export MCP_OPENAI_API_KEY="sk-mcp-..."
   source ~/.bashrc
   ```

3. **Update MCP Configuration**
   ```bash
   nano ~/.claude/mcp-library.json
   # Change OPENAI_API_KEY to ${MCP_OPENAI_API_KEY}
   ```

4. **Restart MCP Servers**
   ```bash
   # Kill existing MCP processes
   pkill -f "mcp-server"

   # Restart Claude Code (will reload MCP servers)
   ```

5. **Test Both Contexts**
   ```bash
   # Test MCP tools in Claude Code
   # Test direct API calls in your application
   ```

6. **Update Documentation**
   - Document which key is which
   - Update team wiki/docs
   - Add to onboarding materials

---

## Troubleshooting

### MCP Server Can't Authenticate
```bash
# Check if MCP key is set
echo $MCP_OPENAI_API_KEY

# If empty, reload bashrc
source ~/.bashrc

# Verify in mcp-library.json
cat ~/.claude/mcp-library.json | grep OPENAI

# Restart MCP servers
pkill -f "mcp-server" && claude
```

### Application Can't Authenticate
```bash
# Check if direct API key is set
echo $OPENAI_API_KEY

# Check .env file (for local development)
cat .env | grep OPENAI_API_KEY

# Verify key in application logs
# Look for authentication errors
```

### Keys Getting Mixed Up
```bash
# Validate separation
env | grep -E "(MCP_|OPENAI_API_KEY|ANTHROPIC)"

# Should see:
# MCP_OPENAI_API_KEY=sk-mcp-...
# OPENAI_API_KEY=sk-direct-...
```

---

## Related Documentation

- **Security Model:** `~/.claude/docs/patterns/security/model.md`
- **Security Setup:** `~/.claude/docs/patterns/security/setup.md`
- **MCP Guide:** `~/.claude/docs/mcp/complete-guide.md`
- **Environment Variables:** Never hardcode - always use env vars

---

## Summary

**Pattern:** `MCP_*` prefix for MCP servers, standard names for direct API usage, descriptive names for platform services.

**Benefit:** Clear separation of concerns, better billing tracking, improved security, easier rotation.

**Implementation:** Update `~/.bashrc` with three-tier structure, update `mcp-library.json` to reference MCP keys, use standard keys in application code.
