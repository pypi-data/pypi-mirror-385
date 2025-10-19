# Design System Template
# Purpose: Establish universal design standards for typography, spacing, colors, and component patterns
# Variables: None (this is a standards document, not a generation template)
# Used by: All frontend agents for consistent UI/UX implementation
# Template location: multiagent_core/templates/.multiagent/frontend/templates/DESIGN_SPECS.md

# Design Specifications - Universal Frontend Standards

> ⚠️ **This is the SINGLE SOURCE OF TRUTH for frontend design. All agents (@claude, @copilot, @codex, @qwen, @gemini) and developers MUST follow this guide.**

---

## 🎯 Universal Design Principles

These principles apply to **ALL frontend stacks** (React, Vue, Angular, Svelte, etc.)

### 1. Typography: Strict Size Hierarchy

**RULE: Use exactly 4 font sizes + 1 exception. No more, no less.**

#### The 4 Font Sizes + Exception:
- **Size 1**: 24px - Page titles only
- **Size 2**: 20px - Section headers, card titles
- **Size 3**: 16px - ALL body text, descriptions, labels
- **Size 4**: 14px - Metadata, timestamps (MINIMUM SIZE)
- **Exception**: 12px - ONLY for tags/badges when space is critical

#### The 2 Font Weights:
- **Primary**: Semibold/600 - Headers and emphasis
- **Secondary**: Normal/400 - Everything else

#### ❌ FORBIDDEN:
- Font sizes larger than 24px
- Font sizes smaller than 14px (except the 12px exception)
- Using 3+ font weights (bold, medium, light, etc.)
- Custom pixel values outside the system

---

### 2. Spacing: 8pt Grid System

**All spacing MUST be divisible by 4 or 8 pixels:**

#### Spacing Scale:
- **4px** (0.25rem) - Minimal spacing, tight gaps
- **8px** (0.5rem) - Small spacing, compact layouts
- **12px** (0.75rem) - Comfortable spacing
- **16px** (1rem) - Standard spacing (most common)
- **24px** (1.5rem) - Section spacing
- **32px** (2rem) - Large spacing between major sections
- **48px** (3rem) - Hero spacing, dramatic separation

#### ❌ FORBIDDEN:
- Odd pixel values (7px, 13px, 19px)
- Random spacing not on the 4/8px grid
- Inconsistent spacing in similar contexts

---

### 3. Color System

#### Color Roles:
- **Primary** - Brand color, CTAs, primary actions
- **Secondary** - Supporting brand color, secondary actions
- **Success** - Green spectrum - Confirmations, success states
- **Warning** - Yellow/Orange spectrum - Caution, warnings
- **Error** - Red spectrum - Errors, destructive actions
- **Info** - Blue spectrum - Informational messages
- **Neutral** - Gray spectrum - Text, backgrounds, borders

#### Color Hierarchy (60/30/10 Rule):
- **60%** Background (neutral colors)
- **30%** Content (text and UI elements)
- **10%** Accent (CTAs, highlights, status indicators)

#### Accessibility Requirements:
- **Text on background**: Minimum 4.5:1 contrast ratio (WCAG AA)
- **Large text (18px+)**: Minimum 3:1 contrast ratio
- **Interactive elements**: Must have visible focus states
- **Status colors**: Never rely on color alone, use icons/text

---

### 4. Component Hierarchy

#### Button Hierarchy (3 levels):
1. **Primary** - Main action on page (1 per section)
2. **Secondary** - Alternative actions (2-3 per section)
3. **Tertiary/Ghost** - Less important actions, cancel, back

#### Card Structure:
- **Header** - Title + optional description
- **Content** - Main card content with consistent padding
- **Footer** (optional) - Actions or metadata

#### Form Elements:
- **Label** - Always visible, positioned above or left of input
- **Input** - Clear borders, adequate touch targets (44px minimum)
- **Helper text** - Below input, smaller size
- **Error state** - Red color + icon + descriptive message

---

## 📦 Stack Detection & Selection

**Agents: Detect the project stack by checking:**

1. **package.json** dependencies:
   - React: `react`, `next`, `gatsby`
   - Vue: `vue`, `nuxt`, `quasar`
   - Angular: `@angular/core`
   - Svelte: `svelte`, `sveltekit`

2. **UI Framework**:
   - Tailwind: `tailwindcss`
   - Material: `@mui/material`, `@angular/material`, `vuetify`
   - Ant Design: `antd`
   - Chakra: `@chakra-ui/react`
   - shadcn: Look for `components/ui/` directory

