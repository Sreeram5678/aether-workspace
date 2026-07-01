import os
import time
import sys

VAULT_DIR = os.path.expanduser("~/.aether_vault")
DESKTOP_DIR = os.path.expanduser("~/Desktop")
PROJECTS_DIR = os.path.join(VAULT_DIR, "30_Active_Projects")
INBOX_DIR = os.path.join(VAULT_DIR, "00_Inbox")
LOG_FILE = os.path.join(VAULT_DIR, "aether_daemon.log")

# ANSI Color codes for styled output
C_CYAN = "\033[1;36m"
C_GREEN = "\033[1;32m"
C_BLUE = "\033[1;34m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_GRAY = "\033[1;30m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

def play_loading_animation():
    animation = [
        "  ⠋ Scanning digital desktop...  ",
        "  ⠙ Reading Aether Vault...      ",
        "  ⠹ Scanning active projects...  ",
        "  ⠸ Compiling disk metrics...    ",
        "  ⠼ Loading TUI dashboard...     "
    ]
    for frame in animation:
        sys.stdout.write(f"\r{C_CYAN}{frame}{C_RESET}")
        sys.stdout.flush()
        time.sleep(0.18)
    sys.stdout.write("\r" + " " * 35 + "\r")
    sys.stdout.flush()

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
    return "CUSTOM"

def get_last_log_entries(n=3):
    if not os.path.exists(LOG_FILE):
        return ["No logs found. Daemon may not be active."]
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return [l.strip() for l in lines[-n:]]
    except:
        return ["Failed to read background daemon logs."]

def render_dashboard():
    play_loading_animation()
    # 1. Fetch data
    mode = get_current_mode()
    inbox_count = get_inbox_count()
    
    # Format Mode colors
    mode_color = C_GRAY
    if mode == "ALL":
        mode_color = C_CYAN
    elif mode == "WORK":
        mode_color = C_BLUE
    elif mode == "STUDY":
        mode_color = C_GREEN
    elif mode == "ADMIN":
        mode_color = C_YELLOW

    # Title Block
    print(f"{C_CYAN}┌────────────────────────────────────────────────────────┐{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_BOLD}{'A E T H E R   W O R K S P A C E':^54} {C_RESET}{C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}└────────────────────────────────────────────────────────┘{C_RESET}")
    
    # Section: System Status
    print(f"  {C_BOLD}SYSTEM STATUS{C_RESET}")
    print(f"  ├─ Mode:         {mode_color}{mode}{C_RESET}")
    print(f"  └─ Inbox Queue:  {C_YELLOW}{inbox_count}{C_RESET} files pending in 00_Inbox")
    print("")

    # Section: Projects Telemetry
    print(f"  {C_BOLD}PROJECTS TELEMETRY{C_RESET}")
    print(f"  ┌──────────────────────┬─────────────┬─────────────────┐")
    
    # Pixel-perfect title alignment
    name_hdr = f"{C_BOLD}{'Project Name':<20}{C_RESET}"
    size_hdr = f"{C_BOLD}{'Disk Size':<11}{C_RESET}"
    status_hdr = f"{C_BOLD}{'Activity Status':<15}{C_RESET}"
    print(f"  │ {name_hdr} │ {size_hdr} │ {status_hdr} │")
    print(f"  ├──────────────────────┼─────────────┼─────────────────┤")
    
    total_savings_mb = 0
    if not os.path.exists(PROJECTS_DIR):
        print(f"  │ {C_GRAY}{'No active projects folder':^20}{C_RESET} │ {C_GRAY}{'-':^11} │ {C_GRAY}{'-':^15} │")
    else:
        projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith('.')]
        if not projects:
            print(f"  │ {C_GRAY}{'No projects found':^20}{C_RESET} │ {C_GRAY}{'-':^11} │ {C_GRAY}{'-':^15} │")
        else:
            for p in sorted(projects):
                p_path = os.path.join(PROJECTS_DIR, p)
                size_mb = get_dir_size_mb(p_path)
                
                # Check for savings
                archive_savings = 0
                for f in os.listdir(p_path):
                    if f.endswith(".tar.gz"):
                        fp = os.path.join(p_path, f)
                        try:
                            archive_savings += os.path.getsize(fp)
                        except:
                            pass
                total_savings_mb += archive_savings
                
                # Calculate active time
                last_mtime = get_last_modified_date(p_path)
                if last_mtime == 0:
                    status_text = "UNKNOWN"
                    status_color = C_GRAY
                else:
                    days_idle = (time.time() - last_mtime) / (24 * 60 * 60)
                    if days_idle > 45:
                        status_text = f"STALE ({round(days_idle)}d)"
                        status_color = C_RED
                    else:
                        status_text = f"ACTIVE ({round(days_idle)}d)"
                        status_color = C_GREEN
                
                is_compressed = any(f.endswith(".tar.gz") for f in os.listdir(p_path))
                name_display = f"{p} [ZIP]" if is_compressed else p
                
                # Format print columns safely (padding before coloring)
                col1 = f"{name_display:<20}"
                col2 = f"{size_mb:>8} MB"
                col3 = f"{status_color}{status_text:<15}{C_RESET}"
                
                print(f"  │ {col1} │ {col2} │ {col3} │")
                
    print(f"  └──────────────────────┴─────────────┴─────────────────┘")
    
    # Storage Optimizer Info
    if total_savings_mb > 0:
        savings_gb = round(total_savings_mb / 1024, 2)
        print(f"  {C_GREEN}✓{C_RESET} {C_BOLD}Storage Saved:{C_RESET} {savings_gb} GB via dependency archiving")
        print("")
    else:
        print("")

    # Section: Daemon Logs
    print(f"  {C_BOLD}DAEMON LOGGER (Latest activity){C_RESET}")
    logs = get_last_log_entries(3)
    for i, log_entry in enumerate(logs):
        prefix = "  ├─" if i < len(logs) - 1 else "  └─"
        if len(log_entry) > 52:
            log_entry = log_entry[:49] + "..."
        print(f"{prefix} {C_GRAY}{log_entry}{C_RESET}")
    
    # Footer Command bar
    print("")
    print(f"{C_CYAN}┌────────────────────────────────────────────────────────┐{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_BOLD}Commands:{C_RESET} desk mode [mode] | desk ask [q] | desk prune  {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}└────────────────────────────────────────────────────────┘{C_RESET}")

if __name__ == "__main__":
    render_dashboard()
