import os
import re
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VAULT_DIR = os.path.expanduser("~/.aether_vault")
INBOX_DIR = os.path.join(VAULT_DIR, "00_Inbox")
ARCHIVE_DUMPS = os.path.join(VAULT_DIR, "50_Archive/System_Dumps")
LOG_FILE = os.path.join(VAULT_DIR, "aether_daemon.log")

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)
    print(log_line.strip())

def get_active_window_info():
    script = '''
    tell application "System Events"
        try
            set frontApp to first application process whose frontmost is true
            set appName to name of frontApp
            tell frontApp
                try
                    set winName to name of window 1
                on error
                    set winName to ""
                end try
            end tell
            return appName & "|" & winName
        on error
            return "Unknown|Unknown"
        end try
    end tell
    '''
    try:
        proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=1.5)
        out = proc.stdout.strip()
        if out and "|" in out:
            app, win = out.split("|", 1)
            return app.strip(), win.strip()
    except Exception as e:
        log(f"Error querying active window: {str(e)}")
    return "Unknown", "Unknown"

def sanitize_name(name):
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    sanitized = re.sub(r'[\s_]+', "_", sanitized)
    sanitized = re.sub(r'-+', "-", sanitized)
    return sanitized.strip("-_")

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        
        if file_name.startswith('.'):
            return
            
        log(f"Detected new file in Inbox: {file_name}")
        
        time.sleep(1.0)
        if not os.path.exists(file_path):
            log(f"File disappeared before processing: {file_name}")
            return
            
        is_screenshot = "screenshot" in file_name.lower()
        is_screen_recording = "screen recording" in file_name.lower()
        
        if is_screenshot or is_screen_recording:
            app, title = get_active_window_info()
            log(f"Context captured - App: {app}, Title: {title}")
            
            dt_match = re.search(r'(\d{4}-\d{2}-\d{2})\s+at\s+(\d+[\.\:]\d+[\.\:]\d+\s*[APMapm]*)', file_name)
            if dt_match:
                date_str = dt_match.group(1)
                time_str = dt_match.group(2).replace('.', ':')
            else:
                date_str = time.strftime("%Y-%m-%d")
                time_str = time.strftime("%H:%M:%S")
                
            clean_app = sanitize_name(app)
            clean_title = sanitize_name(title)
            
            if len(clean_title) > 40:
                clean_title = clean_title[:40]
                
            _, ext = os.path.splitext(file_name)
            prefix = "SS" if is_screenshot else "REC"
            
            if clean_title and clean_title != "Unknown" and clean_title != "":
                new_name = f"{prefix}_{clean_app}_{clean_title}_{date_str}_{sanitize_name(time_str)}{ext}"
            else:
                new_name = f"{prefix}_{clean_app}_{date_str}_{sanitize_name(time_str)}{ext}"
                
            dest_path = os.path.join(INBOX_DIR, new_name)
            
            try:
                if not os.path.exists(dest_path):
                    os.rename(file_path, dest_path)
                    log(f"Renamed screenshot: {file_name} -> {new_name}")
                else:
                    base, extension = os.path.splitext(new_name)
                    new_name_uniq = f"{base}_{int(time.time())}{extension}"
                    os.rename(file_path, os.path.join(INBOX_DIR, new_name_uniq))
                    log(f"Renamed screenshot (collision protection): {file_name} -> {new_name_uniq}")
            except Exception as e:
                log(f"Failed to rename screenshot: {str(e)}")
                
        elif file_name.startswith("WirelessDiagnostics") and file_name.endswith(".tar.gz"):
            dest_path = os.path.join(ARCHIVE_DUMPS, file_name)
            try:
                os.makedirs(ARCHIVE_DUMPS, exist_ok=True)
                os.rename(file_path, dest_path)
                log(f"Auto-routed diagnostics archive to System_Dumps: {file_name}")
            except Exception as e:
                log(f"Failed to route diagnostics: {str(e)}")
                
        elif file_name.endswith(".plist") or file_name.startswith("configd-"):
            dest_path = os.path.join(ARCHIVE_DUMPS, file_name)
            try:
                os.makedirs(ARCHIVE_DUMPS, exist_ok=True)
                os.rename(file_path, dest_path)
                log(f"Auto-routed config file to System_Dumps: {file_name}")
            except Exception as e:
                log(f"Failed to route config file: {str(e)}")

def start_daemon():
    log("Aether Daemon starting up...")
    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, path=INBOX_DIR, recursive=False)
    observer.start()
    log(f"Monitoring inbox directory: {INBOX_DIR}")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_daemon()
