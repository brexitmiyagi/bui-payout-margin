"""Are utilities themselves cheap? A look-through valuation against the 10-year.

Two measures. First, XLU's forward earnings yield (1 / P/E FY1 from State Street, 13 Nov 2026) against the
10-year: a crude equity risk premium for the sector BUI mostly owns. There's no free history of that P/E, so it's
a point, not a series. Second, a series I can build: the income yield of BUI's own book each year, from the
financial highlights (net investment income per share over average NAV, plus the expense ratio, which is what the
holdings paid before BUI's costs), against that year's average 10-year yield.
Also: how much the target moves if earnings growth is FactSet's 9.42% instead of my 7%.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

v = pd.read_csv(os.path.join(DATA, "valuation_snapshot_2026_11_13.csv")).set_index("item").value
y = pd.read_csv(os.path.join(DATA, "dgs10.csv"))
y.columns = ["date", "y"]
y["date"] = pd.to_datetime(y.date)
y = y.set_index("date").y.replace(".", np.nan).astype(float)
y10 = 5.15
pe = v["XLU price/earnings FY1"]
p("XLU forward P/E %.2f -> earnings yield %.2f%% vs 10-year %.2f%%: gap %+.2f points" % (pe, 100 / pe, y10, 100 / pe - y10))

fh = pd.read_csv(os.path.join(DATA, "financial_highlights.csv"))
rows = []
for r in fh.itertuples():
    avg_nav = (r.nav_begin + r.nav_end) / 2
    if r.period == "H1 2026":
        nii, yr, ten = r.nii * 2, "2026 (H1, annualised)", y.loc["2026-01-01":"2026-06-30"].mean()
    else:
        nii, yr, ten = r.nii, str(r.period), y.loc[f"{r.period}-01-01":f"{r.period}-12-31"].mean()
    book = nii / avg_nav * 100 + r.expense_ratio_pct
    rows.append({"year": yr, "book_income_yield": round(book, 2), "avg_10y": round(ten, 2), "gap": round(book - ten, 2)})
t = pd.DataFrame(rows)
p("\nBUI book income yield (before BUI's costs) vs the average 10-year:")
p(t.to_string(index=False))
p("note: 2021-2025 is the covered-call era; option premium is booked as gains, not income, so it isn't in this yield")

# target sensitivity to the growth input (same scenario set as implied_rate_vol.py)
def target(g):
    flat = 2.76 + g - 1.06
    nav0, pay, Dc, y0, fwd, sig = 26.38, 1.848, 8.0, 5.15, 5.24, 1.06
    t_ = 0
    for sh, w, prem in [(-1.41, .25, 1.0), (0, .5, -0.26), (1.41, .25, -5.0)]:
        ye = fwd + sh * sig
        t_ += w * (nav0 * (1 + flat / 100 - Dc * (ye - y0) / 100) - pay) * (1 + prem / 100)
    return t_
g2 = v["XLU est. 3-5 year EPS growth (FactSet)"]
p("\ntarget at 7%% growth $%.2f; at FactSet's %.2f%% for XLU $%.2f; each point of growth is worth $%.2f" %
  (target(7), g2, target(g2), target(8) - target(7)))
t.to_csv(os.path.join(RES, "valuation_lookthrough.csv"), index=False)
open(os.path.join(RES, "valuation_lookthrough.txt"), "w").write("\n".join(out) + "\n")
