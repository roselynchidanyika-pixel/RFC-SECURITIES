"""Shared UI components: global CSS, login screen, sidebar, FX ticker, footer,
cinematic carousel, chart+explanation blocks, news panel and report view.

Speech: window.speechSynthesis is driven from st.html blocks (scripts).
CSS keyframes drive the Ken Burns zoom, crossfade and ticker marquee.
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from assets_gen import ensure_assets, sparkline_svg
from translations import t

GREEN = "#0B3D2E"
GOLD = "#C9A227"
CREAM = "#F2EDE4"


def b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _esc_attr(text: str) -> str:
    return json.dumps(text, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e")


def inject_css():
    st.markdown(
        """
        <style>
        :root { --rfc-gold:#C9A227; --rfc-green:#0B3D2E; --rfc-cream:#F2EDE4; }
        html, body, .stApp { background: var(--rfc-green); }
        .stApp { background: radial-gradient(1200px 500px at 20% -10%, #10493A 0%, #0B3D2E 55%, #072A20 100%); }
        h1, h2, h3, h4 { color: var(--rfc-gold) !important; letter-spacing:.3px; }
        .brand { display:flex; align-items:center; gap:12px; }
        .logo-badge { width:46px; height:46px; border-radius:12px;
          background: linear-gradient(135deg, var(--rfc-gold), #f2d77a);
          display:flex; align-items:center; justify-content:center;
          font-weight:900; color:var(--rfc-green); font-size:20px; box-shadow:0 2px 12px #0006; }
        .login-wrap { display:flex; align-items:center; justify-content:center; min-height:100vh;
          gap:44px; flex-wrap:wrap; padding:24px; }
        .login-left { max-width:430px; }
        .login-card { background:#0E4A37cc; border:1px solid var(--rfc-gold); border-radius:18px;
          padding:26px 28px; width:340px; box-shadow:0 20px 60px #000a; }
        .login-hint { color:var(--rfc-cream); opacity:.85; font-size:.82rem; margin-top:4px; }
        .robot { display:flex; justify-content:flex-end; align-items:flex-end; gap:10px; margin-bottom:18px; }
        .bubble { background:#0E4A37; border:1px solid var(--rfc-gold); color:var(--rfc-cream);
          border-radius:14px 14px 4px 14px; padding:10px 14px; max-width:280px; font-size:.9rem;
          box-shadow:0 8px 24px #000a; }
        @keyframes wave { 0%,100% { transform:rotate(0);} 20% { transform:rotate(-14deg);}
          40% { transform:rotate(10deg);} 60% { transform:rotate(-8deg);} 80% { transform:rotate(6deg);} }
        .robot-fig { font-size:2.4rem; animation: wave 3s ease-in-out infinite; }

        .cine { position:absolute; inset:0; border-radius:18px; overflow:hidden;
          box-shadow:0 18px 50px #000a; border:1px solid #1d5a44; opacity:0;
          animation: xfade 30s linear infinite; }
        .cine img { width:100%; height:100%; object-fit:cover;
          animation: kb 26s ease-in-out infinite alternate; transform-origin:center; }
        @keyframes kb { from { transform:scale(1.0);} to { transform:scale(1.14);} }
        @keyframes xfade {
          0%   { opacity:0; } 3%  { opacity:0; } 10% { opacity:1; } 23% { opacity:1; }
          30%  { opacity:0; } 100%{ opacity:0; } }
        .cine-veil { position:absolute; inset:0; background:linear-gradient(to top,
          #07150f 0%, #07150fe6 18%, #0000 60%); }
        .cine-copy { position:absolute; left:26px; bottom:16px; right:26px; color:var(--rfc-cream); }
        .cine-copy h3 { margin:0 0 6px 0; }
        .cine-copy p { margin:0; opacity:.95; max-width:820px; }
        .cine-spark { position:absolute; left:26px; bottom:108px; right:26px; opacity:.95; }
        .cine-tag { position:absolute; top:14px; left:14px; background:#0B3D2Ed9;
          border:1px solid var(--rfc-gold); color:var(--rfc-gold); font-weight:800;
          letter-spacing:2px; padding:4px 12px; border-radius:999px; font-size:.75rem; }

        .cine-stage { position:relative; height:540px; border-radius:18px; margin-bottom:26px; }
        .rfc-quote { color:#e8dfc8; font-size:1.05rem; font-style:italic; text-align:center;
          padding:4px 0 12px 0; }

        .ticker { position:fixed; left:0; right:0; bottom:0; z-index:998; background:#061811;
          border-top:2px solid var(--rfc-gold); color:var(--rfc-cream); font-family:monospace;
          font-size:.82rem; overflow:hidden; white-space:nowrap; padding:6px 0; }
        .ticker-track { display:inline-block; padding-left:100%; animation: scroll 42s linear infinite; }
        @keyframes scroll { from { transform:translateX(0);} to { transform:translateX(-100%);} }
        .tick-cell { display:inline-block; padding:0 22px; }
        .tick-up { color:#7BDCA6; } .tick-down { color:#ff7b6b; } .tick-stale { color:#ffbf47; }
        .tick-src { opacity:.55; }

        .rfc-footer { position:relative; margin-top:40px; padding:22px 8px 70px 8px;
          border-top:1px solid #1d5a44; color:var(--rfc-cream); font-size:.85rem; text-align:center; }
        .rfc-footer a { color: var(--rfc-gold); }

        div[data-testid="stSidebar"] { background:#082b21; }
        div[data-testid="stFileUploaderDropzone"] { border:1px dashed var(--rfc-gold); border-radius:12px; }
        .speak-btn { background:var(--rfc-gold); color:#0B3D2E; font-weight:800; border:none;
          padding:8px 14px; border-radius:8px; cursor:pointer; margin:4px 0; }
        .speak-btn:hover { filter:brightness(1.08); }
        .rcx { font-family:'Segoe UI',sans-serif; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------------
def render_login(lang: str, sunset: str):
    inject_css()
    b = b64(sunset)
    st.markdown(
        f"""
        <style>.stApp {{ background-image:url(data:image/jpeg;base64,{b});
          background-size:cover; background-position:center; filter:blur(2px) brightness(.82); }}
        </style>
        """,
        unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="login-wrap">
          <div class="login-left">
            <div class="robot"><div class="bubble">{t(lang,'welcome_title')} to RFC Securities.
              {t(lang,'welcome_msg')}</div><div class="robot-fig">🤖</div></div>
            <div class="brand" style="margin-bottom:18px;">
              <div class="logo-badge">RFC<span style="color:#0B5C42;">▲</span></div>
              <div>
                <div class="tagline" style="color:var(--rfc-gold);font-weight:600;letter-spacing:2px;
                  font-size:1.35rem;">{t(lang,'app_name')}</div>
                <div style="color:var(--rfc-cream);">Turn Uncertainty Into Profitability.</div>
                <div style="color:var(--rfc-cream);opacity:.85;letter-spacing:4px;font-size:.85rem;">
                  MODEL. PREDICT. OPTIMIZE.</div>
              </div>
            </div>
            <div style="color:var(--rfc-cream); font-size:.98rem; line-height:1.55;">
              RFC Securities reads your business data, connects it to the Zimbabwe economy -
              inflation, exchange rates, fuel, interest rates, policy news - then explains what is
              happening in clear professional English, with actions you can take today.
            </div>
          </div>
          <div class="login-card">
            <div style="font-weight:800; color:var(--rfc-gold); font-size:1.1rem;">{t(lang,'login_title')}</div>
            <div class="login-hint">{t(lang,'login_hint')}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True)
    st.text_input(t(lang, "login_user"), key="rfc_login_user", label_visibility="collapsed",
                  placeholder=t(lang, "login_user"))
    st.text_input(t(lang, "login_pass"), type="password", key="rfc_login_pass",
                  label_visibility="collapsed", placeholder=t(lang, "login_pass"))
    if st.button(t(lang, "login_btn"), type="primary", width="stretch"):
        st.session_state["authenticated"] = (
            st.session_state.get("rfc_login_user", "").strip() != "" and
            st.session_state.get("rfc_login_pass", "") != ""
        )
        st.session_state["user"] = st.session_state.get("rfc_login_user", "manager")
        st.session_state["play_welcome"] = True
        st.rerun()


WELCOME_TEXT = ("Welcome to RFC Securities. We turn business uncertainty into financial clarity. "
                "RFC Securities helps startups, SMEs and organisations understand profitability, cash flow, "
                "investment opportunities, risks and the best way to allocate their money. We analyse your "
                "business data together with current Zimbabwe market conditions, exchange rates, inflation, "
                "interest rates, government programmes, seasonal demand and market opportunities. We then "
                "explain the results in simple language, identify potential opportunities and risks, and "
                "provide practical financial insights to help you make informed business decisions. You can "
                "receive your complete report through WhatsApp or Gmail. Welcome to RFC Securities — Turn "
                "Uncertainty Into Profitability.")


def render_welcome():
    """Robotic welcome - speechSynthesis audio + a small Mute badge."""
    payload = json.dumps(WELCOME_TEXT, ensure_ascii=True)
    st.html(
        f"""
        <div class="rcx" id="rfc-welcome" style="margin:6px 0 2px 0;">
          <span style="color:#C9A227;font-size:.9rem;font-weight:700;">
            🤖 RFC Assistant speaking...
            <button class="speak-btn" onclick="muteRfc()">Mute</button>
          </span>
        </div>
        <script>
        function muteRfc() {{ try {{
          window.speechSynthesis.cancel();
          var el = document.getElementById('rfc-welcome');
          if (el) el.style.display = 'none';
        }} catch (e) {{}} }}
        (function () {{
          try {{
            var u = new SpeechSynthesisUtterance({payload});
            u.rate = 1; u.pitch = 1;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(u);
            var wax = {{}};
          }} catch (e) {{}}
        }})();
        </script>
        """,
    )


def speak_button(text: str, label: str = "🔊 SPEAK EXPLANATION"):
    """A button that reads the given explanation aloud via speechSynthesis."""
    uid = abs(hash(str(text)[:60])) % 10 ** 8
    payload = _esc_attr(text)
    st.html(
        f"""
        <div class="rcx">
          <button class="speak-btn" id="spk-{uid}"
            data-t="{payload}"
            onclick="spkNow({uid})"> {label} </button>
        </div>
        <script>
        function spkNow(id) {{
          try {{
            var el = document.getElementById('spk-' + id);
            var w = JSON.parse(el.getAttribute('data-t'));
            window.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance(w);
            u.rate = 1;
            window.speechSynthesis.speak(u);
          }} catch (e) {{}}
        }}
        </script>
        """,
    )


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def init_state():
    defaults = {
        "authenticated": False, "user": "", "lang": "en",
        "bundle": None, "source": None, "play_welcome": False,
        "welcome_triggered": False, "show_report": False, "report": None,
        "refresh_clicked": False, "back_cinematic": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_sidebar(assets: dict):
    init_state()
    lang = st.session_state["lang"]
    logo = b64(assets["logo"])
    st.sidebar.markdown(
        f'<div class="brand" style="margin-bottom:4px;">'
        f'<img src="data:image/png;base64,{logo}" style="width:38px;height:38px;border-radius:10px;">'
        f'<span style="color:var(--rfc-gold);font-weight:800;">{t(lang,"app_name")}</span></div>',
        unsafe_allow_html=True)
    st.sidebar.caption(t(lang, "tagline"))

    from data_loader import (DEMO_CHOICES, LABEL_TO_KEY, load_demo_data,
                             parse_upload, upload_metrics)
    upload = st.sidebar.file_uploader(
        t(lang, "sidebar_upload"), type=["xlsx", "xls", "csv"],
        help=t(lang, "sidebar_upload_hint"))
    if upload is not None:
        try:
            st.session_state["bundle"] = parse_upload(upload.getvalue(), upload.name,
                                                      name=os.path.splitext(upload.name)[0])
            st.session_state["source"] = "upload"
            st.session_state["show_report"] = False
            st.sidebar.success("Uploaded data loaded.")
            st.rerun()
        except ValueError as ex:
            st.sidebar.error(str(ex))

    demo = st.sidebar.selectbox(t(lang, "sidebar_demo"), DEMO_CHOICES,
                                index=0, key="demo_sel_box")
    if st.sidebar.button(f"▶ Load Demo: {demo}", width="stretch", disabled=demo == "Select Sector"):
        label = LABEL_TO_KEY.get(demo, demo)
        st.session_state["bundle"] = load_demo_data(label)
        st.session_state["source"] = "demo"
        st.session_state["show_report"] = False
        st.rerun()

    lang_selected = st.sidebar.selectbox(
        t(lang, "sidebar_lang"), ["English", "Shona", "Ndebele"],
        index=["en", "sn", "nd"].index(lang), key="lang_sel_box")
    st.session_state["lang"] = {"English": "en", "Shona": "sn", "Ndebele": "nd"}[lang_selected]

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Live News", width="stretch"):
        st.session_state["refresh_clicked"] = True
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("💰 Report")
    bundle = st.session_state.get("bundle")
    if bundle is not None:
        if st.sidebar.button(t(lang, "sidebar_report"), width="stretch"):
            _make_report()
            st.session_state["show_report"] = True
            st.rerun()
    st.sidebar.caption("📤 Send report (WhatsApp / Gmail)")
    if st.sidebar.button("WhatsApp Send", width="stretch"):
        _whatsapp_link(bundle)
    if st.sidebar.button("Gmail Send", width="stretch"):
        _gmail_link(bundle)
    st.sidebar.markdown(
        f'<div style="font-size:.72rem;color:var(--rfc-cream);opacity:.8;margin-top:6px;">'
        f'{t(lang,"footer_disclaimer")}</div>', unsafe_allow_html=True)


def _whatsapp_link(bundle):
    if bundle is None:
        st.sidebar.warning("No data loaded.")
        return
    from urllib.parse import quote
    if not st.session_state.get("report"):
        _make_report()
    rep = st.session_state.get("report")
    if not rep:
        return
    url = f"https://wa.me/263777479118?text={quote(rep['text'][:3500], safe='')}"
    st.sidebar.markdown(f'<a href="{url}" target="_blank" style="color:#C9A227;">'
                        'Open WhatsApp with the report ready ➜</a>', unsafe_allow_html=True)
    st.sidebar.caption("Mock/embedded send - connects to WhatsApp with the report text.")


def _gmail_link(bundle):
    if bundle is None:
        st.sidebar.warning("No data loaded.")
        return
    from urllib.parse import quote
    if not st.session_state.get("report"):
        _make_report()
    rep = st.session_state.get("report")
    if not rep:
        return
    subj = quote(f"RFC Securities Report - {rep['business_name']}")
    body = quote(rep["text"][:25000], safe="")
    url = f"mailto:chidanyikaroselyn@gmail.com?subject={subj}&body={body}"
    st.sidebar.markdown(f'<a href="{url}" style="color:#C9A227;">Open Gmail pre-filled ➜</a>',
                        unsafe_allow_html=True)


def _make_report():
    from news_tracker import quick_news
    from report_generator import generate_simple_report
    bundle = st.session_state.get("bundle")
    news = quick_news()
    rep = generate_simple_report(bundle, bundle["sector"], news)
    st.session_state["report"] = rep


# ----------------------------------------------------------------------------
# FX ticker + footer
# ----------------------------------------------------------------------------
def render_ticker(fx: dict):
    now = datetime.now().strftime("%H:%M:%S")
    sample = fx.get("sample_mode", False)
    cells = [f'<span class="tick-cell" style="color:var(--rfc-gold);font-weight:800;">LIVE</span>',
             f'<span class="tick-cell" style="opacity:.7">Updated: {now}</span>',
             f'<span class="tick-cell" style="opacity:.7">Source: {fx.get("source_note","RBZ, ZSE, FBC, ZERA")}</span>']
    for it in fx["items"]:
        cls = "tick-stale"
        arrow = "—"
        if it["live"]:
            cls = "tick-up" if it["arrow"] == "up" else "tick-down"
            arrow = "▲" if it["arrow"] == "up" else ("▼" if it["arrow"] == "down" else "→")
        else:
            arrow = "◆"
        cells.append(f'<span class="tick-cell">{it["label"]} '
                     f'<span class="{cls}">{it["value"]} {arrow}</span></span>')
    if not fx["items"]:
        cells.append('<span class="tick-cell tick-stale">DATA UNAVAILABLE/STALE</span>')
    track = "".join(cells)
    st.markdown(f'<div class="ticker"><span class="ticker-track">{track * 2}</span></div>',
                unsafe_allow_html=True)


def render_footer():
    st.markdown(
        f"""
        <div class="rfc-footer">
          📞 0777 479 118 &nbsp;•&nbsp; ✉ <a href="mailto:chidanyikaroselyn@gmail.com">
          chidanyikaroselyn@gmail.com</a> &nbsp;•&nbsp; 📍 Mashava, Masvingo<br>
          <div style="opacity:.85; margin-top:8px;">RFC SECURITIES — EXPLAIN. ANALYSE. PREDICT. STRESS-TEST.<br>
          Clear language. Clear business actions. Decisions remain with management.</div>
        </div>
        """,
        unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Cinematic view (empty state -> 5 pillars)
# ----------------------------------------------------------------------------
PILLAR_ORDER = ["profitability", "cashflow", "investment", "risk", "optimization"]


def render_cinematic(assets: dict, data: dict, econ: dict, sector: str, lang: str):
    quote = t(lang, "tagline")
    tagline = t(lang, "subtagline")
    st.markdown(f'<div class="rfc-quote">{quote}&nbsp;&nbsp;&nbsp;{tagline}</div>',
                unsafe_allow_html=True)
    slides = []
    sample_v = [[40, 60, 55, 80, 70, 100, 130], [30, 70, 50, 90, 120, 110, 150],
                [10, 25, 45, 80, 140, 110, 160], [10, 22, 30, 28, 42, 55, 50],
                [20, 35, 30, 50, 45, 70, 90]]
    for i, key in enumerate(PILLAR_ORDER):
        a = assets[key]
        img = b64(a["path"])
        delay = (12 - i * 12 + 30) * 6
        slides.append(
            f'<div class="cine cine{i}" style="animation-delay:-{i * 6}s;">'
            f'<div class="cine-tag">P{i + 1} • {a["title"]}</div>'
            f'<img src="data:image/jpeg;base64,{img}">'
            f'<div class="cine-veil"></div>'
            f'<div class="cine-copy"><h3>{a["title"]}</h3><p>{a["desc"]}</p></div>'
            f'<div class="cine-spark">{sparkline_svg(sample_v[i])}</div></div>')
    st.markdown(f'<div class="cine-stage">{"".join(slides)}</div>', unsafe_allow_html=True)

    for i, key in enumerate(PILLAR_ORDER):
        a = assets[key]
        with st.expander(f"🔍 Open P{i + 1} — {a['title']} — full chart & explanation",
                         expanded=False):
            render_pillar_block(key, a, data, econ, sector, lang, uid=f"pv_{key}")


def render_pillar_block(key: str, meta: dict, data: dict, econ: dict, sector: str,
                        lang: str, uid: str = "pv"):
    from analysis import build_chart
    from explanation_engine import generate_explanation, render, speak_text
    months_sel = st.radio("Period", [3, 6, 12], index=2,
                          horizontal=True, key=f"{uid}_period", label_visibility="collapsed")
    fig = build_chart(meta["graph"], data["monthly"], months=months_sel)
    fig.update_layout(height=430, template="plotly_dark",
                      font=dict(color="#F2EDE4"), hoverlabel=dict(bgcolor="#0B3D2E"))
    st.plotly_chart(fig, width="stretch", key=f"{uid}_fig")
    expl = generate_explanation(meta["graph"], data, sector, econ)
    render(st, expl, lang)
    speak_button(speak_text(expl))


# ----------------------------------------------------------------------------
# Upload view
# ----------------------------------------------------------------------------
def render_upload_view(bundle: dict):
    from data_loader import upload_metrics
    from translations import t as _t
    lang = st.session_state["lang"]
    metrics = upload_metrics(bundle["products"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(_t(lang, "metric_products"), f"{metrics['total_products']}")
    c2.metric(_t(lang, "metric_avg_price"), f"${metrics['avg_price']:,.2f}")
    c3.metric(_t(lang, "metric_avg_margin"), f"{metrics['avg_margin']}%")
    c4.metric(_t(lang, "metric_stock_value"), f"${metrics['stock_value']:,.0f}")
    st.markdown("### 📦 Products, Prices, Margins and Turnover")
    st.dataframe(bundle["products"], width="stretch", height=360)
    st.caption("Margin% = (Price - Cost) / Price × 100. Status: Fast if margin > 25%, otherwise Slow.")


# ----------------------------------------------------------------------------
# News panel
# ----------------------------------------------------------------------------
def render_news(news: dict, data: dict | None, lang: str):
    items = news.get("items", [])
    last = news.get("last_checked", "unavailable")
    n = news.get("sources_checked", 0)
    live = news.get("live", False)
    status = (t(lang, "refresh_status").format(ts=last, n=n) if (live and items)
              else t(lang, "stale_status"))
    st.markdown("---")
    st.markdown(f"### 🗞 LIVE NEWS TRACKER")
    clicked = st.button(t(lang, "refresh_btn"), key="news_refresh_btn")
    if clicked:
        st.session_state["refresh_clicked"] = True
        st.rerun()
    st.caption(f"🟢 {status} · Cached for 10 minutes")
    if not items:
        st.warning("DATA UNAVAILABLE/STALE — no live feed could be fetched right now. "
                   "Reconnect to the internet and press Refresh Live News. We never fabricate headlines.")
        return
    for it in items:
        tag = it.get("sector", "All")
        impact = it.get("impact", "Low")
        emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(impact, "🟢")
        with st.expander(
                f"{emoji} [{tag}] {it['headline']}  ·  {it.get('date')}  ·  {it.get('source')}",
                expanded=False):
            st.caption(f"{it.get('author','')} · Source: {it.get('source')} · Published: {it.get('date') or 'recent'}")
            st.write(it.get("summary", ""))
            if it.get("content"):
                st.markdown("**Article content**")
                st.write(it["content"][:1600] + (" …" if len(it["content"]) > 1600 else ""))
            if it.get("link"):
                st.markdown(f"[Open original article ↗]({it['link']})")
            st.markdown("**— Business Impact Analysis —**")
            _impact_lines(data, it)


def _impact_lines(data, it):
    st.markdown("**What happened?**")
    st.write(it.get("summary", "") or it.get("headline", ""))
    st.markdown("**Why it matters**")
    st.write(it.get("means", "Relevant to your operating environment."))
    st.markdown("**What your data shows**")
    if data is not None and not data["monthly"].empty:
        m = data["monthly"]
        peak = m.loc[m["month_num"].isin([11, 12])]
        share = (peak["revenue"].sum() / m["revenue"].sum() * 100) if m["revenue"].sum() else 0
        st.write(f"{share:.0f}% of your annual revenue sits in the festive-season window "
                 f"({', '.join(peak['month'].tolist())}) - the period most affected by demand shifts.")
    else:
        st.write("Load or select a business to see the share of your revenue exposed to this event.")
    st.markdown("**Potential exposure ($)**")
    if data is not None and not data["monthly"].empty:
        m = data["monthly"]
        pl = float(m["profit"].mean())
        st.write(f"An average monthly profit of ${pl:,.0f}; a 15% cost shock erodes about "
                 f"${pl - pl / 1.15:,.0f} a month if prices do not move.")
    else:
        st.write("Estimate your exposed revenue after loading business data.")
    st.markdown("**What to consider**")
    st.write("Change hours or location, add or strengthen an online channel, adjust the product mix, "
             "and model staffing against the shifted demand window.")