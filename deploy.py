import os
import shutil
import subprocess
import sys
import time

# Config
BASE_URL = "/Anidle/"
COMMIT_MSG = "Auto deploy: Update Web App"

def run_command(command, cwd=None, ignore_errors=False):
    """Run a shell command and print output."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=True, 
            check=not ignore_errors,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            print(f"Error running command: {e}")
            sys.exit(1)
        return False

def main():
    print("=== Starting Auto Deployment ===")
    
    # 1. Clean
    print("\n[1/4] Cleaning old build folders...")
    if os.path.exists("docs"):
        try:
            shutil.rmtree("docs")
            print("  Deleted 'docs' folder.")
        except Exception as e:
            print(f"  Error deleting docs: {e}")
            sys.exit(1)
            
    if os.path.exists("dist"):
        try:
            shutil.rmtree("dist")
            print("  Deleted 'dist' folder.")
        except Exception as e:
            print(f"  Error deleting dist: {e}")
            sys.exit(1)

    # 2. Build
    print("\n[2/4] Building Flet app...")
    # Using python -m flet to ensure we use the same python env
    success = run_command(f"flet publish main.py --base-url {BASE_URL}")
    if not success:
        print("Build failed.")
        sys.exit(1)

    # 3. Rename
    print("\n[3/4] Packaging...")
    if os.path.exists("dist"):
        try:
            os.rename("dist", "docs")
            print("  Renamed 'dist' to 'docs'.")
        except Exception as e:
            print(f"  Error renaming dist: {e}")
            sys.exit(1)
    else:
        print("Error: 'dist' folder not found after build.")
        sys.exit(1)

    # 4. Git Push
    print("\n[4/4] Pushing to GitHub...")
    run_command("git add .")
    run_command(f'git commit -m "{COMMIT_MSG}"', ignore_errors=True) # Ignore if nothing to commit
    
    print("Pushing... (This might take a few seconds)")
    success = run_command("git push")
    
    if success:
        print("\n✅ Deployment Complete!")
        print(f"Visit: https://rc0824.github.io{BASE_URL}")
        print("(Remember to Hard Reload Ctrl+F5 if you don't see changes immediately)")
    else:
        print("\n❌ Git Push Failed. Please check your git configuration.")

if __name__ == "__main__":
    main()
