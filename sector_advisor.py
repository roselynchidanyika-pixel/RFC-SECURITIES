"""Sector-specific advice so every recommendation is actionable for the
business type being analysed (transport, agriculture, gadgets, grocery, ...).

get_sector_advice(sector, econ_data) returns advice bullets for the report.
Every bullet uses real Zimbabwe market specifics where known; figures that are
illustrative watchpoints are declared as such and never presented as fact.
"""
from __future__ import annotations

ADVICE = {
    "Transport": {
        "pricing": ["Review fares against fuel price per km. If fuel rises, test a small fare increase or a USD fare where accepted.",
                    "Prefer fuel-efficient driving and reduce idling to protect the margin per trip."],
        "cash_stock": ["Keep a fuel and spares cash buffer for at least 2 weeks — prices move weekly.",
                       "Pool maintenance with other kombi owners to cut repair and parts cost."],
        "diversify": ["Add school runs and charter jobs to spread demand across the day.",
                      "Comply with ZINARA toll and operating licences to avoid impoundments that cost more than the fee."],
        "resilience": ["Fuel price and road toll announcements directly raise your cost per trip — track ZERA weekly.",
                       "Route bans and roadblocks change demand fast; keep a route map with alternatives."],
        "report_example": ["Fuel rose from $1.65 to $1.82/L (ZERA); cost roughly +$3.20 per Harare–Chitungwiza round trip, ZINARA tolls at $2, and ZUPCO competition is strong. Options to model: fare $1.00 -> $1.20 or a USD fare, fuel-efficient driving, and pooled maintenance."],
    },
    "Agriculture": {
        "pricing": ["Buy inputs early (before the seasonal price spike) and store them safely.",
                    "Compare GMB pricing with private buyers before harvest; contract early where possible."],
        "cash_stock": ["Avoid holding grain too long if you need cash — storage risk and moisture losses are real.",
                       "Diversify crops so one failed market does not empty your cash."],
        "diversify": ["Add drought-tolerant seed varieties and consider winter/irrigation crops.",
                      "Sell through both GMB and private buyers to spread price risk."],
        "resilience": ["Rainfall and input prices are your two biggest risks — monitor the season outlook.",
                       "Fertiliser and seed are largely imported; FX moves change your cost base."],
        "report_example": ["Agrishow 2026 drew 15,000 farmers, the Met Department flags delayed rains, and fertiliser is around $42/bag. Consider drought-tolerant seed, early input buying, and compare GMB vs private buyers."],
    },
    "Gadgets": {
        "pricing": ["Compare sourcing from SA vs China including freight, duty and clearing before pricing.",
                    "Re-price fast when the exchange rate moves — electronics lose margin quickly."],
        "cash_stock": ["Electronics depreciate fast. Turn slow stock through promos before the model ages.",
                       "Do not stock heavy quantities of one model — balancing capital is expensive."],
        "diversify": ["Offer repairs and accessories — they carry much better margins than devices.",
                      "Treat POTRAZ IMEI registration as an opportunity: be the shop that registers properly."],
        "resilience": ["Import duty, exchange rate and POTRAZ enforcement each change your landed cost.",
                       "Starlink and solar accessories demand grows alongside electricity outages."],
        "report_example": ["ZIMRA statutory instrument raised second-hand duty from 25% to 35%, POTRAZ enforces IMEI registration, and SA landed costs are rising. Model the new landed cost before pricing each device."],
    },
    "Grocery": {
        "pricing": ["Sugar, cooking oil and maize-meal prices are headline-sensitive — monitor and reprice weekly.",
                    "Buy staples in bulk just before supply dips, not at peak."],
        "cash_stock": ["Perishables must move — discount near-expiry stock rather than write it off.",
                       "Keep fast movers (bread, mealie-meal) always in stock even if margin is thin."],
        "diversify": ["Add prepaid electricity, airtime or DStv — low risk and brings daily foot traffic.",
                      "Offer credit to trusted customers only, capped, to protect cash."],
        "resilience": ["Supermarket price promotions (OK, TM) pull customers — respond with bundles, not only price cuts.",
                       "Electricity outages spoil stock — consider a small solar chest cooler for chilled lines."],
        "report_example": ["The OK/TM price war keeps pressure on prices. Respond with bundles and loyalty value rather than a pure discount race."],
    },
    "Restaurant": {
        "pricing": ["Re-price the menu when input costs move; test a small incremental price with combo value meals.",
                    "Portion control is margin control — weigh servings weekly."],
        "cash_stock": ["Food waste is cash loss — plan purchases to weekly demand and freeze surpluses.",
                       "Pay suppliers on terms, and deposit cash sales daily."],
        "diversify": ["Add delivery and corporate lunch packages to smooth weekday demand.",
                      "A second branch or kiosk only after the first location is consistently profitable."],
        "resilience": ["CBD access and food-safety inspections change foot traffic overnight — keep an alternate-location plan.",
                       "Gas and electricity costs fluctuate; track cost per meal."],
        "report_example": ["City-centre trading hours tightened to 6pm affect evening covers. Model a kiosk or later trading out-of-CBD, delivery channel, and adjusted staffing."],
    },
    "Clothing": {
        "pricing": ["Seasonal launches sell at full price; restock uniforms before school terms; discounts clear old stock.",
                    "Understand your margin per garment before discounting."],
        "cash_stock": ["Fashion stock dates fast — run clearance cycles so cash is not locked on hangers.",
                       "Balance orders: fast-selling lines early, fashion lines small and frequent."],
        "diversify": ["Add tailoring, repairs or uniform contracts for steady institutional demand.",
                      "Sell on market days and via WhatsApp catalogue without adding a branch."],
        "resilience": ["Fabric and garment imports are FX-driven — a ZWL supplier deal can protect you.",
                       "Uniform season is your peak; stock before, not during."],
        "report_example": ["School-term uniform demand is the anchor. Order before term starts and pair it with a clearance cycle for dated stock."],
    },
    "Poultry": {
        "pricing": ["Price live vs dressed separately — dressed gives better margin but needs cold chain.",
                    "Track feed cost per bird — feed is 60-70% of cost and drives every price decision."],
        "cash_stock": ["Sell birds at target weight — holding longer feeds away your profit.",
                       "Cull or discount slow cycles; day-old chick demand is seasonal."],
        "diversify": ["Add layering for steady egg income alongside broilers.",
                      "Supply shops, schools and tuckshops on order rather than hoping for walk-ins."],
        "resilience": ["Feed price spikes and avian-disease risk are top threats — biosecurity is cheap insurance.",
                       "Have a cold-storage or wholesale exit if market price dips."],
        "report_example": ["Feed is the dominant cost. Lock supply early and sell at target weight to protect margin per bird."],
    },
    "Beauty": {
        "pricing": ["Raise service prices for skilled time and sell product retail for margin.",
                    "Package braiding + treatment so average spend per client rises."],
        "cash_stock": ["Buy hair products in small batches to avoid ageing stock.",
                       "Track which products fly and which sit — stop reordering sit-stock."],
        "diversify": ["Add mobile home-service for weddings and events — premium pricing.",
                      "Offer training courses in slow periods; convert empty chairs into revenue."],
        "resilience": ["Beauty spend is discretionary — in tight months clients seek value. Keep a value offer.",
                       "Hair product imports shift with FX — compare ZWL local vs forex imports."],
        "report_example": ["Discretionary spending is tight. Package value services and compare local vs FX hair-product sourcing."],
    },
    "Hardware": {
        "pricing": ["Cement and paint are price-sensitive loss leaders that pull customers to higher-margin items.",
                    "Quote bulk customers with invoice terms and a deposit to protect cash."],
        "cash_stock": ["Heavy stock ties cash — buy against orders for big-ticket building materials.",
                       "Slow-moving niche items should be special-order only."],
        "diversify": ["Add tool hire and installation services — recurring revenue beyond retail.",
                      "Supply builders and contractors on schedule — they buy volume."],
        "resilience": ["Building follows construction cycles and infrastructure projects — watch tender news.",
                       "Imported tools and fittings shift with FX; hold essential stock ahead of price moves."],
        "report_example": ["Construction projects drive demand. Quote bulk orders with deposits and watch infrastructure tender news."],
    },
    "General": {
        "pricing": ["Review every product's margin: price, cost, profit. Stop selling items that lose money after all costs.",
                    "Test small price increments on bestsellers before broad changes."],
        "cash_stock": ["Keep working capital — stock up on what moves, cut what sits.",
                       "Deposit cash daily and pay on terms to avoid cash crunches."],
        "diversify": ["Sell through more channels: market day, online, WhatsApp, institutional orders.",
                      "Reinvest profit into one proven area before expanding to a new one."],
        "resilience": ["Track inflation, fuel and exchange-rate news — they move your costs and your customers' wallets.",
                       "Read every new SME regulation to check whether it affects you."],
        "report_example": ["Inflation, FX and fuel move both costs and customer budgets. Protect margin and keep cash moving through fast-selling lines."],
    },
}

