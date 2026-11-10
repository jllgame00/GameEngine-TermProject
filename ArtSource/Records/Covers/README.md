# Original RecordShop sleeve artwork

Three original, code-authored sleeve illustrations for RS004, RS005 and RS006.
These are finished cover artwork sources, not imported Unreal assets.

- RS004: translucent indigo/teal planes, warm light, two interference path families.
- RS005: copper/green chairs around a shared woodgrain table; hand-bent string lines.
- RS006: ivory/ink piano silhouette, patient string curves and an isolated comma.

No external images, fonts, copyrighted references or AI-generated bitmaps are used.
Korean titles and artists are metadata only; the game UI supplies readable text.
The vector scenes are authored in `generate_covers.py`; each exports an editable SVG
and an identical-scene 1024 x 1024 fully opaque RGBA PNG. The SVGs contain vector
paths only, including deterministic paper stippling. PNGs are rendered directly from
the same vector scene, rather than by parsing the saved SVG.

From the repository root, with the already installed Python packages:

```powershell
python ArtSource/Records/Covers/generate_covers.py
```

The generator checks independent render equality, PNG dimensions, full opacity,
nontrivial pixel content, and absence of raster images or text in the SVG. It writes
`provenance.json` with versions, SHA-256 hashes and byte counts. Reproduction is
byte-identical in the recorded package environment; a renderer/library change may
alter antialiasing or serialization. No dependency installation is needed.

`cover_contact_sheet.png` is a QA preview on the UI's dark blue-gray background,
with each design at 256, 128 and 96 pixels. It is not an import source. The three
`T_RS00*_Cover.png` files are the texture import sources.

The artwork has been visually inspected at full size and on the contact sheet.
Final subjective art approval and Unreal material/card presentation remain with
the project owner. No Unreal assets, project settings or other folders are edited.
