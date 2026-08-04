#!/usr/bin/env python3
"""
Regenerates the Personal page's post feed from Import/Personal/posts.json.

Each post's source photos live in Import/Personal/posts/<id>/. Run this
after adding/editing/reordering posts.json (the admin app does this for
you, but it can also be run by hand):

  python3 scripts/sync_posts.py

This OVERWRITES everything between <!-- POSTS:START --> and
<!-- POSTS:END --> in personal.html, and regenerates the resized images
in images/personal/. Nothing outside those markers is touched (the
portrait hero and intro line stay exactly as they are). Source photos
in Import/Personal/ are never modified.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSONAL_SRC = ROOT / "Import" / "Personal"
POSTS_JSON = PERSONAL_SRC / "posts.json"
GRID_DIR = ROOT / "images" / "personal"
LARGE_DIR = GRID_DIR / "large"
PAGE_PATH = ROOT / "personal.html"
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


def load_posts():
    if not POSTS_JSON.exists():
        return []
    return json.loads(POSTS_JSON.read_text())


def sync():
    posts = load_posts()

    # Clear previously generated post images so deletions are respected.
    # Portrait and any non-"post-*" files are left alone.
    for old in GRID_DIR.glob("post-*.jpg"):
        old.unlink()
    for old in LARGE_DIR.glob("post-*.jpg"):
        old.unlink()

    articles = []
    for post in posts:
        pid = post["id"]
        photos = post.get("photos", [])
        alts = post.get("alts", [])
        src_dir = PERSONAL_SRC / "posts" / str(pid)

        photo_blocks = []
        for i, fname in enumerate(photos, start=1):
            src = src_dir / fname
            if not src.exists():
                print(f"WARNING: post {pid} photo missing: {src}")
                continue
            dest_name = f"post-{pid}-{i:02d}.jpg"
            run_sips(src, GRID_DIR / dest_name, GRID_SIZE, GRID_QUALITY)
            run_sips(src, LARGE_DIR / dest_name, LARGE_SIZE, LARGE_QUALITY)
            alt = alts[i - 1] if i - 1 < len(alts) else post.get("title", "Personal photo")
            photo_blocks.append(
                f'  <div class="post-photo">\n'
                f'    <img src="images/personal/{dest_name}" '
                f'data-large="images/personal/large/{dest_name}" '
                f'alt="{alt}" loading="lazy">\n'
                f'  </div>'
            )

        body = "\n".join(photo_blocks)
        articles.append(
            '<article class="post">\n'
            f'{body}\n'
            '  <div class="post-body">\n'
            f'    <div class="post-date">{post.get("date", "")}</div>\n'
            f'    <h2>{post.get("title", "")}</h2>\n'
            f'    {post.get("body_html", "")}\n'
            '  </div>\n'
            '</article>'
        )

    if articles:
        block = "\n\n".join(articles)
    else:
        block = '<div class="coming-soon">\n  <p>More updates coming soon.</p>\n</div>'

    content = PAGE_PATH.read_text()
    pattern = re.compile(
        r"(<!-- POSTS:START -->\n).*(\n<!-- POSTS:END -->)", re.S
    )
    if not pattern.search(content):
        print("WARNING: no POSTS markers found in personal.html, skipping")
        return
    new_content = pattern.sub(lambda m: m.group(1) + block + m.group(2), content)
    PAGE_PATH.write_text(new_content)

    print(f"Personal: {len(posts)} post(s) -> personal.html")


if __name__ == "__main__":
    sys.exit(sync())
