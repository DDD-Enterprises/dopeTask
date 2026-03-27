# CRM Project Transition Instructions

To continue with the CRM User Stories using the newly built `dopeTask` execution engine, follow these steps:

## 1. Project Setup
- **Switch Workspace:** Open the CRM project directory in your IDE/CLI.
- **Reload Gemini:** Start a new session with the CRM project as the root.

## 2. DopeTask Integration
- Ensure `dopeTask` is accessible. You can either:
  - Install it in your CRM environment: `pip install -e /path/to/dopeTask`
  - Add it to your PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:/path/to/dopeTask/src`

## 3. Workflow for CRM Stories
- We will define the CRM user stories as Task Packets (YAML/JSON).
- We will use the command:
  ```bash
  dopetask tp series exec path/to/crm_story.json --agent gemini
  ```
- This will use the **STRICT_EXECUTOR** profile we just built to ensure the CRM components are implemented deterministically without agent drift.

## 4. TTY Repair
- If the terminal looks "broken" (glitchy banners or colors), run:
  ```bash
  export DOPETASK_NEON=0
  export TERM=xterm-256color
  ```
  This disables the cosmetic ASCII banners and resets the terminal type.

---
**Ready for reload.**
