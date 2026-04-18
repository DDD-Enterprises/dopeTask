# PAL_PACKET_TEMPLATE.md

## Status
Reusable packet template for PAL-driven implementation work.

## Instructions
Fill this template before non-trivial work. Keep it tight but explicit. If the packet cannot satisfy its own validation gates, it is not ready.

---

## 1. Packet Metadata

### Packet title
<short, concrete name>

### Objective
<what must be true when this packet is complete>

### Why this packet exists now
<why this scope is the right scope boundary now>

### Risk level
<low / medium / high>

### Task class
<unknown subsystem / architecture-sensitive / runtime bug / ambiguous design fork / API-sensitive / documentation-sensitive / security-sensitive / other>

---

## 2. Scope Control

### Authorized scope
- <files/modules allowed to change>
- <allowed dependency changes>
- <allowed test changes>
- <allowed doc changes>

### Forbidden scope
- <out-of-bounds files/modules>
- <no opportunistic cleanup>
- <no unrelated refactors>
- <no interface expansion unless explicitly allowed>

### Invariants to preserve
- <security invariant>
- <performance invariant>
- <compatibility invariant>
- <data or migration invariant>
- <architecture invariant>

---

## 3. Required Confidence Gates

### Understanding confidence required before planning
MEDIUM / HIGH

### Plan confidence required before implementation
MEDIUM / HIGH

### Root-cause confidence required before fix
HIGH / N/A

### Final confidence required for completion
VERIFIED

---

## 4. Required PAL Chain

### Baseline chain
<select one>
- Minimal: `planner → codereview → precommit`
- Standard: `analyze → thinkdeep → challenge → planner → challenge → codereview → precommit → challenge`
- High-assurance: custom chain below

### Custom chain for this packet
<exact planned chain>

### Why this chain is appropriate
<brief rationale>

---

## 5. Escalation Tools and Triggers

### Use tracer if
<call-flow ambiguity trigger>

### Use consensus if
<approach ambiguity trigger>

### Use debug if
<runtime failure / contradiction trigger>

### Use apilookup if
<API/SDK uncertainty trigger>

### Use testgen if
<coverage/regression trigger>

### Use secaudit if
<security trigger>

### Use docgen if
<documentation trigger>

### Use refactor if
<refactor decomposition trigger>

---

## 6. Stage Artifacts

Each stage artifact must include:
- summary
- evidence ledger
- assumptions
- confidence
- next action

### Understanding artifact
<to be filled during execution>

### Plan artifact
<to be filled during execution>

### Review artifact
<to be filled during execution>

### Final verification artifact
<to be filled during execution>

---

## 7. Commit-Slice Plan

### Slice 1
Objective:
<smallest safe step>

Allowed files:
<list>

Expected verification:
<smallest relevant check>

Exit condition:
<what must be true>

### Slice 2
Objective:
<next safe step>

Allowed files:
<list>

Expected verification:
<check>

Exit condition:
<what must be true>

### Additional slices
<repeat as needed>

---

## 8. Validation Gates

### Understanding gate
Required evidence:
- relevant files identified
- entry points named
- flows or dependencies understood enough to proceed

Tool path:
<analyze / tracer / both>

Pass condition:
<what MEDIUM confidence means here>

### Plan gate
Required evidence:
- stepwise plan exists
- dependencies called out
- validation steps included
- assumptions challenged

Tool path:
<planner / thinkdeep / challenge / consensus if needed>

Pass condition:
<what makes the plan executable>

### Implementation gate
Required evidence:
- slice verification complete
- diff inspected
- no unexplained contradictions

Tool path:
<codereview quick / debug / testgen as needed>

Pass condition:
<what allows continuation>

### Diff gate
Required evidence:
- codereview complete
- material findings addressed or explicitly accepted with rationale

Tool path:
<codereview>

Pass condition:
<what is acceptable before precommit>

### Final gate
Required evidence:
- precommit passed
- evidence ledger complete
- final challenge passed

Tool path:
<precommit → challenge>

Pass condition:
VERIFIED

---

## 9. Documentation Requirements

### Are docs in scope?
Yes / No

### If yes, why?
<public interface / complexity / gotchas / acceptance criteria>

### Required doc surfaces
- <README>
- <inline docs>
- <API docs>
- <runbook>
- <migration note>

### Doc generation path
<docgen / manual / both>

### Doc validation rule
Docs must be checked against final implementation surfaces:
- signatures
- config keys
- behavior-changing conditions
- gotchas
- failure modes

---

## 10. Stop Conditions

Stop chaining when:
- the next tool would not change the decision
- uncertainty can only be resolved by implementation or runtime evidence
- outputs have become repetitive
- the blast radius is growing

Stop the packet when:
- understanding cannot reach required confidence
- the plan cannot be made executable in scope
- required API facts cannot be sourced
- root cause cannot reach HIGH when needed
- final verification cannot reach VERIFIED

---

## 11. Evidence Ledger

Record during execution:
- files inspected
- flows traced
- API docs checked
- failures/logs examined
- tests run
- diffs reviewed
- tool outputs used for decisions
- final review findings
- precommit verdict

### Evidence ledger entries
- <entry 1>
- <entry 2>
- <entry 3>

---

## 12. Final Report Format

### Objective status
Met / Not met / Partially met

### Scope actually changed
<files/modules>

### Tool chain actually executed
<exact chain used>

### Key decisions
- <decision>
- <rationale>
- <alternatives rejected>

### Validation summary
- understanding gate: pass/fail
- plan gate: pass/fail
- implementation gate: pass/fail
- diff gate: pass/fail
- final gate: pass/fail

### Codereview summary
<top findings and disposition>

### Precommit verdict
<approved / fixes required / failed>

### Residual risks
- <risk>
- <mitigation>

### Final confidence
LOW / MEDIUM / HIGH / VERIFIED

### Completion statement
<explicit statement of whether the packet is complete and why>
