"""Data loading for RFC SECURITIES.

Two inputs feed the identical downstream schema:
  * load_demo_data(sector)  - a realistic 12-month, product-level demo business.
  * parse_upload(...)       - a user Excel/CSV (Product / Price / Cost / Qty).

The demo bundle carries everything the advisor needs: product-level sales,
inventory, supplier costs (with a SA-import flag), operating expenses, rent,
transport, cash balances, debts, currencies and VAT.

NOTE (Advantages/Limitations, see README.md):
  * Seasonality and cost drift are modelled so the tool can demonstrate the
    "cash tight, stock rising" pattern - but these are MODELLED figures.
  * Accurate output requires an accurate upload; we never treat an assumption
    as a fact and we never guarantee profit.
"""
from __future__ import annotations

import io
import random
from dataclasses import dataclass, field

import pandas as pd

MONTHS = ["Sep-25", "Oct-25", "Nov-25", "Dec-25", "Jan-26", "Feb-26",
          "Mar-26", "Apr-26", "May-26", "Jun-26", "Jul-26", "Aug-26"]
MONTH_NUMS = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]

# Zimbabwe retail seasonality: festive Nov/Dec peak, January/February slump.
SEASON = {1: 0.92, 2: 0.86, 3: 0.95, 4: 0.98, 5: 1.00, 6: 0.97,
          7: 0.99, 8: 1.04, 9: 1.06, 10: 1.10, 11: 1.22, 12: 1.30}

VAT_RATE = 0.15  # Zimbabwe standard VAT

DEMO_CHOICES = [
    "Select Sector", "Clothing shop", "Grocery shop", "Restaurant",
    "Hardware business", "Transport business (Local commuter)",
    "Poultry business", "Salon", "Agriculture",
    "Gadgets/Electronics Shop", "General SME",
]

LABEL_TO_KEY = {
    "Clothing shop": "Clothing shop",
    "Grocery shop": "Grocery shop",
    "Restaurant": "Restaurant",
    "Hardware business": "Hardware business",
    "Transport business (Local commuter)": "Transport business",
    "Poultry business": "Poultry business",
    "Salon": "Salon",
    "Agriculture": "Agriculture",
    "Gadgets/Electronics Shop": "Gadgets/Electronics Shop",
    "General SME": "General SME",
}


@dataclass
class Product:
    name: str
    price: float
    cost: float
    stock_qty: int
    qty_month_base: int
    import_sa: bool = False


@dataclass
class Business:
    name: str
    sector: str
    products: list = field(default_factory=list)
    fixed_costs: float = 0.0
    currency: str = "USD + ZWL mix"
    debts: float = 0.0

    def avg_margin(self) -> float:
        m = [(p.price - p.cost) / p.price for p in self.products if p.price]
        return sum(m) / len(m) if m else 0.0

    def sa_import_share(self) -> float:
        sa = sum(p.qty_month_base for p in self.products if p.import_sa)
        total = sum(p.qty_month_base for p in self.products) or 1
        return sa / total


def _noise(rng: random.Random) -> float:
    return 0.94 + rng.random() * 0.12


OPEX_RATIO = {
    "Transport": 0.16, "Agriculture": 0.14, "Gadgets": 0.13, "Grocery": 0.10,
    "Restaurant": 0.22, "Clothing": 0.13, "Poultry": 0.15, "Beauty": 0.22,
    "Hardware": 0.13, "General": 0.16,
}


