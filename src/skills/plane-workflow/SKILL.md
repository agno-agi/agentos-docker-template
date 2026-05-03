---
name: plane-workflow
description: Manage projects and tasks in Plane with strict status lifecycle, prompt storage, and living documentation patterns.
metadata:
  version: "1.0.0"
  author: neo-team
  tags: ["plane", "project-management", "workflow"]
---

# Plane Workflow Skill

Use this skill when interacting with Plane as the system of record for projects, tasks, prompts, and templates.

## When to Use

- Creating or updating project tasks from a task plan
- Tracking status transitions for active work
- Storing or retrieving prompts and templates
- Generating project status reports from Plane data

## Status Lifecycle

All issues follow this strict sequence:

```
Backlog → Approved → In Progress → Review → Done
                                          ↘ Blocked
```

- Never skip transitions without documenting the reason
- Always add a comment when changing status
- Include `plane_task_id` in all cross-agent handoffs

## Workflow Patterns

### Task Creation (from PM task plan)
1. Discover the target project: `list_projects`
2. For each task in the plan: `create_issue` with title, description, acceptance criteria, labels
3. Set initial state to `Backlog` or `Approved`
4. Add label `agent-created` for traceability

### Task Progress Tracking
1. When work starts: transition to `In Progress`
2. When work completes: transition to `Review`, add completion comment
3. After verification: transition to `Done`
4. If blocked: transition to `Blocked`, add blocker description

### Prompt Storage
- Store prompts as issues with label `prompt`
- Title format: `[Prompt] Agent Name - Purpose`
- Retrieve via label search + keyword

### Template Storage
- Store templates as issues with label `template`
- Title format: `[Template] Template Name`

## Best Practices

- Always read before writing — avoid duplicates
- Never fabricate project or issue data
- Keep comments concise and timestamped
- Use labels consistently for discoverability
