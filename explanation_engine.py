"""The AI Explanation Engine.

Every chart in RFC is read and explained in plain professional English, tied
to the Zimbabwe economy, with sector-specific actions, before/after numbers
and a cause-and-effect chain. Never a decorative graph.
"""
from __future__ import annotations

from utils.analysis import (consecutive_dir, fmt_money, growth, liquidity,
                            nice, pct, trend)
from utils.sector_advisor import can_do, macro_context_line
from utils.translations import t


def _to_money(v) -> str:
    return fmt_money(float(v))


def _chain_text(sector: str) -> list:
    chains = {
        "Transport": ["Fuel price ↑ → Cost per trip ↑ → Profit margin per trip ↓ → If you do not adjust fares, your daily profit shrinks.",
                      "Exchange rate ↑ → Spares and vehicle prices ↑ → Maintenance budget ↑ → Less cash left for the owner."],
        "Agriculture": ["Inflation ↑ → Fertiliser and feed prices ↑ → Input costs ↑ → Less margin per tonne unless farm-gate prices rise with them.",
                        "Rainfall ↓ → Yield ↓ → Less volume to sell → Same fixed costs → Profit margin ↓."],
        "Gadgets": ["Exchange rate ↑ → Imported gadgets cost more → Your cost price ↑ → If selling price lags, margin ↓ → Slow stock becomes expensive stock.",
                    "Duty/IMEI rule ↑ → Red tape ↑ → More time and cost per unit → Pressure on gross margin."],
        "Grocery": ["Inflation ↑ → Supplier prices ↑ → Your cost price ↑ → Selling price ↑ → Price-sensitive customers buy less → Volume ↓ → Revenue pressure.",
                    "Supermarket promotion ↓ → Your foot traffic ↓ → Volume ↓ → You hold more stock → Cash ↓."],
        "Restaurant": ["Food cost ↑ → Cost per plate ↑ → If menu price stays the same → Margin per plate ↓.",
                       "Customer spending power ↓ (inflation) → Covers ↓ → Fixed rent still due → Profit ↓."],
        "Clothing": ["FX ↑ → Imported garments cost more → Cost price ↑ → Margin ↓ unless price adjusts.",
                     "School term start → Uniform demand ↑ → Stock out risk → Missed sales."],
        "Poultry": ["Feed price ↑ → Cost per bird ↑ → Margin per bird ↓ → Timing of sale matters more.",
                    "Disease scare ↑ → Demand in market ↓ → Prices ↓ → Hold birds longer → More feed cost."],
        "Beauty": ["FX ↑ → Hair products cost more → Cost of service ↑ → Client pays more → Fewer clients if budget tight.",
                   "Discretionary income ↓ → Clients trade down → Average spend ↓."],
        "Hardware": ["Cement producers raise price (inflation) → Your cost ↑ → Gross margin ↓.",
                     "Construction slow-down → Big orders ↓ → Fixed costs still due → Cash pressure."],
        "General": ["Inflation ↑ → All input costs ↑ → Selling prices ↑ → Customer demand ↓ → Volume ↓ → Revenue pressure → Profit margin ↓.",
                    "FX ↑ → Imported inputs cost more → Cost price ↑ → Margin ↓ unless you reprice."],
    }
    return chains.get(sector, chains["General"])