def simulate(b: Business) -> pd.DataFrame:
    """12 months of revenue, cost, profit, cash, inventory, VAT and debt."""
    rng = random.Random(hash(b.name) % (2 ** 32))
    baseline_rev = sum(p.price * p.qty_month_base for p in b.products) or 1000.0
    opex = baseline_rev * OPEX_RATIO.get(b.sector, 0.16)
    rent = opex * 0.35
    transport_cost = opex * 0.22
    debt = b.debts or baseline_rev * 1.8
    revenue_slope = 0.007
    cost_drift = 0.010
    rows = []
    cash = (opex + baseline_rev * 0.6) * 2.5
    for i, (m, mnum) in enumerate(zip(MONTHS, MONTH_NUMS)):
        season = SEASON[mnum]
        rev = sold_cost = 0.0
        for p in b.products:
            qty = p.qty_month_base * season * (1 + revenue_slope * i) * _noise(rng)
            rev += p.price * qty
            sold_cost += p.cost * qty * (1 + cost_drift * i)
            restock = qty * 1.03
            p.stock_qty = max(0, p.stock_qty + restock - qty)
        month_opex = opex * (1 + cost_drift * i)
        costs = sold_cost + month_opex
        profit = rev - costs
        cash_in = rev * 0.96
        cash_out = month_opex + sold_cost * 0.9 + rev * 0.03 + debt * 0.02
        cash = cash + cash_in - cash_out
        debt = max(0.0, debt - debt * 0.02)
        inventory = sum(p.stock_qty * p.cost for p in b.products)
        rows.append({
            "month": m, "month_num": mnum,
            "revenue": round(rev, 2), "costs": round(costs, 2),
            "profit": round(profit, 2),
            "cash_in": round(cash_in, 2), "cash_out": round(cash_out, 2),
            "cash_balance": round(cash, 2), "inventory": round(inventory, 2),
            "supplier_costs": round(sold_cost, 2),
            "rent": round(rent * (1 + cost_drift * i), 2),
            "transport": round(transport_cost * (1 + cost_drift * i), 2),
            "opex": round(month_opex, 2),
            "vat": round(max(0.0, (rev - sold_cost) * VAT_RATE), 2),
            "debt_balance": round(debt, 2),
        })
    return pd.DataFrame(rows)


def products_frame(b: Business) -> pd.DataFrame:
    rows = []
    for p in b.products:
        margin = (p.price - p.cost) / p.price * 100 if p.price else 0.0
        rows.append({
            "Product": p.name,
            "Price": round(p.price, 2),
            "Cost": round(p.cost, 2),
            "Qty": int(p.qty_month_base),
            "Margin %": round(margin, 1),
            "Status": "Fast" if margin > 25 else "Slow",
            "Imported (SA)": "Yes" if p.import_sa else "No",
        })
    return pd.DataFrame(rows)


