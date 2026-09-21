"""Sector-specific advice so every recommendation is actionable for the
business type actually being analysed (transport, agriculture, gadgets, ...).
"""
from __future__ import annotations

ADVICE = {
    "Transport": {
        "pricing": ["Review fares against fuel price per km. If fuel rose, test a small fare increase (e.g. $1.20 adult fare) or convert to USD where accepted.",
                    "Prefer fuel-efficient driving and reduce idling to protect the margin per trip."],
        "cash_stock": ["Keep a fuel and spares cash buffer for at least 2 weeks - prices move weekly.",
                       "Pool maintenance with other kombi owners to cut repair and parts cost."],
        "diversify": ["Add school runs and charter jobs to spread demand across the day.",
                      "Comply with ZINARA toll and load licensing to avoid impoundments that cost more than the fee."],
        "resilience": ["Fuel price and road toll announcements directly raise your cost per trip - track ZERA weekly.",
                       "Roadblocks and route bans change demand fast; keep a route map with alternatives."],
    },
    "Agriculture": {
        "pricing": ["Buy inputs early (before the season price spike) and store them safely.",
                    "Compare GMB pricing with private buyers before harvest; contract early where possible."],
        "cash_stock": ["Avoid holding grain too long if you need cash - storage risk and moisture losses are real.",
                       "Diversify crops so one failed market does not empty your cash."],
        "diversify": ["Add drought-tolerant seed varieties and consider winter/irrigation crops.",
                      "Sell through both GMB and private buyers to spread price risk."],
        "resilience": ["Rainfall and input prices are your two biggest risks - monitor the season outlook.",
                       "Fertiliser and seed are largely imported; FX moves change your cost base."],
    },
    "Gadgets": {
        "pricing": ["Compare sourcing from SA vs China including freight, duty (~up to 10-20%) and clearing before pricing.",
                    "Re-price fast when the exchange rate moves - electronics lose margin quickly."],
        "cash_stock": ["Electronics depreciate fast. Turn slow stock through promos before the model ages.",
                       "Do not stock heavy quantities of one model - balances are expensive."],
        "diversify": ["Offer repairs and accessories - they carry much better margins than devices.",
                      "Use the IMEI / POTRAZ registration rules as an opportunity, not a hurdle: be the shop that registers properly."],
        "resilience": ["Import duty, exchange rate and POTRAZ enforcement each change your landed cost.",
                       "Consider Starlink and solar accessories - demand is growing alongside electricity outages."],
    },
    "Grocery": {
        "pricing": ["Sugar, cooking oil and maize meal prices are headline-sensitive - monitor and reprice weekly.",
                    "Buy staples in bulk from wholesalers just before supply dips, not at peak."],
        "cash_stock": ["Perishables must move - discount near-expiry stock rather than write it off.",
                       "Keep fast movers (bread, mealie-meal) always in stock even if margin is thin."],
        "diversify": ["Add prepaid electricity / airtime / DStv - low risk and brings daily foot traffic.",
                      "Offer credit to trusted customers only, capped, to protect cash."],
        "resilience": ["Supermarket price promotions (OK, Pick n Pay) pull customers - respond with bundles, not just price cuts.",
                       "Electricity outages spoil stock - invest in a small solar chest cooler if chilled lines matter."],
    },
    "Restaurant": {
        "pricing": ["Re-price menu when input costs move; test a small incremental price with combo value meals.",
                    "Portion control is margin control - weigh servings weekly."],
        "cash_stock": ["Food waste is cash loss - plan purchases to weekly demand and freeze surpluses.",
                       "Pay suppliers on terms, and never let cash sales run the week without a bank deposit."],
        "diversify": ["Add delivery / online orders and corporate lunch packages to smooth weekday demand.",
                      "Second branch or a kiosk in a busy area only after the first location is consistently profitable."],
        "resilience": ["CBD closures and food safety inspections change foot traffic overnight - keep an alternate location plan.",
                       "Gas and electricity costs fluctuate; track cost per meal."],
    },
    "Clothing": {
        "pricing": ["Seasonal launches sell at full price - restock uniforms before school terms; discounts clear old stock.",
                    "30-45% markup is typical; know your margin per garment before discounting."],
        "cash_stock": ["Fashion stock dates fast - run clearance cycles so cash is not locked on hangers.",
                       "Balance orders: fast-selling lines early, fashion lines small and frequent."],
        "diversify": ["Add tailoring, repairs or uniform contracts for steady institutional demand.",
                      "Sell on weekends at market days and online (WhatsApp catalogue) without adding a branch."],
        "resilience": ["Import of fabrics and garments is FX-driven - a ZWL supplier deal can protect you.",
                       "Uniform season (start of terms) is your peak - stock before, not during."],
    },
    "Poultry": {
        "pricing": ["Price by live vs dressed margin; dressed gives better margin but needs cold chain.",
                    "Track feed cost per bird - feed is 60-70% of your cost and drives every price decision."],
        "cash_stock": ["Sell birds at target weight - holding longer feeds away your profit.",
                       "Cull or discount slow cycles; day-old chick demand is seasonal."],
        "diversify": ["Add layering for steady egg income alongside broilers.",
                      "Supply local tuckshops, shops and schools on order rather than hoping for walk-ins."],
        "resilience": ["Feed price spikes and Newcastle/flu risk are your top threats - biosecurity is cheap insurance.",
                       "Have a cold-storage or wholesale exit if market price dips."],
    },
    "Beauty": {
        "pricing": ["Raise service prices for skilled time, sell product retail for margin.",
                    "Package braiding + treatment so average spend per client rises."],
        "cash_stock": ["Buy hair products in small batches to avoid ageing stock.",
                       "Track which products fly and which sit - stop reordering sit-stock."],
        "diversify": ["Add mobile home-service for weddings/events - premium pricing.",
                      "Offer training courses when demand is slow; it converts empty chairs into revenue."],
        "resilience": ["Beauty spend is discretionary - during tight months clients seek value, not luxury. Keep a value offer.",
                       "Hair product imports shift with FX - compare ZWL local vs forex imports."],
    },
    "Hardware": {
        "pricing": ["Cement and paint are price-sensitive - thin margin, but they pull customers for higher-margin items.",
                    "Quote bulk customers with invoice terms and a deposit to protect cash."],
        "cash_stock": ["Heavy stock ties cash - buy against orders for big-ticket building materials.",
                       "Slow-moving niche items should be special-order only."],
        "diversify": ["Add tool hire and installation services - recurring revenue beyond retail.",
                      "Supply builders and contractors on schedule - they buy volume."],
        "resilience": ["Building follows construction cycles and government infrastructure projects - watch tender news.",
                       "Imported tools and fittings shift with FX; hold essential stock ahead of price moves."],
    },
    "Agriculture_General": {
        "pricing": ["Price against both market floors and your full cost (inputs, labour, transport).",
                    "Sell in stages to benefit from market moves rather than all at once."],
        "cash_stock": ["Produce is perishable - have a sale or processing plan before it spoils.",
                       "Keep a working-capital reserve for the next planting cycle."],
        "diversify": ["Diversify crops/livestock so a single market failure does not sink you.",
                      "Consider value addition (grinding, processing) to lift margins."],
        "resilience": ["Weather, inputs, and market access are your top risks - monitor all three.",
                       "Join a cooperative or marketing group to strengthen bargaining power."],
    },
    "General": {
        "pricing": ["Review every product's margin: price, cost, profit. Stop selling items that lose money after all costs.",
                    "Test small price increments on bestsellers before broad changes."],
        "cash_stock": ["Keep working capital - stock up on what moves, cut what sits.",
                       "Deposit cash daily and pay on terms to avoid cash crunches."],
        "diversify": ["Sell through more channels: market day, online, WhatsApp, institutional orders.",
                      "Reinvest profit into one proven area before expanding to a new one."],
        "resilience": ["Track inflation, fuel and exchange-rate news - they move your costs and your customers' wallets.",
                       "Read every new SME regulation to check whether it affects you."],
    },
}

