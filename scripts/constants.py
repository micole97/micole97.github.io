"""Shared constants for the photo-management scripts and the admin app.

Single source of truth for the category list and which file extensions
count as a photo — keeping these in one place avoids the kind of drift
that once caused .jpeg uploads to be silently skipped during resizing.
"""

CATEGORIES = ["Home", "People", "Places", "Things"]
PHOTO_EXTS = (".jpg", ".jpeg")