def _demo_businesses() -> dict:
    return {
        "Clothing shop": Business("Clothing Shop", "Clothing",
            [Product("Ladies dress", 18.0, 11.0, 120, 90, True),
             Product("Men's shirt", 14.5, 8.8, 150, 75, True),
             Product("School uniforms", 22.0, 14.0, 80, 60, True),
             Product("Sneakers pair", 30.0, 20.0, 60, 35, True),
             Product("Handbags", 16.0, 9.5, 45, 25, True),
             Product("Children wear", 9.0, 5.4, 200, 110, True)], fixed_costs=1600),
        "Grocery shop": Business("Grocery Shop", "Grocery",
            [Product("Cooking oil 2L", 12.5, 10.2, 300, 180, True),
             Product("Sugar 2kg", 4.0, 3.1, 400, 260, True),
             Product("Maize meal 10kg", 10.5, 8.0, 250, 170, False),
             Product("Bread loaf", 1.8, 1.25, 200, 480, False),
             Product("Rice 5kg", 7.0, 5.4, 160, 90, True),
             Product("Soap bar", 1.0, 0.62, 600, 420, False)], fixed_costs=900),
        "Restaurant": Business("Restaurant", "Restaurant",
            [Product("Sadza & beef plate", 4.5, 3.1, 0, 320, False),
             Product("Chicken & chips", 5.0, 3.4, 0, 260, False),
             Product("Soft drinks", 0.8, 0.5, 300, 400, False),
             Product("Tea / coffee", 1.2, 0.7, 0, 220, False),
             Product("Fish & chips", 4.0, 2.7, 0, 180, False)], fixed_costs=2100),
        "Hardware business": Business("Hardware Store", "Hardware",
            [Product("Cement 50kg", 15.0, 12.2, 220, 95, False),
             Product("Paint 20L", 60.0, 46.0, 40, 14, True),
             Product("Zinc sheets", 19.5, 15.4, 90, 40, False),
             Product("Nails 5kg", 10.0, 7.1, 120, 55, True),
             Product("Bricks (pallet)", 27.0, 20.0, 30, 12, False),
             Product("Plumbing kit", 38.0, 28.0, 25, 8, True)], fixed_costs=1400),
        "Transport business": Business("Transport Business (Local commuter)", "Transport",
            [Product("Kombi route - adult", 1.2, 0.82, 0, 520, False),
             Product("Kombi route - school", 0.8, 0.55, 0, 300, False),
             Product("Long distance trip", 8.0, 5.9, 0, 40, False),
             Product("Charter / hire", 60.0, 42.0, 0, 6, False),
             Product("Goods delivery", 15.0, 10.5, 0, 22, False)], fixed_costs=1700),
        "Poultry business": Business("Poultry Farm", "Poultry",
            [Product("Broiler chicken (live)", 7.0, 4.9, 0, 180, False),
             Product("Broiler (dressed)", 8.6, 6.4, 0, 110, False),
             Product("Layers - eggs tray", 4.5, 3.4, 60, 240, False),
             Product("Chicks (day old)", 1.5, 0.95, 200, 150, False),
             Product("Feed 50kg", 23.0, 18.5, 40, 25, False)], fixed_costs=1100),
        "Salon": Business("Salon", "Beauty",
            [Product("Haircut", 4.0, 0.4, 0, 160, False),
             Product("Braiding service", 15.0, 2.0, 0, 45, False),
             Product("Relaxer kit", 12.0, 8.0, 30, 18, True),
             Product("Manicure / pedicure", 8.0, 1.5, 0, 40, False),
             Product("Hair products retail", 8.0, 5.2, 80, 70, True)], fixed_costs=1300),
        "Agriculture": Business("Agriculture", "Agriculture",
            [Product("Maize (tonne)", 320.0, 230.0, 6, 2, False),
             Product("Tomatoes (crate)", 25.0, 16.0, 0, 40, False),
             Product("Onions (bag)", 18.0, 12.0, 0, 30, False),
             Product("Soya beans (tonne)", 380.0, 290.0, 4, 1.5, False),
             Product("Groundnuts (bag)", 45.0, 32.0, 0, 12, False)], fixed_costs=950),
        "General SME": Business("General SME", "General",
            [Product("Service package A", 50.0, 30.0, 0, 12, False),
             Product("Service package B", 80.0, 48.0, 0, 8, False),
             Product("Retail item X", 5.0, 3.2, 200, 140, False),
             Product("Retail item Y", 12.0, 8.0, 120, 60, True),
             Product("Wholesale lot", 200.0, 150.0, 0, 4, False)], fixed_costs=1500),
        "Gadgets/Electronics Shop": Business("Gadgets & Electronics Shop", "Gadgets",
            [Product("Mobile phone", 245.0, 178.0, 30, 22, True),
             Product("TV 43 inch", 455.0, 356.0, 15, 6, True),
             Product("Laptop", 520.0, 398.0, 12, 4, True),
             Product("Phone accessories", 6.0, 3.6, 500, 320, True),
             Product("Solar panel kit", 280.0, 205.0, 20, 9, True),
             Product("Bluetooth speaker", 28.0, 17.5, 60, 28, True)], fixed_costs=1800),
    }


