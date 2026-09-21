"""Data loading: demo business data (12 months, product level) and user uploads.

Every business is described with:
  - name / sector
  - 12 monthly records (revenue, costs, profit, cash in/out/balance, inventory)
  - a product table (product, selling price, cost, margin %, stock, qty sold, fast/slow)
  - import exposure flags (e.g. SA imports)
The same internal schema is produced for demo and uploaded data so every page
and the explanation engine work identically.
"""
from __future__ import annotations

import io
import math
import random
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import pandas as pd

MONTHS = ["Sep-25", "Oct-25", "Nov-25", "Dec-25", "Jan-26", "Feb-26",
          "Mar-26", "Apr-26", "May-26", "Jun-26", "Jul-26", "Aug-26"]
MONTH_NUMS = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]

# Decorative / informative realism: monthly demand multiplier for Zimbabwe retail.
SEASON = {1: 0.92, 2: 0.86, 3: 0.95, 4: 0.98, 5: 1.00, 6: 0.97,
          7: 0.99, 8: 1.04, 9: 1.06, 10: 1.10, 11: 1.22, 12: 1.30}


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

    def margin(self):
        return [(p.price - p.cost) / p.price for p in self.products]

    def avg_margin(self):
        m = self.margin()
        return sum(m) / len(m) if m else 0.0

    def sa_import_share(self) -> float:
        sa = sum(p.qty_month_base for p in self.products if p.import_sa)
        total = sum(p.qty_month_base for p in self.products) or 1
        return sa / total


def _noise(rng: random.Random) -> float:
    return 0.94 + rng.random() * 0.12


# Operating expense share of baseline revenue, per sector. Keeps every demo
# viable (positive net margin) but tight enough to be worth improving.
OPEX_RATIO = {
    "Transport": 0.16, "Agriculture": 0.14, "Gadgets": 0.13, "Grocery": 0.10,
    "Restaurant": 0.22, "Clothing": 0.13, "Poultry": 0.15, "Beauty": 0.22,
    "Hardware": 0.13, "General": 0.16,
}


def simulate(b: Business) -> pd.DataFrame:
    """Produce the 12-month financial record for a business.

    Model: profit = revenue - (COGS sold + operating expenses). Cash uses a
    collection lag and a small stock build (purchases slightly ahead of sales),
    so cash grows a little slower than profit while inventory creeps up - the
    classic 'cash tight, stock rising' situation many SMEs actually live with.
    """
    rng = random.Random(hash(b.name) % (2 ** 32))
    baseline_rev = sum(p.price * p.qty_month_base for p in b.products)
    opex = baseline_rev * OPEX_RATIO.get(b.sector, 0.16)
    revenue_slope = 0.007      # ~+8% revenue over the year
    cost_drift = 0.010         # ~+12% cost over the year (inflation pressure)
    rows = []
    monthly_out_cash = opex + baseline_rev * 0.6
    cash = monthly_out_cash * 2.5
    for i, (m, mnum) in enumerate(zip(MONTHS, MONTH_NUMS)):
        season = SEASON[mnum]
        rev = 0.0
        sold_cost = 0.0
        for p in b.products:
            qty = p.qty_month_base * season * (1 + revenue_slope * i) * _noise(rng)
            rev += p.price * qty
            sold_cost += p.cost * qty * (1 + cost_drift * i)
            restock = qty * 1.03
            p.stock_qty = max(0, p.stock_qty + restock - qty)
        costs = sold_cost + opex * (1 + cost_drift * i)
        profit = rev - costs
        cash_in = rev * 0.96
        purchases_paid = sold_cost * 0.9
        cash_out = opex * (1 + cost_drift * i) + purchases_paid + rev * 0.03
        cash = cash + cash_in - cash_out
        inventory = sum(p.stock_qty * p.cost for p in b.products)
        rows.append({
            "month": m, "month_num": mnum,
            "revenue": round(rev, 2), "costs": round(costs, 2),
            "profit": round(profit, 2),
            "cash_in": round(cash_in, 2), "cash_out": round(cash_out, 2),
            "cash_balance": round(cash, 2), "inventory": round(inventory, 2),
        })
    return pd.DataFrame(rows)


