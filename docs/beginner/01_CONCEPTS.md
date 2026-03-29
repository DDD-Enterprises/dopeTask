# Core Concepts (Translating Dev Jargon)

When you read software documentation, it can feel like a foreign language. To use dopeTask effectively, you don't need a computer science degree, but you do need to understand a few core concepts. 

Here is what all that "dev jargon" actually means in plain English:

---

### Git & The "Main Branch"
**Developer Jargon:** "A distributed version control system tracking changes in the main branch."

**Plain English:** Think of Git like a massive "Undo" button for folders and files. It remembers every change you ever make.
*   **The "Main Branch":** This is the pristine, working, official version of your app. Think of it like the final draft of a book.
*   **A "Commit":** A commit is just a "Save Point." It's a snapshot of your files at a specific moment in time.

*Why it matters in dopeTask:* We NEVER want the AI to write directly into the `main branch`. That's how things break. dopeTask uses Git to keep your main app safe.

---

### Worktrees
**Developer Jargon:** "A linked working tree allowing multiple branches to be checked out simultaneously."

**Plain English:** A "Safe Room." When you give dopeTask a plan to execute, it doesn't touch your real code. Instead, it creates a completely separate, temporary folder—a "Worktree." It tests the new code inside this Safe Room. If the code blows up, it only blows up the Safe Room. Your real app is untouched.

---

### Pull Request (PR)
**Developer Jargon:** "A formal request to merge a branch into the main integration line."

**Plain English:** A proposal. It's the AI saying, *"Hey, I finished building the feature in the Safe Room. Here is exactly what I changed. Can I add this to the official `main branch` now?"*

*Why it matters in dopeTask:* PRs are the final checkpoint. You, the human, get to look at the PR and hit "Approve" before the AI's code becomes official.

---

### The Task Packet
**Developer Jargon:** "A declarative JSON schema defining the atomic execution steps and invariant validation bounds."

**Plain English:** The Blueprint. This is a file (usually ending in `.json`) that contains step-by-step instructions. You don't write this! You tell ChatGPT or Claude what you want (e.g., "Add a login page"), and the AI writes the Task Packet.

It looks something like this:
1.  **Step 1:** Create `login.html`.
2.  **Validation:** Run a script to prove `login.html` exists.
3.  **Step 2:** Add a password box.
4.  **Validation:** Run a script to prove the password box works.

---

### The Proof Bundle
**Developer Jargon:** "An aggregated, verifiable audit artifact containing deterministic execution traces and checksums."

**Plain English:** The Receipt. After dopeTask finishes following the blueprint in the Safe Room, it spits out a file called `_PROOF_BUNDLE.json`. This receipt proves that every single step was completed and that all the automated tests passed successfully. If a step failed, the receipt tells you exactly where and why.

---

### Summary: The Flow

If you combine all these concepts, the flow of building an app safely looks like this:

1. You tell your Web AI what you want.
2. The AI gives you a **Task Packet** (The Blueprint).
3. You tell dopeTask to run the Blueprint.
4. dopeTask creates a **Worktree** (The Safe Room).
5. dopeTask builds and tests the code.
6. dopeTask hands you a **Proof Bundle** (The Receipt).
7. If the receipt looks good, a **Pull Request** (Proposal) is made to update your **Main Branch**.

When you want the exact current contract behind these concepts, switch to the canonical references:

- `../13_TASK_PACKET_FORMAT.md`
- `../22_WORKFLOW_GUIDE.md`
- `../24_UPGRADE_GUIDE.md`

Ready to get started?

👉 **[Next: Installation & Setup](02_INSTALLATION.md)**
