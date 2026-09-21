"""Cinematic asset generator (Pillow, offline).

Draws the 5 pillar images, the Harare sunset login background and the RFC
logo using the dark-green + gold brand palette. Files are only regenerated
when missing, so hand-crafted replacements with the same filenames are
respected (see assets/README.md).
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFilter

ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
SIZE = (1600, 900)


def _gradient(draw, size, top, bottom):
    w, h = size
    for y in range(h):
        r = int(top[0] + (bottom[0] - top[0]) * y / h)
        g = int(top[1] + (bottom[1] - top[1]) * y / h)
        b = int(top[2] + (bottom[2] - top[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _skyline(img, draw, base_line, color, heights):
    x = 0
    for i, h in enumerate(heights):
        hpx = int(h * (base_line * 0.9))
        draw.rectangle([x, base_line - hpx, x + 90, base_line], fill=color)
        wx = x + 14
        while wx < x + 70:
            wy = base_line - hpx + 16
            while wy < base_line - 14:
                draw.rectangle([wx, wy, wx + 8, wy + 6], fill=(255, 255, 255, 60))
                wy += 22
            wx += 24
        x += 110


def _glow(img, items):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for (x, y), color, r in items:
        od.ellipse([x - r, y - r, x + r, y + r], fill=color)
    img.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(40)))


def _sparkline(draw, x0, y0, w, h, values, color):
    mn, mx = min(values), max(values)
    span = (mx - mn) or 1
    pts = []
    for i, v in enumerate(values):
        px = x0 + i * w / (len(values) - 1)
        py = y0 + h - (v - mn) / span * h
        pts.append((px, py))
    draw.line(pts, fill=color, width=4)
    draw.ellipse([pts[-1][0] - 6, pts[-1][1] - 6, pts[-1][0] + 6, pts[-1][1] + 6],
                 fill=(201, 162, 39, 255))


def build_pillar(idx: int) -> Image:
    img = Image.new("RGBA", SIZE, (11, 61, 46, 255))
    draw = ImageDraw.Draw(img)
    _gradient(draw, SIZE, (17, 74, 58), (6, 34, 26))

    if idx == 0:  # Profitability - engine
        _skyline(img, draw, 700, (232, 226, 214, 90),
                 [60, 90, 45, 120, 70, 100, 55, 130, 80, 115, 60, 95, 75, 120])
        bar = Image.new("RGBA", SIZE, (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
        for x, h in zip([320, 500, 680, 860, 1040], [120, 190, 150, 260, 330]):
            bd.rectangle([x, 700 - h, x + 70, 700], fill=(201, 162, 39, 220))
            bd.polygon([(x + 35, 700 - h - 26), (x, 700 - h - 4), (x + 70, 700 - h - 4)],
                       fill=(255, 214, 88, 240))
        img.alpha_composite(bar)
        _glow(img, [((500, 560), (201, 162, 39, 120), 150)])
        _sparkline(draw, 1300, 120, 220, 90, [40, 60, 55, 80, 70, 100, 130], (111, 220, 150, 255))
    elif idx == 1:  # Cash flow - lifeblood river
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
    elif idx == 2:  # Investment - building the future
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
    elif idx == 3:  # Risk - storm over the city
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
    else:  # Optimization - golden decision network
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
    od.rectangle([0, 900 - 340, 1600, 900], fill=(0, 0, 0, 225))
    img.alpha_composite(overlay)
    return img.convert("RGB")


def build_sunset() -> Image:
    """Blurred Harare sunset cityscape for the login screen."""
    img = Image.new("RGBA", (1280, 800), (201, 162, 39, 255))
    draw = ImageDraw.Draw(img)
    _gradient(draw, (1280, 800), (255, 148, 77), (43, 25, 60))
    draw.ellipse([470, 240, 810, 430], fill=(255, 210, 120, 255))
    _skyline(img, draw, 640, (20, 34, 34, 200),
             [70, 95, 55, 110, 85, 130, 70, 105, 60, 125, 80, 90, 95, 70])
    img = img.filter(ImageFilter.GaussianBlur(6))
    return img.convert("RGB")


PILLARS = {
    "profitability": {
        "file": "pillar_profitability.jpg",
        "title": "PROFITABILITY DRIVERS",
        "sub": "The Engine of the Business",
        "desc": "Understand what drives profitability. Identify what truly drives your profits.",
        "graph": "profitability",
    },
    "cashflow": {
        "file": "pillar_cashflow.jpg",
        "title": "CASH FLOW",
        "sub": "The Financial Lifeblood",
        "desc": "Know where the money is going. Liquidity. Future Cash Position.",
        "graph": "cashflow",
    },
    "investment": {
        "file": "pillar_investment.jpg",
        "title": "INVESTMENT",
        "sub": "Building The Future",
        "desc": "Turn capital into measurable value. NPV, IRR, Payback, DCF, MIRR explained simply and professionally.",
        "graph": "investment",
    },
    "risk": {
        "file": "pillar_risk.jpg",
        "title": "RISK & STRESS TESTING",
        "sub": "Prepare Before The Storm",
        "desc": "Inflation, FX Rates, Interest Rates, Revenue, Costs, Project Delays.",
        "graph": "risk",
    },
    "optimization": {
        "file": "pillar_optimization.jpg",
        "title": "OPTIMIZATION",
        "sub": "Find The Best Allocation",
        "desc": "Resources, Alternatives, Constraints, Optimal Decision.",
        "graph": "optimization",
    },
}


def _draw_text(draw, xy, text, fill, size=78):
    try:
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except Exception:
            font = ImageFont.load_default()
        draw.text(xy, text, fill=fill, font=font)
    except Exception:
        draw.text(xy, text, fill=fill)


def ensure_assets() -> dict:
    """Generate all pillar/sunset/logo files if missing. Returns {key: meta}."""
    os.makedirs(ASSET_DIR, exist_ok=True)
    result = {}
    for key, meta in PILLARS.items():
        path = os.path.join(ASSET_DIR, meta["file"])
        if not os.path.exists(path):
            build_pillar(list(PILLARS).index(key)).save(path, quality=90)
        result[key] = dict(meta, path=path)

    sunset_path = os.path.join(ASSET_DIR, "harare_sunset.jpg")
    if not os.path.exists(sunset_path):
        build_sunset().save(sunset_path, quality=82)

    logo_path = os.path.join(ASSET_DIR, "rfc_logo.png")
    if not os.path.exists(logo_path):
        logo = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
        d = ImageDraw.Draw(logo)
        d.rounded_rectangle([18, 18, 342, 342], radius=40, fill=(11, 61, 46, 250),
                            outline=(201, 162, 39, 255), width=10)
        _draw_text(d, (78, 120), "RFC", (201, 162, 39, 255), 96)
        logo.save(logo_path)

    return {
        **result,
        "sunset": sunset_path,
        "logo": logo_path,
    }


def sparkline_svg(values, color="#7BDCA6", w=260, h=46) -> str:
    """Inline SVG sparkline shown at the bottom of every cinematic card."""
    if not values:
        return ""
    mn, mx = min(values), max(values)
    span = (mx - mn) or 1
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = 4 + i * (w - 8) / (n - 1)
        y = h - 4 - (v - mn) / span * (h - 8)
        pts.append(f"{x:.1f},{y:.1f}")
    last = pts[-1]
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="{last.split(",")[0]}" cy="{last.split(",")[1]}" r="5" fill="#C9A227"/></svg>')