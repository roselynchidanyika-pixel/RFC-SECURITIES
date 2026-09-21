"""RFC SECURITIES - Turn Uncertainty Into Profitability. Model. Predict. Optimize.

Single-page Streamlit app: login with a robotic (speechSynthesis) welcome,
cinematic 5-pillar dashboard, business-data upload or demo data, live news,
a bottom CNN-style FX ticker and a Simple Business Management Report with a
"Download PDF" button plus WhatsApp/Gmail delivery.

ADVANTAGES (implemented in this build):
  - Only tool that reads the graph, understands the trend, connects it to the
    Zimbabwe economy, explains it in plain professional English and quantifies
    the impact on the specific business.
  - Sector-specific real Zimbabwe data (fuel, tolls, ZERA, ZINARA, ZIMRA duty,
    POTRAZ IMEI, Agrishow, fertiliser prices, OK/TM price war).
  - Live current news with date, author and full article on click, rss2json
    fallback, 10-minute cache.
  - Live FX ticker with clearly-labelled offline sample mode.
  - Cinematic pillar pictures (Ken Burns) expanding into Bloomberg-style
    Plotly charts with hover tooltips and a 3M/6M/12M selector.
  - Uploaded products, prices and margins visible with Fast/Slow status.
  - Regional sourcing engine (Zim vs SA landed cost: FX, transport, duty,
    clearing, storage) via the SA-import flags and supplier-cost modelling.
  - Seasonal intelligence: what to stock and when; holding-risk and
    break-even reasoning; never treats an assumption as fact.
  - Never fabricates live data: every live line shows source + timestamp -
    otherwise DATA UNAVAILABLE/STALE.
  - Never guarantees profit: advice uses "potentially viable", "under
    assumptions", "requires validation", "market evidence indicates".
  - WhatsApp/Gmail report delivery, English/Shona/Ndebele, robotic welcome.

LIMITATIONS (see README.md):
  - Requires an accurate Excel/CSV upload.
  - Live news and FX need internet; RBZ/ZIMRA APIs can be down.
  - Not a replacement for a chartered accountant, auditor or lawyer.
  - Shona/Ndebele translation is ongoing; USSD feature-phone access is on the
    roadmap; seasonal forecasts improve with more historical data; a black-swan
    event cannot be predicted.
"""
from __future__ import annotations

import os
import sys

