"""LIVE news tracker - real RSS + scrape from Zimbabwe sources.

Honesty rule: we never generate fake news. If a feed fails the item is
excluded. The tracker reports sources checked and the last-check timestamp.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

import feedparser
import requests
from bs4 import BeautifulSoup

FEEDS = {
    "The Herald": "https://www.herald.co.zw/feed/",
    "NewsDay": "https://www.newsday.co.zw/feed/",
    "Chronicle": "https://www.chronicle.co.zw/feed/",
    "Techzim": "https://www.techzim.co.zw/feed/",
}

SCRAPES = {
    "ZIMRA": "https://www.zimra.co.zw/news",
    "RBZ": "https://www.rbz.co.zw/",
    "ZERA": "https://www.zera.co.zw/",
}

SECTOR_KEYWORDS = {
    "Agriculture": ["farm", "farmer", "maize", "wheat", "tobacco", "rain", "fertilizer",
                    "fertiliser", "seed", "agrishow", "GMB", "livestock", "irrigation", "harvest"],
    "Transport": ["fuel", "petrol", "diesel", "zera", "toll", "zinara", "zupco", "kombi",
                  "road", "transport", "petrol station", "fuel price"],
    "Gadgets": ["phone", "gadget", "laptop", "imei", "potraz", "starlink", "internet",
                "data", "electronics", "tech", "solar"],
    "Grocery": ["sugar", "cooking oil", "maize meal", "mealie", "supermarket", "pick n pay",
                "ok", "price", "food", "bread"],
    "Restaurant": ["restaurant", "food", "cbd", "harare", "safety", "meal", "hospitality",
                   "market"],
    "Clothing": ["clothing", "garment", "textile", "fashion", "uniform", "import"],
    "Poultry": ["poultry", "chicken", "broiler", "feed", "eggs", "chick"],
    "Beauty": ["salon", "beauty", "hair", "cosmetic"],
    "Hardware": ["construction", "cement", "building", "housing", "infrastructure", "tender"],
}


def _relevance(title: str, sector: str) -> tuple:
    kws = SECTOR_KEYWORDS.get(sector, [])
    hits = sum(1 for kw in kws if kw.lower() in title.lower())
    score = min(hits, 3)
    label = ["Low", "Medium", "High"][score] if score > 0 else "Low"
    return label, score


def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\ufffd", "'")
    return re.sub(r"\s+", " ", text).strip()


def _parse_rss():
    items = []
    for source, url in FEEDS.items():
        try:
            f = feedparser.parse(url)
            for e in f.entries[:8]:
                title = _clean_html(e.get("title", ""))
                link = e.get("link", "")
                date_str = ""
                if e.get("published"):
                    try:
                        dt = datetime(*e.published_parsed[:6])
                        date_str = dt.strftime("%d %b %Y, %H:%M")
                    except Exception:
                        date_str = e.get("published", "")[:25]
                author = e.get("author", "") or "Staff Reporter"
                summary = _clean_html(e.get("summary", ""))[:220]
                content = _clean_html(" ".join(c.get("value", "") for c in e.get("content", [])))[:1800]
                items.append({
                    "headline": title, "link": link, "date": date_str,
                    "author": f"By {author} - {source}", "source": source,
                    "summary": summary or "Detail via original source.",
                    "content": content or summary,
                })
        except Exception:
            continue
    return items


def _parse_scrape(source, url):
    items = []
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "RFC-Securities/1.0"})
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        seen = set()
        for a in soup.find_all("a", href=True):
            txt = a.get_text(" ", strip=True)
            if len(txt) < 18 or txt in seen:
                continue
            href = a["href"]
            if not href.startswith("http"):
                href = url.rstrip("/") + ("/" + href.lstrip("/") if href.startswith("/") else href)
            seen.add(txt)
            items.append({
                "headline": txt, "link": href, "date": "",
                "author": f"By {source} Editorial", "source": source,
                "summary": "", "content": "",
            })
            if len(items) >= 6:
                break
    except Exception:
        pass
    return items


def fetch_news(sector_filter: str | None = None, max_items: int = 24) -> dict:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%d %b %Y, %H:%M")
    items = _parse_rss()
    checked_sources = set(FEEDS.keys())
    for src, url in SCRAPES.items():
        scraped = _parse_scrape(src, url)
        if scraped:
            checked_sources.add(src)
        items += scraped
    seen = set()
    unique = []
    for it in items:
        key = it["headline"].lower()
        if key in seen or not it["headline"]:
            continue
        seen.add(key)
        it["sector"], it["score"] = _relevance(it["headline"], sector_filter or "")
        unique.append(it)
    unique = [it for it in unique if it["score"] > 0] if sector_filter else unique
    unique.sort(key=lambda x: (x["score"], x["date"]), reverse=True)
    return {
        "items": unique[:max_items],
        "last_checked": ts,
        "sources_checked": len(checked_sources),
        "sources_list": sorted(checked_sources),
        "live": True,
    }