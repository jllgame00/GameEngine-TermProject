"""Original vector sleeve art. Run: python ArtSource/Records/Covers/generate_covers.py"""
from io import BytesIO
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, PathPatch, Polygon
from matplotlib.path import Path as VectorPath
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
plt.rcParams.update({"svg.hashsalt": "RecordShop-original-sleeves-v1"})


def path(ax, points, color, width=2, alpha=1, fill=False):
    codes = [VectorPath.MOVETO] + [VectorPath.CURVE4] * (len(points) - 1)
    ax.add_patch(PathPatch(VectorPath(points, codes), facecolor=color if fill else "none",
                           edgecolor="none" if fill else color, linewidth=width,
                           alpha=alpha, capstyle="round", joinstyle="round"))


def poly(ax, points, color, alpha=1):
    ax.add_patch(Polygon(points, closed=True, facecolor=color, edgecolor="none", alpha=alpha))


def line(ax, points, color, width=2, alpha=1):
    ax.plot(*zip(*points), color=color, linewidth=width, alpha=alpha,
            solid_capstyle="round", solid_joinstyle="round")


def paper(ax, seed, ink, alpha=.06):
    rng = np.random.default_rng(seed)
    ax.scatter(rng.uniform(0, 1024, 4200), rng.uniform(0, 1024, 4200),
               s=.55, c=ink, alpha=alpha, linewidths=0)


def electronic(ax):
    # Offset translucent planes and slightly detuned paths suggest quiet circuitry.
    poly(ax, [(92, 92), (485, 92), (837, 889), (443, 889)], "#2d666e")
    poly(ax, [(496, 92), (863, 92), (507, 889), (140, 889)], "#87a6a0", .61)
    poly(ax, [(92, 92), (485, 92), (623, 406), (356, 611)], "#a0b6b0", .54)
    poly(ax, [(356, 611), (623, 406), (756, 708), (507, 889)], "#438c8b", .72)
    ax.add_patch(Circle((658, 351), 122, facecolor="#edb583"))
    ax.add_patch(Circle((668, 345), 113, facecolor="#f1c294", alpha=.58))
    poly(ax, [(496, 92), (615, 92), (781, 466), (658, 466)], "#c4c9ad", .33)
    for i in range(15):
        y = 332 + i * 17
        path(ax, [(106, y), (332, y - 65), (468, 883 - i * 8), (901, 724 - i * 14)],
             "#d5ddd0", 1.1, .56)
    for i in range(8):
        path(ax, [(118, 817 + i * 7), (359, 835), (669, 172 + i * 16), (904, 197 + i * 8)],
             "#172e48", 1, .38)
    line(ax, [(92, 92), (485, 92), (837, 889)], "#cfdbc8", 1, .6)
    line(ax, [(140, 889), (507, 889), (863, 92)], "#c4d4c3", 1, .55)
    for x in (92, 114, 136):
        line(ax, [(x, 938), (x + 12, 938)], "#e4bd92", 1.8)
    paper(ax, 4, "#d1dbc7", .055)


def chair(ax, cx, cy, angle, color):
    a = np.deg2rad(angle)
    def tr(points):
        return [(cx + x * np.cos(a) - y * np.sin(a), cy + x * np.sin(a) + y * np.cos(a))
                for x, y in points]
    poly(ax, tr([(-93, -180), (93, -180), (82, -35), (-82, -35)]), color)
    poly(ax, tr([(-82, -27), (82, -27), (104, 15), (-104, 15)]), color)
    for x in (-78, 78):
        line(ax, tr([(x, 10), (x * 1.16, 154)]), color, 13)
    line(ax, tr([(-83, 80), (83, 80)]), color, 6)
    for i in range(8):
        y = -163 + i * 15
        path(ax, tr([(-76, y), (-35, y - 13), (31, y + 12), (76, y - 2)]),
             "#ead2a8", 1.4, .46)
    line(ax, tr([(-88, -169), (-78, -49)]), "#f3dfb8", 1.6, .65)


def folk(ax):
    # A pair of chairs and a shared circular table; hand-bent lines connect them.
    ax.add_patch(Ellipse((511, 747), 700, 108, facecolor="#d7c7a6", alpha=.38))
    ax.add_patch(Ellipse((521, 469), 294, 162, facecolor="#a95e3d"))
    ax.add_patch(Ellipse((521, 454), 294, 162, facecolor="#d39960"))
    for i in range(6):
        ax.add_patch(Ellipse((521, 454), 42 + i * 40, 15 + i * 20,
                             facecolor="none", edgecolor="#9b5c3a", linewidth=1, alpha=.35))
    line(ax, [(521, 535), (521, 690)], "#875134", 14)
    line(ax, [(521, 678), (462, 719)], "#875134", 11)
    line(ax, [(521, 678), (578, 717)], "#875134", 11)
    chair(ax, 295, 552, -16, "#aa6747")
    chair(ax, 747, 548, 17, "#405b58")
    for i in range(5):
        path(ax, [(172, 264 + i * 11), (391, 141 + i * 12), (587, 349 + i * 13),
                  (852, 234 + i * 12)], "#a96a49", 1.4, .65)
    path(ax, [(149, 817), (361, 898), (666, 770), (872, 824)], "#b18d5c", 1.4, .75)
    for x in (92, 114, 136):
        line(ax, [(x, 938), (x + 12, 938)], "#a56648", 1.8)
    paper(ax, 5, "#795332", .09)