3. **Use the appropriate implementation examples below** based on detected stack

---

## 🔧 Implementation Examples by Stack

### React + Tailwind CSS + shadcn/ui

#### Typography
```tsx
// Size 1 - Page titles
<h1 className="text-2xl font-semibold text-white">
  Page Title
</h1>

// Size 2 - Section headers
<h2 className="text-xl font-semibold text-white">
  Section Header
</h2>

// Size 3 - Body text (DEFAULT)
<p className="text-base text-gray-300">
  Body text, descriptions, all content
</p>

// Size 4 - Metadata
<span className="text-sm text-gray-400">
  Posted 2 hours ago
</span>

// Exception - Tags/badges only
<Badge className="text-xs">Premium</Badge>
```

#### Spacing
```tsx
// Padding (8pt grid)
<div className="p-2">     {/* 8px */}
<div className="p-4">     {/* 16px - most common */}
<div className="p-6">     {/* 24px */}
<div className="p-8">     {/* 32px */}

// Gaps
<div className="flex gap-4">        {/* 16px between items */}
<div className="grid gap-6">        {/* 24px between grid items */}

// Margins
<div className="mb-4">              {/* 16px bottom margin */}
<section className="mt-8 mb-8">    {/* 32px vertical spacing */}
```

#### Colors (Dark Theme Example)
```tsx
// Backgrounds
<div className="bg-gray-950">              {/* Page background */}
<Card className="bg-gray-900/50">          {/* Card background */}
<div className="bg-gray-800">              {/* Elevated element */}

// Text
<h1 className="text-white">                {/* Primary headings */}
<p className="text-gray-300">              {/* Body text */}
<span className="text-gray-400">          {/* Secondary text */}
<span className="text-gray-500">          {/* Muted text */}

// Borders
<div className="border border-gray-800">   {/* Standard border */}

// Status colors
<Badge className="bg-green-500/20 text-green-400 border-green-500/50">
  Success
</Badge>
<Badge className="bg-red-500/20 text-red-400 border-red-500/50">
  Error
</Badge>
```

#### Component Templates
```tsx
// Card Component
<Card className="bg-gray-900/50 border-gray-800 hover:bg-gray-900/70 transition-all duration-200">
  <CardHeader className="p-6 pb-4">
    <h3 className="text-xl font-semibold text-white">
      Card Title
    </h3>
    <p className="text-base text-gray-400 mt-1">
      Card description goes here
    </p>
  </CardHeader>
  <CardContent className="p-6 pt-0">
    {/* Content */}
  </CardContent>
</Card>

// Button Hierarchy
<Button className="bg-blue-600 hover:bg-blue-700 text-white text-base px-4 py-2">
  Primary Action
</Button>
<Button className="bg-gray-800 hover:bg-gray-700 text-white text-base px-4 py-2">
  Secondary Action
</Button>
<Button className="text-gray-400 hover:text-white text-base px-3 py-1.5">
  Cancel
</Button>

// Form Input
<div className="space-y-2">
  <Label className="text-sm text-gray-300">Email Address</Label>
  <Input
    type="email"
    className="bg-gray-900 border-gray-800 text-white text-base"
    placeholder="you@example.com"
  />
  <p className="text-sm text-gray-400">We'll never share your email</p>
</div>
```

---

### Vue 3 + Vuetify

#### Typography
```vue
<!-- Size 1 - Page titles -->
<v-card-title class="text-h4 font-weight-semibold">
  Page Title
</v-card-title>

<!-- Size 2 - Section headers -->
<v-card-subtitle class="text-h5 font-weight-semibold">
  Section Header
</v-card-subtitle>

<!-- Size 3 - Body text -->
<v-card-text class="text-body-1">
  Body text content
</v-card-text>

<!-- Size 4 - Metadata -->
<v-chip size="small" variant="text">
  Posted 2 hours ago
</v-chip>
```

#### Spacing
```vue
<!-- Padding (Vuetify uses 4px scale) -->
<v-card class="pa-2">     <!-- 8px -->
<v-card class="pa-4">     <!-- 16px -->
<v-card class="pa-6">     <!-- 24px -->
<v-card class="pa-8">     <!-- 32px -->

<!-- Gaps (use flex/grid utilities) -->
<v-row class="gap-4">     <!-- 16px gap -->
<v-col class="d-flex flex-column gap-6">  <!-- 24px gap -->
```

