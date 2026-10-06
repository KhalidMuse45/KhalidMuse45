"""Turn a photo into an ASCII-art portrait (ascii-portrait.svg, 840x880).

    python scripts/make_ascii_svg.py path/to/photo.jpg
    python scripts/make_ascii_svg.py            # no photo: "KM" monogram

Run by hand when the photo changes; the daily workflow leaves it alone.
Needs Pillow (pip install -r scripts/requirements.txt).
"""
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

from theme import load, window, write

W, H = 840, 880
COLS, ROWS = 96, 80
CHAR_W, LINE_H = 8.0, 10.0
LEFT, TOP = (W - COLS * CHAR_W) / 2, 50
RAMP = " .'`^,:;-~=+*cxoO#%&@"  # sparse -> dense; bright pixels get dense glyphs
COLORS = ["#1a7f37", "#26a641", "#39d353", "#7ee787", "#aff5b4"]  # dim -> bright green


def monogram():
    img = Image.new("L", (COLS * 4, ROWS * 5), 0)
    font = ImageFont.load_default(size=int(ROWS * 2.6))
    draw = ImageDraw.Draw(img)
    box = draw.textbbox((0, 0), "KM", font=font)
    draw.text(((img.width - box[2] - box[0]) / 2, (img.height - box[3] - box[1]) / 2), "KM", fill=255, font=font)
    return img


def load_photo(path):
    img = ImageOps.exif_transpose(Image.open(path)).convert("L")
    # crop to the output aspect (each glyph cell is CHAR_W x LINE_H)
    target = (COLS * CHAR_W) / (ROWS * LINE_H)
    w, h = img.size
    if w / h > target:
        nw = int(h * target)
        img = img.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / target)
        img = img.crop((0, 0, w, nh))  # keep the top: that's where the face is
    img = ImageOps.autocontrast(img, cutoff=2)
    return img.point(lambda v: int(255 * (v / 255) ** 1.3))  # crush shadows so dark backgrounds stay empty


def main():
    img = load_photo(sys.argv[1]) if len(sys.argv) > 1 else monogram()
    px = img.resize((COLS, ROWS), Image.LANCZOS).load()

    rows = []
    for r in range(ROWS):
        # group consecutive glyphs of the same colour band into one tspan
        spans, band, run = [], None, ""
        for c in range(COLS):
            v = px[c, r] / 255
            ch = RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))]
            b = min(len(COLORS) - 1, int(v * len(COLORS)))
            if b != band and run:
                spans.append((band, run))
                run = ""
            band, run = b, run + ch
        spans.append((band, run))
        body = "".join(
            f'<tspan fill="{COLORS[b]}">{t.replace("&", "&amp;").replace("<", "&lt;")}</tspan>' for b, t in spans
        )
        rows.append(
            f'<text class="r" x="{LEFT}" y="{TOP + (r + 1) * LINE_H}" textLength="{COLS * CHAR_W}" '
            f'style="animation-delay:{r * 0.02:.2f}s">{body}</text>'
        )

    style = """
text.r{font-size:13px;white-space:pre;opacity:0;animation:in .5s ease-out forwards}
@keyframes in{to{opacity:1}}
"""
    write("ascii-portrait.svg", window(W, H, f"{load()[0]}@github: ~/whoami", '<g xml:space="preserve">' + "\n".join(rows) + "</g>", style, title_size=18))


if __name__ == "__main__":
    main()
