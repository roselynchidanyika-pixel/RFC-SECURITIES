"""Simple Business Management Report - Mavuno Foods template.

Generates the structured report in Markdown, a downloadable PDF (reportlab),
and ready-to-send messages for WhatsApp and Gmail.
"""
from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from analysis import fmt_money, growth, nice, pct, trend
from sector_advisor import can_do, macro_context_line


def _report_lines(bundle, econ, news_summary: str, period: str) -> list:
    m = bundle["monthly"]
    b = bundle["business"]
    sector = b.sector
    last = m.iloc[-1]
    prev = m.iloc[-2] if len(m) > 1 else last
    up = lambda v: "↑" if v >= 0 else "↓"  # noqa

    rev_d = growth(m, "revenue", 2)
    prof_d = growth(m, "profit", 2)
    cash_d = growth(m, "cash_balance", 2)
    inv_d = growth(m, "inventory", 2)

    L = []
    L.append("SIMPLE BUSINESS MANAGEMENT REPORT")
    L.append("")
    L.append(f"Business: {b.name}")
    L.append(f"Period: {period}")
    L.append("")
    L.append("🟢 YOUR BUSINESS TODAY")
    L.append(f"Sales: {nice(last['revenue'])} {up(rev_d)}")
    L.append(f"Profit: {nice(last['profit'])} {up(prof_d)}")
    L.append(f"Cash: {nice(last['cash_balance'])} {up(cash_d)}")
    L.append(f"Stock: {nice(last['inventory'])} {up(inv_d)}")
    L.append("")
    L.append("🔎 WHAT IS HAPPENING?")
    rev_t, prof_t = trend(m["revenue"]), trend(m["profit"])
    if prof_t == "falling" and rev_t == "rising":
        L.append("You are selling more, but keeping less profit. Costs are rising faster than sales.")
    elif prof_t == "falling":
        L.append("Your profit is under pressure. Check whether prices kept up with costs.")
    else:
        L.append("Your profit is holding. Protect it by watching costs and repricing when inflation moves.")
    L.append("")
    L.append("🇿🇼 WHAT IS HAPPENING AROUND YOU?")
    L.append(macro_context_line(sector, econ))
    L.append(news_summary or "No verifiable live news was available at report time.")
    L.append("")
    L.append("⚠ WHAT DOES THIS MEAN FOR YOU?")
    L.append("You should not depend on one place, one product or one way of selling.")
    L.append("Consider:")
    for bullet in can_do(sector, "diversify"):
        L.append(f"- {bullet}")
    L.append("")
    L.append("💰 PROTECT YOUR PROFIT")
    L.append("Before increasing sales, make sure each sale is still profitable.")
    L.append("Check: Selling price → Cost → Profit. If costs rise and price stays the same, profit shrinks.")
    L.append("")
    L.append("💵 PROTECT YOUR CASH")
    L.append(f"Your stock has {inv_d:+.1f}% vs cash {cash_d:+.1f}%. Check which products sell quickly and which sit on the shelf.")
    L.append("Avoid putting too much cash into slow-moving stock.")
    L.append("")
    L.append("🚨 RFC'S MAIN WARNING")
    L.append(_warning(bundle, econ, sector))
    L.append("")
    L.append("✅ WHAT TO DO NOW")
    for i, s in enumerate([
        "Review your prices.",
        "Reduce slow-moving stock.",
        "Protect your cash.",
        "Diversify where and how you sell.",
        "Monitor Zimbabwe economic and business news.",
        "Check every new regulation to see whether it affects your business.",
    ], 1):
        L.append(f"{i}. {s}")
    L.append("")
    L.append("🤖 RFC'S MESSAGE TO THE OWNER")
    L.append(_owner_message(bundle))
    L.append("")
    L.append("📌 NEXT RFC CHECK")
    L.append(f"Sales: {'Monitor' if abs(rev_d) > 10 else 'Watch closely'}")
    L.append(f"Profit: {'Watch closely' if prof_t == 'falling' else 'Monitor'}")
    L.append(f"Cash: {'Watch closely' if cash_d < -10 else 'Monitor'}")
    L.append(f"Stock: {'Review' if inv_d > 15 else 'Monitor'}")
    L.append("External news: Monitor")
    L.append("Business diversification: Recommended for consideration")
    L.append("")
    L.append("RFC SECURITIES")
    L.append("EXPLAIN. ANALYSE. PREDICT. STRESS-TEST.")
    L.append("Simple language. Clear business actions. Decisions remain with management.")
    return L


