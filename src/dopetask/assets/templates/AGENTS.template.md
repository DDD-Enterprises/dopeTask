# AGENTS Instructions

Repo-aware work should use the strict repo-aware Task Packet contract by default.
When a packet binds to this repository, it must carry `repo_binding`, `execution`, `commit.verify`, `pr`, and a non-empty `steps.validation` plan.
PAL metadata is allowed for all agents, and Gemini packets must keep `pal_chain.enabled = true`.

<!-- DOPETASK:BEGIN -->
(disabled)
<!-- DOPETASK:END -->
<!-- CHATX:BEGIN -->
(disabled)
<!-- CHATX:END -->

Agent-specific rules are inserted in sentinel blocks only.
