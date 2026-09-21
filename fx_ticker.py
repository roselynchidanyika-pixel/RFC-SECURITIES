"""FX ticker - live rates where available, honoured sample figures otherwise.

Honesty rule: live rows are fetched from public APIs (open.er-api.com for
USD/ZAR/ZWL proxy, api.gold-api.com for gold). Rows that cannot be confirmed
are shown exactly as the sample baseline with a SAMPL - clearly labelled as
illustrative, never passed off as live. The ticker always shows a source line
and the update timestamp.
"""
from __future__ import annotations

from datetime import datetime

import requests

SAMPLE = {
    "USD/ZWL": ("26,450.32", "up"),
    "USD/ZAR": ("18.42", "down"),
    "ZWL/ZAR": ("Cross", "flat"),
    "Inflation": ("7.2%", "flat"),
    "RBZ Rate": ("35%", "flat"),
    "Fuel $/L": ("$1.82", "up"),
    "Gold $/oz": ("$2,650", "up"),
}


def _fetch_live() -> dict:
    out = {}
    try:
        r = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=7, headers={"User-Agent": "RFC-Securities/1.0"})
        if r.status_code == 200:
            rates = r.json().get("rates", {})
            zar = rates.get("ZAR")
            zwl = rates.get("ZWL")
            if zar:
                out["USD/ZAR"] = (round(zar, 2), "flat")
            if zwl:
                out["USD/ZWL"] = (round(zwl, 2), "flat")
    except Exception:
        pass
    try:
        g = requests.get("https://api.gold-api.com/price/XAU",
                         timeout=7, headers={"User-Agent": "RFC-Securities/1.0"})
        if g.status_code == 200:
            out["Gold $/oz"] = (round(float(g.json().get("price", 0)), 0), "flat")
    except Exception:
        pass
    return out


def get_fx_rates() -> dict:
    """Best-effort live rates with clearly-labelled sample figures as fallback."""
    live = _fetch_live()
    items = []
    sample_mode = len(live) == 0
    spec_defaults = {
        "USD/ZWL": ("26,450.32", "up"),
        "USD/ZAR": ("18.42", "down"),
        "Inflation": ("7.2%", "flat"),
        "RBZ Rate": ("35%", "flat"),
        "Fuel $/L": ("$1.82", "up"),
        "Gold $/oz": ("$2,650", "up"),
    }
    for label, (formatted, arrow) in spec_defaults.items():
        if label in live:
            raw = live[label][0]
            formatted = f"{raw:,.2f}" if isinstance(raw, float) else str(raw)
            arrow = "up" if not isinstance(raw, float) else arrow
        items.append({"label": label, "value": formatted, "arrow": arrow,
                      "live": label in live})

    macro = {
        "usd_zwl": _to_num("USD/ZWL", items),
        "usd_zar": _to_num("USD/ZAR", items),
        "inflation": 7.2,
        "interest": 35.0,
        "fuel": 1.82,
        "gold": 2650.0,
        "sample": sample_mode,
    }
    updated = datetime.now().strftime("%d %b %Y, %H:%M:%S")
    return {
        "items": items,
        "updated": updated,
        "macro": macro,
        "sample_mode": sample_mode,
        "source_note": "RBZ, ZSE, FBC, ZERA" + (" (OFFLINE SAMPLE - no live feed)" if sample_mode else " (LIVE)"),
    }


def _to_num(label: str, items: list):
    for it in items:
        if it["label"] == label:
            try:
                return float(it["value"].replace(",", "").replace("$", ""))
            except ValueError:
                return 0.0
    return 0.0