def _warning(bundle, econ, sector) -> str:
    m = bundle["monthly"]
    cash_t = trend(m["cash_balance"])
    stock_t = trend(m["inventory"])
    bits = []
    if cash_t == "falling":
        bits.append("your cash balance is falling while inflation keeps prices moving")
    if stock_t == "rising":
        bits.append("your stock is growing while cash is not - cash is being locked on shelves")
    if not bits:
        bits.append("costs tend to rise faster than prices during this period - margin watch is essential")
    warn = "Your biggest near-term risk: " + " and ".join(bits) + "."
    if econ and econ.get("inflation") is not None:
        warn += f" At ~{econ['inflation']:.1f}% inflation, delaying price and stock decisions costs real money each month."
    return warn


def _owner_message(bundle) -> str:
    m = bundle["monthly"]
    b = bundle["business"]
    prof_final = m["profit"].iloc[-1]
    if prof_final > 0:
        return (f"{b.name} is currently making a profit, which is your foundation. The fight is to keep "
                "that profit growing faster than inflation. Protect cash, keep margins healthy, and only "
                "expand into what the data shows is working.")
    return (f"{b.name} is under profit pressure. This is not the end - it is a signal to reprice, cut "
            "slow-moving stock and protect cash before funding growth. Small, data-backed steps restore "
            "profitability faster than big, hopeful ones.")


def build_report(bundle, econ, news, period: str | None = None, lang: str = "en"):
    period = period or datetime.now().strftime("%B %Y")
    ns = ""
    if news and news.get("items"):
        ns = f"Recent news that may matter to you: {news['items'][0]['headline']} ({news['items'][0]['source']})."
    lines = _report_lines(bundle, econ, ns, period)
    return {
        "text": "\n".join(lines),
        "period": period,
        "lines": lines,
    }


def report_markdown(report) -> str:
    return report["text"]


def report_pdf(report) -> bytes:
    """Render the report to a PDF using reportlab."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFillColorRGB(0.043, 0.239, 0.18)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(25 * mm, h - 25 * mm, "RFC SECURITIES - Simple Business Report")
    c.setFillColorRGB(0.13, 0.13, 0.13)
    y = h - 45 * mm
    c.setFont("Helvetica", 9.5)
    for line in report["lines"]:
        if y < 22 * mm:
            c.showPage()
            y = h - 22 * mm
            c.setFont("Helvetica", 9.5)
            c.setFillColorRGB(0.13, 0.13, 0.13)
        text = line[:118]
        if line.startswith(("SIMPLE", "RFC SECURITIES")):
            continue
        if line.strip().startswith(("🟢", "🔎", "🇿🇼", "⚠", "💰", "💵", "🚨", "✅", "🤖", "📌")) \
                or line in ("WHAT IS HAPPENING AROUND YOU?",):
            c.setFont("Helvetica-Bold", 10.5)
            c.setFillColorRGB(0.04, 0.24, 0.18)
        elif line.strip().startswith(("Business:", "Period:")):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(0.5, 0.44, 0.1)
        else:
            c.setFont("Helvetica", 9.5)
            c.setFillColorRGB(0.13, 0.13, 0.13)
        c.drawString(25 * mm, y, text)
        y -= 6.2 * mm
    c.showPage()
    c.save()
    return buf.getvalue()


def whatsapp_text(report) -> str:
    body = report["text"][:1800].replace("\n\n", "\n")
    return body


def gmail_body(report) -> str:
    return report["text"]