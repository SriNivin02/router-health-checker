"""Creates router-health-checker.zip containing the entire project cleanly."""
import os
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ZIP_OUT = BASE_DIR.parent / "router-health-checker.zip"

EXCLUDE_DIRS = {".venv", "venv", "env", "__pycache__", ".pytest_cache", ".git", "data"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".log", ".zip"}

def create_zip():
    print(f"Packaging {BASE_DIR} into {ZIP_OUT}...")
    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDE_EXTS or file.startswith(".env"):
                    if file != ".env.example":
                        continue
                full_path = Path(root) / file
                arc_name = Path("router-health-checker") / full_path.relative_to(BASE_DIR)
                zf.write(full_path, arc_name)
                print(f"Added: {arc_name}")
                
    print(f"\nSuccessfully created: {ZIP_OUT}")
    print(f"Size: {ZIP_OUT.stat().st_size / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    create_zip()
