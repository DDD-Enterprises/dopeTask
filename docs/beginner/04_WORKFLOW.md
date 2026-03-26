# The Daily Workflow

You have dopeTask installed, and your AI is acting as a Supervisor. Now, how do you actually build your app?

Building with dopeTask is a repeating 4-step loop. Once you get the hang of it, it becomes incredibly fast and incredibly safe.

---

## The Loop: Plan ➡️ Execute ➡️ Verify ➡️ Merge

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
dopetask tp exec dark_mode.json --agent gemini
```

**What happens next?**
1.  dopeTask creates a "Safe Room" (a worktree).
2.  It spins up a specialized AI agent (the `gemini` agent) to act as the "Implementer."
3.  The Implementer reads the first step of your blueprint and writes the code.
4.  dopeTask runs the tests you specified in the blueprint.
5.  If it passes, it moves to the next step. If it fails, the Implementer tries to fix it. If it can't fix it, dopeTask stops completely to keep your app safe.

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

### 4. Merge (Making it Official)

If the Proof Bundle says "VALIDATED," you know the code is safe.

Now you just need to tell Git to add the Safe Room's code to your official `main branch`.

In your terminal, run:
```bash
dopetask tp git pr <TP_ID>
dopetask tp git merge <TP_ID>
dopetask tp git cleanup <TP_ID>
```
*(Replace `<TP_ID>` with the ID found in your JSON file).*

This creates a Pull Request (proposal), merges it into your main app, and cleans up the temporary Safe Room.

---

### You just built a feature safely with AI!

You never wrote code directly, and the AI never touched your main app without proving its work first. This is deterministic execution. This is how you build software that doesn't break.