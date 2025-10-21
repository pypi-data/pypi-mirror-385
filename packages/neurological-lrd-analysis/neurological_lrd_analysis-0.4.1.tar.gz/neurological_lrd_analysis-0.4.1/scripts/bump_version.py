#!/usr/bin/env python3
"""
Version bumping script for Neurological LRD Analysis

This script helps bump the version number across all relevant files
when creating a new release.

Usage:
    python scripts/bump_version.py 0.4.1
"""

import sys
import re
from pathlib import Path

def update_file_version(file_path: Path, old_version: str, new_version: str):
    """Update version in a file."""
    if not file_path.exists():
        return False
    
    content = file_path.read_text()
    updated_content = content.replace(old_version, new_version)
    
    if content != updated_content:
        file_path.write_text(updated_content)
        print(f"✓ Updated {file_path}")
        return True
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <new_version>")
        print("Example: python scripts/bump_version.py 0.4.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("Error: Version must be in format X.Y.Z (e.g., 0.4.1)")
        sys.exit(1)
    
    # Files to update
    files_to_update = [
        Path("pyproject.toml"),
        Path("setup.py"),
        Path("neurological_lrd_analysis/__init__.py"),
        Path("docs/source/conf.py"),
    ]
    
    # Extract current version from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        version_match = re.search(r'version = "([^"]+)"', content)
        if version_match:
            old_version = version_match.group(1)
            print(f"Current version: {old_version}")
            print(f"New version: {new_version}")
        else:
            print("Error: Could not find current version in pyproject.toml")
            sys.exit(1)
    else:
        print("Error: pyproject.toml not found")
        sys.exit(1)
    
    # Update files
    updated_files = 0
    for file_path in files_to_update:
        if update_file_version(file_path, old_version, new_version):
            updated_files += 1
    
    print(f"\n✓ Updated {updated_files} files with version {new_version}")
    print("\nNext steps:")
    print("1. Review the changes")
    print("2. Commit the changes: git add . && git commit -m 'Bump version to {new_version}'")
    print("3. Create a tag: git tag v{new_version}")
    print("4. Push to GitHub: git push origin main --tags")

if __name__ == "__main__":
    main()
