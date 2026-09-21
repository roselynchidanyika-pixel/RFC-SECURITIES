"""The AI Explanation Engine.

Every chart is read and explained in clear, professional English, tied to the
Zimbabwe economy, with sector-specific actions, a before/after example and a
cause-and-effect chain.

generate_explanation(graph_type, data, sector, econ_data) returns a dict:
  what, changed, trend, why, affect, investigate, can_do,
  before_after, chain, macro, speak
Also provides render(...) to display it and speak_text(...) for TTS.

NOTE: numbers disclosed come from the loaded/modeled data; we never present an
assumption as fact, and we never guarantee profit (advice is phrased as
"potentially viable", "under assumptions", "requires validation",
"market evidence indicates").
"""
from __future__ import annotations

import pandas as pd

from analysis import consecutive_dir, forecast, growth, liquidity, pct, trend
from sector_advisor import can_do, macro_context_line


def _fm(v) -> str:
    return f"${v:,.2f}"


def _num(v) -> str:
    return f"{v:,.0f}"


def _chain(sector: str) -> str:
    chains = {
        "Transport": "Inflation ↑ → Fuel price ↑ → Cost per trip ↑ → If fares do not adjust → Profit margin per trip ↓ → Less cash for the owner.",
        "Agriculture": "Inflation ↑ → Fertiliser and seed prices ↑ → Input costs ↑ → Margin per tonne ↓ unless farm-gate prices move with them.",
        "Gadgets": "Exchange rate ↑ → Imported devices cost more → Cost price ↑ → If selling price lags → Margin ↓ → Slow stock becomes expensive stock.",
        "Grocery": "Inflation ↑ → Supplier prices ↑ → Selling prices ↑ → Price-sensitive customers buy less → Volume ↓ → Revenue pressure → Profit margin ↓.",
        "Restaurant": "Food cost ↑ → Cost per plate ↑ → If the menu price stays flat → Margin per plate ↓.",
        "Clothing": "FX ↑ → Imported garments cost more → Cost price ↑ → Margin ↓ unless you reprice.",
        "Poultry": "Feed price ↑ → Cost per bird ↑ → Margin per bird ↓ → Sale timing matters more.",
        "Beauty": "FX ↑ → Hair products cost more → Service cost ↑ → If clients' budgets stay tight → Fewer visits → Revenue ↓.",
        "Hardware": "Inflation ↑ → Cement and inputs ↑ → Cost ↑ → Gross margin ↓ unless tenders reprice.",
        "General": "Inflation ↑ → Supplier costs ↑ → Selling prices ↑ → Customer demand ↓ → Sales volume ↓ → Revenue pressure ↓ → Profit margin ↓.",
    }
    return chains.get(sector, chains["General"])


def generate_explanation(graph_type: str, data: dict, sector: str, econ_data: dict = None) -> dict:
    """Full explanation dict for one pillar (graph)."""
    monthly: pd.DataFrame = data["monthly"]
    products: pd.DataFrame = data["products"]
    b = data["business"]
    sector = b.sector or sector
    m = monthly
    econ_data = econ_data or {}

    rev, costs, profit = m["revenue"], m["costs"], m["profit"]
    rev0, rev1 = rev.iloc[0], rev.iloc[-1]
    cost0, cost1 = costs.iloc[0], costs.iloc[-1]
    prof0, prof1 = profit.iloc[0], profit.iloc[-1]
    cash = liquidity(m)
    g_rev = growth(m, "revenue")
    g_prof = growth(m, "profit")
    margin0 = (rev0 - cost0) / rev0 * 100 if rev0 else 0
    margin1 = (rev1 - cost1) / rev1 * 100 if rev1 else 0
    liq = liquidity(m)

    expl = {
        "what": _what(graph_type, m, margin1),
        "changed": _changed(graph_type, m, rev0, rev1, cost0, cost1, prof0, prof1, margin0, margin1, liq),
        "trend": _trend(graph_type, m, g_rev, g_prof, margin1),
        "why": _why(graph_type, m, sector, econ_data, products),
        "affect": _affect(graph_type, m, sector, products, prof1, liq),
        "investigate": _investigate(graph_type, m, products),
        "can_do": can_do(sector, _dimension(graph_type)),
        "before_after": _before_after(graph_type, m, prof1),
        "chain": _chain(sector),
        "macro": macro_context_line(sector, econ_data or None),
        "graph_type": graph_type,
        "sector": sector,
    }
    expl["speak"] = speak_text(expl)
    return expl


