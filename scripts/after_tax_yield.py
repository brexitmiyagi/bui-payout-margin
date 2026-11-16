"""After-tax yield and tax drag for a taxable US holder: BUI against XLU.

BUI's mix: 2025 final (annual report: ordinary dividends, of which qualified, plus long-term gains) and the 2026
estimate to Oct 30 (Section 19: net income, short-term gains, long-term gains). The qualified share of 2026's net
income isn't known until the annual report; I assume 2025's 85%, and show the all-ordinary case too.
XLU's 2025 distributions were 100% qualified dividends (State Street 2025 tax summary).
Federal rates for 2026 (IRS Rev. Proc. 2025-32, NIIT page). State tax ignored. Not tax advice.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

q = pd.read_csv(os.path.join(DATA, "qualified_dividend_designations_2025.csv")).set_index("fund")
tc = pd.read_csv(os.path.join(DATA, "blackrock_tax_character_2023_2025.csv"))
b25 = tc[(tc.ticker == "BUI") & (tc.year == 2025)].iloc[0]
qshare = q.loc["BUI", "qualified_dividend_income"] / q.loc["BUI", "ordinary_dividends"]
tot25 = b25.ordinary_income + b25.lt_gains + b25.return_of_capital
pref25 = (q.loc["BUI", "qualified_dividend_income"] + b25.lt_gains) / tot25
s19 = pd.read_csv(os.path.join(DATA, "section19_notices_2026.csv")).iloc[-1]
t = s19.ytd_distributions
nii, st, lt = s19.ytd_net_income / t, s19.ytd_st_gains / t, s19.ytd_lt_gains / t
pref26 = nii * qshare + lt
pref26_worst = lt
p("BUI 2025 final: %.0f%% of ordinary dividends qualified; %.0f%% of the payout taxed at preferential rates" % (qshare * 100, pref25 * 100))
p("BUI 2026 estimate to Oct 30: net income %.0f%%, short-term gains %.0f%%, long-term gains %.0f%%" % (nii * 100, st * 100, lt * 100))
p("  -> preferential share %.0f%% if 2026 income is %.0f%% qualified like 2025; %.0f%% if none of it is" % (pref26 * 100, qshare * 100, pref26_worst * 100))

yields = {"BUI": 0.154 * 12 / 26.21 * 100, "XLU": 2.77}
brackets = {"top bracket (37% / 20% + 3.8% NIIT)": (40.8, 23.8), "24% bracket (24% / 15%, no NIIT)": (24.0, 15.0)}
rows = []
for bname, (ordr, pref) in brackets.items():
    for lab, ps in [("BUI 2025 mix", pref25), ("BUI 2026 mix", pref26), ("BUI 2026, income all ordinary", pref26_worst)]:
        rate = ps * pref + (1 - ps) * ordr
        rows.append({"bracket": bname, "vehicle": lab, "yield": round(yields["BUI"], 2), "tax_rate": round(rate, 1),
                     "after_tax_yield": round(yields["BUI"] * (1 - rate / 100), 2), "tax_drag_pts": round(yields["BUI"] * rate / 100, 2)})
    rows.append({"bracket": bname, "vehicle": "XLU (100% qualified)", "yield": yields["XLU"], "tax_rate": pref,
                 "after_tax_yield": round(yields["XLU"] * (1 - pref / 100), 2), "tax_drag_pts": round(yields["XLU"] * pref / 100, 2)})
r = pd.DataFrame(rows)
p("\n" + r.to_string(index=False))
top = r[r.bracket.str.startswith("top")].set_index("vehicle")
p("\ntop bracket: BUI's 2026 mix costs %.2f points of price a year in tax against XLU's %.2f, a gap of %.2f points;"
  " the gap was %.2f on BUI's 2025 mix" % (top.loc["BUI 2026 mix", "tax_drag_pts"], top.loc["XLU (100% qualified)", "tax_drag_pts"],
  top.loc["BUI 2026 mix", "tax_drag_pts"] - top.loc["XLU (100% qualified)", "tax_drag_pts"],
  top.loc["BUI 2025 mix", "tax_drag_pts"] - top.loc["XLU (100% qualified)", "tax_drag_pts"]))
p("reading: most of the gap is that BUI pays out about 7% a year, gains included, while XLU pays under 3% and leaves"
  " the rest to compound untaxed until sold. For an IRA or other tax-deferred account none of this applies.")
r.to_csv(os.path.join(RES, "after_tax_yield.csv"), index=False)
open(os.path.join(RES, "after_tax_yield.txt"), "w").write("\n".join(out) + "\n")
