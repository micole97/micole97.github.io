# Website Maintenance — Updating Photos

This covers how to add, remove, reorder, and caption photos on the site,
including the homepage highlights. No coding required — everything below
is done in Finder plus one command.

## The short version

1. Open `Import/Portfolio/` — there are 4 folders: `Home`, `People`, `Places`, `Things`.
2. Add, delete, or drag photos between those folders in Finder.
3. Rename files to control the order they appear in (see below).
4. Run the sync command (see below).
5. Done — the live site now matches what's in those folders.

## Where photos live

- `Import/Portfolio/Home/` — the 6 curated photos on the homepage.
- `Import/Portfolio/People/` — everything on the People page.
- `Import/Portfolio/Places/` — everything on the Places page.
- `Import/Portfolio/Things/` — everything on the Things page (empty until you shoot product work).

These folders hold your **original, full-quality photos**. The website never
uses these directly — it uses smaller, web-friendly copies that get
automatically generated from them (see "How this works" below).

## Adding a photo

Drag the photo file into the right category folder (`Home`, `People`,
`Places`, or `Things`). Then run the sync command. That's it.

## Removing a photo

Delete the file from its category folder (or drag it out, e.g. to a
separate "archive" folder somewhere outside `Import/Portfolio/` if you
want to keep it without it showing on the site). Then run the sync command.

## Reordering photos

Photos display in the order their filenames sort alphabetically. Each file
should start with a two-digit number, like:

```
01_DSF5211.JPG
02_DSF8947.jpg
03_DSF7080.jpg
```

To reorder, rename the numbers. Fastest way for a whole folder:

1. In Finder, select all the photos in the category folder.
2. Right-click → **Rename N items…**
3. Choose **Format**, set a name and starting number, and Finder will
   number them all in whatever order you selected them in.
4. Run the sync command.

## Moving a photo between categories

Drag the file from one category folder into another (e.g. `People` →
`Places`). Rename it with a number prefix so it sorts where you want in
its new home. Then run the sync command.

## Changing the homepage photos

Same process, just using the `Home` folder instead of a nav-page folder.
Add/remove/reorder photos in `Import/Portfolio/Home/` exactly as above,
then run the sync command. The homepage currently shows 6 photos, but you
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
- Photos not listed get a generic default like "People photograph 3" —
  totally fine to leave as-is, just less descriptive.
- **Renaming a file breaks its caption match** (since captions are keyed
  to the exact filename). If you rename a file as part of reordering,
  either update its line in `captions.json` to the new filename, or just
  accept the generic fallback.

## Running the sync command

Ask Claude to "sync the galleries," or run it yourself in Terminal:

```bash
cd "/Users/michaelcole/Documents/Website/Photography"
python3 scripts/sync_galleries.py
```

This resizes any new photos, removes generated files for anything you
deleted, and rewrites the photo grids on the site to match your folders.
It takes a few seconds and prints a summary like:

```
Home: 6 photo(s) -> index.html
People: 14 photo(s) -> people.html
Places: 13 photo(s) -> places.html
Things: 0 photo(s) -> things.html
Sync complete.
```

## How this works (good to know, not required reading)

- The sync script generates two web-friendly copies of every photo: a
  smaller one for the photo grids (2200px) and a larger one for the
  zoomed-in lightbox view (4200px). Your originals in `Import/Portfolio/`
  are never modified.
- It only rewrites the photo grid itself on each page — nothing else on
  the page (text, layout, nav) is touched.
- If a category folder is empty (like `Things` right now), that page
  automatically shows a "coming soon" message instead of an empty grid.