def _dimension(t: str) -> str:
    return {"profitability": "pricing", "cashflow": "cash_stock",
            "investment": "diversify", "risk": "resilience",
            "optimization": "cash_stock"}.get(t, "pricing")


# --- section builders ------------------------------------------------------
def _what(t, m, margin1):
    labels = {
        "profitability": ("This graph shows monthly revenue against the cost of running the business, "
                          "and the profit that remains after all costs. It reveals which driving force moves your bottom line."),
        "cashflow": ("This graph shows money entering (cash in), money leaving (cash out), and the resulting "
                     "bank balance each month. Profit and cash are different: you can be profitable on paper and still run out of cash."),
        "investment": ("This graph analyses whether spending capital today (expansion, equipment, stock) returns more "
                       "than keeping the same money in the bank, after inflation and time value are considered. "
                       "It is measured with Net Present Value (NPV), Internal Rate of Return (IRR), Payback period, "
                       "Discounted Cash Flow (DCF) and Modified IRR (MIRR) - each one translates one idea: does the project repay its capital."),
        "risk": ("This graph stress-tests your data: if revenue falls or costs rise by 10-30%, and if inflation, "
                 "exchange rates, interest rates or fuel move against you, how much profit is at risk in a bad month."),
        "optimization": ("This graph shows your limited resources (cash, stock, staff, vehicles), the alternative uses "
                         "for them, the constraints around you, and the allocation that an optimisation model recommends."),
    }
    return labels[t]


def _changed(t, m, rev0, rev1, cost0, cost1, prof0, prof1, margin0, margin1, liq):
    if t == "profitability":
        return (f"Revenue changed from {_num(rev0)} to {_num(rev1)} ({pct(growth(m, 'revenue'))}). "
                f"Costs changed from {_num(cost0)} to {_num(cost1)}. Net profit changed from {_num(prof0)} to {_num(prof1)}.")
    if t == "cashflow":
        return (f"Cash in moved from {_num(m['cash_in'].iloc[0])} to {_num(m['cash_in'].iloc[-1])}. "
                f"Cash out moved from {_num(m['cash_out'].iloc[0])} to {_num(m['cash_out'].iloc[-1])}. "
                f"Closing cash balance is {_num(liq['closing'])}.")
    if t == "investment":
        return (f"Average monthly profit available to reinvest is {_num(m['profit'].mean())}. "
                f"Closing cash of {_num(liq['closing'])} could fund expansion, repay debt, or stay as a buffer.")
    if t == "risk":
        return (f"Revenue today is {_num(rev1)}/month and costs are {_num(cost1)}/month, leaving {_num(prof1)}/month "
                f"of profit. At today's figures a 15% cost jump removes roughly {_num(prof1 - prof1 / 1.15)} of monthly profit.")
    return (f"About {_num(m['inventory'].iloc[-1])} sits in stock, {_num(liq['closing'])} in cash, "
            f"and {_num(cost1)}/month goes to costs. Margins average {margin1:.1f}% across product lines.")


