---
name: research-synthesis
description: Conduct evidence-based research with source grading, structured findings, and actionable recommendations.
metadata:
  version: "1.0.0"
  author: neo-team
  tags: ["research", "analysis", "evidence"]
---

# Research Synthesis Skill

Use this skill when gathering evidence, evaluating sources, and producing decision-ready research findings.

## When to Use

- A decision needs supporting evidence
- Comparing technical approaches or tools
- Evaluating feasibility of a proposed solution
- Domain exploration before project planning

## Process

1. **Frame the decision question** — what needs to be decided?
2. **Break into sub-questions** — 2-4 specific, answerable queries
3. **Gather evidence** from multiple sources
4. **Grade sources** using the quality hierarchy:
   - **A — Primary:** Official docs, specs, academic papers
   - **B — Secondary:** Reputable analysis, expert tutorials
   - **C — Tertiary:** Blog posts, forums, opinion pieces
   - **D — Unverified:** Single-source claims, undated content
5. **Evaluate evidence** — separate facts from assumptions, note contradictions
6. **Synthesize findings** into a structured report with recommendations

## Output Format

```
## Research Findings: [Topic]

**Decision question:** [what this answers]

**Summary:** [2-3 sentence conclusion]

**Key findings:**
1. [finding] — [source] — confidence: high | medium | low
2. [finding] — [source] — confidence: high | medium | low

**Source quality:** [grading summary]

**Recommendation:** [what to do and why]

**Trade-offs:**
- Option A: [pros / cons]
- Option B: [pros / cons]

**Open questions:** [unknowns]
```

## Best Practices

- Every finding must cite a source
- Contradictory evidence must be acknowledged, not hidden
- Recommendations must be supported by evidence, not opinion
- "We don't know" is a valid and valuable finding
- Flag information older than 12 months as potentially stale
