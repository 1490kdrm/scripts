import os
import subprocess
import sys
try:
    from tqdm import tqdm
except ImportError:
    print("⚠️  tqdm not found. Install with: sudo pacman -S python-tqdm")
    sys.exit(1)

# --- CONFIGURATION ---
TARGET_DIRS = ["/usr", "/bin", "/lib", "/etc", "/opt"]
LOG_FILE = "guardian_verbose_report.txt"
VT_PATH = "/usr/bin/vt"

# ANSI Color Codes
RED = "\033[91m"
RESET = "\033[0m"

def get_pacman_owner(path):
    """Returns the package name owning the file, or None if orphaned."""
    try:
        result = subprocess.run(['pacman', '-Qqo', path], 
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def is_binary(path):
    """Check for null bytes to identify binary data."""
    try:
        if not os.path.isfile(path) or os.path.getsize(path) == 0: 
            return False 
        with open(path, 'rb') as f:
            return b'\0' in f.read(1024)
    except Exception:
        return False

def run_audit():
    results = {
        "reinstall_queue": set(),
        "orphan_binaries": [],
        "broken_files": []
    }

    print("📊 Calculating total files (Pre-scan)...")
    total_files = 0
    valid_paths = [d for d in TARGET_DIRS if os.path.exists(d)]
    for target in valid_paths:
        for _, _, files in os.walk(target):
            total_files += len(files)

    print(f"🔍 Starting scan on {total_files} files across: {', '.join(valid_paths)}")
    
    with tqdm(total=total_files, desc="Auditing System", unit="file", leave=True) as pbar:
        for target in valid_paths:
            for root, _, files in os.walk(target):
                for file in files:
                    full_path = os.path.join(root, file)
                    pbar.update(1)
                    
                    try:
                        if not os.path.lexists(full_path):
                            continue
                        
                        size = os.path.getsize(full_path)

                        if size == 0:
                            owner = get_pacman_owner(full_path)
                            if owner:
                                tqdm.write(f"\n[!] EMPTY FILE: {full_path} (Owner: {owner})")
                                results["reinstall_queue"].add(owner)
                                results["broken_files"].append(full_path)
                        
                        if file.startswith('.') and is_binary(full_path):
                            owner = get_pacman_owner(full_path)
                            if not owner:
                                tqdm.write(f"{RED}\n[X] UNTRACKED HIDDEN BINARY: {full_path}{RESET}")
                                results["orphan_binaries"].append(full_path)
                                
                    except (FileNotFoundError, PermissionError):
                        continue
                    except Exception:
                        continue

    with open(LOG_FILE, "w") as f:
        f.write("Guardian Audit Report\n" + "="*20 + "\n")
        f.write(f"Broken Files: {results['broken_files']}\n")
        f.write(f"Orphan Binaries: {results['orphan_binaries']}\n")
        f.write(f"Packages to Reinstall: {list(results['reinstall_queue'])}\n")

    return results

def heal_system(pkg_list):
    if not pkg_list:
        print("\n✅ No broken packages to reinstall.")
        return

    print(f"\n🛠️  HEALING PHASE: Reinstalling {len(pkg_list)} packages...")
    for pkg in pkg_list:
        print(f"   -> Reinstalling: {pkg}")
        subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', pkg])

def scan_threats(orphans):
    if not orphans:
        print("\n✅ No suspicious orphan binaries found.")
        return

    print(f"\n🛡️  SECURITY PHASE: Found {len(orphans)} untracked hidden binaries.")
    choice = input("Send these to VirusTotal for analysis? (y/n): ")
    if choice.lower() == 'y':
        for path in orphans:
            if os.path.exists(path):
                print(f"🚀 Uploading to VT: {path}")
                subprocess.run([VT_PATH, "scan", "file", path])

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{RED}❌ Error: This script must be run with sudo.{RESET}")
        sys.exit(1)

    data = run_audit()
    heal_system(list(data["reinstall_queue"]))
    scan_threats(data["orphan_binaries"])

    print(f"\n✨ Task complete. Report: {LOG_FILE}")
