#!/usr/bin/env python3
"""
The script behind "Update Photos.command" — the one thing to double-click
after dropping new photos into an import/ folder and/or reordering
existing photos in Import/Portfolio/.

For each category (Home/People/Places/Things):
  1. Look in Import/Portfolio/<Category>/import/ for new .jpg files.
  2. Sort them by their (1), (2), (3)... prefix.
  3. Move each one into Import/Portfolio/<Category>/, renumbered to
     continue after whatever's already there (e.g. if the category
     already goes up to 14_..., new photos become 15_, 16_, 17_...).
     Files are MOVED, not copied — import/ ends up empty again.
  4. Never overwrites an existing file; skips with a warning instead.

Then it runs sync_galleries.py to resize everything and rewrite the
website's photo grids to match.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ["Home", "People", "Places", "Things"]

IMPORT_NUM_RE = re.compile(r"^\((\d+)\)_?")
EXISTING_NUM_RE = re.compile(r"^(\d+)_")
PHOTO_EXTS = (".jpg", ".jpeg")


def existing_max(category_dir: Path) -> int:
    max_n = 0
    for f in category_dir.iterdir():
        if f.is_dir() or f.name == "captions.json":
            continue
        m = EXISTING_NUM_RE.match(f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n


def import_sort_key(f: Path):
    m = IMPORT_NUM_RE.match(f.name)
    if m:
        return (0, int(m.group(1)), f.name)
    return (1, 0, f.name)


def process_category(category: str) -> int:
    category_dir = ROOT / "Import" / "Portfolio" / category
    import_dir = category_dir / "import"
    category_dir.mkdir(parents=True, exist_ok=True)
    import_dir.mkdir(parents=True, exist_ok=True)

    all_import_files = [f for f in import_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
    pending = sorted(
        (f for f in all_import_files if f.suffix.lower() in PHOTO_EXTS),
        key=import_sort_key,
    )

    for f in all_import_files:
        if f.suffix.lower() not in PHOTO_EXTS:
            print(f"  NOTE: {category}/import/{f.name} isn't a .jpg file — leaving it there, not imported")

    if not pending:
        return 0

    next_n = existing_max(category_dir) + 1
    moved = 0
    for f in pending:
        m = IMPORT_NUM_RE.match(f.name)
        core = f.name[m.end():] if m else f.name
        dest_name = f"{next_n:02d}_{core}"
        dest = category_dir / dest_name
        if dest.exists():
            print(f"  SKIPPED {category}/import/{f.name}: {dest_name} already exists — check manually")
            continue
        f.rename(dest)
        print(f"  {category}/import/{f.name}  ->  {category}/{dest_name}")
        next_n += 1
        moved += 1

    return moved


def main():
    sys.stdout.reconfigure(line_buffering=True)
    print("Checking import folders...")
    total = 0
    for category in CATEGORIES:
        total += process_category(category)

    if total == 0:
        print("No new photos found in any import folder.")
    else:
        print(f"\nImported {total} new photo(s).")

    print("\nSyncing galleries (resizing photos, updating the website)...")
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_galleries.py")])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