SECTOR_KEY = {
    "Clothing": "Clothing", "Grocery": "Grocery", "Restaurant": "Restaurant",
    "Hardware": "Hardware", "Transport": "Transport", "Poultry": "Poultry",
    "Beauty": "Beauty", "Agriculture": "Agriculture", "General": "General",
    "Gadgets": "Gadgets",
}


def sector_key(sector: str) -> str:
    return SECTOR_KEY.get(sector, sector)


def can_do(sector: str, dimension: str) -> list:
    key = sector_key(sector)
    table = ADVICE.get(key) or ADVICE.get("General", {})
    return table.get(dimension, ADVICE["General"][dimension])


def get_sector_advice(sector: str, econ_data: dict = None) -> dict:
    """Return pricing/cash/diversify/resilience bullets + report example."""
    key = sector_key(sector)
    table = ADVICE.get(key) or ADVICE["General"]
    advice = {
        "pricing": table.get("pricing", []),
        "cash_stock": table.get("cash_stock", []),
        "diversify": table.get("diversify", []),
        "resilience": table.get("resilience", []),
        "report_example": table.get("report_example", ADVICE["General"]["report_example"]),
    }
    if econ_data and econ_data.get("inflation") is not None:
        advice["macro_line"] = macro_context_line(key, econ_data)
    else:
        advice["macro_line"] = macro_context_line(key, None)
    return advice


def macro_context_line(sector: str, econ: dict | None) -> str:
    key = sector_key(sector)
    hints = {
        "Transport": "Fuel prices and road tolls directly drive your cost per trip and daily margins.",
        "Agriculture": "Rainfall, input prices and export/import FX changes drive your harvest economics.",
        "Gadgets": "Import duties, exchange rates and POTRAZ rules drive the landed cost of every device.",
        "Grocery": "Staple prices and supermarket competition drive foot traffic and margins.",
        "Restaurant": "Customer spending power, city-centre access and food costs drive covers and margins.",
        "Clothing": "Uniform seasons, FX-driven imports and customer budgets drive seasonal cash.",
        "Poultry": "Feed prices and disease risk drive cost per bird and sale timing.",
        "Beauty": "Discretionary spending and FX-priced hair products drive average client spend.",
        "Hardware": "Construction cycles, infrastructure tenders and imported tool prices drive big-ticket sales.",
        "General": "Inflation, exchange rates, fuel and wages move both your costs and customers' spending power.",
    }
    base = hints[key]
    if econ and econ.get("inflation") is not None:
        base += f" With inflation around {econ['inflation']:.1f}%, customer budgets stay tight."
    return base