def _trend(t, m, g_rev, g_prof, margin1):
    if t == "profitability":
        d = consecutive_dir(m["profit"], lookback=5)
        d_txt = (f"{d} consecutive months declining" if d == "down" else
                 (f"{d} consecutive months rising" if d == "up" else "broadly flat"))
        return (f"Profit is trending {trend(m['profit'])}. Revenue is {trend(m['revenue'])}. "
                f"Profit margin sits at {margin1:.1f}% - the key number to protect.")
    if t == "cashflow":
        cash_t = trend(m['cash_balance'])
        return (f"Cash balance is {cash_t}. "
                f"You currently hold near {liquidity(m)['months_of_cash']} months of cash cover.")
    if t == "investment":
        fc = forecast(m, "profit", 3)
        return (f"Modelled 3-month profit outlook: {', '.join(_num(v) for v in fc)}. "
                f"Invest only if the modelled return clears the bank rate plus inflation.")
    if t == "risk":
        return (f"Monthly profit volatility is meaningful (std {max(0.0, ((m['profit'] - m['profit'].mean()) ** 2).mean() ** 0.5):,.0f}). "
                f"A downturn therefore needs a defined response, not a guess.")
    return (f"Stock is trending {trend(m['inventory'])} while profit is {trend(m['profit'])}. "
            f"That gap is where cash gets trapped.")


def _why(t, m, sector, econ, products) -> list:
    lines = []
    infl = econ.get("inflation")
    rev_t, cost_t, prof_t = trend(m["revenue"]), trend(m["costs"]), trend(m["profit"])
    if prof_t == "falling":
        lines.append(f"Profit fell while costs moved {cost_t} and revenue is {rev_t}. "
                     "When cost growth outruns price growth, every sale earns less.")
    elif rev_t == "rising" and cost_t == "rising":
        lines.append("Sales rose, but costs rose faster - the classic squeeze: working harder for the same or less profit.")
    if infl is not None:
        lines.append(f"Inflation around {infl:.1f}% pushes supplier prices up, which pushes your prices up, "
                     "which can push price-sensitive customers away.")
    lines.append(macro_context_line(sector, econ or None))
    season = _season_hint(m)
    if season:
        lines.append(season)
    if products is not None and not products.empty and "Margin %" in products:
        worst = products.sort_values("Margin %").iloc[0]
        lines.append(f"The thinnest line is '{worst['Product']}' at {worst['Margin %']:.1f}% margin - "
                     "little buffer against supplier increases there.")
    return lines


def _affect(t, m, sector, products, prof1, liq) -> str:
    if t == "cashflow":
        return (f"The main effect is cash conversion: stock bought ahead and debtors tie cash before it returns as sales. "
                f"With {liquidity(m)['months_of_cash']} months of cover, a single missed season has limited protection.")
    if t == "investment":
        return ("Capital spent today is unavailable for two weeks of fuel, a supplier deal or a staff payroll lean month. "
                "The offset is only justified if the modelled return beats keeping the money working in the business.")
    if t == "risk":
        return (f"A {_num(abs(prof1 - prof1 / 1.15))}/month swing is the difference between a healthy month "
                "and a painful one. Pre-arranged cost cuts are the cheapest insurance.")
    if t == "optimization":
        return ("Misallocated cash slows the business: slow stock earns nothing, idle cash earns nothing after inflation, "
                "and every $ in fast-moving margin lines earns more.")
    return ("The core effect is margin pressure: if costs rise faster than prices, more activity converts "
            "into less usable profit, and cash for the owner shrinks.")


def _investigate(t, m, products) -> list:
    qs = []
    if t == "profitability":
        rev_t = trend(m["revenue"])
        qs.append("Are fewer customers coming, or are they buying less? Different fixes follow.")
        if products is not None and not products.empty and "Status" in products:
            slow = products[products["Status"] == "Slow"]
            if len(slow):
                qs.append(f"Inspect the {len(slow)} slow-moving lines - how much cash sits on those shelves?")
        qs.append("Compare your prices against the market before holding or raising them.")
    elif t == "cashflow":
        qs.append("Which purchases sit longest before converting to cash? Rank stock days for every line.")
        qs.append("Are suppliers' terms being used, or is cash leaving before stock sells?")
    elif t == "investment":
        qs.append("What is the worst realistic case for new revenue, and what breaks at that point?")
        qs.append("Does the return beat the bank rate plus inflation after costs and taxes?")
    elif t == "risk":
        qs.append("Which single line would hurt most if its cost rose 15%? Fix that first.")
        qs.append("Do you have a pre-agreed response for a 20% revenue drop?")
    else:
        qs.append("Rank every line by margin per dollar of capital, not by habit.")
        qs.append("What stops the business from reallocating cash to the best-margin line this month?")
    return qs


