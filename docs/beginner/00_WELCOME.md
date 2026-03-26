# Welcome to dopeTask

**Building software with AI is amazing, but it can also be terrifying.**

If you are using tools like ChatGPT, Claude, or cursor to build your app, you are basically handing the keys to your codebase to a brilliant but reckless intern.

They can write code faster than any human. But if you let them type directly into your files, they will eventually:
- Delete something important by accident.
- "Hallucinate" code that looks right but completely breaks your app.
- Get confused and overwrite their own work.

This happens because AI models don't naturally understand **safety** or **process**. They just want to write code.

## Enter dopeTask: The Strict Manager

**dopeTask** is not an AI. It is a strict, deterministic management system that sits between your AI and your code.

Think of it like this: Instead of letting the "intern" (the AI) touch the actual building materials, dopeTask forces them to draw up a detailed, step-by-step blueprint first. We call this blueprint a **Task Packet**.

Once the AI hands over the blueprint, dopeTask takes over:
1. **The Safe Room:** dopeTask creates a temporary, isolated copy of your code (called a "worktree").
2. **The Execution:** It follows the AI's blueprint exactly, step-by-step.
3. **The Inspection:** After every single step, dopeTask runs automated tests to prove the code actually works.
4. **The Receipt:** If everything passes, dopeTask gives you a "Proof Bundle"—a verifiable receipt showing exactly what changed and that it was tested.

Only then is the code allowed into your main project.

## Why You Need dopeTask

If you don't have a background in software engineering, it is very hard to know if the code an AI just gave you is safe.

dopeTask gives you **Deterministic Execution**. This means:
- **No Silent Failures:** If the AI makes a mistake, dopeTask catches it immediately during the "Inspection" phase and stops. It fails safely.
- **Auditability:** You always have a receipt (the Proof Bundle) showing exactly what happened.
- **Peace of Mind:** You can let the AI work on complex features without worrying that it's going to accidentally destroy your working app.

## Ready to build safely?

Let's start by translating some developer jargon into plain English so you know exactly what dopeTask is doing under the hood.

👉 **[Next: Understanding Core Concepts](01_CONCEPTS.md)**