#### Component Templates
```vue
<!-- Card Component -->
<v-card
  color="grey-darken-4"
  variant="outlined"
  class="pa-4"
>
  <v-card-title class="text-h5 font-weight-semibold">
    Card Title
  </v-card-title>
  <v-card-subtitle class="text-body-1 text-grey-lighten-1">
    Card description
  </v-card-subtitle>
  <v-card-text>
    Content goes here
  </v-card-text>
</v-card>

<!-- Button Hierarchy -->
<v-btn color="primary" size="default">Primary Action</v-btn>
<v-btn color="secondary" size="default">Secondary</v-btn>
<v-btn variant="text" size="default">Cancel</v-btn>

<!-- Form Input -->
<v-text-field
  label="Email Address"
  type="email"
  variant="outlined"
  density="comfortable"
  hint="We'll never share your email"
  persistent-hint
></v-text-field>
```

---

### Angular + Angular Material

#### Typography
```html
<!-- Size 1 - Page titles -->
<h1 mat-headline-4 class="font-semibold">
  Page Title
</h1>

<!-- Size 2 - Section headers -->
<h2 mat-headline-5 class="font-semibold">
  Section Header
</h2>

<!-- Size 3 - Body text -->
<p mat-body-1>
  Body text content
</p>

<!-- Size 4 - Metadata -->
<span mat-caption>
  Posted 2 hours ago
</span>
```

#### Spacing
```html
<!-- Padding (Angular Material uses density, custom CSS for spacing) -->
<mat-card [style.padding.px]="16">  <!-- 16px padding -->
<mat-card [style.padding.px]="24">  <!-- 24px padding -->

<!-- Use custom CSS classes for spacing -->
<div class="spacing-4">  <!-- 16px -->
<div class="spacing-6">  <!-- 24px -->
```

```css
/* styles.css - Define spacing utilities */
.spacing-2 { padding: 8px; }
.spacing-4 { padding: 16px; }
.spacing-6 { padding: 24px; }
.spacing-8 { padding: 32px; }

.gap-4 > * + * { margin-left: 16px; }
.gap-6 > * + * { margin-left: 24px; }
```

#### Component Templates
```html
<!-- Card Component -->
<mat-card appearance="outlined" class="spacing-4">
  <mat-card-header>
    <mat-card-title class="font-semibold">
      Card Title
    </mat-card-title>
    <mat-card-subtitle>
      Card description
    </mat-card-subtitle>
  </mat-card-header>
  <mat-card-content>
    Content goes here
  </mat-card-content>
</mat-card>

<!-- Button Hierarchy -->
<button mat-raised-button color="primary">Primary Action</button>
<button mat-raised-button color="accent">Secondary</button>
<button mat-button>Cancel</button>

<!-- Form Input -->
<mat-form-field appearance="outline">
  <mat-label>Email Address</mat-label>
  <input matInput type="email" placeholder="you@example.com">
  <mat-hint>We'll never share your email</mat-hint>
</mat-form-field>
```

---

### CSS Modules / Styled Components / Plain CSS

#### Typography
```tsx
// CSS Module approach
<h1 className={styles.titleLarge}>Page Title</h1>
<h2 className={styles.titleMedium}>Section Header</h2>
<p className={styles.bodyText}>Body text</p>
<span className={styles.metadata}>Posted 2 hours ago</span>
```

```css
/* styles.module.css */
.titleLarge {
  font-size: 1.5rem;     /* 24px */
  font-weight: 600;
  line-height: 1.2;
}

.titleMedium {
  font-size: 1.25rem;    /* 20px */
  font-weight: 600;
  line-height: 1.3;
}

.bodyText {
  font-size: 1rem;       /* 16px */
  font-weight: 400;
  line-height: 1.5;
}

.metadata {
  font-size: 0.875rem;   /* 14px */
  font-weight: 400;
  color: var(--text-secondary);
}
```

#### Spacing
```css
/* Define CSS custom properties for spacing */
:root {
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-12: 3rem;    /* 48px */
}

.card {
  padding: var(--spacing-4);
  gap: var(--spacing-4);
}

.section {
  margin-bottom: var(--spacing-8);
}
```

#### Component Templates
```tsx
// Card Component (Styled Components)
import styled from 'styled-components';

const Card = styled.div`
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: var(--spacing-6);
  transition: background 0.2s;

  &:hover {
    background: var(--bg-card-hover);
  }
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-2);
`;

const CardDescription = styled.p`
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.5;
`;
```

---

## 🎨 Responsive Design (Universal)

### Breakpoints (Industry Standard)
```
Mobile:   320px - 639px   (single column)
Tablet:   640px - 1023px  (2 columns)
Laptop:   1024px - 1279px (3 columns)
Desktop:  1280px+          (4 columns)
```