SECTOR_LABELS = {
    "Clothing": "Clothing", "Grocery": "Grocery", "Restaurant": "Restaurant",
    "Hardware": "Hardware", "Transport": "Transport", "Poultry": "Poultry",
    "Beauty": "Beauty", "Agriculture": "Agriculture", "General": "General",
    "Gadgets": "Gadgets",
}


def sector_key(sector: str) -> str:
    return SECTOR_LABELS.get(sector, sector)


def can_do(sector: str, dimension: str) -> list:
    key = sector_key(sector)
    table = ADVICE.get(key) or ADVICE.get("General", {})
    return table.get(dimension, ADVICE["General"][dimension])


def macro_context_line(sector: str, econ: dict) -> str:
    """One line linking the macro economy to this sector."""
    key = sector_key(sector)
    hints = {
        "Transport": "Fuel prices and road tolls directly drive your cost per trip and your daily margins.",
        "Agriculture": "Rainfall, input prices and export/import FX changes drive your harvest economics.",
        "Gadgets": "Import duties, exchange rates and POTRAZ rules drive your landed cost for every device.",
        "Grocery": "Sugar, cooking oil and mealie-meal prices, plus supermarket competition, drive your foot traffic and margins.",
        "Restaurant": "Customer spending power, CBD access and food costs drive your covers and margins.",
        "Clothing": "Uniform seasons, FX-driven imports and customer budgets drive your seasonal cash.",
        "Poultry": "Feed prices and disease risk drive your cost per bird and your sale timing.",
        "Beauty": "Discretionary spending and FX-priced hair products drive your average client spend.",
        "Hardware": "Construction cycles, infrastructure tenders and imported tool prices drive your big-ticket sales.",
        "General": "Inflation, exchange rates, fuel and wages move both your costs and your customers' spending power.",
    }
    base = hints[key]
    if econ and econ.get("inflation") is not None:
        base += f" With inflation around {econ['inflation']:.1f}%, customer budgets stay tight."
    return base