def products_frame(b: Business) -> pd.DataFrame:
    """Product table: name, price, cost, margin %, stock, qty, fast/slow."""
    rows = []
    for p in b.products:
        margin = (p.price - p.cost) / p.price * 100
        slow = p.stock_qty > p.qty_month_base * 2.5
        rows.append({
            "Product": p.name,
            "Selling Price": round(p.price, 2),
            "Cost": round(p.cost, 2),
            "Profit Margin %": round(margin, 1),
            "Stock Qty": p.stock_qty,
            "Monthly Qty Sold": p.qty_month_base,
            "Fast/Slow Moving": "Slow Moving" if slow else "Fast Moving",
            "Imported (SA)": "Yes" if p.import_sa else "No",
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Demo businesses - realistic Zimbabwe product mixes.
# --------------------------------------------------------------------------
def _demo_businesses() -> dict:
    return {
        "Clothing shop": Business("Clothing Shop (Demo)", "Clothing",
            [Product("Ladies dress", 18.0, 11.0, 120, 90, True),
             Product("Men's shirt", 14.5, 8.8, 150, 75, True),
             Product("School uniforms", 22.0, 14.0, 80, 60, True),
             Product("Sneakers pair", 30.0, 20.0, 60, 35, True),
             Product("Handbags", 16.0, 9.5, 45, 25, True),
             Product("Children wear", 9.0, 5.4, 200, 110, True)], fixed_costs=1600),
        "Grocery shop": Business("Grocery Shop (Demo)", "Grocery",
            [Product("Cooking oil 2L", 12.5, 10.2, 300, 180, True),
             Product("Sugar 2kg", 4.0, 3.1, 400, 260, True),
             Product("Maize meal 10kg", 10.5, 8.0, 250, 170, False),
             Product("Bread loaf", 1.8, 1.25, 200, 480, False),
             Product("Rice 5kg", 7.0, 5.4, 160, 90, True),
             Product("Soap bar", 1.0, 0.62, 600, 420, False)], fixed_costs=900),
        "Restaurant": Business("Restaurant (Demo)", "Restaurant",
            [Product("Sadza & beef plate", 4.5, 3.1, 0, 320, False),
             Product("Chicken & chips", 5.0, 3.4, 0, 260, False),
             Product("Soft drinks", 0.8, 0.5, 300, 400, False),
             Product("Tea / coffee", 1.2, 0.7, 0, 220, False),
             Product("Fish & chips", 4.0, 2.7, 0, 180, False)], fixed_costs=2100),
        "Hardware business": Business("Hardware Store (Demo)", "Hardware",
            [Product("Cement 50kg", 15.0, 12.2, 220, 95, False),
             Product("Paint 20L", 60.0, 46.0, 40, 14, True),
             Product("Zinc sheets", 19.5, 15.4, 90, 40, False),
             Product("Nails 5kg", 10.0, 7.1, 120, 55, True),
             Product("Bricks (pallet)", 27.0, 20.0, 30, 12, False),
             Product("Plumbing kit", 38.0, 28.0, 25, 8, True)], fixed_costs=1400),
        "Transport business": Business("Transport Business (Demo)", "Transport",
            [Product("Kombi route - adult", 1.2, 0.82, 0, 520, False),
             Product("Kombi route - school", 0.8, 0.55, 0, 300, False),
             Product("Long distance trip", 8.0, 5.9, 0, 40, False),
             Product("Charter / hire", 60.0, 42.0, 0, 6, False),
             Product("Goods delivery", 15.0, 10.5, 0, 22, False)], fixed_costs=1700),
        "Poultry business": Business("Poultry Farm (Demo)", "Poultry",
            [Product("Broiler chicken (live)", 7.0, 4.9, 0, 180, False),
             Product("Broiler (dressed)", 8.6, 6.4, 0, 110, False),
             Product("Layers - eggs tray", 4.5, 3.4, 60, 240, False),
             Product("Chicks (day old)", 1.5, 0.95, 200, 150, False),
             Product("Feed 50kg", 23.0, 18.5, 40, 25, False)], fixed_costs=1100),
        "Salon": Business("Salon (Demo)", "Beauty",
            [Product("Haircut", 4.0, 0.4, 0, 160, False),
             Product("Braiding service", 15.0, 2.0, 0, 45, False),
             Product("Relaxer kit", 12.0, 8.0, 30, 18, True),
             Product("Manicure / pedicure", 8.0, 1.5, 0, 40, False),
             Product("Hair products retail", 8.0, 5.2, 80, 70, True)], fixed_costs=1300),
        "Agriculture": Business("Agriculture (Demo)", "Agriculture",
            [Product("Maize (tonne)", 320.0, 230.0, 6, 2, False),
             Product("Tomatoes (crate)", 25.0, 16.0, 0, 40, False),
             Product("Onions (bag)", 18.0, 12.0, 0, 30, False),
             Product("Soya beans (tonne)", 380.0, 290.0, 4, 1.5, False),
             Product("Groundnuts (bag)", 45.0, 32.0, 0, 12, False)], fixed_costs=950),
        "General SME": Business("General SME (Demo)", "General",
            [Product("Service package A", 50.0, 30.0, 0, 12, False),
             Product("Service package B", 80.0, 48.0, 0, 8, False),
             Product("Retail item X", 5.0, 3.2, 200, 140, False),
             Product("Retail item Y", 12.0, 8.0, 120, 60, True),
             Product("Wholesale lot", 200.0, 150.0, 0, 4, False)], fixed_costs=1500),
        "Gadgets/Electronics Shop": Business("Gadgets Shop (Demo)", "Gadgets",
            [Product("Mobile phone", 245.0, 178.0, 30, 22, True),
             Product("TV 43 inch", 455.0, 356.0, 15, 6, True),
             Product("Laptop", 520.0, 398.0, 12, 4, True),
             Product("Phone accessories", 6.0, 3.6, 500, 320, True),
             Product("Solar panel kit", 280.0, 205.0, 20, 9, True),
             Product("Bluetooth speaker", 28.0, 17.5, 60, 28, True)], fixed_costs=1800),
    }


def demo_business(sector: str) -> Business:
    return _demo_businesses()[sector]


def demo_sectors() -> list:
    return list(_demo_businesses().keys())


def load_demo(sector: str) -> dict:
    b = demo_business(sector)
    return {
        "business": b,
        "monthly": simulate(b),
        "products": products_frame(b),
        "is_demo": True,
        "uploaded": False,
        "sector": b.sector,
    }


# --------------------------------------------------------------------------
# Uploaded file parsing.
# --------------------------------------------------------------------------
def _col(df: pd.DataFrame, aliases) -> str | None:
    lower = {str(c).strip().lower(): str(c) for c in df.columns}
    for a in aliases:
        if a in lower:
            return lower[a]
    for k, v in lower.items():
        if any(a in k for a in aliases):
            return v
    return None


def load_uploaded(file_bytes: bytes, filename: str, name_override: str | None = None) -> dict:
    """Parse an uploaded Excel/CSV into the standard analysis bundle."""
    if filename.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        df = pd.read_csv(io.BytesIO(file_bytes))
    df.columns = [str(c).strip() for c in df.columns]

    rev_col = _col(df, ["revenue", "sales", "income"])
    cost_col = _col(df, ["costs", "expenses", "cogs"]) or _col(df, ["cost of goods"])

    # Shape A: monthly ledger (has a date/month column + revenue).
    if rev_col and (_col(df, ["month"]) or _col(df, ["date"])):
        return _build_monthly_bundle(df, rev_col, cost_col, name_override)

    # Shape B: product list (has price + cost).
    price_col = _col(df, ["price", "selling price", "unit price"])
    cost_p = _col(df, ["cost", "unit cost", "purchase price"])
    if price_col is not None and cost_p is not None:
        return _build_product_bundle(df, price_col, cost_p, name_override)

    raise ValueError(
        "File format not recognised. Use a product list at least with "
        "'Price' and 'Cost' columns, or a monthly table with 'Month' and 'Revenue'.")


def _build_monthly_bundle(df, rev_col, cost_col, name):
    name = name or "Uploaded Business"
    recs = []
    for _, row in df.iterrows():
        try:
            recs.append({
                "month": str(row.get(_col(df, ["month"]) or _col(df, ["date"]), "")),
                "revenue": float(row[rev_col] or 0),
                "costs": float(row[cost_col] or 0) if cost_col else 0,
            })
        except (TypeError, ValueError):
            continue
    cash_in = [r["revenue"] * 0.92 for r in recs]
    cash_out = [r["costs"] + r["costs"] * 0.06 for r in recs]
    cash = 0.0
    rows = []
    for i, r in enumerate(recs):
        cash += cash_in[i] - cash_out[i]
        rows.append({
            "month": r["month"] or MONTHS[i] if i < len(MONTHS) else f"M{i+1}",
            "month_num": MONTH_NUMS[i] if i < len(MONTH_NUMS) else (i % 12) + 1,
            "revenue": round(r["revenue"], 2), "costs": round(r["costs"], 2),
            "profit": round(r["revenue"] - r["costs"], 2),
            "cash_in": round(cash_in[i], 2), "cash_out": round(cash_out[i], 2),
            "cash_balance": round(cash, 2), "inventory": 0.0,
        })
    monthly = pd.DataFrame(rows)
    products = pd.DataFrame()
    if cost_col is not None:
        avg_cost = monthly["costs"].mean()
        avg_rev = monthly["revenue"].mean()
        products = pd.DataFrame([{
            "Product": "Aggregated business", "Selling Price": round(avg_rev, 2),
            "Cost": round(avg_cost, 2),
            "Profit Margin %": round((avg_rev - avg_cost) / avg_rev * 100, 1) if avg_rev else 0,
            "Stock Qty": 0, "Monthly Qty Sold": 1, "Fast/Slow Moving": "Fast Moving",
            "Imported (SA)": "Unknown",
        }])
    return {"business": Business(name, "General", fixed_costs=0.0), "monthly": monthly,
            "products": products, "is_demo": False, "uploaded": True, "sector": "General"}


def _build_product_bundle(df, price_col, cost_p, name):
    name = name or "Uploaded Business"
    products = []
    stock_col = _col(df, ["stock", "qty", "stock qty", "quantity", "on hand"])
    qty_col = _col(df, ["qty sold", "sold", "monthly qty", "volume"])
    for _, row in df.iterrows():
        try:
            price = float(row[price_col] or 0)
            cost = float(row[cost_p] or 0)
        except (TypeError, ValueError):
            continue
        stock = float(row[stock_col]) if stock_col else 0
        qty = float(row[qty_col]) if qty_col else (0.5 * price)
        if price <= 0:
            continue
        products.append(Product(str(row.get(df.columns[0], "Item")), price, cost,
                                int(stock), int(max(1, round(qty)))))
    if not products:
        raise ValueError("No valid product rows found (need price and cost).")
    b = Business(name, "General", products, fixed_costs=300)
    table = products_frame(b)
    return {"business": b, "monthly": simulate(b), "products": table,
            "is_demo": False, "uploaded": True, "sector": "General"}