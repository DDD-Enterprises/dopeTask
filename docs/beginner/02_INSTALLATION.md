# Installation & Setup

Before you can start building software safely with dopeTask, you need to install it and prepare your workspace.

Don't worry—you only have to do this once!

This page is the beginner walkthrough. For the canonical setup reference, see `../01_SETUP.md`.

---

## 1. Install dopeTask

dopeTask is a command-line tool. You install it using `pip` (the standard installer for Python).

Open your Terminal (or Command Prompt) and type:

```bash
pip install dopetask
```

*Note: You may need to use `pip3` depending on how Python is installed on your computer.*

**Verify Installation**
To check if it worked, type:
```bash
dopetask --version
```
If it prints a version number (like `0.3.0`), you are ready to go!

---

## 2. Set Up Your Project Folder

dopeTask works inside a specific folder on your computer where your app's code will live. 

1. Create a new folder for your app (e.g., "my-awesome-app").
2. Open your Terminal and navigate into that folder.

```bash
mkdir my-awesome-app
cd my-awesome-app
```

---

## 3. Initialize Git (The Time Machine)

Remember from the [Concepts Guide](01_CONCEPTS.md) that dopeTask relies heavily on Git to keep your code safe. 

If your project isn't already a Git repository, use the bootstrap command inside your project folder:

```bash
dopetask setup-git --visibility private
```

This command checks for `git` and `gh`, installs them when a supported package manager is available, makes sure `gh` is authenticated, initializes the repo on `main`, creates the remote GitHub repository, makes the first commit, pushes it, and sets safe local and GitHub defaults.

If `gh` authentication fails, the command prints the next commands to try, including `gh auth login --web --git-protocol https` and token-based login guidance.

---

## 4. Install dopeTask into the Project

Once Git is set up, tell dopeTask that it should manage this specific folder. Run:

```bash
dopetask project shell init
```

This command creates a few hidden folders (like `.dopetask/`) where dopeTask will store its temporary "Safe Rooms" and Proof Receipts.

---

### You are done!

Your computer is now ready. The next step is to set up your AI (like ChatGPT or Claude) so it knows how to act as your "Strict Manager."

If you are upgrading an existing installation instead of starting fresh, read `../24_UPGRADE_GUIDE.md` before continuing.

👉 **[Next: Setting up your Web LLM](03_WEB_LLM_SETUP.md)**
