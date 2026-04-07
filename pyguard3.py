import os
import subprocess
import sys

# --- CONFIGURATION ---
TARGET_DIRS = ["/usr", "/bin", "/lib", "/etc", "/opt"]
LOG_FILE = "guardian_verbose_report.txt"
VT_PATH = "/usr/bin/vt"
VERBOSE = True  # Set to False to silence the per-file output

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
            # Only need to check the first bit of the file
            return b'\0' in f.read(1024)
    except Exception:
        return False

def run_audit():
    results = {
        "reinstall_queue": set(),
        "orphan_binaries": [],
        "broken_files": []
    }

    print(f"🔍 Starting verbose scan on: {', '.join(TARGET_DIRS)}")
    
    file_count = 0
    for target in TARGET_DIRS:
        if not os.path.exists(target):
            print(f"⚠️  Skipping {target}: Directory not found.")
            continue
            
        for root, _, files in os.walk(target):
            for file in files:
                full_path = os.path.join(root, file)
                
                # --- TOUGHNESS UPGRADE: Handle missing/locked files ---
                try:
                    # Check if file exists and isn't a broken symlink
                    if not os.path.lexists(full_path):
                        continue
                    
                    size = os.path.getsize(full_path)
                    file_count += 1
                    
                    # Verbose Output
                    if VERBOSE:
                        sys.stdout.write(f"\r[FILE {file_count}] Checking: {full_path[:60]}...")
                        sys.stdout.flush()

                    # LOGIC 1: Identify Empty System Files (Corruption Check)
                    if size == 0:
                        owner = get_pacman_owner(full_path)
                        if owner:
                            if VERBOSE: print(f"\n[!] EMPTY FILE DETECTED: {full_path} (Owner: {owner})")
                            results["reinstall_queue"].add(owner)
                            results["broken_files"].append(full_path)
                    
                    # LOGIC 2: Identify Hidden Binaries (Security Check)
                    if file.startswith('.') and is_binary(full_path):
                        owner = get_pacman_owner(full_path)
                        if not owner:
                            if VERBOSE: print(f"\n[X] UNTRACKED HIDDEN BINARY: {full_path}")
                            results["orphan_binaries"].append(full_path)
                            
                except (FileNotFoundError, PermissionError):
                    # Silently skip files that disappear or are locked
                    continue
                except Exception as e:
                    if VERBOSE: print(f"\n⚠️  Error accessing {full_path}: {e}")
                    continue

    print(f"\n\n✅ Scan Complete. Inspected {file_count} files.")
    
    # Write findings to log file
    with open(LOG_FILE, "w") as f:
        f.write(f"Guardian Audit Report\n{'='*20}\n")
        f.write(f"Broken Files: {results['broken_files']}\n")
        f.write(f"Orphan Binaries: {results['orphan_binaries']}\n")
        f.write(f"Packages to Reinstall: {list(results['reinstall_queue'])}\n")

    return results

def heal_system(pkg_list):
    if not pkg_list:
        print("✅ No broken packages to reinstall.")
        return

    print(f"\n🛠️  HEALING PHASE: Reinstalling {len(pkg_list)} packages...")
    for pkg in pkg_list:
        print(f"   -> Reinstalling: {pkg}")
        subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', pkg])

def scan_threats(orphans):
    if not orphans:
        print("✅ No suspicious orphan binaries found.")
        return

    print(f"\n🛡️  SECURITY PHASE: Found {len(orphans)} untracked hidden binaries.")
    choice = input("Send these to VirusTotal for analysis? (y/n): ")
    if choice.lower() == 'y':
        for path in orphans:
            if os.path.exists(path):
                print(f"🚀 Uploading to VT: {path}")
                subprocess.run([VT_PATH, "scan", "file", path])

if __name__ == "__main__":
    # Ensure root privileges
    if os.geteuid() != 0:
        print("❌ Error: This script must be run with sudo.")
        sys.exit(1)

    # 1. Run Audit
    data = run_audit()
    
    # 2. Heal the Arch System
    heal_system(list(data["reinstall_queue"]))
    
    # 3. Security Scan
    scan_threats(data["orphan_binaries"])

    print(f"\n✨ Guardian task complete. Report saved to: {LOG_FILE}")