### Mobile-First Approach (All Stacks)

**Tailwind:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Cards */}
</div>
```

**CSS:**
```css
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}
```

**Vuetify:**
```vue
<v-row>
  <v-col cols="12" md="6" lg="4">
    <!-- Card -->
  </v-col>
</v-row>
```

**Angular Material:**
```html
<div fxLayout="row wrap" fxLayoutGap="16px grid">
  <div fxFlex="100" fxFlex.md="50" fxFlex.lg="33">
    <!-- Card -->
  </div>
</div>
```

---

## ✅ Design Audit Checklist

Before marking any UI task complete, **ALL agents must verify**:

### Typography
- [ ] Only using the 4 defined font sizes (24px, 20px, 16px, 14px)?
- [ ] Exception (12px) only used for tags/badges?
- [ ] Only using 2 font weights (semibold 600 / normal 400)?
- [ ] Text is readable (minimum 14px for content)?
- [ ] Line height adequate (1.5 for body text)?

### Colors & Contrast
- [ ] Following the defined color roles (primary, secondary, semantic)?
- [ ] Text contrast meets WCAG AA (4.5:1 minimum)?
- [ ] Status colors use icons/text, not color alone?
- [ ] Interactive elements have visible focus states?
- [ ] Hover states on all interactive elements?

### Spacing
- [ ] All spacing uses 4px or 8px increments?
- [ ] Consistent padding in similar components?
- [ ] Proper breathing room between sections (24px+)?
- [ ] Touch targets minimum 44px for mobile?

### Components
- [ ] Cards follow the header/content/footer template?
- [ ] Buttons have clear hierarchy (primary/secondary/tertiary)?
- [ ] Forms have proper labels, helpers, error states?
- [ ] Loading states for async operations?
- [ ] Empty states for zero data?

### Responsive
- [ ] Works on mobile (320px minimum width)?
- [ ] Tablet layout optimized (640px-1023px)?
- [ ] Desktop makes use of available space (1280px+)?
- [ ] Touch-friendly on mobile (44px touch targets)?
- [ ] No horizontal scroll at any breakpoint?

### Accessibility
- [ ] All images have alt text?
- [ ] Form inputs have associated labels?
- [ ] Keyboard navigation works?
- [ ] Focus indicators visible?
- [ ] Semantic HTML used (<main>, <nav>, <button>)?

---

## 📐 Common Layout Patterns (Universal)

### Dashboard Layout

**Concept:**
```
┌─────────────────────────────────────┐
│  Header (64px fixed)                │
├──────────┬──────────────────────────┤
│ Sidebar  │  Main Content            │
│ (256px)  │  (flexible)              │
│          │                          │
└──────────┴──────────────────────────┘
```

**Tailwind:**
```tsx
<div className="min-h-screen bg-gray-950">
  <header className="h-16 border-b border-gray-800">
    {/* Logo, nav, user menu */}
  </header>
  <div className="flex">
    <aside className="w-64 border-r border-gray-800">
      {/* Navigation */}
    </aside>
    <main className="flex-1 p-6">
      {/* Page content */}
    </main>
  </div>
</div>
```

**CSS:**
```css
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  height: 64px;
  border-bottom: 1px solid var(--border-color);
}

.content {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 256px;
  border-right: 1px solid var(--border-color);
}

.main {
  flex: 1;
  padding: 24px;
}
```

### Centered Form Layout

**Tailwind:**
```tsx
<div className="min-h-screen flex items-center justify-center p-4">
  <div className="w-full max-w-md">
    <Card className="p-6">
      {/* Form content */}
    </Card>
  </div>
