"""After-tax wealth at the end of a hold: BUI against XLU, for a taxable US holder.

after_tax_yield.py compares the tax paid each year. That overstates BUI's cost, because an XLU holder pays tax on
the gains too, only later, when they sell. So here I hold each one for 5 and 10 years, tax every distribution in the
year it's paid at BUI's mix, reinvest what's left (which raises the cost basis), sell at the end and pay long-term
gains tax on whatever gain is left. The difference in after-tax annual return is what the vehicle really costs.

Same book for both: 2.76% income plus 7% growth before fees, rates flat (the target's rates-flat case). BUI nets
1.06% of fees and pays 7.05% of price a year; XLU nets 0.08% and pays 2.77%, all qualified. BUI's price stays at NAV.

Two views:
  tax only: both earn BUI's 8.70% before tax, so the gap is tax alone.
  all in:   each earns its own after-fee return, so the gap is fees plus tax.

Then the discount you'd need to buy BUI at to end level with XLU after tax, assuming you sell at NAV.
Federal rates for 2026 (IRS Rev. Proc. 2025-32, NIIT page). State tax ignored. Not tax advice.
"""
import os
import pandas as pd
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

q = pd.read_csv(os.path.join(DATA, "qualified_dividend_designations_2025.csv")).set_index("fund")
tc = pd.read_csv(os.path.join(DATA, "blackrock_tax_character_2023_2025.csv"))
b25 = tc[(tc.ticker == "BUI") & (tc.year == 2025)].iloc[0]
qshare = q.loc["BUI", "qualified_dividend_income"] / q.loc["BUI", "ordinary_dividends"]
pref25 = (q.loc["BUI", "qualified_dividend_income"] + b25.lt_gains) / (b25.ordinary_income + b25.lt_gains + b25.return_of_capital)
s19 = pd.read_csv(os.path.join(DATA, "section19_notices_2026.csv")).iloc[-1]
t = s19.ytd_distributions
pref26 = s19.ytd_net_income / t * qshare + s19.ytd_lt_gains / t

GROSS = 2.76 + 7.0
FEE = {"BUI": 1.06, "XLU": 0.08}
YLD = {"BUI": 0.154 * 12 / 26.21 * 100, "XLU": 2.77}
BRACKETS = {"top (37% / 20% + 3.8% NIIT)": (40.8, 23.8), "24% (24% / 15%)": (24.0, 15.0)}


def wealth(total_ret, yld, dist_rate, ltcg, years, start_nav_per_dollar=1.0):
    """$1 invested. Price grows at total_ret - yld; distributions taxed at dist_rate and reinvested."""
    g = (1 + total_ret / 100) / (1 + yld / 100) - 1   # so price growth plus the payout compounds to total_ret
    units, basis = start_nav_per_dollar, 1.0           # $1 buys 1/(1 - discount) units of NAV
    nav = 1.0
    for _ in range(years):
        nav *= 1 + g
        dist = units * nav * yld / 100
        net = dist * (1 - dist_rate / 100)
        units += net / nav      # reinvested at NAV (price at NAV from year 1)
        basis += net
    value = units * nav
    return value - max(value - basis, 0) * ltcg / 100


def ann(w, years):
    return (w ** (1 / years) - 1) * 100


rows = []
for bname, (ordr, ltcg) in BRACKETS.items():
    for mixlab, ps in [("2026 mix", pref26), ("2025 mix", pref25)]:
        rate = ps * ltcg + (1 - ps) * ordr
        for H in (5, 10):
            xlu_tax_only = ann(wealth(GROSS - FEE["BUI"], YLD["XLU"], ltcg, ltcg, H), H)
            bui = ann(wealth(GROSS - FEE["BUI"], YLD["BUI"], rate, ltcg, H), H)
            xlu = ann(wealth(GROSS - FEE["XLU"], YLD["XLU"], ltcg, ltcg, H), H)
            target = wealth(GROSS - FEE["XLU"], YLD["XLU"], ltcg, ltcg, H)
            f = lambda d: wealth(GROSS - FEE["BUI"], YLD["BUI"], rate, ltcg, H, 1 / (1 - d)) - target
            d_star = brentq(f, -0.5, 0.9) * 100
            rows.append({"bracket": bname, "bui_mix": mixlab, "years": H,
                         "bui_after_tax": round(bui, 2), "xlu_after_tax": round(xlu, 2),
                         "tax_only_cost_pts": round(xlu_tax_only - bui, 2), "fees_plus_tax_pts": round(xlu - bui, 2),
                         "fee_gap_pts": round(FEE["BUI"] - FEE["XLU"], 2), "breakeven_discount_pct": round(d_star, 1)})
# tax-deferred account: fees only
for H in (5, 10):
    target = wealth(GROSS - FEE["XLU"], YLD["XLU"], 0, 0, H)
    f = lambda d: wealth(GROSS - FEE["BUI"], YLD["BUI"], 0, 0, H, 1 / (1 - d)) - target
    rows.append({"bracket": "tax-deferred (IRA)", "bui_mix": "n/a", "years": H,
                 "bui_after_tax": round(ann(wealth(GROSS - FEE["BUI"], YLD["BUI"], 0, 0, H), H), 2),
                 "xlu_after_tax": round(ann(target, H), 2), "tax_only_cost_pts": 0.0,
                 "fees_plus_tax_pts": round(ann(target, H) - ann(wealth(GROSS - FEE["BUI"], YLD["BUI"], 0, 0, H), H), 2),
                 "fee_gap_pts": round(FEE["BUI"] - FEE["XLU"], 2), "breakeven_discount_pct": round(brentq(f, -0.5, 0.9) * 100, 1)})
r = pd.DataFrame(rows)
p("BUI preferential-rate share: 2026 mix %.0f%%, 2025 mix %.0f%%" % (pref26 * 100, pref25 * 100))
p(r.to_string(index=False))
p("\nreading: tax_only_cost_pts is the after-tax return BUI gives up to XLU on the same pre-tax return. It's the value"
  " of deferral, and it's smaller than the annual tax-paid gap in after_tax_yield.txt (1.55 points top bracket, 2026 mix)"
  " because XLU's gains are taxed at the end. breakeven_discount_pct is the discount to NAV at purchase that leaves"
  " BUI level with XLU after tax at the end of the hold, selling BUI at NAV.")
r.to_csv(os.path.join(RES, "after_tax_wealth.csv"), index=False)
open(os.path.join(RES, "after_tax_wealth.txt"), "w").write("\n".join(out) + "\n")
