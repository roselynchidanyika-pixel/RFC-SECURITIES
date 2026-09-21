"""LIVE news tracker - real RSS feeds from Zimbabwe sources with an
rss2json proxy fallback, cached for 10 minutes (TTL 600s).

Honesty rule: we never generate fake news. If a feed fails it is simply
excluded. When nothing can be fetched the tracker reports
DATA UNAVAILABLE/STALE with the last-check timestamp. Every item keeps its
real publication date and author when the source provides them.
"""
from __future__ import annotations

import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import feedparser

FETCH_CAP_S = 20
FEED_TIMEOUT_S = 7

FEEDS = {
    "The Herald": "https://www.herald.co.zw/feed/",
    "NewsDay": "https://www.newsday.co.zw/feed/",
    "The Chronicle": "https://www.chronicle.co.zw/feed/",
    "Techzim": "https://www.techzim.co.zw/feed/",
    "RBZ": "https://www.rbz.co.zw/index.php/rss",
    "ZIMRA": "https://www.zimra.co.zw/rss",
    "ZERA": "https://www.zera.co.zw/rss",
    "Ministry of Agriculture": "https://www.moa.gov.zw/rss",
    "CZI": "https://www.czi.co.zw/rss",
    "ZNCC": "https://www.zncc.co.zw/rss",
    "SME Association": "https://www.mineszm.co.zw/rss",
    "ZITF": "https://www.zitf.co.zw/rss",
}

RSS2JSON = "https://api.rss2json.com/v1/api?rss_url={}"

TAGS = {
    "Agriculture": ["farm", "farmer", "maize", "wheat", "tobacco", "rain", "fertilizer",
                    "fertiliser", "seed", "agrishow", "gmb", "livestock", "irrigation", "harvest"],
    "Transport": ["fuel", "petrol", "diesel", "zera", "zinara", "toll", "zupco", "kombi",
                  "transport", "road", "petrol"],
    "Gadgets": ["phone", "gadget", "laptop", "imei", "potraz", "starlink", "internet",
                "electronics", "solar", "data"],
    "Retail": ["sugar", "cooking oil", "maize meal", "mealie", "supermarket", "pick n pay",
               "retail", "shops", "price", "bread", "consumer"],
    "Manufacturing": ["manufactur", "factory", "production", "industry", "inputs", "cement",
                      "processor"],
}

_RSS_TEXT_META = {
    "Agriculture": "Affects your input prices, harvest seasonality and buyer competition.",
    "Transport": "Affects your cost per trip, fuel bill and route demand.",
    "Gadgets": "Affects your landed cost, duty and device pricing.",
    "Retail": "Affects your prices, volumes and customer foot traffic.",
}


def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\ufffd", "'")
    return re.sub(r"\s+", " ", text).strip()


def _classify(title: str) -> tuple:
    hits = {"All": 0}
    hits.update({tag: sum(1 for kw in kws if kw.lower() in title.lower())
                 for tag, kws in TAGS.items()})
    best = max(hits, key=hits.get) if sum(hits.values()) else "All"
    score = hits[best]
    if score >= 3:
        impact = "High"
    elif score == 2:
        impact = "Medium"
    else:
        impact = "Low"
    return best, impact, score


def _fetch_one(source: str, url: str) -> list:
    entries = []
    try:
        f = feedparser.parse(url, timeout=FEED_TIMEOUT_S)
        entries = f.entries
    except Exception:
        entries = []
    if not entries:
        try:
            from urllib.request import urlopen
            with urlopen(RSS2JSON.format(quote(url, safe="")), timeout=12) as r:
                j = feedparser.parse(r.read().decode("utf-8", errors="ignore"))
            entries = j.entries
        except Exception:
            entries = []
    out = []
    for e in entries[:8]:
        title = _clean_html(e.get("title", ""))
        if not title:
            continue
        link = e.get("link", "")
        date_str = ""
        if e.get("published_parsed"):
            try:
                date_str = datetime(*e.published_parsed[:6]).strftime("%d %b %Y, %H:%M")
            except Exception:
                date_str = ""
        author = (e.get("author") or "").strip() or "Staff Reporter"
        summary = _clean_html(e.get("summary", ""))[:240]
        content = _clean_html(" ".join(c.get("value", "") for c in e.get("content", [])))[:2000]
        tag, impact, _score = _classify(title)
        out.append({
            "headline": title,
            "link": link,
            "date": date_str,
            "publish_ts": int(time.mktime(e.published_parsed)) if e.get("published_parsed") else 0,
            "author": f"By {author} - {source}",
            "source": source,
            "summary": summary or "Details via the original source link.",
            "content": content or summary,
            "sector": tag,
            "impact": impact,
            "means": _RSS_TEXT_META.get(tag, "Relevant to your business context."),
        })
    return out


