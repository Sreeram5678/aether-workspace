# Aether Workspace

**Aether Workspace** is a state-of-the-art, context-aware digital desktop ecosystem designed for macOS. Instead of maintaining a static, cluttered grid of directories, Aether acts as a digital workbench, dynamically swapping project shortcuts based on your focus while automating screenshot naming, document search, and development dependency pruning.

---

## Core Features

1.  **Dynamic Viewports (Context Switching):** Instantly swap what directories are visible on your Desktop. Hide academic files when coding, and hide code repositories when studying.
2.  **Context-Aware Screenshot Auto-Namer:** Automatically captures the frontmost app name and active window title when you capture a screenshot, renaming files from `Screenshot...png` to `SS_[App]_[WindowName]_[Date]_[Time].png`.
3.  **Active Dependency Garbage Collector:** Automates disk optimization. It scans inactive projects, compresses `node_modules` or `.venv` folders into tarballs, and restores them automatically upon request.
4.  **Local Semantic Search Assistant:** Indexes text from notes, code files, and PDFs to search study documents locally with instant keyword highlights and clickable links.
5.  **Weekly Productivity Digest:** Aggregates Git commit logs and modified files to generate a weekly progress report.

---

## Installation & Setup

Simply clone the repository and run the installer:

```bash
git clone https://github.com/Sreeram5678/aether-workspace.git
cd aether-workspace
chmod +x install.sh
./install.sh
```

Restart your terminal or run `source ~/.zshrc` to activate the `desk` alias.

---

## CLI Reference & Cheat-sheet

Use the `desk` command to control your workspace:

### 1. Viewport Modes
Change what is visible on your Desktop:
*   `desk mode all` — Shows all primary folders (`00_Inbox`, `GATE_Prep`, `College`, `Active_Projects`, `Resources`, `Archive`).
*   `desk mode study` — Shows only the inbox, GATE prep, and College academics folders.
*   `desk mode work` — Shows only the inbox and Active Projects.
*   `desk mode admin` — Links only your Inbox and your Administrative reference folder.
*   `desk mode zen` (or `none`) — Clears all folder shortcuts from the Desktop for zero distraction.

### 2. Workspace Diagnostics & Telemetry
*   `desk status` — Renders an ASCII dashboard showing the active mode, inbox queue length, storage savings, and project activity status (including idle warnings).

### 3. Study & Search Assistant
*   `desk index` — Recalculates and updates the local text index of study documents.
*   `desk ask "[query]"` — Queries notes and PDFs, displaying matching sentences, confidence scores, and clickable file links.
    *   *Example:* `desk ask "backpropagation"`

### 4. Dependency Management
*   `desk prune` — Automatically identifies active projects untouched for >45 days and compresses their `node_modules` / `.venv` folders.
*   `desk prune [project]` — Forces immediate dependency archiving for a specific project.
*   `desk restore [project]` — Unarchives and restores the dependency folders for a project so you can run it.

### 5. Automated Reports
*   `desk digest` — Generates a markdown report inside the Inbox summarizing recent Git logs, modifications, and study files.

---

## Security & Privacy

Aether Workspace runs **100% locally and offline**. It has no cloud sync features, does not collect analytics, and stores all indices, logs, and files safely in your home directory (`~/.aether_vault/`).
EOF
