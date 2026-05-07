# NSCoutureStudio Catalogue — GitHub Pages

Automatically updating product catalogue hosted on GitHub Pages.
**Upload or delete images → the site rebuilds and goes live automatically.**

---

## Adding Items to the Catalogue

### Easiest: upload an image
1. GitHub → your repo → click **Add file → Upload files**
2. Navigate into the `images/` folder
3. Drag your photo(s) in
4. Click **Commit changes**

GitHub Actions fires, scans the folder, adds the item to `catalogue.json`
with a name derived from the filename, and rebuilds `index.html`.
**Live in ~60 seconds.**

### Filename = item name on the site
| Filename                     | Displays as              |
|------------------------------|--------------------------|
| `ivory-lace-ballgown.jpg`    | Ivory Lace Ballgown      |
| `blush-tulle-a-line.jpg`     | Blush Tulle A Line       |
| `black-evening-gown.jpg`     | Black Evening Gown       |

### Adding a description or price
After uploading, open `catalogue.json` and edit the auto-generated entry:
```json
{
  "filename":    "ivory-lace-ballgown.jpg",
  "name":        "Ivory Lace Ballgown",
  "description": "Hand-crafted ivory lace with cathedral train. Sizes 2–18.",
  "category":    "Bridal",
  "available":   true,
  "order":       1
}
```

### Removing an item
Delete the image from the `images/` folder — it disappears from the
catalogue automatically on the next build.

---

## Categories
Defined in `catalogue.json`. Items are filterable by category on the live site:
```json
"categories": ["Bridal", "High Fashion", "Accessories"]
```

---

## Customising the Design
The entire visual identity is controlled by CSS variables in
`scripts/generate.py`, which writes the generated `/* DESIGN TOKENS */` block
at the top of `index.html`. Decorative vector assets live in `assets/svg/` and
are referenced directly by the generator.

**For Claude Design:** paste the contents of `index.html` directly —
all brand decisions (fonts, colours, spacing) are in one block at the top.

**For Canva:** use Canva's website editor and import the colour palette
and fonts from the tokens block.

---

## Running Locally (optional preview)
```bash
python scripts/generate.py   # rebuilds index.html from current images/
# Open index.html in your browser to preview
```

---

## File Structure
```
your-repo/
├── .github/
│   └── workflows/
│       └── build-catalogue.yml   ← GitHub Actions (do not edit)
├── assets/
│   └── svg/
│       ├── logo.svg              ← brand and ornamental vector assets
│       ├── divider.svg
│       ├── monogram.svg
│       ├── corner.svg
│       └── petals.svg
├── images/
│   ├── .gitkeep                  ← keeps the folder tracked when empty
│   └── your-photos-here.jpg
├── scripts/
│   └── generate.py               ← catalogue generator
├── catalogue.json                ← brand info + item metadata ← EDIT THIS
├── index.html                    ← auto-generated (do not edit manually)
├── _config.yml                   ← GitHub Pages config
└── README.md
```

---

## How It Works
```
You upload/delete an image in images/
           ↓
GitHub Actions triggers (path: images/**)
           ↓
generate.py scans folder, rebuilds index.html
           ↓
Bot commits index.html back to main [skip ci]
           ↓
GitHub Pages serves the updated site (~60 sec)
           ↓
QR code on business cards → always shows current catalogue
```
