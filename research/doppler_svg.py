"""Pure-Python SVG visualization of the Doppler effect on a spacecraft radio signal."""
import math

C = 299_792_458.0  # speed of light, m/s


def doppler_shift_hz(f_hz, v_ms):
    """Approximate shift for line-of-sight speed v (positive = receding)."""
    return -f_hz * v_ms / C


def wave_path(x0, x1, y, amp, wavelength, steps=400):
    pts = []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        pts.append(f"{x:.1f},{y - amp * math.sin(2 * math.pi * (x - x0) / wavelength):.1f}")
    return "M" + " L".join(pts)


def doppler_svg(f_ghz=8.4, speed_ms=1.0):
    f = f_ghz * 1e9
    w, h = 900, 680
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="sans-serif" font-size="14">',
         f'<rect width="{w}" height="{h}" fill="#0b1026"/>',
         '<text x="450" y="30" fill="white" font-size="20" text-anchor="middle">'
         'Doppler effect on a spacecraft radio signal (wavelengths exaggerated)</text>']

    rows = [
        ("Spacecraft stationary: wavelength as transmitted", 100, 55, "#9ecbff",
         "received frequency = transmitted frequency"),
        ("Spacecraft approaching Earth: waves compressed", 230, 40, "#6ee7a8",
         "higher frequency (blueshift)"),
        ("Spacecraft receding from Earth: waves stretched", 360, 75, "#ff9e7a",
         "lower frequency (redshift)"),
    ]
    for label, y, wl, color, note in rows:
        s.append(f'<text x="40" y="{y - 38}" fill="white">{label}</text>')
        s.append(f'<path d="{wave_path(120, 780, y, 22, wl)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        s.append(f'<circle cx="60" cy="{y}" r="14" fill="#f2c94c"/>'
                 f'<text x="60" y="{y + 32}" fill="#f2c94c" font-size="11" text-anchor="middle">spacecraft</text>')
        s.append(f'<circle cx="840" cy="{y}" r="16" fill="#3b82f6"/>'
                 f'<text x="840" y="{y + 32}" fill="#9ecbff" font-size="11" text-anchor="middle">Earth (DSN)</text>')
        s.append(f'<text x="450" y="{y + 52}" fill="{color}" text-anchor="middle">{note}</text>')

    # Frequency shift vs speed chart
    cx0, cx1, cy0, cy1 = 120, 780, 645, 500
    vmax = 10.0
    fmax = abs(doppler_shift_hz(f, vmax))
    s.append(f'<text x="450" y="{cy1 - 20}" fill="white" text-anchor="middle">'
             f'Frequency shift for a {f_ghz:g} GHz signal (|Δf| = f · v / c)</text>')
    s.append(f'<line x1="{cx0}" y1="{cy0}" x2="{cx1}" y2="{cy0}" stroke="#888"/>')
    s.append(f'<line x1="{cx0}" y1="{cy0}" x2="{cx0}" y2="{cy1}" stroke="#888"/>')
    s.append(f'<path d="M{cx0},{cy0} L{cx1},{cy1}" stroke="#f2c94c" stroke-width="3" fill="none"/>')
    for v in (0, 2, 4, 6, 8, 10):
        x = cx0 + (cx1 - cx0) * v / vmax
        s.append(f'<text x="{x}" y="{cy0 + 16}" fill="#ccc" font-size="11" text-anchor="middle">{v} m/s</text>')
    for k in (0, 0.5, 1.0):
        y = cy0 - (cy0 - cy1) * k
        s.append(f'<text x="{cx0 - 8}" y="{y + 4}" fill="#ccc" font-size="11" text-anchor="end">{k * fmax:.0f} Hz</text>')
    x = cx0 + (cx1 - cx0) * speed_ms / vmax
    d = abs(doppler_shift_hz(f, speed_ms))
    y = cy0 - (cy0 - cy1) * d / fmax
    s.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#ff9e7a"/>')
    s.append(f'<text x="{x + 14}" y="{y - 60}" fill="#ff9e7a">{speed_ms:g} m/s gives about {d:.0f} Hz</text>')
    s.append('</svg>')
    return "\n".join(s)