</div>
```

**CSS:**
```css
.formContainer {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.formCard {
  width: 100%;
  max-width: 28rem;
  padding: 1.5rem;
}
```

### Grid of Cards

**Tailwind:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => (
    <Card key={item.id}>
      {/* Card content */}
    </Card>
  ))}
</div>
```

**CSS:**
```css
.cardGrid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .cardGrid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .cardGrid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## 🚨 Common Mistakes to Avoid

### Typography Mistakes
1. ❌ Using text-3xl, text-4xl, etc. → **Stick to 4 sizes**
2. ❌ Mixing too many font weights → **Only semibold & normal**
3. ❌ Text smaller than 14px for content → **14px minimum**
4. ❌ No line height → **Set 1.5 for body, 1.2 for headings**

### Spacing Mistakes
1. ❌ Random pixel values (13px, 19px) → **Use 8pt grid**
2. ❌ Inconsistent card padding → **Standardize to 16px or 24px**
3. ❌ Cramped mobile layouts → **Minimum 16px padding on mobile**
4. ❌ No spacing between sections → **Minimum 24px between sections**

### Color Mistakes
1. ❌ Too many colors → **Follow 60/30/10 rule**
2. ❌ Low contrast text → **Test with contrast checker**
3. ❌ Color-only status → **Add icons & text labels**
4. ❌ No hover states → **All buttons need hover feedback**

### Component Mistakes
1. ❌ Buttons without hierarchy → **Clear primary/secondary/tertiary**
2. ❌ Forms without labels → **Every input needs a label**
3. ❌ Missing loading states → **Show spinners for async**
4. ❌ No empty states → **Handle zero data gracefully**

### Responsive Mistakes
1. ❌ Desktop-only testing → **Test at 320px minimum**
2. ❌ Tiny touch targets → **44px minimum for mobile**
3. ❌ Horizontal scroll → **Check at all breakpoints**
4. ❌ Hidden content on mobile → **Make all content accessible**

---

## 🎯 Agent Implementation Guide

### Step 1: Detect Stack
Read `package.json` to determine:
- Framework: React / Vue / Angular / Svelte
- UI Library: Tailwind / Material / Vuetify / shadcn / etc.

### Step 2: Read This Document
Before writing ANY UI code:
1. Review universal principles (typography, spacing, colors)
2. Find your stack's implementation section
3. Copy the appropriate component templates
4. Follow the audit checklist

### Step 3: Implementation
```markdown
For @claude (architecture):
- Set up design system CSS variables
- Create base component library
- Define shared styles

For @copilot (implementation):
- Build pages using component templates
- Apply consistent spacing & typography
- Implement responsive layouts

For @codex (testing):
- Verify responsive behavior
- Test accessibility with keyboard
- Validate contrast ratios

For @qwen (optimization):
- Optimize CSS bundle size
- Remove unused styles
- Improve render performance

For @gemini (documentation):
- Document component usage
- Create Storybook/style guide
- Write accessibility notes
```

### Step 4: Validation
Run through the Design Audit Checklist before marking complete.

---

## 📝 Project Customization Checklist

When starting a new project, customize these sections:

### 1. Brand Colors
```yaml
Primary: [YOUR_PRIMARY_COLOR]      # Main brand color (buttons, links)
Secondary: [YOUR_SECONDARY_COLOR]  # Supporting color (accents)
Success: green-500                  # Or your preferred green
Warning: yellow-500                 # Or your preferred yellow
Error: red-500                      # Or your preferred red
Info: blue-500                      # Or your preferred blue
```

### 2. Font Family
```css
/* Define in your root CSS */
:root {
  --font-sans: [YOUR_FONT], -apple-system, system-ui, sans-serif;
  --font-mono: [YOUR_MONO_FONT], 'Courier New', monospace;
}
```

### 3. Component Library Choice
- [ ] shadcn/ui (React + Tailwind)
- [ ] Material-UI (React)
- [ ] Vuetify (Vue)
- [ ] Angular Material (Angular)
- [ ] Chakra UI (React)
- [ ] Ant Design (React)
- [ ] Custom components

### 4. Animation Preferences
- [ ] Subtle transitions (200ms) - Recommended
- [ ] No animations (accessibility-first)
- [ ] Elaborate animations (marketing sites)
- [ ] Always respect `prefers-reduced-motion`

### 5. Dark/Light Mode
- [ ] Dark mode only
- [ ] Light mode only
- [ ] Both with toggle
- [ ] System preference detection

---

## 📚 Additional Resources

### Design Tools
- **Color Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **8pt Grid Calculator**: Multiply by 4 or 8
- **Responsive Tester**: Test at 320px, 768px, 1024px, 1280px

### Accessibility Standards
- **WCAG 2.1 AA**: Minimum for production
- **Focus indicators**: 2px outline minimum
- **Touch targets**: 44x44px minimum
- **Alt text**: Descriptive, not decorative

### Framework Documentation
- **Tailwind CSS**: https://tailwindcss.com
- **Vuetify**: https://vuetifyjs.com
- **Angular Material**: https://material.angular.io
- **shadcn/ui**: https://ui.shadcn.com

---

**Remember**: Consistency > Creativity. A boring but consistent UI is better than a creative mess.

**This is a living document** - Update as design decisions are made. All agents must stay synchronized with this spec.

---

**Last Updated**: {{CURRENT_DATE}}
**Maintained by**: {{TEAM_NAME}}
**Questions**: {{DESIGN_TEAM_CONTACT}}
