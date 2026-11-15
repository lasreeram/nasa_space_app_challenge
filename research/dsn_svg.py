"""Pure-Python SVG figures for the Deep Space Network: site spacing and signal handover.

Station longitudes are approximate (Goldstone 116.9 W, Madrid 4.25 W, Canberra 149.0 E).
"""
import math

BG = "#0b1026"
STATIONS = {
    "Goldstone": {"lon": -116.9, "color": "#ffb347", "place": "California, USA"},
    "Madrid": {"lon": -4.25, "color": "#6ee7a8", "place": "Spain"},
    "Canberra": {"lon": 149.0, "color": "#9ecbff", "place": "Australia"},
}
EARTH_DEG_PER_HOUR = 15.0  # simplified: one rotation per 24 h


def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def _header(w, h, title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="sans-serif" font-size="14">',
            f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            f'<text x="{w / 2}" y="30" fill="white" font-size="20" text-anchor="middle">{title}</text>']


def _earth(s, cx, cy, r):
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#16408a" stroke="#4f8fe0" stroke-width="2"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.55}" fill="none" stroke="#2a62b8" stroke-width="1" '
             'stroke-dasharray="3 5"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="white"/>')


def spacing_svg():
    w, h = 960, 620
    cx, cy, r = 300, 340, 150
    s = _header(w, h, "DSN sites around the globe (view from above the North Pole)")

    _earth(s, cx, cy, r)
    s.append(f'<text x="{cx}" y="{cy + 22}" fill="white" text-anchor="middle">North Pole</text>')
    s.append(f'<text x="{cx}" y="{cy - r - 56}" fill="#ccc" text-anchor="middle">0\u00b0 longitude (Greenwich) at top</text>')
    s.append(f'<text x="{cx - r + 10}" y="{cy + 5}" fill="#ccc">90\u00b0 E</text>')
    s.append(f'<text x="{cx + r - 10}" y="{cy + 5}" fill="#ccc" text-anchor="end">90\u00b0 W</text>')

    # Greenwich at the top, east is counterclockwise as seen from above the pole.
    ang = {n: 90 + d["lon"] for n, d in STATIONS.items()}
    order = sorted(STATIONS, key=lambda n: STATIONS[n]["lon"] % 360)  # eastward order from Greenwich
    for i, name in enumerate(order):
        nxt = order[(i + 1) % 3]
        a1, a2 = ang[name], ang[nxt]
        gap = (STATIONS[nxt]["lon"] - STATIONS[name]["lon"]) % 360
        ra = r + 34
        x1, y1 = _pt(cx, cy, ra, a1)
        x2, y2 = _pt(cx, cy, ra, a2)
        s.append(f'<path d="M{x1:.1f},{y1:.1f} A{ra},{ra} 0 {1 if gap > 180 else 0} 0 {x2:.1f},{y2:.1f}" '
                 'fill="none" stroke="#f2c94c" stroke-width="2" stroke-dasharray="6 4"/>')
        lx, ly = _pt(cx, cy, ra + 22, a1 + gap / 2)
        s.append(f'<text x="{lx:.1f}" y="{ly + 5:.1f}" fill="#f2c94c" text-anchor="middle" font-weight="bold">'
                 f'{gap:.0f}\u00b0</text>')

    for name, d in STATIONS.items():
        px, py = _pt(cx, cy, r, ang[name])
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{px:.1f}" y2="{py:.1f}" stroke="{d["color"]}" stroke-width="1.5" '
                 'stroke-opacity="0.6"/>')
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="9" fill="{d["color"]}" stroke="white" stroke-width="2"/>')
        tx, ty = _pt(cx, cy, r - 38, ang[name])
        s.append(f'<text x="{tx:.1f}" y="{ty + 5:.1f}" fill="white" text-anchor="middle" font-size="13">{name}</text>')

    # Side table
    tx = 590
    s.append(f'<text x="{tx}" y="120" fill="white" font-size="17" font-weight="bold">Approximate station longitudes</text>')
    y = 155
    for name in order:
        d = STATIONS[name]
        lon = d["lon"]
        hemi = "E" if lon >= 0 else "W"
        nxt = order[(order.index(name) + 1) % 3]
        gap = (STATIONS[nxt]["lon"] - lon) % 360
        s.append(f'<circle cx="{tx + 8}" cy="{y - 5}" r="8" fill="{d["color"]}"/>')
        s.append(f'<text x="{tx + 26}" y="{y}" fill="white">{name} ({d["place"]})</text>')
        s.append(f'<text x="{tx + 26}" y="{y + 20}" fill="#aab4d4" font-size="13">'
                 f'{abs(lon):.1f}\u00b0 {hemi}; {gap:.0f}\u00b0 east to {nxt}</text>')
        y += 56
    s.append(f'<text x="{tx}" y="{y + 10}" fill="#f2c94c" font-size="14">NASA: sites are "approximately 120\u00b0 apart".</text>')
    s.append(f'<text x="{tx}" y="{y + 32}" fill="#f2c94c" font-size="14">The real gaps are about 94\u00b0 to 153\u00b0, and</text>')
    s.append(f'<text x="{tx}" y="{y + 54}" fill="#f2c94c" font-size="14">always add up to 360\u00b0.</text>')
    s.append(f'<text x="{tx}" y="{y + 90}" fill="#aab4d4" font-size="12">Longitudes are approximate (not from NASA\'s pages).</text>')
    s.append('</svg>')
    return "\n".join(s)


