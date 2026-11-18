"""Is a closed-end fund worth it over the matching ETF? A screen of 108 equity CEFs, BUI as the worked example.

Two numbers per fund, both for a tax-deferred account (in a taxable account the gap is bigger for funds that pay out
their gains; see after_tax_wealth.py for BUI):

  breakeven_discount_5y   the discount at purchase that leaves the CEF level with the ETF after five years of the fee
                          gap, if the discount has closed by then. Gross return 8% a year for both; the answer barely
                          moves with it.
  edge_if_discount_stays  what you get each year if the discount never closes: buying a dollar of distributions for
                          less than a dollar raises your yield by distribution rate x d / (1 - d). Minus the fee gap.

Fund data: CEF Connect, November 13, 2026 (discount, distribution rate on NAV, expense ratio, which for leveraged funds
includes borrowing costs). ETF for each category and its fee: data/category_etf_fees_2026_11.csv. Sector funds all get
a Select Sector SPDR at 0.08%, which is right for BUI and rough for the rest. Leverage, tax and the quality of the
manager are all left out. It's a first cut, not a recommendation.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

u = pd.read_csv(os.path.join(DATA, "equity_cef_universe_2026_11_13.csv"))
f = pd.read_csv(os.path.join(DATA, "category_etf_fees_2026_11.csv")).set_index("category_prefix")
u = u.join(f, on="category")
assert u.etf_expense_pct.notna().all()
R, YRS = 0.08, 5
u["fee_gap"] = u.expense_ratio_pct - u.etf_expense_pct
u["breakeven_discount_5y"] = (1 - ((1 + R - u.expense_ratio_pct / 100) / (1 + R - u.etf_expense_pct / 100)) ** YRS) * 100
u["discount"] = -u.discount_pct
d = u.discount.clip(lower=0) / 100
u["edge_if_discount_stays"] = u.dist_rate_nav_pct * d / (1 - d) - u.fee_gap
u["discount_minus_breakeven"] = u.discount - u.breakeven_discount_5y
cols = ["ticker", "category_meaning", "matching_etf", "expense_ratio_pct", "etf_expense_pct", "discount_pct",
        "dist_rate_nav_pct", "breakeven_discount_5y", "discount_minus_breakeven", "edge_if_discount_stays", "leverage_pct"]
s = u[cols].sort_values("edge_if_discount_stays", ascending=False)
p("108 equity CEFs, November 13, 2026, tax-deferred account")
p("  pass on both tests (discount above its 5-year breakeven, and a positive edge if the discount never closes): %d"
  % ((u.discount_minus_breakeven > 0) & (u.edge_if_discount_stays > 0)).sum())
p("  fail both: %d" % ((u.discount_minus_breakeven <= 0) & (u.edge_if_discount_stays <= 0)).sum())
p("  median breakeven discount %.1f%%, median actual discount %.1f%%" % (u.breakeven_discount_5y.median(), u.discount.median()))
p("\ntop 15 by edge if the discount never closes:")
p(s.head(15).round(2).to_string(index=False))
p("\nBUI and its peers:")
p(s[s.ticker.isin(["BUI", "UTF", "DNP", "GLU"])].round(2).to_string(index=False))
p("\nbottom 10:")
p(s.tail(10).round(2).to_string(index=False))
s.round(3).to_csv(os.path.join(RES, "cef_vs_etf_screen.csv"), index=False)
open(os.path.join(RES, "cef_vs_etf_screen.txt"), "w").write("\n".join(out) + "\n")
