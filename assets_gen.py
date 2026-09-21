"""Generate the 5 cinematic pillar images used on the empty-state dashboard.

These are drawn programmatically with Pillow so the app runs offline and
never depends on external imagery. 1600x900, dark green + gold brand palette.
Only regenerated if the asset file is missing.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ASSET_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
SIZE = (1600, 900)


def _gradient(draw, size, top, bottom):
    w, h = size
    for y in range(h):
        r = int(top[0] + (bottom[0] - top[0]) * y / h)
        g = int(top[1] + (bottom[1] - top[1]) * y / h)
        b = int(top[2] + (bottom[2] - top[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _skyline(img, draw, base_line, color, seed_heights, peak_ok=0):
    """Draw a simple city skyline silhouette starting at base_line (y)."""
    x = 0
    for i, h in enumerate(seed_heights):
        hpx = int(h * (base_line * 0.9))
        draw.rectangle([x, base_line - hpx, x + 90, base_line], fill=color)
        win = 12
        wx = x + 14
        while wx < x + 70:
            wy = base_line - hpx + 16
            while wy < base_line - 14:
                draw.rectangle([wx, wy, wx + 8, wy + 6], fill=(255, 255, 255, 60))
                wy += 22
            wx += 24
        x += 110
    if peak_ok:
        draw.polygon([(800, 60), (780, 180), (820, 180)], fill=(201, 162, 39, 255))


def _glow(img, xy_color_radius):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for (x, y), color, r in xy_color_radius:
        od.ellipse([x - r, y - r, x + r, y + r], fill=color)
    img.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(40)))


def _sparkline(draw, x0, y0, w, h, values, color):
    vals = values
    mn, mx = min(vals), max(vals)
    span = (mx - mn) or 1
    pts = []
    for i, v in enumerate(vals):
        px = x0 + i * w / (len(vals) - 1)
        py = y0 + h - (v - mn) / span * h
        pts.append((px, py))
    draw.line(pts, fill=color, width=4)
    draw.ellipse([pts[-1][0] - 6, pts[-1][1] - 6, pts[-1][0] + 6, pts[-1][1] + 6],
                 fill=(201, 162, 39, 255))


def build_pillar(idx: int) -> Image:
    img = Image.new("RGBA", SIZE, (11, 61, 46, 255))
    draw = ImageDraw.Draw(img)
    base = (17, 74, 58)
    deep = (6, 34, 26)
    _gradient(draw, SIZE, base, deep)

    if idx == 0:  # Profitability - the engine of the business
        _skyline(img, draw, 700, (232, 226, 214, 90),
                 [60, 90, 45, 120, 70, 100, 55, 130, 80, 115, 60, 95, 75, 120], peak_ok=1)
        bar = Image.new("RGBA", SIZE, (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
        xs = [320, 500, 680, 860, 1040]
        hs = [120, 190, 150, 260, 330]
        for x, h in zip(xs, hs):
            bd.rectangle([x, 700 - h, x + 70, 700], fill=(201, 162, 39, 220))
            bd.polygon([(x + 35, 700 - h - 26), (x, 700 - h - 4), (x + 70, 700 - h - 4)],
                       fill=(255, 214, 88, 240))
        img.alpha_composite(bar)
        _glow(img, [((500, 560), (201, 162, 39, 120), 150)])
        _sparkline(draw, 1300, 120, 220, 90, [40, 60, 55, 80, 70, 100, 130], (111, 220, 150, 255))
        overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0)); od = ImageDraw.Draw(overlay)
        od.rectangle([0, 900 - 260, 1600, 900], fill=(0, 0, 0, 210))
        img.alpha_composite(overlay)

    elif idx == 1:  # Cash Flow - the financial lifeblood
        draw.ellipse([-250, 300, 1400, 1200], fill=(13, 104, 74, 255))
        river = Image.new("RGBA", SIZE, (0, 0, 0, 0)); rd = ImageDraw.Draw(river)
        rd.polygon([(0, 780), (600, 480), (760, 540), (1200, 380), (1600, 560),
                    (1600, 900), (0, 900)], fill=(35, 178, 122, 255))
        for i in range(6):
            y = 560 + i * 40
            rd.line([(100, y), (1520, y - 120 * (i % 2))], fill=(180, 255, 214, 120), width=3)
        img.alpha_composite(river)
        _glow(img, [((780, 560), (90, 255, 170, 90), 220)])
        _sparkline(draw, 240, 120, 220, 90, [30, 70, 50, 90, 120], (111, 220, 150, 255))
        overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0)); od = ImageDraw.Draw(overlay)
        od.rectangle([0, 900 - 260, 1600, 900], fill=(0, 0, 0, 210))
        img.alpha_composite(overlay)

    elif idx == 2:  # Investment - building the future (crane + blueprints)
        draw.rectangle([340, 300, 365, 760], fill=(201, 162, 39, 255))
        draw.line([(340, 300), (760, 210)], fill=(201, 162, 39, 255), width=14)
        draw.line([(760, 210), (760, 360)], fill=(201, 162, 39, 255), width=10)
        draw.line([(760, 210), (960, 260)], fill=(201, 162, 39, 255), width=8)
        draw.polygon([(360, 700), (150, 820), (620, 820)], fill=(233, 226, 214, 230))
        draw.rectangle([1080, 480, 1420, 760], fill=(23, 107, 78, 255), outline=(201, 162, 39, 255), width=5)
        for i in range(4):
            for j in range(3):
                draw.rectangle([1100 + i * 78, 510 + j * 80, 1128 + i * 78, 536 + j * 80],
                               fill=(255, 214, 88, 200))
        _glow(img, [((760, 220), (255, 214, 88, 90), 160)])
        _sparkline(draw, 1300, 120, 220, 90, [10, 25, 45, 80, 140], (111, 220, 150, 255))
        overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0)); od = ImageDraw.Draw(overlay)
        od.rectangle([0, 900 - 260, 1600, 900], fill=(0, 0, 0, 210))
        img.alpha_composite(overlay)

    elif idx == 3:  # Risk & stress testing - stormy city
        storm = Image.new("RGBA", SIZE, (0, 0, 0, 0)); sd = ImageDraw.Draw(storm)
        sd.polygon([(200, 80), (140, 340), (260, 340)], fill=(150, 170, 200, 190))
        sd.polygon([(340, 60), (290, 280), (390, 280)], fill=(150, 170, 200, 190))
        for i, x in enumerate(range(0, 1600, 90)):
            sd.rectangle([x, 760 - (i % 3) * 40, x + 60, 800], fill=(180, 195, 220, 80))
        _skyline(img, draw, 700, (150, 170, 200, 60),
                 [80, 60, 110, 70, 95, 60, 120, 75, 90, 105, 65, 85])
        img.alpha_composite(storm)
        top = Image.new("RGBA", SIZE, (0, 0, 0, 0)); td = ImageDraw.Draw(top)
        td.rectangle([0, 0, 1600, 300], fill=(60, 70, 100, 90))
        img.alpha_composite(top)
        _glow(img, [((800, 500), (255, 60, 60, 60), 260)])
        _sparkline(draw, 240, 120, 220, 90, [10, 22, 30, 28, 42, 55], (255, 120, 110, 255))
        overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0)); od = ImageDraw.Draw(overlay)
        od.rectangle([0, 900 - 260, 1600, 900], fill=(0, 0, 0, 210))
        img.alpha_composite(overlay)

    else:  # Optimization - golden network / optimal decision
        nodes = [(420, 400), (760, 260), (800, 620), (1120, 360), (1280, 640)]
        net = Image.new("RGBA", SIZE, (0, 0, 0, 0)); nd = ImageDraw.Draw(net)
        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                nd.line([a, b], fill=(201, 162, 39, 120), width=5)
        for (x, y), size in zip(nodes, (26, 30, 30, 26, 28)):
            nd.ellipse([x - size, y - size, x + size, y + size], fill=(201, 162, 39, 255))
        nd.ellipse([700 - 46, 430 - 46, 700 + 46, 430 + 46], fill=(255, 222, 120, 255))
        img.alpha_composite(net)
        _glow(img, [((700, 430), (255, 214, 88, 100), 190)])
        _sparkline(draw, 240, 120, 220, 90, [20, 35, 30, 50, 45, 70, 90], (255, 214, 88, 255))
        overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0)); od = ImageDraw.Draw(overlay)
        od.rectangle([0, 900 - 260, 1600, 900], fill=(0, 0, 0, 210))
        img.alpha_composite(overlay)

    return img.convert("RGB")


PILLARS = {
    "profitability": {"file": "pillar_profitability.jpg", "title": "Profitability - The Engine of the Business",
                      "desc": "Sales, costs and margins - the engine that powers your business."},
    "cashflow": {"file": "pillar_cashflow.jpg", "title": "Cash Flow - The Financial Lifeblood",
                 "desc": "The money moving in and out - your business must always stay liquid."},
    "investment": {"file": "pillar_investment.jpg", "title": "Investment - Building The Future",
                   "desc": "Where to invest today so the business grows tomorrow. NPV. IRR. Payback."},
    "risk": {"file": "pillar_risk.jpg", "title": "Risk & Stress Testing - Prepare Before The Storm",
             "desc": "Inflation, FX rates, interest rates, costs. Stress-test before the storm hits."},
    "optimization": {"file": "pillar_optimization.jpg", "title": "Optimization - Find The Best Allocation",
                     "desc": "Your resources, alternatives and limits - choose the best way to use your money."},
}


def ensure_assets() -> dict:
    """Generate all 5 pillar images if missing. Returns {key: (path, meta)}."""
    os.makedirs(ASSET_DIR, exist_ok=True)
    result = {}
    for key, meta in PILLARS.items():
        path = os.path.join(ASSET_DIR, meta["file"])
        if not os.path.exists(path):
            img = build_pillar(list(PILLARS).index(key))
            img.save(path, quality=88)
        result[key] = {"path": path, "title": meta["title"], "desc": meta["desc"]}
    return result


def sparkline_svg(values, color="#7BDCA6", w=260, h=70) -> str:
    """Inline SVG sparkline for the bottom of each cinematic card."""
    if not values:
        return ""
    mn, mx = min(values), max(values)
    span = (mx - mn) or 1
    n = len(values)
    parts = []
    for i, v in enumerate(values):
        x = 4 + i * (w - 8) / (n - 1)
        y = h - 6 - (v - mn) / span * (h - 12)
        parts.append(f"{x:.1f},{y:.1f}")
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<polyline points="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="{parts[-1].split(",")[0]}" cy="{parts[-1].split(",")[1]}" r="5" fill="#C9A227"/></svg>'
    )