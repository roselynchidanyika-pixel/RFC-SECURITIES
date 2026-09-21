"""Shared UI components: global CSS, login card, sidebar, FX ticker, footer,
cinematic carousel, and the chart + explanation display helper."""
from __future__ import annotations

import base64
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from assets_gen import ensure_assets, sparkline_svg
from translations import t

GREEN = "#0B3D2E"
GOLD = "#C9A227"


def b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def inject_css():
    st.markdown(
        """
        <style>
        :root { --rfc-gold: #C9A227; --rfc-green: #0B3D2E; --rfc-cream: #F2EDE4; }
        html, body, .stApp { background: var(--rfc-green); }
        .stApp { background: radial-gradient(1200px 500px at 20% -10%, #10493A 0%, #0B3D2E 55%, #072A20 100%); }
        h1, h2, h3, h4 { color: var(--rfc-gold) !important; letter-spacing: .3px; }
        .brand { display:flex; align-items:center; gap:12px; }
        .logo-badge { width:46px; height:46px; border-radius:12px;
          background: linear-gradient(135deg, var(--rfc-gold), #f2d77a);
          display:flex; align-items:center; justify-content:center;
          font-weight:900; color:var(--rfc-green); font-size:20px; box-shadow: 0 2px 12px #0006; }
        .logo-arrow { color:#0B5C42; }
        .tagline { color: var(--rfc-gold); font-weight:600; letter-spacing:2px; }
        .subtag { color: var(--rfc-cream); opacity:.85; letter-spacing:4px; font-size:.85rem; }

        /* Login */
        .login-wrap { display:flex; align-items:center; justify-content:center; min-height:100vh; gap:40px; flex-wrap:wrap; }
        .login-left { max-width:420px; }
        .login-card { background:#0E4A37cc; border:1px solid var(--rfc-gold); border-radius:18px;
          padding:26px 28px; width:340px; box-shadow:0 20px 60px #000a; backdrop-filter: blur(6px); }
        .login-card input { width:100%; padding:10px 12px; margin:6px 0 12px 0; border-radius:8px;
          border:1px solid #3f7a63; background:#0B3D2E; color:var(--rfc-cream); }
        .login-btn { width:100%; padding:11px; border-radius:8px; border:none; cursor:pointer;
          background:var(--rfc-gold); color:#0B3D2E; font-weight:800; font-size:1rem; }
        .login-btn:hover { filter:brightness(1.08); }

        /* Robot */
        .robot { position: fixed; top:16px; right:22px; z-index: 999; display:flex; justify-content:flex-end; align-items:center; gap:10px;}
        .bubble { background:#0E4A37; border:1px solid var(--rfc-gold); color:var(--rfc-cream);
          border-radius:14px 14px 4px 14px; padding:10px 14px; max-width:280px; font-size:.9rem;
          box-shadow:0 8px 24px #000a; }
        @keyframes wave { 0%,100% { transform: rotate(0); } 20% { transform: rotate(-14deg);} 40% { transform: rotate(10deg);} 60% { transform: rotate(-8deg);} 80%{transform: rotate(6deg);} }
        .robot-fig { font-size:2.3rem; animation: wave 3s ease-in-out infinite; }

        /* Cinematic card */
        .cine { position:relative; border-radius:18px; overflow:hidden; margin-bottom:22px;
          box-shadow:0 18px 50px #000a; border:1px solid #1d5a44; }
        .cine img { width:100%; height:460px; object-fit:cover; animation: kb 26s ease-in-out infinite alternate; transform-origin:center; }
        @keyframes kb { from { transform: scale(1.0); } to { transform: scale(1.14); } }
        .cine-veil { position:absolute; inset:0; background: linear-gradient(to top, #07150f 0%, #07150fe6 18%, #0000 60%); }
        .cine-copy { position:absolute; left:26px; bottom:18px; right:26px; color:var(--rfc-cream); }
        .cine-copy h3 { margin:0 0 6px 0; }
        .cine-copy p { margin:0 0 10px 0; opacity:.95; }
        .cine-spark { position:absolute; left:26px; bottom:96px; right:26px; opacity:.95; }
        .cine-tag { position:absolute; top:14px; left:14px; background:#0B3D2Ed9; border:1px solid var(--rfc-gold);
          color:var(--rfc-gold); font-weight:800; letter-spacing:2px; padding:4px 10px; border-radius:999px; font-size:.75rem;}

        /* Ticker */
        .ticker { position: fixed; left:0; right:0; bottom:0; z-index: 998; background:#061811;
          border-top:2px solid var(--rfc-gold); color:var(--rfc-cream); font-family:monospace;
          font-size:.82rem; overflow:hidden; white-space:nowrap; padding:6px 0; }
        .ticker-track { display:inline-block; padding-left:100%; animation: scroll 40s linear infinite; }
        @keyframes scroll { from { transform: translateX(0); } to { transform: translateX(-100%); } }
        .tick-cell { display:inline-block; padding:0 22px; }
        .tick-up { color:#7BDCA6; } .tick-down { color:#ff7b6b; } .tick-stale { color:#ffbf47; }

        /* Footer */
        .rfc-footer { position: relative; margin-top: 40px; padding: 22px 8px 54px 8px; border-top:1px solid #1d5a44;
          color: var(--rfc-cream); font-size:.85rem; text-align:center; }
        .rfc-footer a { color: var(--rfc-gold); }

        div[data-testid="stSidebar"] { background:#082b21; }
        div[data-testid="stFileUploaderDropzone"] { border:1px dashed var(--rfc-gold); border-radius:12px;}
        .rfc-quote { color:#e8dfc8; font-size:1.05rem; font-style:italic; text-align:center; padding:6px 0 2px 0;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------------
def render_login(lang: str):
    inject_css()
    assets = ensure_assets()
    hero = assets["risk"]["path"]
    b = b64(hero)
    st.markdown(
        f"""
        <div class="login-wrap">
          <div class="login-left">
            <div class="brand" style="margin-bottom:18px;">
              <div class="logo-badge">RFC <span class="logo-arrow">▲</span></div>
              <div>
                <div class="tagline" style="font-size:1.35rem;">{t(lang,'app_name')}</div>
                <div style="color:var(--rfc-cream);">Turn Uncertainty Into Profitability.</div>
                <div class="subtag">MODEL. PREDICT. OPTIMIZE.</div>
              </div>
            </div>
            <div style="color:var(--rfc-cream); font-size:1rem; line-height:1.5;">
              RFC Securities reads your business data, connects it to the Zimbabwe economy -
              inflation, exchange rates, fuel, interest rates, policy news - and then explains
              what is happening in plain English, with actions you can take today.
            </div>
          </div>
          <div class="login-card">
            <div style="font-weight:800; color:var(--rfc-gold); font-size:1.1rem;">{t(lang,'login_title')}</div>
            <div style="color:var(--rfc-cream); font-size:.85rem;">{t(lang,'login_hint')}</div>
            <label style="color:var(--rfc-cream); font-size:.9rem;">{t(lang,'login_user')}</label>
            <input id="rfc-user" placeholder="you@business.co.zw">
            <label style="color:var(--rfc-cream); font-size:.9rem;">{t(lang,'login_pass')}</label>
            <input id="rfc-pass" type="password" placeholder="••••••••">
            <button class="login-btn" onclick="loginRfc()">{t(lang,'login_btn')}</button>
          </div>
        </div>
        <script>
        function loginRfc() {{
          const u = document.getElementById('rfc-user').value;
          const p = document.getElementById('rfc-pass').value;
          const el = document.createElement('input');
          el.type = 'hidden'; el.id = 'rfc-login'; el.value = u + '|' + p;
          el.dataset.user = u || 'manager';
          document.body.appendChild(el);
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )
    st.text_input("Username / Email", key="rfc_login_user", label_visibility="collapsed",
                  placeholder=t(lang, "login_user"))
    st.text_input("Password", type="password", key="rfc_login_pass", label_visibility="collapsed",
                  placeholder=t(lang, "login_pass"))
    if st.button(t(lang, "login_btn"), type="primary", width="stretch"):
        st.session_state["authenticated"] = (
            st.session_state.get("rfc_login_user", "").strip() != "" and
            st.session_state.get("rfc_login_pass", "") != ""
        )
        st.session_state["user"] = st.session_state.get("rfc_login_user", "manager")
        st.session_state["play_welcome"] = True
        st.rerun()
    st.markdown(f'<div style="background:#0B3D2E; border-radius:14px; padding:14px;">'
                f'<div style="background-image:linear-gradient(0deg,#081f16,#0a3124), url("data:image/jpeg;base64,{b}"); '
                f'background-size:cover; background-position:center; border-radius:14px; height:180px;"></div></div>',
                unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def _init_state():
    defaults = {
        "authenticated": False, "user": "", "lang": "en", "source": None,
        "bundle": None, "play_welcome": False, "subtitles": False,
        "muted": False, "show_report": False, "sector_filter": "All sectors",
        "report": None, "cinematic": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_bundle():
    return st.session_state.get("bundle")


def page_boot(page_title: str, page_icon: str = "📈"):
    """Standard bootstrap for every page: config, css, auth guard, sidebar,
    ticker and footer. Returns the current macro dict."""
    _init_state()
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout="wide",
                       initial_sidebar_state="expanded")
    inject_css()
    page_guard()
    render_global_sidebar()
    macro = _load_macro()
    render_ticker(macro)
    return macro


def page_guard():
    """Call at the top of every page: stops if not logged in."""
    _init_state()
    if not st.session_state.get("authenticated"):
        st.warning("Please log in first.")
        st.stop()


def welcome_audio_html(lang: str) -> tuple[str | None, bytes | None]:
    """Generate (or load) the robotic welcome greeting. Returns (html, bytes)."""
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "welcome_en.mp3")
    text = ("Welcome to RFC Securities. We turn business uncertainty into financial clarity. "
            "RFC Securities helps startups, SMEs and organisations understand profitability, cash flow, "
            "investment opportunities, risks and the best way to allocate their money. We analyse your "
            "business data together with current Zimbabwe market conditions, exchange rates, inflation, "
            "interest rates, government programmes, seasonal demand and market opportunities. We then "
            "explain the results in simple language, identify potential opportunities and risks, and "
            "provide practical financial insights to help you make informed business decisions. You can "
            "receive your complete report through WhatsApp or Gmail. Welcome to RFC Securities — Turn "
            "Uncertainty Into Profitability.")
    audio = None
    if os.path.exists(path):
        with open(path, "rb") as f:
            audio = f.read()
    else:
        try:
            from gtts import gTTS
            gTTS(text=text, lang="en").save(path)
            with open(path, "rb") as f:
                audio = f.read()
        except Exception:
            audio = None
    if not audio:
        return None, None
    b = base64.b64encode(audio).decode()
    html = (
        '<div style="position:fixed; right:22px; bottom:60px; z-index:997; max-width:300px;">'
        '<audio controls autoplay style="width:100%;">'
        f'<source src="data:audio/mpeg;base64,{b}" type="audio/mpeg"></audio></div>')
    return html, audio


def render_global_sidebar():
    """Full sidebar: branding, upload, demo, language, sector filter, report actions."""
    _init_state()
    lang = st.session_state["lang"]
    st.sidebar.markdown(
        '<div class="brand" style="margin-bottom:4px;">'
        '<div class="logo-badge" style="width:34px;height:34px;font-size:14px;">RFC▲</div>'
        f'<span style="color:var(--rfc-gold);font-weight:800;">{t(lang,"app_name")}</span></div>',
        unsafe_allow_html=True)
    st.sidebar.markdown(
        f'<div style="font-size:.8rem; color:var(--rfc-cream); margin-bottom:10px;">'
        f'{t(lang,"sidebar_upload_hint")}</div>', unsafe_allow_html=True)

    from data_loader import demo_sectors, load_demo, load_uploaded
    upload = st.sidebar.file_uploader(
        t(lang, "sidebar_upload"), type=["xlsx", "xls", "csv"],
        help=t(lang, "sidebar_upload_hint"))
    if upload is not None:
        try:
            st.session_state["bundle"] = load_uploaded(upload.getvalue(), upload.name)
            st.session_state["source"] = "upload"
            st.session_state["show_report"] = False
            st.sidebar.success("Uploaded data loaded.")
            st.rerun()
        except ValueError as ex:
            st.sidebar.error(str(ex))

    sectors = demo_sectors()
    if "demo_sel" not in st.session_state:
        st.session_state["demo_sel"] = "General SME"
    demo = st.sidebar.selectbox(
        t(lang, "sidebar_demo"), sectors,
        index=sectors.index(st.session_state.get("demo_sel", "General SME")),
        key="demo_sel_box")
    if st.sidebar.button(f"▶ {t(lang,'sidebar_demo')}: {demo}", width="stretch"):
        st.session_state["bundle"] = load_demo(demo)
        st.session_state["source"] = "demo"
        st.session_state["demo_sel"] = demo
        st.session_state["show_report"] = False
        st.rerun()

    if st.session_state.get("source") is None and st.session_state.get("bundle") is None:
        st.session_state["bundle"] = load_demo("General SME")
        st.session_state["source"] = "demo"
        st.session_state["demo_sel"] = "General SME"

    lang_selected = st.sidebar.selectbox(
        t(lang, "sidebar_lang"), ["English", "Shona", "Ndebele"],
        index=["en", "sn", "nd"].index(lang))
    st.session_state["lang"] = {"English": "en", "Shona": "sn", "Ndebele": "nd"}[lang_selected]

    offline = st.sidebar.toggle("Offline sample rates (clearly labelled)",
                                value=bool(st.session_state.get("offline_mode", False)),
                                help="ON: shows SAMPLE rates marked as samples for offline demo "
                                     "(never used to claim a real live rate). OFF: live sources only; "
                                     "unreachable items show DATA UNAVAILABLE/STALE.")
    st.session_state["offline_mode"] = offline

    filters = ["All sectors", "Agriculture", "Transport", "Gadgets", "Grocery",
               "Restaurant", "Clothing", "Poultry", "Beauty", "Hardware"]
    st.session_state["sector_filter"] = st.sidebar.selectbox(
        t(lang, "sidebar_sector_filter"), filters,
        index=filters.index(st.session_state["sector_filter"]))

    st.sidebar.markdown("---")
    st.sidebar.caption("💰 Report")
    bundle = get_bundle()
    if bundle is not None:
        if st.sidebar.button(t(lang, "sidebar_report"), width="stretch"):
            _generate_report()
        if st.session_state.get("report"):
            pdf = st.session_state["report"].get("pdf")
            if pdf:
                st.sidebar.download_button("⬇ Download PDF Report", pdf,
                                           file_name="rfc_report.pdf", mime="application/pdf",
                                           width="stretch")
    st.sidebar.markdown("---")
    st.sidebar.caption("📤 Send report")
    if st.sidebar.button("WhatsApp", width="stretch"):
        _send_whatsapp()
    if st.sidebar.button("Gmail", width="stretch"):
        _send_gmail()
    st.sidebar.markdown(
        f'<div style="font-size:.72rem;color:var(--rfc-cream);opacity:.8;margin-top:6px;">'
        f'{t(lang,"footer_disclaimer")}</div>', unsafe_allow_html=True)


def _generate_report():
    from report_generator import build_report, report_pdf
    bundle = get_bundle()
    if bundle is None:
        st.sidebar.warning("No data loaded.")
        return
    econ = _load_macro()
    news = _load_news(st.session_state.get("sector_filter", "All sectors"))
    rep = build_report(bundle, econ, news)
    rep["pdf"] = report_pdf(rep)
    st.session_state["report"] = rep
    st.session_state["show_report"] = True


def render_report_view():
    """Render the generated report in the main area."""
    rep = st.session_state.get("report")
    if not rep:
        return
    with st.expander("📄 SIMPLE BUSINESS MANAGEMENT REPORT - click to open / close", expanded=False):
        for line in rep["lines"]:
            st.markdown(line)
        st.download_button("⬇ Download PDF Report", rep["pdf"], file_name="rfc_report.pdf",
                           mime="application/pdf")


def _send_whatsapp():
    from urllib.parse import quote
    from report_generator import build_report, whatsapp_text
    bundle = get_bundle()
    if bundle is None:
        st.sidebar.warning("No data loaded.")
        return
    rep = build_report(bundle, _load_macro(), _load_news("All sectors"))
    text = whatsapp_text(rep)
    number = "263777479118"
    url = f"https://wa.me/{number}?text={quote(text)}"
    html = f'<a href="{url}" target="_blank" style="color:#C9A227;">Open WhatsApp to send the report ➜</a>'
    st.sidebar.markdown(html, unsafe_allow_html=True)
    st.sidebar.caption("WhatsApp will open with the report ready to send.")


def _send_gmail():
    from urllib.parse import quote
    from report_generator import build_report, gmail_body
    bundle = get_bundle()
    if bundle is None:
        st.sidebar.warning("No data loaded.")
        return
    rep = build_report(bundle, _load_macro(), _load_news("All sectors"))
    body = quote(gmail_body(rep))
    subj = quote(f"RFC Securities Report - {bundle['business'].name}")
    url = (f"mailto:chidanyikaroselyn@gmail.com?subject={subj}&body={body}")
    st.sidebar.markdown(f'<a href="{url}" style="color:#C9A227;">Open Gmail with the report pre-filled ➜</a>',
                        unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Data caches (live fetches)
# ----------------------------------------------------------------------------
@st.cache_data(ttl=180, show_spinner=False)
def _load_macro_cached(offline: bool) -> dict:
    from fx_ticker import fetch_macro
    try:
        return fetch_macro(offline_sample=offline)
    except Exception:
        return {"sample": offline, "fresh_usd_zar": False, "fresh_usd_zwl": False,
                "fresh_inflation": False, "fresh_interest": False,
                "fresh_fuel": False, "fresh_gold": False, "source": {},
                "usd_zar": None, "usd_zwl": None, "inflation": None,
                "interest": None, "fuel_usd": None, "gold": None}


def _load_macro() -> dict:
    offline = bool(st.session_state.get("offline_mode", False))
    return _load_macro_cached(offline)


@st.cache_data(ttl=600, show_spinner=False)
def _load_news(sector_filter: str) -> dict:
    from news_tracker import fetch_news
    if sector_filter == "All sectors":
        sector_filter = None
    try:
        return fetch_news(sector_filter)
    except Exception:
        return {"items": [], "last_checked": "unavailable", "sources_checked": 0,
                "sources_list": [], "live": False}


# ----------------------------------------------------------------------------
# Ticker + footer
# ----------------------------------------------------------------------------
def render_ticker(macro: dict):
    from fx_ticker import ticker_items
    now = datetime.now().strftime("%H:%M:%S")
    sample = macro.get("sample")
    src_note = "OFFLINE SAMPLE MODE - rates are not live" if sample else "Live sources: er-api, gold-api, ZERA, RBZ* where reachable"
    cells = []
    for it in ticker_items(macro):
        val = it["value"] if it["value"] else "DATA UNAVAILABLE/STALE"
        cls = "tick-stale" if not it["fresh"] else "tick-up"
        cells.append(
            f'<span class="tick-cell">{it["label"]} <span class="{cls}">{val}</span> '
            f'<span style="opacity:.6">[{it["src"]}]</span></span>')
    st.markdown(
        f'<div class="ticker"><span class="ticker-track">'
        f'<span class="tick-cell" style="color:var(--rfc-gold);font-weight:800;">LIVE</span>'
        f'<span class="tick-cell" style="opacity:.7">• Updated: {now}</span>'
        f'<span class="tick-cell" style="opacity:.7">• {src_note}</span>'
        + "".join(cells) * 2 +
        f'</span></div>',
        unsafe_allow_html=True)


def render_footer():
    st.markdown(
        f"""
        <div class="rfc-footer">
          📞 0777 479 118 &nbsp;•&nbsp; ✉ <a href="mailto:chidanyikaroselyn@gmail.com">chidanyikaroselyn@gmail.com</a>
          &nbsp;•&nbsp; 📍 Mashava, Masvingo<br>
          <div style="opacity:.85; margin-top:8px;">RFC SECURITIES — EXPLAIN. ANALYSE. PREDICT. STRESS-TEST.<br>
          Simple language. Clear business actions. Decisions remain with management.</div>
        </div>
        """,
        unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Cinematic carousel
# ----------------------------------------------------------------------------
def render_carousel():
    assets = ensure_assets()
    order = ["profitability", "cashflow", "investment", "risk", "optimization"]
    slides = []
    sample_v = [[40, 60, 55, 80, 70, 100, 130], [30, 70, 50, 90, 120, 110, 150],
                [10, 25, 45, 80, 140, 110, 160], [10, 22, 30, 28, 42, 55, 50],
                [20, 35, 30, 50, 45, 70, 90]]
    for i, key in enumerate(order):
        a = assets[key]
        img = b64(a["path"])
        tag = ["PILLAR 1 • PROFITABILITY", "PILLAR 2 • CASH FLOW", "PILLAR 3 • INVESTMENT",
               "PILLAR 4 • RISK", "PILLAR 5 • OPTIMIZATION"][i]
        slides.append(
            f'<div class="cine cine{i}" style="display:none;">'
            f'<div class="cine-tag">{tag}</div>'
            f'<img src="data:image/jpeg;base64,{img}">'
            f'<div class="cine-veil"></div>'
            f'<div class="cine-copy"><h3>{a["title"]}</h3><p>{a["desc"]}</p></div>'
            f'<div class="cine-spark">{sparkline_svg(sample_v[i])}</div></div>')
    dots = "".join(f'<span class="cidot" data-i="{i}" style="cursor:pointer;font-size:1.3rem;color:#fff;">•</span>'
                   for i in range(len(order)))
    st.markdown(
        f"""
        <div style="max-width:960px; margin:0 auto;">
          <div class="rfc-quote">Turn Uncertainty Into Profitability.&nbsp;&nbsp;Model. Predict. Optimize.</div>
          {''.join(slides)}
          <div style="text-align:center; margin-top:-12px;">{dots}</div>
        </div>
        <script>
        (function(){{
          const imgs = document.querySelectorAll('.cine');
          let cur = 0;
          function show(n){{
            imgs.forEach((el,i)=>{{ el.style.display = i===n ? 'block' : 'none'; }});
          }}
          show(0);
          setInterval(()=>{{ cur = (cur+1) % imgs.length; show(cur); }}, 6000);
          document.querySelectorAll('.cidot').forEach((d,i)=>{{
            d.addEventListener('click', ()=>{{ cur = i; show(cur); }});
          }});
        }})();
        </script>
        """,
        unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Chart + explanation display helper (shared by all 5 pages)
# ----------------------------------------------------------------------------
def period_slice(df: pd.DataFrame, months: int):
    """Slice a monthly frame to the last `months` months."""
    if len(df) <= months:
        return df
    return df.iloc[-months:].reset_index(drop=True)


def render_chart_block(st_ctl, title: str, fig: go.Figure, expl: dict, key: str, height=420):
    """Expandable plotly chart + the structured explanation below it."""
    st_ctl.subheader(title)
    with st_ctl.expander("📈 Open full chart (hover for details)", expanded=True):
        fig.update_layout(height=height, template="plotly_dark",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#F2EDE4"), margin=dict(l=20, r=20, t=40, b=20))
        st_ctl.plotly_chart(fig, width="stretch", key=f"fig_{key}")
    with st_ctl.expander("🤖 EXPLAIN THIS", expanded=False):
        from explanation_engine import render
        render(st_ctl, st.session_state.get("lang", "en"), expl, key_prefix=key)


def dash_metric(st_ctl, label: str, value: str, delta: str | None = None):
    st_ctl.metric(label, value, delta=delta, delta_color="normal")