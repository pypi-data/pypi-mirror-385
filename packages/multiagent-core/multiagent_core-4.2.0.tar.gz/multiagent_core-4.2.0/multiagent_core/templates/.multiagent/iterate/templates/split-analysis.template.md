# Spec Split Analysis: {{SPEC_NAME}}

**Date:** {{DATE}}
**Analyzed By:** @claude
**Strategy:** {{STRATEGY}}

---

## Instructions for Filling This Template

**For the agent analyzing the spec:**

1. **Read ALL spec files** in `specs/{{SPEC_DIR}}/`:
   - `spec.md` - Count FRs, identify functional groupings
   - `tasks.md` - Count tasks, identify phases, find natural breakpoints
   - `data-model.md` - Count tables/models, understand data relationships
   - `plan.md` - Identify architecture components, system boundaries
   - `research.md` - Understand technical domains

2. **Count everything**:
   - Total lines, FRs, tasks, phases, tables, components
   - Look for patterns in naming (FR-INF, FR-MCP, etc.)
   - Identify logical groupings

3. **Identify natural boundaries**:
   - Architecture layers (infrastructure, integrations, features, deployment)
   - Functional domains (auth, payments, notifications, etc.)
   - Task phases (setup, core, advanced, deployment)
   - User stories (if mentioned in spec)

4. **Decide on split strategy**:
   - Architecture-based: Technical layers
   - User-story-based: Feature groupings
   - Phase-based: Development timeline
   - Domain-based: Functional areas

5. **Propose structure**:
   - How many new specs? (typically 5-10)
   - What should they be named? (002-{descriptive-name}, 003-{descriptive-name}, etc.)
   - How many tasks per spec? (aim for 15-50 tasks each)
   - What dependencies exist?

6. **Fill ALL {{PLACEHOLDERS}}** with actual analyzed data
   - If a section doesn't apply, write "N/A" and explain why
   - Add or remove spec entries as needed (not limited to 8!)

---

## Current Spec Statistics

- **Spec directory:** {{SPEC_DIR}}
- **Total lines in spec.md:** {{TOTAL_LINES}}
- **Functional requirements:** {{FR_COUNT}} total
- **FR range:** {{FR_MIN}} to {{FR_MAX}}
- **Total tasks:** {{TASK_COUNT}}
- **Task phases identified:** {{PHASE_LIST}} ({{PHASE_COUNT}} phases)
- **Data models/tables:** {{TABLE_COUNT}}
- **Components identified:** {{COMPONENT_COUNT}}
- **Component list:** {{COMPONENT_LIST}}

---

## Detected Boundaries

### {{BOUNDARY_TYPE_1}} (e.g., "Architecture Layers" or "Functional Domains")

{{BOUNDARY_1_DESCRIPTION}}

**Identified boundaries:**

1. **{{BOUNDARY_1_NAME_1}}** (e.g., "Infrastructure Setup" or "User Management")
   - FRs: {{BOUNDARY_1_FRS_1}} (e.g., "FR-001 to FR-015" or "FR-AUTH-001 to FR-AUTH-008")
   - Tasks: {{BOUNDARY_1_TASKS_1}} (e.g., "20 tasks, Phase 1-2")
   - Description: {{BOUNDARY_1_DESC_1}}

2. **{{BOUNDARY_1_NAME_2}}**
   - FRs: {{BOUNDARY_1_FRS_2}}
   - Tasks: {{BOUNDARY_1_TASKS_2}}
   - Description: {{BOUNDARY_1_DESC_2}}

3. **{{BOUNDARY_1_NAME_3}}**
   - FRs: {{BOUNDARY_1_FRS_3}}
   - Tasks: {{BOUNDARY_1_TASKS_3}}
   - Description: {{BOUNDARY_1_DESC_3}}

{{ADD_MORE_BOUNDARIES_AS_NEEDED}}

---

### {{BOUNDARY_TYPE_2}} (e.g., "Task Phase Distribution" or "User Story Groupings")

{{BOUNDARY_2_DESCRIPTION}}

**Distribution:**

{{BOUNDARY_2_BREAKDOWN}}

---

## Recommended Strategy: {{STRATEGY_NAME}}

**Rationale:**

{{STRATEGY_RATIONALE}}

**Why this approach?**

{{STRATEGY_REASONING}}

**Alternative strategies considered:**