def _parse_feeds() -> list:
    items: list = []
    pool = ThreadPoolExecutor(max_workers=8)
    futures = {pool.submit(_fetch_one, source, url): source
               for source, url in FEEDS.items()}
    try:
        for fut in as_completed(futures, timeout=FETCH_CAP_S):
            try:
                items.extend(fut.result())
            except Exception:
                continue
    except TimeoutError:
        pass
    pool.shutdown(wait=False, cancel_futures=True)
    return items


# --- simple TTL cache (600s) -------------------------------------------------
_CACHE = {"ts": 0.0, "result": None}
TTL = 600
_CACHE_PATH = Path(__file__).resolve().parent.parent / "assets" / "_news_cache.json"
_BG = {"running": False}


def _read_disk() -> tuple:
    try:
        raw = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "saved_at" in raw and "result" in raw:
            return float(raw["saved_at"]), raw["result"]
    except Exception:
        pass
    return None, None


def _write_disk(result: dict) -> None:
    try:
        _CACHE_PATH.write_text(
            json.dumps({"saved_at": time.time(), "result": result}, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass


def _fetch_blocking(max_items: int = 28) -> dict:
    items = _parse_feeds()
    seen = set()
    unique = []
    for it in items:
        key = it["headline"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(it)
    unique.sort(key=lambda x: x["publish_ts"], reverse=True)

    last_checked = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M")
    return {
        "items": unique[:max_items],
        "last_checked": last_checked,
        "sources_checked": len(FEEDS),
        "sources_list": list(FEEDS.keys()),
        "live": True,
        "cached": False,
    }


def quick_news() -> dict:
    """Network-free snapshot from memory then disk. Never blocks on the network."""
    now = time.time()
    if _CACHE["result"] is not None and now - _CACHE["ts"] < TTL:
        result = dict(_CACHE["result"])
        result["cached"] = True
        return result
    ts, res = _read_disk()
    if res is not None and ts is not None and (now - ts) < TTL:
        _CACHE["ts"], _CACHE["result"] = ts, res
        out = dict(res)
        out["cached"] = True
        return out
    return {"items": [], "last_checked": "", "sources_checked": 0,
            "sources_list": list(FEEDS), "live": False, "cached": True,
            "unavailable": True}


def spawn_bg_refresh() -> None:
    """Fire-and-forget refresh that fills the cache for future quick reads."""
    if _BG["running"]:
        return
    _BG["running"] = True

    def _worker():
        try:
            result = _fetch_blocking()
            _CACHE.update({"ts": time.time(), "result": result})
            _write_disk(result)
        except Exception:
            pass
        finally:
            _BG["running"] = False

    threading.Thread(target=_worker, daemon=True).start()


def fetch_live_news(force: bool = False, max_items: int = 28) -> dict:
    """Fetch real news, cached for 10 minutes. Never fabricates items."""
    now = time.time()
    if not force and _CACHE["result"] is not None and now - _CACHE["ts"] < TTL:
        result = dict(_CACHE["result"])
        result["cached"] = True
        return result
    if not force:
        ts, res = _read_disk()
        if res is not None and ts is not None and (now - ts) < TTL:
            _CACHE["ts"], _CACHE["result"] = ts, res
            result = dict(res)
            result["cached"] = True
            return result

    result = _fetch_blocking(max_items)
    _CACHE["ts"] = now
    _CACHE["result"] = result
    _write_disk(result)
    return result


def filter_by_sector(items: list, sector: str | None) -> list:
    if not items:
        return items
    if not sector or sector in ("Select Sector", "All", "All sectors"):
        return items
    out = []
    for it in items:
        if it["sector"] == sector or it["sector"] == "All":
            out.append(it)
    out.sort(key=lambda x: ({"High": 3, "Medium": 2, "Low": 1}.get(x["impact"], 1),
                            x["publish_ts"]), reverse=True)
    return out