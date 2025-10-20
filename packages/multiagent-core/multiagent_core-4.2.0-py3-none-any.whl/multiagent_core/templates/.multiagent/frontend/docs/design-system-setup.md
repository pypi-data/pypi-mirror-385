# Design System Setup During Project Initialization

## Problem

When starting a new frontend/fullstack project, agents need a filled DESIGN_SYSTEM.md to ensure UI consistency. Currently, the template exists but needs to be filled with project-specific values.

## Solution

Add design system initialization to `/core:project-setup` for frontend/fullstack projects.

### Project Type Detection

During setup, detect project type by analyzing:
- `package.json` - Check for React, Next.js, Vue, Angular, Svelte
- `spec.md` - Look for UI/frontend requirements
- User input - Ask "Is this frontend/backend/fullstack?"

### Design System Creation Flow

```bash
/core:project-setup
  ↓
  Detect project type
  ↓
  IF frontend OR fullstack:
    ↓
    Fill DESIGN_SYSTEM.md
    ↓
    (Options):
    A) Interactive prompts for design decisions
    B) AI-assisted: Agent reads spec → fills design system
    C) Use defaults → user customizes later
```

### Required Design Decisions

The DESIGN_SYSTEM.md template has placeholders that need values:

**Brand & Identity**:
- {{PROJECT_NAME}}
- {{BRAND_VOICE}} (Professional/Friendly/Technical)
- {{BRAND_TONE}} (Formal/Casual/Conversational)

**Colors**:
- {{PRIMARY_COLOR}} (e.g., #3B82F6)
- {{SECONDARY_COLOR}}
- {{SUCCESS_COLOR}}, {{WARNING_COLOR}}, {{ERROR_COLOR}}
- {{TEXT_PRIMARY}}, {{BACKGROUND_COLOR}}

**Typography**:
- {{PRIMARY_FONT}} (e.g., Inter, -apple-system)
- {{HEADING_FONT}}
- {{MONOSPACE_FONT}} (e.g., 'Fira Code', 'JetBrains Mono')
- Font sizes, weights, line heights

**Spacing**:
- {{SPACING_BASE_UNIT}} (e.g., 4px, 8px)
- {{SPACING_SM}}, {{SPACING_MD}}, {{SPACING_LG}}

**Breakpoints**:
- {{MOBILE_BREAKPOINT}} (e.g., 320px)
- {{TABLET_BREAKPOINT}} (e.g., 768px)
- {{DESKTOP_BREAKPOINT}} (e.g., 1024px)

**Accessibility**:
- {{WCAG_LEVEL}} (A/AA/AAA)
- Contrast ratios
- Touch target sizes

## Implementation Options

### Option A: Interactive Prompts (Quick Start)

```bash
# During /core:project-setup
echo "🎨 Frontend project detected - Design System Setup"
echo ""
echo "Quick design decisions:"
read -p "Primary color (hex): " PRIMARY_COLOR
read -p "Font family (default: Inter): " PRIMARY_FONT
read -p "Base spacing unit (default: 8px): " SPACING_BASE
read -p "WCAG level (AA recommended): " WCAG_LEVEL

# Fill template with values
sed -i "s/{{PRIMARY_COLOR}}/$PRIMARY_COLOR/g" .multiagent/frontend/templates/DESIGN_SYSTEM.md
# ... more replacements
```

### Option B: AI-Assisted (Smart)

```bash
# Call frontend agent to analyze spec and create design system
/frontend:develop --init-design-system

# Agent reads:
# - spec.md for brand personality, target audience
# - industry standards for project type (e.g., fintech = professional, startup = modern)
# - accessibility requirements from spec

# Agent fills DESIGN_SYSTEM.md with intelligent defaults
```

### Option C: Sensible Defaults (Fastest)

```bash
# Use battle-tested defaults, let user customize later
cp .multiagent/frontend/templates/DESIGN_SYSTEM.defaults.md \
   .multiagent/frontend/templates/DESIGN_SYSTEM.md

# Defaults could be:
# - Tailwind default colors
# - System font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', ...)
# - 8px spacing base
# - WCAG AA compliance
# - Standard breakpoints (768px, 1024px, 1280px)
```

## Recommended Approach

**For /core:project-setup**:

1. **Detect project type** (check package.json, ask user)

2. **If frontend/fullstack**:
   ```bash
   # Use sensible defaults + spec analysis
   # - Copy default design system
   # - Call frontend agent to customize based on spec
   # - Agent fills brand-specific values from spec.md
   ```

3. **Verify before proceeding**:
   ```bash
   echo "✅ Design system created: .multiagent/frontend/templates/DESIGN_SYSTEM.md"
   echo "   Review and customize before running /frontend:develop"
   ```

## Why This Matters

**Without filled DESIGN_SYSTEM.md**:
- ❌ Each agent makes different UI decisions
- ❌ Inconsistent colors, spacing, typography
- ❌ Accessibility overlooked
- ❌ Rework needed to unify styles later

**With filled DESIGN_SYSTEM.md from start**:
- ✅ All agents (@claude, @copilot, @codex, @qwen, @gemini) follow same design
- ✅ UI consistency across components
- ✅ Accessibility built-in from day one
- ✅ No rework needed

## Next Steps

- [ ] Add project type detection to `/core:project-setup`
- [ ] Create DESIGN_SYSTEM.defaults.md with sensible defaults
- [ ] Add design system fill step to setup flow
- [ ] Test with frontend and fullstack projects
- [ ] Document customization process for users

---

**Status**: 📋 Planning
**Affects**: `/core:project-setup`, frontend/fullstack projects
**Priority**: High (blocks consistent UI development)
