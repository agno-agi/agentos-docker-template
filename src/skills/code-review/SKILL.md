---
name: code-review
description: Review code against acceptance criteria with structured pass/fail validation, edge case checking, and actionable feedback.
metadata:
  version: "1.0.0"
  author: neo-team
  tags: ["code-review", "quality", "validation"]
---

# Code Review Skill

Use this skill when validating implementation work against defined acceptance criteria.

## When to Use

- Implementation is complete and needs verification
- Code changes need quality assessment
- Acceptance criteria need pass/fail validation

## Process

1. **Read acceptance criteria** — these are the checklist
2. **Examine the implementation** — what was built, decisions made, deviations
3. **Validate each criterion** — pass or fail with specific reasoning
4. **Check for gaps** — edge cases, error handling, missing requirements
5. **Deliver verdict** — pass (all criteria met) or fail (with actionable feedback)

## Output Format

```
## Review: [Task Title]

**Verdict:** PASS | FAIL

**Criteria validation:**
| Criterion | Result | Notes |
|---|---|---|
| [criterion] | PASS / FAIL | [reasoning] |

**Edge cases checked:**
- [case]: [result]

**Issues found:**
- [issue]: [specific fix needed]

**Recommendation:** [approve / fix and re-submit]
```

## Best Practices

- Be specific — "this is wrong" is useless, "the handler doesn't catch TimeoutError" is actionable
- Be fair — review against stated criteria, not personal preferences
- Every FAIL must include what needs to change to become a PASS
- Minor style issues don't warrant a FAIL — note them but approve
