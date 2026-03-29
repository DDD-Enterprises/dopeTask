# The Daily Workflow

You have dopeTask installed, and your AI is acting as a Supervisor. Now, how do you actually build your app?

Building with dopeTask is a repeating 4-step loop. Once you get the hang of it, it becomes incredibly fast and incredibly safe.

This page is the beginner tutorial version of the workflow. For the canonical operator reference, use `../22_WORKFLOW_GUIDE.md`. For migration from older workflows, use `../24_UPGRADE_GUIDE.md`.

---

## The Loop: Plan ➡️ Execute ➡️ Verify ➡️ Finalize

### 1. Plan (The Blueprint)

You start by talking to your AI (Claude, ChatGPT, or Cursor).

1.  **Give the AI a goal:** *"Add a dark mode toggle to the website header."*
2.  **The AI investigates:** If it needs to see your code to know how to add the toggle, it will ask you for it (or look itself if using Cursor).
3.  **The AI writes the Task Packet:** It will output a JSON file (the blueprint) containing step-by-step instructions and automated tests to verify the toggle works.
4.  **Save the file:** Save the AI's JSON output to a file in your project, for example: `dark_mode.json`.

### 2. Execute (The Safe Room)

Now you hand the blueprint over to dopeTask.

Open your terminal and type:
```bash
dopetask tp series exec dark_mode.json --agent gemini
```

**What happens next?**
1.  dopeTask creates a fresh "Safe Room" (a worktree) for this one Task Packet.
2.  It spins up a specialized AI agent (the `gemini` agent) to act as the "Implementer."
3.  The Implementer reads the first step of your blueprint and writes the code.
4.  dopeTask runs the tests you specified in the blueprint.
5.  If it passes, dopeTask commits that packet's allowlisted changes onto the packet branch and records the result in the series ledger. If it fails, dopeTask stops completely to keep your app safe.

If your feature needs multiple packets, your Supervisor will give each packet the same `series.id` and explicit `depends_on` rules. Run each ready packet with `dopetask tp series exec ...`. You can inspect the ledger any time with:

```bash
dopetask tp series status <series-id>
```

### 3. Verify (The Receipt)

When dopeTask finishes, it spits out a Proof Bundle. This is your receipt.

You don't even need to read the whole file. Just look at the terminal output or the top of the `proof/<TP_ID>_PROOF_BUNDLE.json` file for the `"status"`.

*   **If the status is "VALIDATED":** The code was written perfectly, and all tests passed!
*   **If the status is "FAILED":** The Implementer got stuck.

**What to do if it fails:**
Don't panic! This means dopeTask protected your app from bad code.
1. Copy the error message from the terminal (or the Proof Bundle).
2. Paste it back to your Supervisor AI.
3. The AI will realize its blueprint was flawed, write a *new, corrected* `dark_mode.json`, and you run step 2 again.

### 4. Finalize (Making it Official)

If the Proof Bundle says "VALIDATED," you know the code is safe.

When the final packet in the series has completed, open the single PR for the whole series:

In your terminal, run:
```bash
dopetask tp series finalize <SERIES_ID> --title "feat: add dark mode toggle"
```
*(Replace `<SERIES_ID>` with the `series.id` found in your JSON file).*

This pushes the final packet branch and opens one Pull Request against your base branch. Earlier packet commits are already part of that final branch through the declared packet ancestry.

---

### You just built a feature safely with AI!

You never wrote code directly, and the AI never touched your main app without proving its work first. This is deterministic execution. This is how you build software that doesn't break.