def _before_after(t, m, prof1) -> str:
    if t == "risk":
        return ("BEFORE/AFTER: Inventory cost $5,000 -> $5,700 after a supplier increase. Expected margin 30% -> 21%. "
                "Impact: about -9 percentage points (pp), before any defensive price action.")
    if t == "profitability":
        return ("BEFORE/AFTER: a $10 item whose supplier cost rises to $11, priced flat, moves its margin "
                "from 28% to 18% - roughly -10pp of profit on every sale.")
    if t == "cashflow":
        return ("BEFORE/AFTER: one bulk-buy of $5,000 stock drains cash now for margin later; if that stock "
                "turns in 4 months, your cash is tied for 4 months before it returns as sales.")
    if t == "investment":
        return ("BEFORE/AFTER: a project returning 6% nominal while inflation runs higher effectively loses "
                "value; the same cash in fast-moving stock at 20%+ margin works harder.")
    return ("BEFORE/AFTER: moving $1,000 from a slow line into the best-margin fast mover can lift monthly "
            "profit materially at unchanged revenue.")


def _season_hint(m) -> str | None:
    if "month_num" not in m.columns:
        return None
    peak = m.loc[m["month_num"].isin([11, 12])]
    rest = m.loc[~m["month_num"].isin([11, 12])]
    if len(peak) and len(rest):
        hi = peak["revenue"].mean()
        lo = rest["revenue"].mean()
        if hi and lo and hi > lo * 1.12:
            return (f"Sales concentrate late in the year (festive period +{((hi/lo)-1)*100:.0f}% vs other months). "
                    "Plan stock, staff and cash around that window.")
    return None


def render(st, expl: dict, lang: str = "en"):
    """Render the mandated explanation sections under a chart."""
    st.markdown(f"#### 🤖 WHAT AM I LOOKING AT?\n{expl['what']}")
    st.markdown(f"**WHAT CHANGED?**  \n{expl['changed']}")
    st.markdown(f"**WHAT IS THE TREND?**  \n{expl['trend']}")
    st.markdown(f"**WHY COULD THIS BE HAPPENING?**")
    for line in expl["why"]:
        st.markdown(f"- {line}")
    st.markdown(f"**HOW DOES IT AFFECT THE BUSINESS?**  \n{expl['affect']}")
    st.markdown(f"**WHAT SHOULD I INVESTIGATE?**")
    for q in expl["investigate"]:
        st.markdown(f"- {q}")
    st.markdown(f"**WHAT CAN I DO?**")
    for o in expl["can_do"]:
        st.markdown(f"- {o}")
    st.markdown(f"**BEFORE/AFTER**  \n{expl['before_after']}")
    st.markdown("**CAUSE-AND-EFFECT CHAIN**")
    st.markdown(f"`{expl['chain']}`")
    st.markdown(f"**CONNECTION TO THE ZIMBABWE ECONOMY**  \n{expl['macro']}")


def speak_text(expl: dict) -> str:
    """Concise spoken version of the explanation for window.speechSynthesis."""
    parts = [expl["what"], expl["changed"], expl["trend"]]
    for w in expl["why"][:2]:
        parts.append(w)
    parts.append(expl["affect"])
    parts.append("What can you do? " + "; ".join(expl["can_do"][:2]))
    parts.append(expl["before_after"])
    return " ".join(parts)