def _bundle(b: Business, monthly: pd.DataFrame, products: pd.DataFrame,
            is_demo: bool) -> dict:
    return {
        "business": b,
        "name": b.name,
        "sector": b.sector,
        "monthly": monthly,
        "products": products,
        "is_demo": is_demo,
        "uploaded": not is_demo,
        "summary": {
            "sa_import_share": round(b.sa_import_share() * 100, 1),
            "vat_rate": VAT_RATE * 100,
            "currencies": b.currency,
            "debts": round(float(monthly["debt_balance"].iloc[-1]), 2) if len(monthly) else 0.0,
            "rent": round(float(monthly["rent"].iloc[-1]), 2) if len(monthly) else 0.0,
            "transport": round(float(monthly["transport"].iloc[-1]), 2) if len(monthly) else 0.0,
            "stock_value": round(float(monthly["inventory"].iloc[-1]), 2) if len(monthly) else 0.0,
            "avg_margin": round(b.avg_margin() * 100, 1),
        },
    }


def load_demo_data(sector: str) -> dict:
    """Return the full analysis bundle for a demo sector label."""
    key = LABEL_TO_KEY.get(sector, sector)
    b = _demo_businesses()[key]
    return _bundle(b, simulate(b), products_frame(b), is_demo=True)


# --------------------------------------------------------------------------
# Uploaded file parsing (Product / Price / Cost / Qty).
# --------------------------------------------------------------------------
def _find_col(df: pd.DataFrame, aliases) -> str | None:
    lower = {str(c).strip().lower(): str(c) for c in df.columns}
    for a in aliases:
        if a in lower:
            return lower[a]
    for k, v in lower.items():
        if any(a in k for a in aliases):
            return v
    return None


def parse_upload(file_bytes: bytes, filename: str, name: str = "Uploaded Business") -> dict:
    """Parse an uploaded CSV/XLSX built on Product / Price / Cost / Qty."""
    if filename.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        df = pd.read_csv(io.BytesIO(file_bytes))
    df.columns = [str(c).strip() for c in df.columns]

    prod_col = _find_col(df, ["product", "item", "name", "route", "description"])
    price_col = _find_col(df, ["price", "selling price", "unit price"])
    cost_col = _find_col(df, ["cost", "unit cost", "purchase price"])
    qty_col = _find_col(df, ["qty", "quantity", "stock", "on hand"])
    import_col = _find_col(df, ["imported", "source", "origin"])

    if price_col is None or cost_col is None:
        raise ValueError(
            "File must contain 'Price' and 'Cost' columns (expected: "
            "Product, Price, Cost, Qty).")

    products = []
    for idx, row in df.iterrows():
        try:
            price = float(row[price_col])
            cost = float(row[cost_col])
        except (TypeError, ValueError):
            continue
        if price <= 0:
            continue
        qty = 0
        if qty_col is not None:
            try:
                qty = int(float(row[qty_col] or 0))
            except (TypeError, ValueError):
                qty = 0
        name_val = str(row[prod_col]) if prod_col else f"Item {idx + 1}"
        is_sa = False
        if import_col is not None:
            cell = str(row[import_col]).strip().lower()
            is_sa = "sa" in cell or "south africa" in cell or cell == "import"
        products.append(Product(name_val, price, cost, qty, max(1, qty), import_sa=is_sa))

    if not products:
        raise ValueError("No valid product rows found (Price and Cost must be numbers).")

    b = Business(name, "General", products, fixed_costs=300)
    monthly = simulate(b)
    return _bundle(b, monthly, products_frame(b), is_demo=False)


def upload_metrics(products: pd.DataFrame) -> dict:
    """Metrics shown in the upload view: products, avg price, avg margin, stock value."""
    if products is None or products.empty:
        return {"total_products": 0, "avg_price": 0.0, "avg_margin": 0.0, "stock_value": 0.0}
    qty = products["Qty"] if "Qty" in products else 0
    price = products["Price"]
    return {
        "total_products": int(len(products)),
        "avg_price": round(float(price.mean()), 2),
        "avg_margin": round(float(products["Margin %"].mean()), 1),
        "stock_value": round(float((price * qty).sum()), 2) if "Qty" in products else 0.0,
    }
