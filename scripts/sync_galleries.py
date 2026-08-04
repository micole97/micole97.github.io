#!/usr/bin/env python3
"""
Regenerates the Home/People/Places/Things galleries from whatever photos
are currently sitting in Import/Portfolio/<Category>/.

Home is the small curated highlights grid on the homepage (index.html) —
it works exactly like the other categories, just with its own folder.

Workflow for adding/removing/reordering photos:
  - Add a photo:    drop the file into Import/Portfolio/<Category>/
  - Remove a photo:  delete it from that folder
  - Reorder photos:  rename files so they sort in the order you want
                      (e.g. 01_..., 02_..., 03_...)
  - Custom captions: edit captions.json inside that category folder,
                      mapping the exact filename to alt text. Photos not
                      listed there get a generic default.

Then run:  python3 scripts/sync_galleries.py

This OVERWRITES everything between the <!-- GALLERY:START --> and
<!-- GALLERY:END --> markers in people.html / places.html / things.html,
and regenerates the resized images in images/<category>/ and
images/<category>/large/. Nothing outside those markers is touched, and
the original photos in Import/Portfolio/ are never modified.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ["Home", "People", "Places", "Things"]
PHOTO_EXTS = (".jpg", ".jpeg")
COMING_SOON_LABEL = {"Things": "Product", "Home": "Featured"}
COMING_SOON_TEXT = {"Things": "Coming soon."}
PAGE_FILENAME = {"Home": "index.html"}
GRID_SIZE = 2200
GRID_QUALITY = "75"
LARGE_SIZE = 4200
LARGE_QUALITY = "88"


def run_sips(src: Path, out: Path, max_dim: int, quality: str):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["sips", "-Z", str(max_dim), "-s", "format", "jpeg",
         "-s", "formatOptions", quality, str(src), "--out", str(out)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def sync_category(category: str):
    slug = category.lower()
    src_dir = ROOT / "Import" / "Portfolio" / category
    grid_dir = ROOT / "images" / slug
    large_dir = ROOT / "images" / slug / "large"
    page_path = ROOT / PAGE_FILENAME.get(category, f"{slug}.html")

    grid_dir.mkdir(parents=True, exist_ok=True)
    large_dir.mkdir(parents=True, exist_ok=True)

    # Clear previously generated files so deletions/reorders are respected.
    for old in grid_dir.glob(f"{slug}-*.jpg"):
        old.unlink()
    for old in large_dir.glob(f"{slug}-*.jpg"):
        old.unlink()

    captions = {}
    captions_path = src_dir / "captions.json"
    if captions_path.exists():
        captions = json.loads(captions_path.read_text())

    photos = []
    if src_dir.exists():
        photos = sorted(
            p for p in src_dir.iterdir()
            if p.suffix.lower() in PHOTO_EXTS and p.name != "captions.json"
        )

    figures = []
    for i, src in enumerate(photos, start=1):
        nn = f"{i:02d}"
        dest_name = f"{slug}-{nn}.jpg"
        run_sips(src, grid_dir / dest_name, GRID_SIZE, GRID_QUALITY)
        run_sips(src, large_dir / dest_name, LARGE_SIZE, LARGE_QUALITY)
        alt = captions.get(src.name, f"{category} photograph {i}")
        figures.append(
            f'  <figure><img src="images/{slug}/{dest_name}" '
            f'data-large="images/{slug}/large/{dest_name}" '
            f'alt="{alt}" loading="lazy"></figure>'
        )

    if figures:
        block = '<div class="gallery">\n' + "\n".join(figures) + "\n</div>"
    else:
        if category in COMING_SOON_TEXT:
            text = COMING_SOON_TEXT[category]
        else:
            label = COMING_SOON_LABEL.get(category, category)
            text = f"{label} photography coming soon."
        block = (
            '<div class="coming-soon">\n'
            f"  <p>{text}</p>\n"
            "</div>"
        )

    content = page_path.read_text()
    pattern = re.compile(
        r"(<!-- GALLERY:START -->\n).*(\n<!-- GALLERY:END -->)", re.S
    )
    if not pattern.search(content):
        print(f"WARNING: no GALLERY markers found in {page_path.name}, skipping")
        return
    new_content = pattern.sub(lambda m: m.group(1) + block + m.group(2), content)
    page_path.write_text(new_content)

    print(f"{category}: {len(photos)} photo(s) -> {page_path.name}")


def main():
    for category in CATEGORIES:
        sync_category(category)
    print("Sync complete.")


if __name__ == "__main__":
    sys.exit(main())