def build(bundle, pillar: str, econ: dict) -> dict:
    """Generate the full explanation dict for a pillar."""
    monthly = bundle["monthly"]
    products = bundle["products"]
    b = bundle["business"]
    sector = b.sector
    m = monthly
    rev0, rev1 = m["revenue"].iloc[0], m["revenue"].iloc[-1]
    cost0, cost1 = m["costs"].iloc[0], m["costs"].iloc[-1]
    prof0, prof1 = m["profit"].iloc[0], m["profit"].iloc[-1]
    cash = liquidity(m)
    g = growth(m)

    base = {
        "sector": sector,
        "chain": _chain_text(sector),
        "macro": macro_context_line(sector, econ),
        "inflation": (econ or {}).get("inflation"),
    }

    if pillar == "profitability":
        margin0 = (rev0 - cost0) / rev0 * 100 if rev0 else 0
        margin1 = (rev1 - cost1) / rev1 * 100 if rev1 else 0
        margin_trend = trend(m["profit"])
        rev_dir = consecutive_dir(m["revenue"])
        base.update({
            "title": "Profitability: Revenue, Costs and Profit",
            "what": "This chart shows your monthly sales (revenue) against what it costs to run the business, and the profit that remains. The donut shows how many cents of every dollar stay as profit.",
            "changed": f"Revenue changed from {nice(rev0)} to {nice(rev1)} ({pct(g)}). Costs changed from {nice(cost0)} to {nice(cost1)}. Profit changed from {nice(prof0)} to {nice(prof1)}.",
            "margin": f"Profit margin moved from {margin0:.1f}% to {margin1:.1f}%. Gross margin is the key number a lender or investor will ask about.",
            "trend": f"Profit has been {margin_trend} over the period; revenue is {rev_dir or 'broadly flat'} overall.",
            "why": _profit_why(m, sector, econ, products),
            "affect": _profit_affect(m, sector, prod_df=products),
            "investigate": _profit_investigate(monthly, products),
            "options": can_do(sector, "pricing"),
            "before_after": f"Example: if a supplier raises cost on a $10 item to $10.60 and you keep the price at $10, you lose the sale or the margin. Margin 30% → 21%, impact −9pp.",
        })
    elif pillar == "cashflow":
        base.update({
            "title": "Cash Flow: Money In vs Money Out",
            "what": "This shows money actually entering your account (cash in) vs money leaving (cash out), and the resulting bank balance. Profit and cash are different: you can be profitable on paper and still run out of cash.",
            "changed": f"Cash in moved from {nice(m['cash_in'].iloc[0])} to {nice(m['cash_in'].iloc[-1])}. Cash out moved from {nice(m['cash_out'].iloc[0])} to {nice(m['cash_out'].iloc[-1])}. Your cash balance is now {nice(cash['closing'])}.",
            "margin": f"You currently hold about {cash['months_of_cash']} months of cash cover.",
            "trend": f"Your cash balance is {cash['trend']}. Stock, debtors and purchases all consume cash before it returns as sales.",
            "why": [], "affect": [], "investigate": [], "options": can_do(sector, "cash_stock"),
            "before_after": f"Example: buying a supplier deal that triples stock uses cash now for margin later. $5,000 stock bought in one month can drain $5,000 of cash and add warehouse/insurance cost before it sells.",
        })
    elif pillar == "investment":
        base.update({
            "title": "Investment: NPV, IRR, Payback, DCF, ROI",
            "what": "This analyses whether spending money today (expansion, equipment, stock) will return more than the same money kept in the bank, once time and inflation are considered.",
            "changed": "" ,
            "margin": "",
            "trend": "",
            "why": [],
            "affect": [],
            "investigate": [],
            "options": ["Compare the project return against the bank rate and inflation before committing.",
                        "Model a base case, a good case and a bad case - never decide on the base case alone."],
            "before_after": "",
        })
    elif pillar == "risk":
        base.update({
            "title": "Risk & Stress Testing: What Could Go Wrong?",
            "what": "This stress-tests your revenue and costs if inflation, the exchange rate, interest rates or prices move against you, and if your own revenue or costs shift by 10-30%.",
            "changed": f"Your revenue is currently {nice(rev1)}/month with {nice(cost1)}/month of costs, giving {nice(prof1)}/month of profit. A 15% cost jump removes roughly {_to_money(prof1 - prof1 / 1.15)} of monthly profit.",
            "margin": "",
            "trend": "",
            "why": [], "affect": [], "investigate": [],
            "options": can_do(sector, "resilience"),
            "before_after": f"Example: Inventory costing $5,000 after a supplier increase becomes $5,700. If selling prices do not move, your expected margin drops from 30% to 21%.",
        })
    elif pillar == "optimization":
        base.update({
            "title": "Optimization: Best Use of Your Money",
            "what": "This shows your resources (cash, stock, staff, vehicles), the alternatives for using them, the constraints around you, and the recommended allocation.",
            "changed": f"Right now about {nice(sum(monthly['inventory'].tolist()))} sits in stock, {nice(cash['closing'])} in cash, and {nice(cost1)}/month goes to costs.",
            "margin": "",
            "trend": "",
            "why": [], "affect": [], "investigate": [],
            "options": [
                "Allocate by margin per dollar, not by habit: which product earns the most profit per $ invested.",
                "Cap stock days on shelf, keep a cash buffer, and fund one growth area deliberately.",
            ],
            "before_after": f"Example: shifting $1,000 from slow-moving stock into your best-margin fast mover can lift monthly profit by {_to_money(max(0, m['profit'].sum()) * 0.03)} at unchanged revenue.",
        })
    return base