1. **{{ALT_STRATEGY_1}}**: {{ALT_REASON_1}}
2. **{{ALT_STRATEGY_2}}**: {{ALT_REASON_2}}

---

## Proposed New Structure

**Total new specs to create:** {{NEW_SPEC_COUNT}}

**IMPORTANT:** New specs numbered 002 onwards (original 001 remains as reference)

```
specs/
├── 002-{{SPEC_NAME_2}}/        ({{SPEC_TASKS_2}} tasks)
│   ├── spec.md                 # {{SPEC_FRS_2}}
│   ├── tasks.md
│   ├── data-model.md
│   ├── plan.md
│   ├── research.md
│   ├── contracts/
│   ├── checklists/
│   ├── agent-tasks/
│   └── reports/
│
├── 003-{{SPEC_NAME_3}}/        ({{SPEC_TASKS_3}} tasks)
│   └── [same structure]        # {{SPEC_FRS_3}}
│
{{REPEAT_FOR_EACH_ADDITIONAL_SPEC}}
```

**Naming Convention:** {{NAMING_EXPLANATION}}

---

## Detailed Spec Breakdown

### 002-{{SPEC_NAME_2}}

**Focus:** {{SPEC_FOCUS_2}}

**Contains:**
- FRs: {{SPEC_FR_LIST_2}}
- Tasks: {{SPEC_TASK_RANGE_2}}
- Data models: {{SPEC_TABLES_2}}
- Key components: {{SPEC_COMPONENTS_2}}

**Dependencies:**
- Depends on: {{SPEC_DEPS_2}}
- Blocks: {{SPEC_BLOCKS_2}}

**Rationale:** {{SPEC_REASON_2}}

---

### 003-{{SPEC_NAME_3}}

**Focus:** {{SPEC_FOCUS_3}}

**Contains:**
- FRs: {{SPEC_FR_LIST_3}}
- Tasks: {{SPEC_TASK_RANGE_3}}
- Data models: {{SPEC_TABLES_3}}
- Key components: {{SPEC_COMPONENTS_3}}

**Dependencies:**
- Depends on: {{SPEC_DEPS_3}}
- Blocks: {{SPEC_BLOCKS_3}}

**Rationale:** {{SPEC_REASON_3}}

---

{{REPEAT_FOR_ALL_SPECS}}

---

## Task Distribution Summary

| Spec | Name | Tasks | % of Total | FRs | Focus Area |
|------|------|-------|------------|-----|------------|
{{TABLE_ROW_FOR_EACH_SPEC}}

**Total:** {{TOTAL_TASKS}} tasks distributed across {{NEW_SPEC_COUNT}} specs

**Distribution metrics:**
- Average: ~{{AVG_TASKS}} tasks per spec
- Largest: {{LARGEST_SPEC}} ({{LARGEST_TASKS}} tasks)
- Smallest: {{SMALLEST_SPEC}} ({{SMALLEST_TASKS}} tasks)
- Std deviation: {{TASK_STDDEV}} (balance quality indicator)

**Balance assessment:** {{BALANCE_ASSESSMENT}}

---

## Dependencies Flow

```
{{DEPENDENCY_DIAGRAM}}
```

**Example format:**
```
002 (Foundation)
 ↓
003 (Integration) + 004 (Core Feature)  [Parallel]
 ↓
005-007 (Additional Features)  [Sequential or Parallel]
 ↓
{{LAST_SPEC}} (Deployment/Testing)
```

**Critical path:** {{CRITICAL_PATH}}

**Parallelization opportunities:** {{PARALLEL_WORK}}

---

## Dependency Details

{{FOR_EACH_SPEC}}

### {{SPEC_NUMBER}}-{{SPEC_NAME}}

**Depends on:**
{{LIST_DEPENDENCIES_OR_NONE}}

**Blocks:**
{{LIST_BLOCKED_SPECS_OR_NONE}}

**Can start when:** {{START_CONDITION}}

**Estimated duration:** {{DURATION_ESTIMATE}}

{{END_FOR_EACH_SPEC}}

---

## Data Model Distribution Strategy

{{DATA_STRATEGY}}

**Options considered:**
1. **Full copy to foundation spec, references elsewhere** (Recommended)
2. **Create shared/data-model.md**
3. **Distribute tables by domain**

**Chosen approach:** {{CHOSEN_DATA_APPROACH}}

**Rationale:** {{DATA_RATIONALE}}

