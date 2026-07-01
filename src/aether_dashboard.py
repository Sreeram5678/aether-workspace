import os
import time

VAULT_DIR = os.path.expanduser("~/.aether_vault")
DESKTOP_DIR = os.path.expanduser("~/Desktop")
PROJECTS_DIR = os.path.join(VAULT_DIR, "30_Active_Projects")
INBOX_DIR = os.path.join(VAULT_DIR, "00_Inbox")

def get_inbox_count():
    if not os.path.exists(INBOX_DIR):
        return 0
    return len([f for f in os.listdir(INBOX_DIR) if not f.startswith('.')])

def get_dir_size_mb(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
            except:
                pass
    return round(total / (1024 * 1024), 2)

def get_last_modified_date(path):
    max_mtime = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ["node_modules", "venv", ".venv", ".git"] and not d.startswith('.')]
        for f in files:
            if f.startswith('.'):
                continue
            fp = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(fp)
                if mtime > max_mtime:
                    max_mtime = mtime
            except:
                pass
    return max_mtime

def get_current_mode():
    if not os.path.exists(DESKTOP_DIR):
        return "Unknown"
    links = [f for f in os.listdir(DESKTOP_DIR) if os.path.islink(os.path.join(DESKTOP_DIR, f))]
    
    if len(links) == 0:
        return "ZEN / NONE"
    elif "10_GATE_Prep" in links and "20_College_Academics" in links and "30_Active_Projects" in links:
        return "ALL"
    elif "30_Active_Projects" in links:
        return "WORK"
    elif "10_GATE_Prep" in links and "20_College_Academics" in links:
        return "STUDY"
    elif "Administrative" in links:
        return "ADMIN"
    return "Custom"

def render_dashboard():
    print("\033[1;36m" + "="*55)
    print("                 AETHER WORKSPACE STATUS                 ")
    print("="*55 + "\033[0m")
    
    mode = get_current_mode()
    inbox_count = get_inbox_count()
    print(f"  \033[1mActive Mode:\033[0m  \033[1;32m{mode}\033[0m")
    print(f"  \033[1mInbox Status:\033[0m {inbox_count} pending files in 00_Inbox")
    print("\033[1;36m" + "-"*55 + "\033[0m")
    
    print("  \033[1mActive Projects Info:\033[0m")
    
    if not os.path.exists(PROJECTS_DIR):
        print("   No projects directory found.")
    else:
        projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith('.')]
        
        if not projects:
            print("   No projects found inside 30_Active_Projects.")
        else:
            total_savings_mb = 0
            for p in sorted(projects):
                p_path = os.path.join(PROJECTS_DIR, p)
                
                size_mb = get_dir_size_mb(p_path)
                
                archive_savings = 0
                for f in os.listdir(p_path):
                    if f.endswith(".tar.gz"):
                        fp = os.path.join(p_path, f)
                        try:
                            archive_savings += os.path.getsize(fp)
                        except:
                            pass
                total_savings_mb += archive_savings
                
                last_mtime = get_last_modified_date(p_path)
                if last_mtime == 0:
                    status_str = "\033[1;30mUNKNOWN\033[0m"
                else:
                    days_idle = (time.time() - last_mtime) / (24 * 60 * 60)
                    if days_idle > 45:
                        status_str = f"\033[1;31mSTALE\033[0m (idle {round(days_idle)} days) -> \033[3mdesk prune {p}\033[0m"
                    else:
                        status_str = f"\033[1;32mACTIVE\033[0m (idle {round(days_idle)} days)"
                
                is_compressed = any(f.endswith(".tar.gz") for f in os.listdir(p_path))
                comp_tag = " [ZIP]" if is_compressed else ""
                
                print(f"   • \033[1m{p}\033[0m{comp_tag:<6} [{size_mb} MB]  - {status_str}")
                
            if total_savings_mb > 0:
                savings_gb = round(total_savings_mb / 1024, 2)
                print(f"\n  \033[1mStorage Optimizer:\033[0m Reclaimed {savings_gb} GB via dependency compression.")
                
    print("\033[1;36m" + "="*55 + "\033[0m")
    print("  \033[3mCommands: desk mode [mode] | desk ask [query] | desk prune\033[0m")

if __name__ == "__main__":
    render_dashboard()
