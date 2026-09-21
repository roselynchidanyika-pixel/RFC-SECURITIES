"""Simple Business Management Report (Mavuno Foods-style, dynamic).

generate_simple_report(business_data, sector, news) returns:
  { lines, text, html, pdf_bytes, summary_kpis, business_name, period }

The template is fixed but every figure is computed from the loaded data;
market lines pull from the live news tracker. Advice uses guarded language
("potentially viable", "under assumptions", "requires validation",
"market evidence indicates") - RFC never guarantees profit.
"""
from __future__ import annotations

from datetime import datetime

from analysis import growth, liquidity, trend
from simple_pdf import pdf_from_lines
from sector_advisor import get_sector_advice


def _signed(v: float) -> str:
    return f"↑ {v:,.0f}" if v > 0 else (f"↓ {abs(v):,.0f}" if v < 0 else "→ flat")


def _kfmt(v: float) -> str:
    if abs(v) >= 1000:
        return f"${v/1000:.1f}k"
    return f"${v:,.0f}"


def generate_simple_report(business_data: dict, sector: str, news: dict) -> dict:
    m = business_data["monthly"]
    bname = business_data.get("name") or "Mavuno Foods"
    period = datetime.now().strftime("%B %Y")

    sales = float(m["revenue"].sum())
    profit = float(m["profit"].iloc[-1])
    cash = float(m["cash_balance"].iloc[-1])
    stock = float(m["inventory"].iloc[-1])
    rev_g = growth(m, "revenue")
    prof_g = growth(m, "profit")
    cash_t = trend(m["cash_balance"])
    stock_t = trend(m["inventory"])

    summary = {
        "sales": sales, "profit": profit, "cash": cash, "stock": stock,
        "sales_arrow": "↑" if rev_g > 0 else "↓", "profit_arrow": "↑" if prof_g >= 0 else "↓",
        "cash_arrow": "↑" if cash_t == "rising" else "↓", "stock_arrow": "↑" if stock_t == "rising" else "↓",
    }

    advice = get_sector_advice(business_data.get("sector") or sector)

    lines: list = []
    lines.append("#TITLE SIMPLE BUSINESS MANAGEMENT REPORT")
    lines.append(f"Business: {bname}")
    lines.append(f"Period: {period}")
    lines.append("_" * 50)
    lines.append("#H 1. YOUR BUSINESS TODAY")
    lines.append(f"Sales {_kfmt(sales)} {summary['sales_arrow']}   Profit {_kfmt(profit)} {summary['profit_arrow']}   Cash {_kfmt(cash)} {summary['cash_arrow']}   Stock {_kfmt(stock)} {summary['stock_arrow']}")
    lines.append("_" * 50)
    lines.append("#H 2. WHAT IS HAPPENING")
    if prof_g < 0:
        lines.append(f"Profit moved {prof_g:+.1f}% over the year while revenue moved {rev_g:+.1f}% - costs are outrunning prices, compressing margin.")
    elif rev_g > 0:
        lines.append(f"Revenue grew {rev_g:+.1f}% and profit moved {prof_g:+.1f}%. The question is whether growth converts into cash.")
    else:
        lines.append(f"Revenue is flat over the year ({rev_g:+.1f}%) - growth needs a driver, not hope.")
    if stock_t == "rising":
        lines.append(f"Stock is rising ({_kfmt(stock)} closing) while cash is {cash_t} - the classic sign cash is being converted into slow inventory.")
    lines.append("_" * 50)
    lines.append("#H 3. WHAT IS HAPPENING AROUND YOU (LIVE)")
    new_items = (news or {}).get("items", [])
    if new_items:
        for it in new_items[:4]:
            lines.append(f"- {it['headline']} ({it['source']}, {it['date'] or 'recent'}). {it['means']}")
    else:
        lines.append("- Live feeds unavailable at report time; re-run with internet to refresh market context.")
    lines.append("_" * 50)
    lines.append("#H 4. WHAT DOES THIS MEAN FOR YOU")
    for b in advice["report_example"]:
        lines.append(f"- {b}")
    lines.append(f"- {advice['macro_line']}")
    lines.append("_" * 50)
    lines.append("#H 5. PROTECT YOUR PROFIT")
    lines.append("- Check the chain on every line: Selling price -> Cost -> Profit. Reprice before margin erodes.")
    lines.append("#H 6. PROTECT YOUR CASH")
    lines.append("- Avoid slow-moving stock: discount it, special-order it, or stop reordering it.")
    lines.append("_" * 50)
    lines.append("#H 7. RFC'S MAIN WARNING")
    lines.append(_warning(m, profit, cash, prof_g))
    lines.append("_" * 50)
    lines.append("#H 8. WHAT TO DO NOW")
    todo = [
        f"1. Reprice your lowest-margin lines; test a small increment on bestsellers (advice is 'potentially viable' - validate against the market).",
        "2. Discount or clear slow-moving stock this week to free cash.",
        "3. Set a daily cash deposit routine and negotiate supplier terms.",
        "4. Prepare for the festive-season peak: stock up before demand spikes.",
        "5. Track fuel, FX and inflation headlines weekly in this dashboard.",
        "6. Book the next RFC check to measure what changed.",
    ]
    for tline in todo:
        lines.append(tline)
    lines.append("_" * 50)
    lines.append("#H 9. RFC'S MESSAGE TO THE OWNER")
    lines.append(f"{bname}, the business is generating activity but the pattern that matters is margin and cash conversion. If {_kfmt(stock)} of stock is turning slowly, cash will stay tight even while sales look fine. Protect margin per sale and make stock work faster; that is where improvement is most reliable, under your current data.")
    lines.append("_" * 50)
    lines.append("#H 10. NEXT RFC CHECK")
    lines.append("- Sales Monitor: next month revenue vs this month")
    lines.append("- Profit Watch: margin % on your top five lines")
    lines.append("- Cash Position: closing balance and stock days")
    lines.append("_" * 50)
    lines.append("RFC SECURITIES - EXPLAIN ANALYSE PREDICT STRESS-TEST")

    pdf_bytes = pdf_from_lines(lines, title="RFC Securities - Simple Management Report")
    text = "\n".join(lines).replace("#TITLE ", "").replace("#H ", "").replace("_" * 50, "")
    html_parts = []
    for x in lines:
        if x.startswith("#TITLE "):
            html_parts.append(f"<h2 style='color:#C9A227'>{_html_escape(x[7:])}</h2>")
        elif x.startswith("#H "):
            html_parts.append(f"<h4 style='color:#C9A227'>{_html_escape(x[3:])}</h4>")
        else:
            html_parts.append(f"<p style='margin:3px 0'>{_html_escape(x)}</p>")
    html = (
        "<div style='background:#0B3D2E;color:#E8E4D8;padding:18px;border-radius:12px;font-family:sans-serif'>"
        + "".join(html_parts) + "</div>"
    )
    return {
        "lines": lines, "text": text, "html": html,
        "pdf_bytes": pdf_bytes, "summary": summary,
        "business_name": bname, "period": period,
        "advice": advice,
    }


def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _warning(m, profit, cash, prof_g) -> str:
    if prof_g >= 0 and trend(m["cash_balance"]) != "falling":
        return f"Sales are holding, but the real risk is stock: with {m['inventory'].iloc[-1]:,.0f} in inventory, a demand dip turns inventory into locked cash. Do not buy stock on hope - buy against evidence."
    if cash <= 0:
        return "CASH IS THE PRIORITY: the modelled closing cash balance is at or below zero. Stop new stock purchases until cash cover is restored."
    return (f"Costs are moving faster than prices (profit {prof_g:+.1f}%). The single most reliable action is defending margin: "
            f"reprice low-margin lines and clear slow stock before prices move again.")