def _profit_why(m, sector, econ, products) -> list:
    lines = []
    rev_t = trend(m["revenue"]); cost_t = trend(m["costs"]); prof_t = trend(m["profit"])
    if prof_t == "falling":
        lines.append(f"Profit has fallen even though costs moved {cost_t} and revenue is {rev_t}. When cost growth outruns price growth, every sale earns less.")
    elif rev_t == "rising" and cost_t == "rising":
        lines.append("Sales are rising, but costs rising faster is the classic squeeze: you are working harder for the same or less profit.")
    lines.append(macro_context_line(sector, econ))
    if econ and econ.get("inflation") is not None:
        lines.append(f"Inflation around {econ['inflation']:.1f}% pushes supplier prices up, which pushes your prices up, which can push customers away.")
    season = _season_hint(m)
    if season:
        lines.append(season)
    return lines


def _season_hint(m) -> str | None:
    if "month_num" not in m.columns:
        return None
    peak = m.loc[m["month_num"].isin([11, 12])]
    if len(peak):
        hi = peak["revenue"].mean()
        rest = m.loc[~m["month_num"].isin([11, 12])]["revenue"].mean()
        if hi and rest and hi > rest * 1.12:
            return f"Your sales peak late in the year (Dec festive period: +{((hi/rest)-1)*100:.0f}% vs other months). Plan stock and staff around it."
    return None


def _profit_affect(m, sector, prod_df) -> list:
    lines = [f"The core effect: your cash conversion is at risk. More activity may be turning into less usable profit."]
    if not prod_df.empty and sector != "General":
        worst = prod_df.sort_values("Profit Margin %").iloc[0]
        lines.append(f"Your thinnest line is '{worst['Product']}' at {worst['Profit Margin %']}% margin - every sale there adds little buffer against inflation.")
    return lines


def _profit_investigate(monthly, products) -> list:
    qs = []
    rev_t = trend(monthly["revenue"])
    if rev_t == "falling":
        qs.append("Are fewer customers coming, or are they buying less? Different fixes follow.")
    elif rev_t == "rising":
        qs.append("Is growth coming from more customers or higher prices? Price-led growth can reverse quickly.")
    if not products.empty:
        try:
            slow = products[products["Fast/Slow Moving"].str.contains("Slow")]
            if len(slow):
                qs.append(f"Check top {len(slow)} slow-moving lines - how much cash is sitting on those shelves?")
        except Exception:
            pass
    qs.append("Compare your prices against the market before raising them or holding them.")
    return qs


def render(st, lang: str, expl: dict, key_prefix: str):
    """Render the explanation sections under a chart in the mandated structure."""
    s = expl
    st.markdown(f"### 🤖 What this chart is telling you")
    st.markdown(f"**WHAT AM I LOOKING AT?**  \n{s.get('what') or expl.get('title')}")
    for frag in s.get("chain", []):
        st.markdown(f"• {frag}")
    if s.get("why"):
        st.markdown("**WHY COULD THIS BE HAPPENING?**")
        for line in s["why"]:
            st.markdown(f"• {line}")
    st.markdown(f"**HOW DOES IT AFFECT THE BUSINESS?**  \n{(s.get('affect') and s['affect'][0]) or ''}")
    if s.get("investigate"):
        st.markdown("**WHAT SHOULD I INVESTIGATE?**")
        for q in s["investigate"]:
            st.markdown(f"• {q}")
    st.markdown("**WHAT CAN YOU DO?**  \n" + "".join(f"• {o}  \n" for o in s["options"]))
    if s.get("before_after"):
        st.markdown(f"**QUICK EXAMPLE**  \n{s['before_after']}")
    if s.get("macro"):
        st.markdown(f"**CONNECTION TO THE ZIMBABWE ECONOMY**  \n{s['macro']}")