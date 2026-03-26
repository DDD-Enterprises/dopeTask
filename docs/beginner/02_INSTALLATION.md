# Installation & Setup

Before you can start building software safely with dopeTask, you need to install it and prepare your workspace.

Don't worry—you only have to do this once!

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

If your project isn't already a Git repository, you need to initialize one. Inside your project folder, run:

```bash
git init
```

This tells your computer: *"Start tracking all the changes made in this folder."*

---

## 4. Install dopeTask into the Project

Finally, tell dopeTask that it should manage this specific folder. Run:

```bash
dopetask project shell init
```

This command creates a few hidden folders (like `.dopetask/`) where dopeTask will store its temporary "Safe Rooms" and Proof Receipts.

---

### You are done!

Your computer is now ready. The next step is to set up your AI (like ChatGPT or Claude) so it knows how to act as your "Strict Manager."

👉 **[Next: Setting up your Web LLM](03_WEB_LLM_SETUP.md)**
