#!/usr/bin/env python3
"""
Catalogue Generator
-------------------
Scans /images, cross-references catalogue.json metadata,
and patches index.html in-place.

Only the three dynamic regions are ever touched:
  - The catalogue grid (card items)
  - The filter bar (category buttons)
  - The footer "Last updated" timestamp

Every other part of index.html — styles, colours, copy,
structure — is preserved exactly as written. Design changes
made directly to index.html will never be overwritten.

Run automatically by GitHub Actions on every push that
touches the images/ folder. Also runnable locally:
  python scripts/generate.py
"""

import html
import json
import pathlib
import re
from datetime import datetime, timezone
from urllib.parse import quote

ROOT = pathlib.Path(__file__).parent.parent
IMAGES_DIR = ROOT / "images"
META_FILE = ROOT / "catalogue.json"
OUTPUT = ROOT / "index.html"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
OVERLAY_DEFAULT_TEXT = "View full-size image."


def slug_to_title(s):
    return re.sub(r"[-_]+", " ", pathlib.Path(s).stem).title()


def esc(value):
    return html.escape(str(value), quote=True)


def image_src(filename):
    return f"images/{quote(str(filename))}"


def load_meta():
    if META_FILE.exists():
        with open(META_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"site": {}, "categories": [], "items": []}


def save_meta(data):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def sync(data):
    """Add new images to catalogue.json; remove entries for deleted images."""
    existing = {i["filename"] for i in data.get("items", [])}
    image_files = sorted(
        f for f in IMAGES_DIR.iterdir() if f.suffix.lower() in IMAGE_EXTS
    )

    added = 0
    for img in image_files:
        if img.name not in existing:
            data["items"].append({
                "filename": img.name,
                "name": slug_to_title(img.stem),
                "description": "",
                "category": (data["categories"] or [""])[0],
                "available": True,
                "order": 9999,
            })
            added += 1

    all_files = {f.name for f in image_files}
    before = len(data["items"])
    data["items"] = [i for i in data["items"] if i["filename"] in all_files]
    removed = before - len(data["items"])

    if added or removed:
        save_meta(data)
        print(f"  catalogue.json: +{added} added, -{removed} removed")
    return data


def render_cards(items):
    visible = sorted(
        [i for i in items if i.get("available", True)],
        key=lambda item: (item.get("order", 9999), item.get("name", "")),
    )
    if not visible:
        return '          <div class="empty-state"><p>New pieces arriving soon — check back shortly.</p></div>'

    out = []
    for item in visible:
        name = esc(item.get("name", slug_to_title(item["filename"])))
        desc = esc(item.get("description", ""))
        category = esc(item.get("category", ""))
        filename = image_src(item["filename"])
        desc_html = f'<p class="item-desc">{desc}</p>' if desc else ""
        overlay_desc = (
            f'<p class="overlay-desc">{desc}</p>'
            if desc
            else f'<p class="overlay-desc">{esc(OVERLAY_DEFAULT_TEXT)}</p>'
        )
        category_data = f' data-category="{category}"' if category else ""
        category_badge = f'<span class="item-cat">{category}</span>' if category else ""
        overlay_category = category or "Collection"
        out.append(
            f'          <article class="item-card"{category_data}>\n'
            f'            <div class="item-img-wrap">\n'
            f'              <img src="{filename}" alt="{name}" loading="lazy" decoding="async" width="600" height="800">\n'
            f'              <div class="item-overlay">\n'
            f'                <span class="overlay-category">{overlay_category}</span>\n'
            f'                <h3 class="overlay-title">{name}</h3>\n'
            f'                {overlay_desc}\n'
            f'                <a class="card-link" href="{filename}" target="_blank" rel="noopener noreferrer" aria-label="View {name}">View Piece</a>\n'
            f'              </div>\n'
            f'            </div>\n'
            f'            <div class="item-info">\n'
            f'              {category_badge}\n'
            f'              <h3 class="item-name">{name}</h3>\n'
            f'              {desc_html}\n'
            f'            </div>\n'
            f'          </article>'
        )
    return "\n".join(out)


def render_filter_bar(categories):
    if not categories:
        return ""
    buttons = "\n".join(
        f'          <button class="filter-btn" data-category="{esc(cat)}">{esc(cat)}</button>'
        for cat in categories
        if cat
    )
    return (
        '        <div class="filter-bar" role="group" aria-label="Filter by category">\n'
        '          <button class="filter-btn active" data-category="all">All</button>\n'
        f"{buttons}\n"
        "        </div>"
    )


def patch_html(source, data):
    """Patch only the three dynamic regions in index.html, leaving everything else intact."""
    categories = data.get("categories", [])
    items = data.get("items", [])
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 1. Catalogue grid — replace all content inside id="catalogue-grid"
    source = re.sub(
        r'(<div class="catalogue-grid" id="catalogue-grid">)'
        r".*?"
        r"(</div>)",
        lambda m: m.group(1) + "\n" + render_cards(items) + "\n        " + m.group(2),
        source,
        flags=re.DOTALL,
    )

    # 2. Filter bar — replace the entire <div class="filter-bar"…>…</div> block
    new_nav = render_filter_bar(categories)
    if new_nav:
        source = re.sub(
            r'<div class="filter-bar"[^>]*>.*?</div>',
            new_nav,
            source,
            flags=re.DOTALL,
        )

    # 3. Footer timestamp — update in place
    source = re.sub(
        r'(<span class="footer-meta">Last updated: )([^<]*)(</span>)',
        rf"\g<1>{built_at}\g<3>",
        source,
    )

    return source


def main():
    print("Loading catalogue.json ...")
    data = load_meta()
    print("Syncing images/ ...")
    data = sync(data)
    print("Patching index.html ...")
    source = OUTPUT.read_text(encoding="utf-8")
    patched = patch_html(source, data)
    OUTPUT.write_text(patched, encoding="utf-8")
    visible = len([i for i in data["items"] if i.get("available", True)])
    print(f"Done — {visible} item(s) in catalogue")


if __name__ == "__main__":
    main()
