import os
import time
import subprocess
import sys

VAULT_DIR = os.path.expanduser("~/.aether_vault")
INBOX_DIR = os.path.join(VAULT_DIR, "00_Inbox")
PROJECTS_DIR = os.path.join(VAULT_DIR, "30_Active_Projects")
ACADEMICS_DIR = os.path.join(VAULT_DIR, "20_College_Academics")
GATE_DIR = os.path.join(VAULT_DIR, "10_GATE_Prep")

SECONDS_IN_WEEK = 7 * 24 * 60 * 60

def get_git_commits(repo_path):
    try:
        cmd = ["git", "log", "--since=7.days.ago", "--oneline"]
        proc = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, timeout=3)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip().split("\n")
    except Exception:
        pass
    return []

def scan_modified_files(directory):
    modified = []
    current_time = time.time()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ["node_modules", "venv", ".venv", ".git"] and not d.startswith('.')]
        
        for f in files:
            if f.startswith('.'):
                continue
            file_path = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(file_path)
                if current_time - mtime < SECONDS_IN_WEEK:
                    rel_path = os.path.relpath(file_path, VAULT_DIR)
                    modified.append((rel_path, mtime))
            except Exception:
                pass
    modified.sort(key=lambda x: x[1], reverse=True)
    return modified

def generate_weekly_digest():
    print("Generating Weekly Productivity Digest...")
    date_str = time.strftime("%Y-%m-%d")
    digest_path = os.path.join(INBOX_DIR, f"Weekly_Digest_{date_str}.md")
    
    git_reports = {}
    if os.path.exists(PROJECTS_DIR):
        projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith('.')]
        for p in projects:
            p_path = os.path.join(PROJECTS_DIR, p)
            if os.path.exists(os.path.join(p_path, ".git")):
                commits = get_git_commits(p_path)
                if commits:
                    git_reports[p] = commits
                    
    gate_modified = scan_modified_files(GATE_DIR)
    college_modified = scan_modified_files(ACADEMICS_DIR)
    
    if not git_reports and not gate_modified and not college_modified:
        print("No activity detected in the last 7 days. Digest generation skipped.")
        return
        
    markdown_content = []
    markdown_content.append(f"# Weekly Productivity Digest — {date_str}")
    markdown_content.append("\nHere is a summary of your workspace activity and milestones over the last 7 days.\n")
    
    markdown_content.append("## 💻 Software Development")
    if git_reports:
        for repo, commits in git_reports.items():
            markdown_content.append(f"\n### {repo}")
            for c in commits:
                markdown_content.append(f"- {c}")
    else:
        proj_modified = scan_modified_files(PROJECTS_DIR)
        if proj_modified:
            markdown_content.append("\nFiles modified recently in active projects:")
            for p, _ in proj_modified[:10]:
                markdown_content.append(f"- `{os.path.basename(p)}` ({os.path.dirname(p)})")
        else:
            markdown_content.append("\nNo development activity recorded.")
            
    markdown_content.append("\n## 📚 GATE Preparation")
    if gate_modified:
        markdown_content.append("\nNotes and materials touched in the last 7 days:")
        for file, _ in gate_modified[:10]:
            markdown_content.append(f"- [{os.path.basename(file)}](file://{VAULT_DIR}/{file})")
    else:
        markdown_content.append("\nNo files modified in GATE prep folder.")
        
    markdown_content.append("\n## 🎓 College & Academics")
    if college_modified:
        markdown_content.append("\nAcademic files modified in the last 7 days:")
        for file, _ in college_modified[:10]:
            markdown_content.append(f"- [{os.path.basename(file)}](file://{VAULT_DIR}/{file})")
    else:
        markdown_content.append("\nNo files modified in college folder.")
        
    try:
        with open(digest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))
        print(f"SUCCESS: Generated weekly digest in inbox: {os.path.basename(digest_path)}")
    except Exception as e:
        print(f"Failed to generate digest: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    generate_weekly_digest()
