#!/usr/bin/env python3
"""
Local admin app for managing the photography site. Runs on localhost
only — launch via the "Admin Portal.command" file at the project root,
or `python3 admin/app.py` from a terminal. Never exposed to the internet.

Wraps the existing scripts/ logic (sync_galleries.py, update_photos.py,
sync_posts.py) instead of replacing it, so the Drop Zone / captions.json
/ posts.json conventions stay the source of truth.
"""

import itertools
import json
import re
import subprocess
import sys
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sync_galleries  # noqa: E402
import update_photos  # noqa: E402
import sync_posts  # noqa: E402
from constants import CATEGORIES as CATEGORY_NAMES, PHOTO_EXTS  # noqa: E402

app = Flask(__name__)
app.secret_key = "local-admin-only"  # never exposed off localhost

CATEGORIES = {name.lower(): name for name in CATEGORY_NAMES}
EXISTING_NUM_RE = re.compile(r"^(\d+)_")


# ---------- helpers ----------

def category_dir(category: str) -> Path:
    return ROOT / "Import" / "Portfolio" / category


def load_captions(category: str) -> dict:
    p = category_dir(category) / "captions.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}


def save_captions(category: str, captions: dict):
    p = category_dir(category) / "captions.json"
    p.write_text(json.dumps(captions, indent=2, ensure_ascii=False) + "\n")


def list_photos(category: str):
    d = category_dir(category)
    if not d.exists():
        return []
    return sorted(
        p.name for p in d.iterdir()
        if p.suffix.lower() in PHOTO_EXTS
    )


def next_dropzone_index(category: str) -> int:
    dz = category_dir(category) / update_photos.DROP_ZONE_NAME
    dz.mkdir(parents=True, exist_ok=True)
    existing = [f for f in dz.iterdir() if f.is_file() and not f.name.startswith(".")]
    n = 0
    for f in existing:
        m = update_photos.IMPORT_NUM_RE.match(f.name)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def load_posts():
    p = ROOT / "Import" / "Personal" / "posts.json"
    if p.exists():
        return json.loads(p.read_text())
    return []


def save_posts(posts):
    p = ROOT / "Import" / "Personal" / "posts.json"
    p.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n")


def next_post_id(posts):
    return max((p["id"] for p in posts), default=0) + 1


# ---------- routes: dashboard ----------

@app.route("/")
def dashboard():
    counts = {slug: len(list_photos(name)) for slug, name in CATEGORIES.items()}
    posts = load_posts()
    return render_template("dashboard.html", categories=CATEGORIES, counts=counts, post_count=len(posts))


@app.route("/site-images/<path:filename>")
def site_images(filename):
    return send_from_directory(ROOT / "images", filename)


# ---------- routes: photo categories ----------

def require_category(view):
    """Validates the <slug> URL param and injects the matching category name."""
    @wraps(view)
    def wrapper(**kwargs):
        slug = kwargs.get("slug")
        if slug not in CATEGORIES:
            return "Unknown category", 404
        kwargs["category"] = CATEGORIES[slug]
        return view(**kwargs)
    return wrapper


@app.route("/category/<slug>")
@require_category
def category_view(slug, category):
    captions = load_captions(category)
    photos = list_photos(category)
    photo_rows = [
        {
            "filename": f,
            "thumb": f"{slug}/{slug}-{i:02d}.jpg",
            "alt": captions.get(f, ""),
        }
        for i, f in enumerate(photos, start=1)
    ]
    return render_template("category.html", slug=slug, category=category, photos=photo_rows)


@app.route("/category/<slug>/upload", methods=["POST"])
@require_category
def category_upload(slug, category):
    files = request.files.getlist("photos")
    dz = category_dir(category) / update_photos.DROP_ZONE_NAME
    dz.mkdir(parents=True, exist_ok=True)
    n = next_dropzone_index(category)
    saved = 0
    for f in files:
        if not f.filename:
            continue
        ext = Path(f.filename).suffix.lower()
        if ext not in PHOTO_EXTS:
            flash(f"Skipped {f.filename}: not a .jpg file")
            continue
        dest = dz / f"({n})_{Path(f.filename).name}"
        f.save(dest)
        n += 1
        saved += 1
    if saved:
        update_photos.process_category(category)
        sync_galleries.sync_category(category)
        flash(f"Added {saved} photo(s).")
    return redirect(url_for("category_view", slug=slug))


@app.route("/category/<slug>/reorder", methods=["POST"])
@require_category
def category_reorder(slug, category):
    new_order = request.form.getlist("order")  # list of original filenames, new order
    d = category_dir(category)
    # Rename in two passes to avoid collisions when shuffling numbers.
    temp_names = []
    for f in new_order:
        src = d / f
        tmp = d / f".tmp__{f}"
        src.rename(tmp)
        temp_names.append((tmp, f))
    for i, (tmp, original) in enumerate(temp_names, start=1):
        m = EXISTING_NUM_RE.match(original)
        core = original[m.end():] if m else original
        dest = d / f"{i:02d}_{core}"
        tmp.rename(dest)
    sync_galleries.sync_category(category)
    flash("Order updated.")
    return redirect(url_for("category_view", slug=slug))


@app.route("/category/<slug>/delete/<path:filename>", methods=["POST"])
@require_category
def category_delete(slug, filename, category):
    f = category_dir(category) / filename
    if f.exists():
        f.unlink()
    captions = load_captions(category)
    if filename in captions:
        del captions[filename]
        save_captions(category, captions)
    sync_galleries.sync_category(category)
    flash(f"Deleted {filename}.")
    return redirect(url_for("category_view", slug=slug))


