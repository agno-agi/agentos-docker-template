---
name: task-decomposition
description: Decompose complex objectives into structured task plans with dependencies, acceptance criteria, and agent assignments following GSD methodology.
metadata:
  version: "1.0.0"
  author: neo-team
  tags: ["planning", "project-management", "gsd"]
---

# Task Decomposition Skill

Use this skill when breaking down a complex objective, project, or request into executable tasks.

## When to Use

- User provides a multi-step project or objective
- A structured brief needs to be turned into actionable work
- Tasks need dependency mapping and priority ordering

## Process

1. **Restate the objective** in one sentence to confirm understanding
2. **Identify deliverables** — what tangible outputs does this produce?
3. **Decompose into tasks** (max 6 per plan; split into phases if larger)
4. **For each task define:**
   - Title (verb-first, action-oriented)
   - Description (what, not how)
   - Acceptance criteria (specific, testable)
   - Complexity: S (< 1 hour), M (1-4 hours), L (4+ hours)
   - Dependencies (which tasks must finish first)
   - Agent assignment: Dev Team, Research Team, Content, or Tools
5. **Order by dependency graph**, then priority within tiers
6. **Identify risks** and propose mitigations

## Output Format

```
## Task Plan: [Objective]

**Deliverables:** [list]

### Task 1: [Verb-first title]
- **Description:** [what to do]
- **Acceptance criteria:**
  - [ ] [criterion]
- **Complexity:** S | M | L
- **Dependencies:** none | Task N
- **Assigned to:** [agent]
- **Status:** pending

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| ... | ... | ... |

### Execution Order
1. Task 1 (no deps)
2. Task 2 (depends on 1)
```

## Best Practices

- Never create a task without acceptance criteria
- Keep tasks small enough that "done" is unambiguous
- Surface dependencies early — parallel work is faster
- Flag unknowns as research tasks, not assumptions
