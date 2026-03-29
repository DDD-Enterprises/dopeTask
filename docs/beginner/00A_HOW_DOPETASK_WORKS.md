# How dopeTask works

This page is the beginner-friendly explanation of what dopeTask is doing for you and why it exists.

If you want the short version:

dopeTask is a task orchestration system for AI-assisted software development.

In plain English:

It tells AI agents exactly what to do, in what order, under what rules, so they stop freelancing like chaotic interns.

Instead of:

- vague prompts
- random code
- hidden bugs
- hallucinated files
- late-night debugging

You get:

- structured tasks
- deterministic execution
- proof of what happened
- repeatable results

It is less "chatting with AI" and more "running a controlled operation."

## What dopeTask does

### 1. Breaks work into Task Packets

Each Task Packet is a fully specified unit of work with clear steps, constraints, and outputs.

Think:

- `TP-001` add login system
- `TP-002` add validation
- `TP-003` add tests

Except stricter and more machine-checkable.

### 2. Controls AI agents

Instead of letting an AI guess, skip steps, or invent structure, dopeTask forces:

- step-by-step execution
- rule compliance
- validation before completion

### 3. Produces proof bundles

Every run generates evidence showing:

- what changed
- what ran
- what passed
- what failed

So you do not have to guess whether the system actually did what you asked.

### 4. Enables repeatable workflows

You can:

- rerun tasks
- audit results
- reproduce outputs

That is something ordinary AI chat sessions do not do well on their own.

## The real flow

The core flow is:

You -> Task Packet -> Supervisor -> Implementer -> Repo -> Proof

### Supervisor

The supervisor:

- reads the task
- enforces rules
- decides the next packet or correction

### Implementer

The implementer is the coding agent, such as Codex, Gemini CLI, Claude Code, or Copilot CLI.

It:

- executes the packet
- writes code
- runs commands

### Repo

This is your actual project. dopeTask keeps changes isolated until they have passed the packet rules.

### Proof Bundle

The proof bundle is the evidence artifact that shows what happened and whether the execution validated successfully.

## Practical usage

### Step 1: Define the work clearly

Do not just say:

```text
build auth system
```

A proper task needs structure:

- goal
- steps
- constraints
- outputs

For example:

- Goal: add email/password login
- Steps: create auth service, add login endpoint, add validation, add tests
- Constraints: no new dependencies, must pass existing tests
- Output: updated files and passing validation

The point is to remove ambiguity before the implementer starts.

### Step 2: Run through a supervisor

The supervisor turns your request into a JSON Task Packet and keeps the work bounded.

Without that layer, an AI will often:

- skip steps
- invent APIs
- rewrite unrelated parts of the repo

### Step 3: Execute through dopeTask

The implementer agent can be:

- Codex
- Gemini CLI
- Claude Code
- Copilot CLI

dopeTask keeps the execution path deterministic and bounded.

### Step 4: Review the proof

You always review:

- what changed
- what passed
- what failed

Blind trust is not the workflow.

## How this works with Git

dopeTask uses isolation to keep your main branch safe.

At a high level:

- each Task Packet runs in its own worktree
- changes are allowlist-checked
- each packet creates one bounded commit
- a packet series ends in one PR

That keeps rollback simple and history readable.

## Why this helps beginners

AI systems have limited memory and weak discipline.

Without structure, they:

- forget instructions
- contradict themselves
- hallucinate missing context

dopeTask compensates by using:

- small contained tasks
- explicit inputs
- stateless execution boundaries
- proof logs instead of vibes

The result is that you stop depending on AI memory and start depending on system design.

## Advantages

- Reliability: less randomness, more control
- Repeatability: the same input can produce the same output
- Debuggability: you can inspect failures instead of guessing
- Lower cognitive load: you think in tasks, not chaos
- Cross-agent portability: the workflow is not tied to one model

## Tradeoffs

- More upfront structure
- Slower than one-shot prompting
- Some learning curve
- Requires discipline

The tradeoff is deliberate: more structure up front, less damage later.

## The right mental model

Stop thinking:

```text
AI is helping me code
```

Start thinking:

```text
I am orchestrating a system that uses AI as a tool
```

That shift is the difference between AI-assisted guessing and controlled engineering.

When you want the exact current contract behind this beginner explanation, switch to the canonical docs:

- `../00_OVERVIEW.md`
- `../13_TASK_PACKET_FORMAT.md`
- `../22_WORKFLOW_GUIDE.md`
- `../26_SUPERVISOR_PROMPTS.md`

👉 **[Next: Understanding Core Concepts](01_CONCEPTS.md)**
