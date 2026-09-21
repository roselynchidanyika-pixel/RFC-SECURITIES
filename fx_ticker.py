"""Live FX / macro ticker.

Honesty rule: real values are only shown when a live source answered. If a
source fails, the item is displayed as DATA UNAVAILABLE/STALE - never a
fabricated rate. A clearly-labelled offline sample mode is available for
local demo use only.
"""
from __future__ import annotations

import requests


def _get_json(url, timeout=8):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "RFC-Securities/1.0"})
        return r.json()
    except Exception:
        return None


def fetch_macro(offline_sample: bool = False) -> dict:
    """Fetch as much real macro data as possible. Returns dict with values +
    'fresh' flags. If offline_sample is True, returns clearly-labelled sample."""
    out = {
        "usd_zwl": None, "usd_zar": None, "inflation": None, "interest": None,
        "fuel_usd": None, "gold": None, "fresh_usd_zwl": False, "fresh_usd_zar": False,
        "fresh_inflation": False, "fresh_interest": False,
        "fresh_fuel": False, "fresh_gold": False, "source": {},
        "sample": offline_sample, "ts": None,
    }
    if offline_sample:
        out.update({"usd_zwl": 26450.32, "usd_zar": 17.42, "inflation": 23.5,
                    "interest": 35.0, "fuel_usd": 1.62, "gold": 2620.0})
        out["source"] = {"usd_zwl": "OFFLINE SAMPLE (stale)", "fuel": "OFFLINE SAMPLE (stale)"}
        return out

    # USD/ZAR + gold from open exchange-rate/commodity endpoints.
    j = _get_json("https://open.er-api.com/v6/latest/USD")
    if j and j.get("result") == "success" and j.get("rates", {}).get("ZAR"):
        out["usd_zar"] = round(j["rates"]["ZAR"], 2)
        out["fresh_usd_zar"] = True
        out["source"]["usd_zar"] = "open.er-api.com"
    jg = _get_json("https://api.gold-api.com/price/XAU")
    if jg and jg.get("price"):
        out["gold"] = round(jg["price"], 0)
        out["fresh_gold"] = True
        out["source"]["gold"] = "gold-api.com"

    # ZWL rate - only shown when an operator-configured authoritative feed
    # (e.g. an RBZ/interbank endpoint) answers. RFC_ZWL_API is a JSON URL with
    # "rate" (USD->ZWL). Without a trusted source the cell is DATA UNAVAILABLE.
    import os
    zwl_url = os.getenv("RFC_ZWL_API")
    if zwl_url:
        jz = _get_json(zwl_url)
        if jz:
            val = jz.get("rate", jz.get("usd_zwl", jz.get("USD_ZWL")))
            try:
                out["usd_zwl"] = round(float(val), 2)
                out["fresh_usd_zwl"] = True
                out["source"]["usd_zwl"] = zwl_url.split("/")[2] if len(zwl_url.split("/")) > 2 else "config"
            except (TypeError, ValueError):
                pass

    # Fuel prices from ZERA (public CSV/JSON if available).
    jf = _get_json("https://www.zera.co.zw/api/fuelprices") or \
         _get_json("https://zera.co.zw/fuelprices.json")
    if jf and isinstance(jf, dict):
        for k in ("petrol", "diesel", "price"):
            if jf.get(k):
                try:
                    out["fuel_usd"] = round(float(str(jf[k]).replace(",", "")), 2)
                    out["fresh_fuel"] = True
                    out["source"]["fuel"] = "ZERA"
                    break
                except (TypeError, ValueError):
                    pass
    return out


def ticker_items(macro: dict) -> list:
    """Build the ticker entries in the CNN style."""
    def cell(label, value, fresh, src):
        if not fresh:
            value = "DATA UNAVAILABLE/STALE"
        return {"label": label, "value": value, "fresh": fresh, "src": src or "—"}

    items = [
        cell("USD/ZWL", f"{macro['usd_zwl']:,.2f}" if macro["usd_zwl"] else None,
             macro["fresh_usd_zwl"], macro["source"].get("usd_zwl")),
        cell("USD/ZAR", f"{macro['usd_zar']:,.2f}" if macro["usd_zar"] else None,
             macro["fresh_usd_zar"], macro["source"].get("usd_zar")),
        cell("Inflation %", f"{macro['inflation']:.1f}" if macro["inflation"] is not None else None,
             macro["fresh_inflation"], macro["source"].get("inflation")),
        cell("RBZ Rate %", f"{macro['interest']:.1f}" if macro["interest"] is not None else None,
             macro["fresh_interest"], macro["source"].get("interest")),
        cell("Fuel (USD)", f"{macro['fuel_usd']:.2f}" if macro["fuel_usd"] else None,
             macro["fresh_fuel"], macro["source"].get("fuel")),
        cell("Gold (USD/oz)", f"{macro['gold']:,.0f}" if macro["gold"] else None,
             macro["fresh_gold"], macro["source"].get("gold")),
    ]
    return items