def classical(ax):
    # A piano-like dark mass, open strings, and a suspended comma of silence.
    poly(ax, [(106, 128), (443, 128), (443, 786), (106, 786)], "#e4dcc8")
    path(ax, [(242, 237), (513, 186), (570, 308), (413, 425),
              (335, 485), (443, 559), (411, 651), (370, 708), (242, 691), (242, 691)],
         "#253938", fill=True)
    poly(ax, [(242, 632), (414, 632), (414, 700), (242, 700)], "#253938")
    for i in range(10):
        x = 249 + i * 15.7
        poly(ax, [(x, 639), (x + 14, 639), (x + 14, 693), (x, 693)], "#f4eddb")
    for i in (0, 1, 3, 4, 5, 7, 8):
        x = 260 + i * 15.7
        poly(ax, [(x, 637), (x + 8, 637), (x + 8, 670), (x, 670)], "#253938")
    for i in range(9):
        path(ax, [(374 + i * 8, 182), (596 + i * 11, 296), (478 + i * 13, 561),
                  (791 + i * 4, 736)], "#b08c54", 1.05, .8)
    path(ax, [(606, 755), (691, 744), (735, 800), (694, 845),
              (714, 807), (655, 798), (606, 793)], "#253938", fill=True)
    ax.add_patch(Circle((621, 772), 25, facecolor="#253938"))
    line(ax, [(106, 128), (443, 128)], "#b99b6b", 1)
    line(ax, [(106, 814), (443, 814)], "#b99b6b", 1)
    for x in (92, 114, 136):
        line(ax, [(x, 938), (x + 12, 938)], "#ab8b58", 1.8)
    paper(ax, 6, "#725c3c", .07)


DESIGNS = [
    ("RS004", "#23364e", electronic, "빛의 잔결", "느린 회로"),
    ("RS005", "#efe3cb", folk, "마주 놓은 의자", "나무결 셋"),
    ("RS006", "#f1ecdc", classical, "남겨 둔 쉼표", "작은 방 실내악"),
]


def render(background, draw):
    fig = plt.figure(figsize=(8, 8), dpi=128, facecolor=background)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 1024), ylim=(1024, 0))
    ax.axis("off")
    draw(ax)
    files = {}
    for fmt in ("svg", "png"):
        stream = BytesIO()
        metadata = {"Date": None, "Creator": "RecordShop original vector sleeve art"} if fmt == "svg" else {"Software": "RecordShop original vector sleeve art"}
        fig.savefig(stream, format=fmt, dpi=128, facecolor=background, metadata=metadata)
        files[fmt] = stream.getvalue()
    plt.close(fig)
    return files


def main():
    records = []
    for record, background, draw, title, artist in DESIGNS:
        files = render(background, draw)
        assert files == render(background, draw), f"Non-deterministic export: {record}"
        image = Image.open(BytesIO(files["png"]))
        pixels = np.asarray(image.convert("RGB"))
        assert image.size == (1024, 1024)
        assert image.convert("RGBA").getchannel("A").getextrema() == (255, 255)
        assert pixels.std() > 10 and len(np.unique(pixels.reshape(-1, 3), axis=0)) > 1000
        svg = ET.fromstring(files["svg"])
        assert not any(node.tag.endswith(("image", "text")) for node in svg.iter())
        hashes = {}
        for fmt, data in files.items():
            filename = f"T_{record}_Cover.{fmt}"
            (OUT / filename).write_bytes(data)
            hashes[filename] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        records.append({"id": record, "title": title, "artist": artist,
                        "size": [1024, 1024], "opaque": True, "files": hashes})
    manifest = {"author": "OpenAI Codex for RecordShop", "origin": "Original code-authored vector artwork; no external images, fonts, references, or AI bitmap generation.",
                "method": "Matplotlib vector primitives exported to editable SVG and 1024px PNG from the same deterministic scene; seeded paper stippling.",
                "environment": {"matplotlib": matplotlib.__version__, "numpy": np.__version__, "pillow": Image.__version__},
                "checks": ["two independent exports byte-identical", "1024 x 1024", "fully opaque", "nontrivial image content", "SVG contains no raster images or text"],
                "records": records}
    (OUT / "provenance.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preview = Image.new("RGB", (888, 680), "#23303c")
    labels = ImageDraw.Draw(preview)
    for column, (record, *_rest) in enumerate(DESIGNS):
        image = Image.open(OUT / f"T_{record}_Cover.png").convert("RGB")
        x = 30 + column * 288
        for y, size in ((40, 256), (338, 128), (526, 96)):
            preview.paste(image.resize((size, size), Image.Resampling.LANCZOS), (x, y))
            labels.text((x, y + size + 10), f"{record} / {size}px", fill="#e9e0cb")
    preview.save(OUT / "cover_contact_sheet.png")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
