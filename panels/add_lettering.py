"""Letter 'OUT OF LOCK' onto every screen of panel_003.

Usage: python add_lettering.py [--debug]
  --debug  draws numbered outlines instead of text, to check the screen positions.

Each screen is a quad (top-left, top-right, bottom-right, bottom-left) in pixels of the
1344x768 base image. The text is drawn flat, warped onto the quad, and multiplied into the
image so the pencil texture shows through.
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).parent
BASE = HERE / 'panel_003_base.png'
OUT = HERE / 'panel_003_lettered.png'
DEBUG_OUT = HERE / 'panel_003_debug.png'
TEXT = 'OUT OF LOCK'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
INK = (35, 35, 35)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# Wall screens first, then console monitors.
SCREENS = [
    rect(375, 197, 828, 396),
    rect(20, 205, 197, 306),
    rect(219, 211, 342, 312),
    rect(20, 335, 193, 402),
    rect(218, 340, 343, 402),
    rect(850, 200, 965, 312),
    rect(855, 330, 962, 402),
    rect(988, 205, 1085, 305),
    rect(990, 322, 1086, 405),
    rect(1106, 197, 1208, 303),
    rect(1105, 322, 1210, 407),
    rect(1226, 190, 1344, 298),
    rect(1228, 327, 1305, 400),
    rect(1310, 327, 1344, 400),
    rect(93, 483, 146, 527),
    rect(160, 497, 207, 535),
    rect(217, 505, 291, 553),
    rect(432, 511, 504, 563),
    rect(527, 517, 598, 568),
    rect(770, 513, 845, 550),
    rect(888, 517, 975, 566),
    rect(1020, 505, 1100, 548),
    rect(1142, 497, 1198, 545),
    rect(1245, 487, 1278, 527),
]


def perspective_coeffs(dst, src):
    """Coefficients for Image.transform(PERSPECTIVE): maps output points dst back to input points src."""
    rows, rhs = [], []
    for (x, y), (u, v) in zip(dst, src):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); rhs.append(u)
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y]); rhs.append(v)
    n = 8
    a = [r + [b] for r, b in zip(rows, rhs)]
    for i in range(n):  # Gauss-Jordan elimination
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[p] = a[p], a[i]
        a[i] = [v / a[i][i] for v in a[i]]
        for r in range(n):
            if r != i:
                f = a[r][i]
                a[r] = [vr - f * vi for vr, vi in zip(a[r], a[i])]
    return [a[i][n] for i in range(n)]


def fit(d, lines, w, h):
    """Largest font size where the stacked lines fit inside the window with a margin."""
    for fs in range(h, 5, -1):
        font = ImageFont.truetype(FONT, fs)
        boxes = [d.textbbox((0, 0), t, font=font) for t in lines]
        total_h = sum(b[3] - b[1] for b in boxes) + (len(lines) - 1) * fs * 0.25
        if max(b[2] - b[0] for b in boxes) <= w * 0.86 and total_h <= h * 0.7:
            return font, boxes, fs
    return font, boxes, 6


def text_layer(size, text):
    """White canvas with the text centred; one or two lines, whichever gives larger text."""
    w, h = size
    layer = Image.new('RGB', (w, h), 'white')
    d = ImageDraw.Draw(layer)
    words = text.split(' ')
    options = [[text], [' '.join(words[:2]), ' '.join(words[2:])]]
    font, boxes, fs = max((fit(d, lines, w, h) + (lines,) for lines in options), key=lambda o: o[2])[:3]
    lines = max((fit(d, l, w, h) + (l,) for l in options), key=lambda o: o[2])[3]
    total_h = sum(b[3] - b[1] for b in boxes) + (len(lines) - 1) * fs * 0.25
    y = (h - total_h) / 2
    for t, b in zip(lines, boxes):
        d.text(((w - (b[2] - b[0])) / 2 - b[0], y - b[1]), t, font=font, fill=INK)
        y += b[3] - b[1] + fs * 0.25
    return layer


def wash(base, quad):
    """Lighten the screen so dark lettering reads over the map or chart drawn on it."""
    mask = Image.new('L', base.size, 0)
    ImageDraw.Draw(mask).polygon(quad, fill=170)
    return Image.composite(Image.new('RGB', base.size, 'white'), base, mask)


def letter(base, quad):
    xs, ys = [p[0] for p in quad], [p[1] for p in quad]
    w, h = int(max(xs) - min(xs)), int(max(ys) - min(ys))
    scale = 4  # draw big, warp, then let the multiply keep it crisp
    flat = text_layer((w * scale, h * scale), TEXT)
    coeffs = perspective_coeffs(quad, [(0, 0), (w * scale, 0), (w * scale, h * scale), (0, h * scale)])
    overlay = flat.transform(base.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor='white')
    return ImageChops.multiply(wash(base, quad), overlay)


def main():
    base = Image.open(BASE).convert('RGB')
    if '--debug' in sys.argv:
        d = ImageDraw.Draw(base)
        for i, q in enumerate(SCREENS):
            d.polygon(q, outline=(255, 0, 0))
            d.text((q[0][0] + 2, q[0][1] + 2), str(i), fill=(255, 0, 0))
        base.save(DEBUG_OUT)
        print('wrote', DEBUG_OUT)
        return
    for q in SCREENS:
        base = letter(base, q)
    base.save(OUT)
    print('wrote', OUT, 'with', len(SCREENS), 'screens')


main()
