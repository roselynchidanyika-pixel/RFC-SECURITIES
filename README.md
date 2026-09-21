# RFC SECURITIES

**Turn Uncertainty Into Profitability.**  *Model. Predict. Optimize.*

RFC Securities is a financial modelling & business intelligence advisor for Zimbabwean SMEs,
startups, entrepreneurs, investors and any legitimate business. It reads your business data
(Excel/CSV upload or a built-in demo), connects it to live Zimbabwe economic conditions —
exchange rates, inflation, interest rates, fuel prices, government & policy news — and explains
the results in plain, professional English with sector-specific actions. No academic jargon.

---

## 1. What's inside

| Area | What it does |
| --- | --- |
| **Login** | Dark-green/gold branded screen. Any username + password logs you in for demo access. |
| **Robotic welcome** | Auto-plays after login (gTTS voice). Replay, Mute and Subtitles controls included. |
| **Dashboard** | 5 cinematic pillar cards (Profitability, Cash Flow, Investment, Risk, Optimization) with Ken Burns auto-carousel until you load data, then your product table + key metrics. |
| **Pillar pages** | 5 deep-dive pages. Every chart is expandable and comes with a **🤖 EXPLAIN THIS** block: WHAT AM I LOOKING AT / WHAT CHANGED / WHAT IS THE TREND / WHY / HOW DOES IT AFFECT THE BUSINESS / WHAT SHOULD I INVESTIGATE / WHAT CAN YOU DO + before/after example + cause-effect chain + **Zimbabwe economy connection**. |
| **Investment toolkit** | NPV, IRR, MIRR, Payback, PI, DCF with interactive sliders and plain-English definitions. |
| **Live news tracker** | Real RSS + scrape from The Herald, NewsDay, Chronicle, Techzim, ZIMRA, RBZ, ZERA (cached 10 min). Sector-filtered, relevance-tagged, with a Business Impact Analysis per story. |
| **FX / macro ticker** | Fixed CNN-style bottom ticker. Live where a source answers; otherwise **DATA UNAVAILABLE/STALE** — never fabricated. An optional "offline sample" toggle shows clearly-labelled sample rates. |
| **Simple Business Report** | Mavuno Foods-style management report; download as PDF or send via **WhatsApp** / **Gmail**. |
| **Languages** | Switch the interface between English, Shona and Ndebele. |
| **Honesty rule** | Live data is never invented. Every live item shows its source and refresh status. Business advice is evidence-based ("potentially viable", "requires further validation"), never a profit guarantee. |

---

## 2. Project structure

```
rfc_securities/
├── app.py                     # main entry: login, welcome audio, dashboard, ticker, news
├── pages/
│   ├── 1_Profitability.py
│   ├── 2_CashFlow.py
│   ├── 3_Investment.py
│   ├── 4_Risk.py
│   └── 5_Optimization.py
├── utils/
│   ├── data_loader.py         # demo businesses + Excel/CSV upload parsing
│   ├── analysis.py            # trends, growth, forecasts, liquidity
│   ├── explanation_engine.py  # plain-English explanations & chains
│   ├── news_tracker.py        # live RSS + scrape (sector-aware)
│   ├── fx_ticker.py           # live macro fetch / stale handling
│   ├── report_generator.py    # Simple Business Report (Markdown + PDF)
│   ├── sector_advisor.py      # sector-specific advice
│   ├── translations.py        # English / Shona / Ndebele
│   └── ui.py                  # shared layout, carousel, ticker, sidebar
├── assets/                    # auto-generated pillar images + welcome voice
├── .streamlit/config.toml     # Streamlit theme (dark green #0B3D2E + gold #C9A227)
├── requirements.txt
└── .env.example               # optional config (copy to .env)
```

**Keep `utils/__init__.py` and the `utils/` folder — the app will not import without them.**

---

## 3. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 and log in with any username/password.

---

## 4. Deploy on Streamlit Cloud

