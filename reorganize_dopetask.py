#!/usr/bin/env python3
"""
Reorganize dopeTask from flat src/ to proper src/dopetask/ package structure.
Part of the early dopeTask package migration.
"""
import os
import shutil
from pathlib import Path

def main():
    repo_root = Path("/Users/hue/code/dopeTask")
    src = repo_root / "src"
    dopetask_pkg = src / "dopetask"
    
    # Create src/dopetask if it doesn't exist
    dopetask_pkg.mkdir(exist_ok=True)
    print(f"✓ Created {dopetask_pkg}")
    
    # Move top-level Python files into src/dopetask/
    files_to_move = [
        "__init__.py",
        "__main__.py", 
        "cli.py",
        "doctor.py",
        "ci_gate.py",
    ]
    
    for fname in files_to_move:
        src_file = src / fname
        dest_file = dopetask_pkg / fname
        if src_file.exists() and not dest_file.exists():
            shutil.move(str(src_file), str(dest_file))
            print(f"✓ Moved {fname} → dopetask/{fname}")
        elif dest_file.exists():
            print(f"  Skip {fname} (already exists in dopetask/)")
        else:
            print(f"⚠ Skip {fname} (not found)")
    
    # Move subdirectories into src/dopetask/
    dirs_to_move = ["utils", "schemas", "pipeline"]
    
    for dirname in dirs_to_move:
        src_dir = src / dirname
        dest_dir = dopetask_pkg / dirname
        if src_dir.exists() and not dest_dir.exists():
            shutil.move(str(src_dir), str(dest_dir))
            print(f"✓ Moved {dirname}/ → dopetask/{dirname}/")
        elif dest_dir.exists():
            print(f"  Skip {dirname}/ (already exists in dopetask/)")
        else:
            print(f"⚠ Skip {dirname}/ (not found)")
    
    # dopetask_adapters stays as separate package (already correctly namespaced)
    print("\n✓ dopetask_adapters remains at src/dopetask_adapters/")
    
    print("\n✓ Package restructure complete")
    print(f"\nNew structure:")
    for root, dirs, files in os.walk(dopetask_pkg):
        level = root.replace(str(dopetask_pkg), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in sorted(files)[:5]:  # Show first 5 files per dir
            print(f'{subindent}{file}')
        if len(files) > 5:
            print(f'{subindent}... and {len(files) - 5} more')

if __name__ == "__main__":
    main()