# --- import bootstrap (works on Streamlit Cloud without repo layout tricks) ---
_ROOT = os.path.dirname(os.path.abspath(__file__))
for _p in (_ROOT, os.path.join(_ROOT, "utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

st.set_page_config(page_title="RFC SECURITIES", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

from assets_gen import ensure_assets
from data_loader import load_demo_data
from fx_ticker import get_fx_rates
from news_tracker import fetch_live_news, quick_news, spawn_bg_refresh
from ui import (inject_css, init_state, render_cinematic, render_footer,
                render_login, render_news, render_sidebar, render_ticker,
                render_upload_view, render_welcome, _make_report)

DARK = {"paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#F2EDE4"}, "hoverlabel": {"bgcolor": "#0B3D2E"}}


def main():
    init_state()
    assets = ensure_assets()

    if not st.session_state["authenticated"]:
        render_login(st.session_state["lang"], assets["sunset"])
        render_footer()
        st.stop()

    fx = get_fx_rates()
    st.session_state["fx"] = fx
    render_ticker(fx)

    if st.session_state.get("play_welcome") and not st.session_state.get("welcome_triggered"):
        st.session_state["welcome_triggered"] = True
        render_welcome()

    render_sidebar(assets)

    _brand_header(assets)

    if st.session_state.get("show_report"):
        _report_view()

    _dashboard(assets)
    _news_section()
    render_footer()


def _brand_header(assets):
    import base64
    logo = base64.b64encode(open(assets["logo"], "rb").read()).decode()
    st.markdown(
        f'<div class="brand" style="margin-bottom:6px;">'
        f'<img src="data:image/png;base64,{logo}" style="width:42px;height:42px;border-radius:12px;">'
        f'<div><div style="color:#C9A227;font-weight:900;letter-spacing:1px;font-size:1.2rem;">RFC SECURITIES</div>'
        f'<div style="color:#F2EDE4;opacity:.8;font-size:.82rem;">'
        f'Turn Uncertainty Into Profitability. · Model. Predict. Optimize.</div></div></div>',
        unsafe_allow_html=True)


def _report_view():
    rep = st.session_state.get("report")
    if not rep:
        return
    st.markdown("## 📄 SIMPLE BUSINESS MANAGEMENT REPORT")
    st.caption(f"Business: <b>{rep['business_name']}</b> · Period: {rep['period']} · RFC SECURITIES",
               unsafe_allow_html=True)
    for line in rep["lines"]:
        if line.startswith("#TITLE "):
            st.markdown(f"### {_md(line[7:])}")
        elif line.startswith("#H "):
            st.markdown(f"#### {_md(line[3:])}")
        else:
            st.markdown(_md(line))
    c1, c2, c3 = st.columns(3)
    c1.download_button("⬇ Download PDF", rep["pdf_bytes"],
                       file_name="rfc_securities_report.pdf", mime="application/pdf")
    if c2.button("WhatsApp Send"):
        from urllib.parse import quote
        url = f"https://wa.me/263777479118?text={quote(rep['text'][:3500], safe='')}"
        c2.markdown(f'<a href="{url}" target="_blank" style="color:#C9A227;">Open WhatsApp ➜</a>',
                    unsafe_allow_html=True)
    if c3.button("Gmail Send"):
        from urllib.parse import quote
        subj = quote(f"RFC Securities Report - {rep['business_name']}")
        body = quote(rep["text"][:25000], safe="")
        c3.markdown(f'<a href="mailto:chidanyikaroselyn@gmail.com?subject={subj}&body={body}" '
                    f'style="color:#C9A227;">Open Gmail ➜</a>', unsafe_allow_html=True)
    if st.button("✖ CLOSE REPORT"):
        st.session_state["show_report"] = False
        inject_css()
        import streamlit as _s
        _s.rerun()
    st.markdown("---")


def _md(s: str) -> str:
    return s.replace("_" * 50, "")


def _dashboard(assets):
    bundle = st.session_state.get("bundle")
    source = st.session_state.get("source")

    if bundle is None:
        illust = load_demo_data("General SME")
        st.session_state["_illust"] = illust
        render_cinematic(assets, illust, _macro(), "General", st.session_state["lang"])
        st.info("Choose a demo business or upload your own data from the left panel "
                "to see these pillars powered by YOUR numbers.", icon="💡")
        return

    data = bundle
    econ = _macro()
    sector = bundle["sector"]
    if source == "upload" and not st.session_state.get("back_cinematic"):
        st.markdown(f"### 📊 {bundle['name']} — Uploaded Data")
        st.caption("Margin% = (Price - Cost) / Price × 100 · Status: Fast if margin > 25%, else Slow. "
                   "This table feeds the cinematic charts and the report below.")
        render_upload_view(bundle)
        if st.button("🎬 Back to Cinematic View", width="stretch"):
            st.session_state["back_cinematic"] = True
            st.rerun()
        return

    if st.session_state.get("back_cinematic") and bundle is not None:
        if st.button("📊 Show Uploaded Data Table"):
            st.session_state["back_cinematic"] = False
            st.rerun()
    banner = "DEMO data — upload your own from the left panel." if bundle.get("is_demo") \
        else "YOUR uploaded data — used live across every chart."
    st.info(f"🟢 {banner}", icon="📈")
    render_cinematic(assets, data, econ, sector, st.session_state["lang"])


def _news_section():
    bundle = st.session_state.get("bundle")
    sector = bundle["sector"] if bundle else None
    force = bool(st.session_state.get("refresh_clicked"))
    if force:
        try:
            with st.spinner(t(st.session_state["lang"], "news_loading")):
                news = fetch_live_news(force=True)
        except Exception:
            news = {"items": [], "last_checked": "unavailable", "sources_checked": 0,
                    "sources_list": [], "live": False}
        st.session_state["refresh_clicked"] = False
    else:
        news = quick_news()
        spawn_bg_refresh()
    if sector:
        from news_tracker import filter_by_sector
        news = dict(news, items=filter_by_sector(news.get("items", []), sector))
    render_news(news, bundle, st.session_state["lang"])


def _macro():
    fx = st.session_state.get("fx")
    if fx is None:
        fx = get_fx_rates()
        st.session_state["fx"] = fx
    return fx.get("macro", {})


if __name__ == "__main__":
    main()