1. Push **the whole folder** (including `pages/`, `utils/`, `assets/`, `.streamlit/`, `requirements.txt`) to a GitHub repository. Do **not** use `.gitignore` lines that would exclude `utils/__init__.py` or `.streamlit/config.toml`.
2. On Streamlit Cloud: **Create app → Main file path = `app.py`**, select your repo and branch.
3. Deploy. Create the app once, then decrease the CPU/memory limits to the free tier if you wish.

### If you hit `ModuleNotFoundError` on deploy (redacted error)

The app now imports its own modules by plain name (the app root **and** the
`utils/` folder are placed directly on `sys.path` at boot, so Python's package
resolution of `utils` is never relied on). A remaining `ModuleNotFoundError`
therefore almost always means the deployed copy is **missing the `utils/`
folder or is an old build**. Check, in this order:

1. **Does the GitHub repo actually contain `utils/` with the `.py` files?**
   In GitHub, open the repo and confirm you see `utils/ui.py`,
   `utils/translations.py`, `pages/1_Profitability.py`, `.streamlit/config.toml`
   next to `app.py`. If they are not there, commit them and push again.
2. **Did Streamlit Cloud pick up the newest commit?** On the app page click
   **Manage app → Rebuild** (or redeploy the branch) so Cloud runs the latest
   code — an old build replays the old error.
3. **Did `requirements.txt` install cleanly?** Cloud → *Settings → Packages*
   should list streamlit, pandas, plotly, openpyxl, feedparser, requests,
   beautifulsoup4, python-dotenv, gTTS, Pillow, reportlab with no failures.
4. **Python version**: the code needs Python 3.9 or newer (uses
   `str | None` style annotations, which the app handles on older versions via
   `from __future__ import annotations`). No `runtime.txt` needed.
5. If it still fails, click **Manage app → Logs** and look at the **first**
   frame of the traceback past the redacted banner — that line names the exact
   module that was not found.

As a last resort there is a built-in guard: if the `utils/` files genuinely are
absent from the deployment, the app now shows a clear on-screen message telling
you exactly which folder is missing, instead of a raw error page.

---

## 5. Optional configuration (`.env` or Cloud secrets)

| Variable | Purpose |
| --- | --- |
| `RFC_ZWL_API` | JSON endpoint returning `{"rate": <USD→ZWL>}` from an authoritative source. When set, the ticker shows a live USD/ZWL; when unset it shows **DATA UNAVAILABLE/STALE** instead of a made-up number. |
| `RFC_GMAIL_USER` / `RFC_GMAIL_PASS` | Reserved for in-app SMTP sending (the default **Gmail** button opens a pre-filled email via `mailto:`). |
| `RFC_PHONE` / `RFC_EMAIL` / `RFC_LOCATION` | Contact defaults used in the footer / WhatsApp deep-link. |

**Live-data policy:** on the ticker and news tracker, only values the app really fetched are shown. If a source doesn't answer in time, the item reads `DATA UNAVAILABLE/STALE` and retries. The "Offline sample rates" toggle in the sidebar demonstrates the ticker with rates explicitly labelled *sample*.

---

## 6. Demo businesses

Clothing shop, Grocery shop, Restaurant, Hardware, Transport, Poultry, Salon, Agriculture,
General SME, Gadgets/Electronics — each loaded with 12 months of realistic product-level data
(imports from SA flagged, seasonality, inflation drift), replaceable with your own Excel/CSV.

Uploaded files must contain either:
- a **product list** (columns with `Price` and `Cost`, optionally `Stock`, `Qty Sold`), or
- a **monthly ledger** (a `Month`/`Date` column plus `Revenue` and optionally `Costs`).

---

## 7. Contact

- Phone: 0777 479 118
- Email: chidanyikaroselyn@gmail.com
- Location: Mashava, Masvingo

---

RFC SECURITIES — **EXPLAIN. ANALYSE. PREDICT. STRESS-TEST.**
Simple language. Clear business actions. **Decisions remain with management.** Not a substitute for professional advice.