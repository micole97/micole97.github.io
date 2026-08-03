# Website Maintenance — Updating Photos

This covers how to add, remove, reorder, and caption photos on the site,
including the homepage highlights. No coding required, and nothing here
needs Claude — everything is done in Finder plus one double-click.

## The short version

1. Drop new full-size photos into the right **Drop Zone** folder (see below).
2. Number them `(1)`, `(2)`, `(3)`... in the order you want them added.
3. Double-click **`Update Photos.command`** (in the main website folder).
4. Reorder anything if needed (see "Reordering photos"), then double-click again.

## Where photos live

- `Import/Portfolio/Home/` — the curated photos on the homepage.
- `Import/Portfolio/People/` — everything on the People page.
- `Import/Portfolio/Places/` — everything on the Places page.
- `Import/Portfolio/Things/` — everything on the Things page (empty until you shoot product work).
- Each of those has a **`Drop Zone` subfolder** — this is where new photos go.

These folders hold your **original, full-quality photos**. The website never
uses these directly — it uses smaller, web-friendly copies that get
automatically generated from them (see "How this works" below).

## Adding a photo

1. Drop the full-size file into the `Drop Zone` subfolder of the right
   category (e.g. `Import/Portfolio/People/Drop Zone/`).
2. Make sure its filename starts with `(1)`, `(2)`, `(3)`, etc. — this
   just controls the order *among the new photos you're adding right now*.
   If you're only adding one photo, `(1)` is fine.
3. Double-click **`Update Photos.command`**.

That's it — the photo gets moved out of `Drop Zone` into the real category
folder (renumbered to continue after whatever's already there), resized,
and added to the live site. A Terminal window will pop up and print what
it did; press Enter to close it when you're done reading.

## Removing a photo

Delete the file from its category folder (not `Drop Zone` — the main
folder). Then double-click `Update Photos.command`.

## Reordering photos

Photos display in the order their filenames sort alphabetically. Each file
in a category folder should start with a number, like:

```
01_DSF5211.JPG
02_DSF8947.jpg
03_DSF7080.jpg
```

To reorder, rename the numbers. Fastest way for a whole folder:

1. In Finder, select all the photos in the category folder (not `Drop Zone`).
2. Right-click → **Rename N items…**
3. Choose **Format**, set a name and starting number, and Finder will
   number them all in whatever order you selected them in.
4. Double-click `Update Photos.command`.

## Moving a photo between categories

Drag the file from one category folder into another (e.g. `People` →
`Places`). Rename it with a number prefix so it sorts where you want in
its new home. Then double-click `Update Photos.command`.

## Changing the homepage photos

Same process, just using the `Home` folder instead of a nav-page folder.
Drop new photos in `Import/Portfolio/Home/Drop Zone/`, or reorder/remove
photos already in `Import/Portfolio/Home/`, then double-click
`Update Photos.command`. The homepage currently shows 6 photos, but you
can add more or fewer — the layout adjusts automatically.

## Captions (alt text)

Each category folder has a `captions.json` file — a simple list matching
an exact filename to a short description, used for accessibility and
search engines. Example:

```json
{
  "01_DSF5211.JPG": "Concert crowd at an outdoor festival",
  "02_DSF8947.jpg": "Gothic cathedral spires against a blue sky"
}
```

- To add/change a caption: open `captions.json` in a text editor, add or
  edit a line matching the exact filename, save.
- New photos you import won't have one yet — they'll get a generic
  default like "People photograph 15" until you add a line for them.
- **Renaming a file breaks its caption match** (since captions are keyed
  to the exact filename). If you rename a file as part of reordering,
  either update its line in `captions.json` to the new filename, or just
  accept the generic fallback.

## Running the update

Double-click **`Update Photos.command`** in the main website folder. It:

1. Moves anything sitting in a `Drop Zone` folder into place, renumbered
   correctly.
2. Resizes any new photos and rewrites the photo grids on every page to
   match your folders — whether you imported something new, reordered
   existing photos, or both.

It's always safe to double-click, even if you haven't changed anything —
it'll just say "No new photos found" and leave everything else as-is.

If you ever prefer Terminal, or the `.command` file stops working for
some reason, the same thing runs with:

```bash
cd "/Users/michaelcole/Documents/Website/Photography"
python3 scripts/update_photos.py
```

## How this works (good to know, not required reading)

- Every photo gets two web-friendly copies generated: a smaller one for
  the photo grids (2200px) and a larger one for the zoomed-in lightbox
  view (4200px). Your originals in `Import/Portfolio/` are never modified
  or deleted — only moved from `Drop Zone` into the category folder.
- The update only ever touches the photo grid on each page — nothing else
  (text, layout, nav) is affected.
- If a category folder is empty (like `Things` right now), that page
  automatically shows a "coming soon" message instead of an empty grid.
- If something in `Drop Zone` isn't a photo (like a stray text file), it's
  left alone and flagged in the printed output rather than silently
  ignored.
- If a rename would ever overwrite an existing photo, it's skipped with a
  warning instead of overwriting anything.