@app.route("/category/<slug>/caption/<path:filename>", methods=["POST"])
@require_category
def category_caption(slug, filename, category):
    alt = request.form.get("alt", "").strip()
    captions = load_captions(category)
    if alt:
        captions[filename] = alt
    elif filename in captions:
        del captions[filename]
    save_captions(category, captions)
    sync_galleries.sync_category(category)
    return redirect(url_for("category_view", slug=slug))


# ---------- routes: personal posts ----------

@app.route("/posts")
def posts_list():
    posts = load_posts()
    for p in posts:
        p["thumb"] = f"personal/post-{p['id']}-01.jpg" if p.get("photos") else None
    return render_template("posts_list.html", posts=posts)


@app.route("/posts/reorder", methods=["POST"])
def posts_reorder():
    order = [int(x) for x in request.form.getlist("order")]
    posts = load_posts()
    by_id = {p["id"]: p for p in posts}
    posts = [by_id[i] for i in order if i in by_id]
    save_posts(posts)
    sync_posts.sync()
    flash("Post order updated.")
    return redirect(url_for("posts_list"))


@app.route("/posts/new", methods=["GET", "POST"])
def post_new():
    if request.method == "GET":
        return render_template("post_form.html", post=None)

    posts = load_posts()
    pid = next_post_id(posts)
    post_dir = ROOT / "Import" / "Personal" / "posts" / str(pid)
    post_dir.mkdir(parents=True, exist_ok=True)

    photos, alts = [], []
    for f, alt in itertools.zip_longest(
        request.files.getlist("photos"), request.form.getlist("photo_alts"), fillvalue=""
    ):
        if not f or not f.filename:
            continue
        dest = post_dir / Path(f.filename).name
        f.save(dest)
        photos.append(dest.name)
        alts.append((alt or "").strip())

    post = {
        "id": pid,
        "date": request.form.get("date", "").strip(),
        "title": request.form.get("title", "").strip(),
        "body_html": sanitize_html(request.form.get("body_html", "")),
        "photos": photos,
        "alts": alts,
    }
    posts.append(post)
    save_posts(posts)
    sync_posts.sync()
    flash("Post created.")
    return redirect(url_for("posts_list"))


@app.route("/posts/<int:pid>/edit", methods=["GET", "POST"])
def post_edit(pid):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == pid), None)
    if post is None:
        return "Post not found", 404

    if request.method == "GET":
        existing = [
            {
                "filename": fname,
                "alt": post.get("alts", [])[i] if i < len(post.get("alts", [])) else "",
                "thumb": f"personal/post-{pid}-{i + 1:02d}.jpg",
            }
            for i, fname in enumerate(post.get("photos", []))
        ]
        return render_template("post_form.html", post=post, existing=existing)

    post_dir = ROOT / "Import" / "Personal" / "posts" / str(pid)
    post_dir.mkdir(parents=True, exist_ok=True)

    delete_set = set(request.form.getlist("delete_photos"))
    kept_photos, kept_alts = [], []
    for fname, alt in zip(
        request.form.getlist("existing_filename"), request.form.getlist("existing_alt")
    ):
        if fname in delete_set:
            f = post_dir / fname
            if f.exists():
                f.unlink()
        else:
            kept_photos.append(fname)
            kept_alts.append(alt.strip())

    for f, alt in itertools.zip_longest(
        request.files.getlist("photos"), request.form.getlist("photo_alts"), fillvalue=""
    ):
        if not f or not f.filename:
            continue
        dest = post_dir / Path(f.filename).name
        f.save(dest)
        kept_photos.append(dest.name)
        kept_alts.append((alt or "").strip())

    post["date"] = request.form.get("date", "").strip()
    post["title"] = request.form.get("title", "").strip()
    post["body_html"] = sanitize_html(request.form.get("body_html", ""))
    post["photos"] = kept_photos
    post["alts"] = kept_alts

    save_posts(posts)
    sync_posts.sync()
    flash("Post updated.")
    return redirect(url_for("posts_list"))


@app.route("/posts/<int:pid>/delete", methods=["POST"])
def post_delete(pid):
    posts = load_posts()
    posts = [p for p in posts if p["id"] != pid]
    save_posts(posts)
    post_dir = ROOT / "Import" / "Personal" / "posts" / str(pid)
    if post_dir.exists():
        for f in post_dir.iterdir():
            f.unlink()
        post_dir.rmdir()
    sync_posts.sync()
    flash("Post deleted.")
    return redirect(url_for("posts_list"))


def sanitize_html(html: str) -> str:
    # Local single-user tool, but strip script tags defensively.
    return re.sub(r"<script.*?>.*?</script>", "", html, flags=re.I | re.S)


# ---------- publish ----------

def git_ahead_count() -> int:
    result = subprocess.run(
        ["git", "rev-list", "--count", "origin/main..HEAD"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        return 0
    return int(result.stdout.strip() or 0)


@app.route("/publish")
def publish():
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True
    ).stdout
    ahead = git_ahead_count()
    return render_template("publish.html", status=status, ahead=ahead)


@app.route("/publish/save", methods=["POST"])
def publish_save():
    message = request.form.get("message", "").strip() or "Update site content"
    subprocess.run(["git", "add", "-A"], cwd=ROOT)
    result = subprocess.run(
        ["git", "commit", "-m", message], cwd=ROOT, capture_output=True, text=True
    )
    flash(result.stdout + result.stderr)
    return redirect(url_for("publish"))


@app.route("/publish/push", methods=["POST"])
def publish_push():
    result = subprocess.run(
        ["git", "push", "origin", "main"], cwd=ROOT, capture_output=True, text=True
    )
    if result.returncode == 0:
        flash("Published — live in a minute or two.")
    else:
        flash("Publish failed: " + result.stderr)
    return redirect(url_for("publish"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5151, debug=True)