---

## File Distribution Plan

### spec.md Files
{{SPEC_MD_DISTRIBUTION}}

### tasks.md Files
{{TASKS_MD_DISTRIBUTION}}

### data-model.md Files
{{DATA_MODEL_DISTRIBUTION}}

### plan.md Files
{{PLAN_MD_DISTRIBUTION}}

### research.md Files
{{RESEARCH_MD_DISTRIBUTION}}

### contracts/ Directories
{{CONTRACTS_DISTRIBUTION}}

### checklists/ Directories
{{CHECKLISTS_DISTRIBUTION}}

---

## Risks and Mitigations

**Identified risks:**

1. **{{RISK_1}}**
   - Impact: {{RISK_1_IMPACT}}
   - Mitigation: {{RISK_1_MITIGATION}}

2. **{{RISK_2}}**
   - Impact: {{RISK_2_IMPACT}}
   - Mitigation: {{RISK_2_MITIGATION}}

{{ADD_MORE_RISKS_AS_NEEDED}}

---

## Quality Checks

**Pre-execution checklist:**

- [ ] Task distribution is balanced (no spec > 60 tasks)
- [ ] Dependencies are logical (no circular dependencies)
- [ ] All original FRs accounted for
- [ ] All original tasks accounted for
- [ ] Spec names are descriptive and consistent
- [ ] Data model strategy is clear
- [ ] Numbering starts at 002 (not duplicate 001)

**Validation criteria:**

- Sum of new tasks = Original task count: {{TASK_SUM_MATCHES}}
- No orphaned FRs: {{NO_ORPHANED_FRS}}
- Dependency graph is acyclic: {{NO_CIRCULAR_DEPS}}

---

## Next Steps

### 1. Review This Analysis

**Action items:**
- [ ] Verify proposed structure makes sense
- [ ] Check task distribution is balanced
- [ ] Confirm dependencies are logical
- [ ] Review spec naming conventions
- [ ] Validate data model strategy

**Questions to answer:**
- Does the split make parallel development easier?
- Are dependencies realistic?
- Can specs be developed independently?
- Is the granularity appropriate (not too fine, not too coarse)?

---

### 2. Run Scaffold Phase

**Command:**
```bash
/split:spec-scaffold {{SPEC_NUMBER}}
```

**What this does:**
- Reads this analysis report
- Creates spec directories: 002-{{SPEC_NAME_2}}, 003-{{SPEC_NAME_3}}, etc.
- Creates empty files: spec.md, tasks.md, data-model.md, plan.md, research.md
- Creates empty directories: contracts/, checklists/, agent-tasks/, reports/

**Expected output:**
```
✅ Scaffold Complete
Created: {{NEW_SPEC_COUNT}} spec directories
```

---

### 3. Run Content Distribution Phase

**Command:**
```bash
/split:spec-execute {{SPEC_NUMBER}} --strategy={{STRATEGY}}
```

**What this does:**
- Invokes spec-splitter subagent
- Distributes FRs across spec.md files
- Distributes tasks across tasks.md files
- Implements data model strategy
- Splits plan.md sections
- Moves contracts and checklists
- Generates specs/SPEC_INDEX.md

**Expected output:**
```
✅ Spec Split Complete
Created {{NEW_SPEC_COUNT}} new specs
Total: {{TOTAL_TASKS}} tasks distributed
```

---

### 4. Post-Split Actions

**After splitting:**

1. **Review all new specs:**
   ```bash
   ls -la specs/00*/
   cat specs/SPEC_INDEX.md
   ```

2. **Run task layering:**
   ```bash
   /iterate:tasks --all
   ```

3. **Setup worktrees:**
   ```bash
   ~/.multiagent/iterate/scripts/setup-spec-worktrees.sh --all
   ```

4. **Begin parallel development:**
   - Each agent works on assigned spec
   - Follow dependency order
   - Create PRs independently

---

## Analysis Metadata

**Analysis completed:** {{DATE}}
**Analyzer:** @claude
**Original spec:** {{SPEC_DIR}}
**Proposed specs:** {{NEW_SPEC_COUNT}}
**Total tasks:** {{TASK_COUNT}}
**Strategy:** {{STRATEGY}}
**Status:** ✅ Ready for scaffold phase

---

**Next command:** `/split:spec-scaffold {{SPEC_NUMBER}}`

---