def _windows():
    """Hours (from Canberra rise) when each station can see a distant spacecraft.

    Simplified: spacecraft on the celestial equator, 0 degree horizon, so each pass lasts 12 h.
    Earth turns eastward, so the object rises first at the easternmost site.
    """
    lon_c = STATIONS["Canberra"]["lon"]
    start = {"Canberra": 0.0}
    for n in ("Madrid", "Goldstone"):
        start[n] = ((lon_c - STATIONS[n]["lon"]) % 360) / EARTH_DEG_PER_HOUR
    return start


def handover_svg():
    w, h = 1000, 760
    s = _header(w, h, "Handover: the spacecraft passes from one DSN site to the next as Earth rotates")
    start = _windows()
    # Screen angle of each station at hour t, spacecraft fixed to the right (0 degrees).
    base = {n: -90 - EARTH_DEG_PER_HOUR * start[n] for n in start}

    snaps = [("A", 11.0, "Canberra \u2192 Madrid"), ("B", 20.0, "Madrid \u2192 Goldstone"),
             ("C", 27.0, "Goldstone \u2192 Canberra")]
    pw = 335
    for i, (tag, t, label) in enumerate(snaps):
        ox = 10 + i * pw
        cx, cy, r = ox + 125, 190, 62
        sx, sy = ox + 280, 190
        s.append(f'<text x="{ox + 10}" y="62" fill="white" font-size="15" font-weight="bold">'
                 f'{tag}: t = {t:.0f} h, {label}</text>')
        _earth(s, cx, cy, r)
        s.append(f'<circle cx="{sx}" cy="{sy}" r="9" fill="#f2c94c"/>')
        s.append(f'<text x="{sx}" y="{sy - 16}" fill="#f2c94c" text-anchor="middle" font-size="12">spacecraft</text>')
        s.append(f'<text x="{sx}" y="{sy + 28}" fill="#f2c94c" text-anchor="middle" font-size="12">far away</text>')
        for name, d in STATIONS.items():
            a = base[name] + EARTH_DEG_PER_HOUR * t
            px, py = _pt(cx, cy, r, a)
            visible = math.cos(math.radians(a)) > 0
            if visible:
                s.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{sx - 10}" y2="{sy}" stroke="{d["color"]}" '
                         'stroke-width="2.5" stroke-dasharray="7 4"/>')
            op = 1.0 if visible else 0.35
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="{d["color"]}" fill-opacity="{op}" '
                     'stroke="white" stroke-width="1.5"/>')
            lx, ly = _pt(cx, cy, r + 24, a)
            s.append(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" fill="{d["color"]}" fill-opacity="{op}" '
                     f'text-anchor="middle" font-size="12">{name}</text>')
        s.append(f'<text x="{ox + 10}" y="{cy + r + 62}" fill="#aab4d4" font-size="12">'
                 'Dashed line = site can see the spacecraft</text>')

    # Timeline
    x0, x1 = 150, 960
    tmax = 36.0

    def tx(t):
        return x0 + (x1 - x0) * t / tmax

    s.append('<text x="40" y="340" fill="white" font-size="16" font-weight="bold">'
             'Which site can see the spacecraft (simplified, 36 hours)</text>')
    rows = {"Canberra": 395, "Madrid": 455, "Goldstone": 515}
    for name, y in rows.items():
        d = STATIONS[name]
        s.append(f'<text x="{x0 - 12}" y="{y + 5}" fill="{d["color"]}" text-anchor="end">{name}</text>')
        s.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#223" stroke-width="1"/>')
        t = start[name]
        while t - 24 > 0:
            t -= 24
        while t < tmax:
            a, b = max(t, 0.0), min(t + 12, tmax)
            if b > a:
                s.append(f'<rect x="{tx(a):.1f}" y="{y - 16}" width="{tx(b) - tx(a):.1f}" height="32" rx="4" '
                         f'fill="{d["color"]}" fill-opacity="0.75"/>')
                if tx(b) - tx(a) > 60:
                    s.append(f'<text x="{(tx(a) + tx(b)) / 2:.1f}" y="{y + 5}" fill="#0b1026" text-anchor="middle" '
                             f'font-size="12" font-weight="bold">in view</text>')
            t += 24
    for tag, t, _ in snaps:
        s.append(f'<line x1="{tx(t):.1f}" y1="374" x2="{tx(t):.1f}" y2="545" stroke="white" stroke-width="1.5" '
                 'stroke-dasharray="4 4"/>')
        s.append(f'<text x="{tx(t):.1f}" y="368" fill="white" text-anchor="middle" font-weight="bold">{tag}</text>')
    for hr in range(0, 37, 6):
        s.append(f'<line x1="{tx(hr):.1f}" y1="560" x2="{tx(hr):.1f}" y2="566" stroke="#aab4d4"/>')
        s.append(f'<text x="{tx(hr):.1f}" y="583" fill="#aab4d4" text-anchor="middle" font-size="12">{hr} h</text>')
    s.append(f'<text x="{(x0 + x1) / 2}" y="606" fill="#aab4d4" text-anchor="middle" font-size="12">'
             'hours after the spacecraft rises at Canberra</text>')

    notes = [
        "Windows overlap, so the next site can lock on before the current one loses the spacecraft.",
        "Simplified model: spacecraft on the celestial equator, flat horizon (0\u00b0 elevation), steady 15\u00b0/hour rotation.",
        "Real passes are shorter and differ with the spacecraft's position in the sky, and the station order repeats every day.",
    ]
    for i, n in enumerate(notes):
        s.append(f'<text x="40" y="{650 + 24 * i}" fill="#f2c94c" font-size="13">{n}</text>')
    s.append('</svg>')
    return "\n".join(s)


if __name__ == "__main__":
    for fname, fn in (("dsn_site_spacing.svg", spacing_svg), ("dsn_handover.svg", handover_svg)):
        with open(fname, "w", encoding="utf-8") as f:
            f.write(fn())
        print("wrote", fname)
