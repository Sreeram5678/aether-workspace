import os
import tarfile
import shutil
import time
import sys

VAULT_DIR = os.path.expanduser("~/.aether_vault")
PROJECTS_DIR = os.path.join(VAULT_DIR, "30_Active_Projects")
DAYS_INACTIVE = 45
INACTIVE_THRESHOLD = DAYS_INACTIVE * 24 * 60 * 60  # seconds

DEPENDENCY_FOLDERS = ["node_modules", "venv", ".venv", "env"]

def get_last_active_time(project_path):
    max_mtime = 0
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in DEPENDENCY_FOLDERS and d != ".git" and not d.startswith('.')]
        for f in files:
            if f.startswith('.'):
                continue
            file_path = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > max_mtime:
                    max_mtime = mtime
            except Exception:
                pass
    return max_mtime

def compress_folder(folder_path, archive_path):
    print(f"Compressing: {os.path.basename(folder_path)} -> {os.path.basename(archive_path)}...")
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(folder_path, arcname=os.path.basename(folder_path))
        return True
    except Exception as e:
        print(f"Error compressing {folder_path}: {str(e)}", file=sys.stderr)
        return False

def prune_project(project_name, force=False):
    project_path = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        print(f"Error: Project '{project_name}' not found at {project_path}")
        return False
        
    last_active = get_last_active_time(project_path)
    current_time = time.time()
    inactive_duration = current_time - last_active
    
    if inactive_duration > INACTIVE_THRESHOLD or force:
        days_idle = round(inactive_duration / (24 * 60 * 60), 1)
        print(f"\nProcessing project: {project_name} (Idle for {days_idle} days)")
        
        cleaned = False
        for dep in DEPENDENCY_FOLDERS:
            dep_path = os.path.join(project_path, dep)
            if os.path.exists(dep_path) and os.path.isdir(dep_path):
                archive_name = f"{dep}.tar.gz"
                archive_path = os.path.join(project_path, archive_name)
                
                if compress_folder(dep_path, archive_path):
                    shutil.rmtree(dep_path)
                    print(f"SUCCESS: Pruned and archived {dep} in {project_name}.")
                    cleaned = True
        if not cleaned:
            print(f"No active dependencies (node_modules/venv) found to prune in '{project_name}'.")
        return cleaned
    else:
        days_idle = round(inactive_duration / (24 * 60 * 60), 1)
        print(f"Project '{project_name}' is active (Idle for {days_idle} days). Skipping.")
        return False

def restore_project(project_name):
    project_path = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        print(f"Error: Project '{project_name}' not found.")
        return False
        
    restored = False
    for dep in DEPENDENCY_FOLDERS:
        archive_name = f"{dep}.tar.gz"
        archive_path = os.path.join(project_path, archive_name)
        dep_path = os.path.join(project_path, dep)
        
        if os.path.exists(archive_path) and os.path.isfile(archive_path):
            print(f"Restoring {dep} in project '{project_name}' from archive...")
            try:
                if os.path.exists(dep_path):
                    shutil.rmtree(dep_path)
                
                # Check for filter argument compatibility with Python 3.12+
                kwargs = {}
                if sys.version_info >= (3, 12):
                    kwargs['filter'] = 'data'
                    
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(path=project_path, **kwargs)
                
                os.remove(archive_path)
                print(f"SUCCESS: Restored {dep} folder.")
                restored = True
            except Exception as e:
                print(f"Error restoring {dep}: {str(e)}", file=sys.stderr)
                
    if not restored:
        print(f"No compressed archives found to restore for '{project_name}'.")
    return restored

def run_gc_all():
    print("Running Aether Workspace Garbage Collector...")
    if not os.path.exists(PROJECTS_DIR):
        print(f"No projects folder found at {PROJECTS_DIR}")
        return
        
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith('.')]
    
    total_cleaned = 0
    for p in projects:
        if prune_project(p, force=False):
            total_cleaned += 1
            
    print(f"\nGarbage Collection Complete. Cleaned {total_cleaned} projects.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "prune":
            if len(sys.argv) > 2:
                prune_project(sys.argv[2], force=True)
            else:
                run_gc_all()
        elif cmd == "restore":
            if len(sys.argv) > 2:
                restore_project(sys.argv[2])
            else:
                print("Error: Please specify the project name to restore.")
        else:
            print(f"Error: Unknown command '{cmd}'")
    else:
        run_gc_all()
