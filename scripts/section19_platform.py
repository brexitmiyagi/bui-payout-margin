"""Where BUI sits on BlackRock's own Section 19 numbers, how UTF compares, and how often the final tax
character of BlackRock equity trusts ended up including return of capital.

Inputs: BlackRock's 30 October 2026 Section 19(a) notice (all equity trusts), Cohen & Steers' 27 October 2026
UTF notice, and the "tax character of distributions paid" tables in BlackRock's 2024 and 2025 annual reports.

Note: BlackRock only keeps the current year's notices online, so I cannot line up the December estimates of
2023-2025 against the final 1099 character. What I can score is the outcome.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

s = pd.read_csv(os.path.join(DATA, "blackrock_section19_2026_10_30.csv"))
s["gap"] = s.five_yr_avg_nav_tr_pct - s.dist_rate_nav_pct
term = {"BCAT", "ECAT", "BMEZ", "BSTZ", "BTX"}
s["type"] = ["term trust" if t in term else "perpetual" for t in s.ticker]
p("BlackRock equity trusts, Section 19 gap (5-yr NAV TR minus distribution rate on NAV), 30 Sep 2026:")
p(s.sort_values("gap")[["ticker", "type", "five_yr_avg_nav_tr_pct", "dist_rate_nav_pct", "gap", "ytd_roc_share_pct"]]
  .to_string(index=False))
perp = s[s.type == "perpetual"].sort_values("gap")
rank = list(perp.ticker).index("BUI") + 1
p("BUI's gap %.2f ranks %d of %d perpetual BlackRock equity trusts (1 = thinnest)" %
  (s.set_index("ticker").gap["BUI"], rank, len(perp)))
p("UTF on the same measure (Cohen & Steers notice, 30 Sep 2026): 7.25 - 7.82 = %.2f" % (7.25 - 7.82))
p("UTF year to date: NAV total return 4.44% vs distributions 6.40% of NAV; BUI: 5.83% vs 5.16%")

t = pd.read_csv(os.path.join(DATA, "blackrock_tax_character_2023_2025.csv"))
t["total"] = t.ordinary_income + t.lt_gains + t.return_of_capital
t["roc_share"] = t.return_of_capital / t.total * 100
p("\nfinal tax character, share paid as return of capital (%):")
pv = t.pivot(index="ticker", columns="year", values="roc_share").round(0)
p(pv.to_string())
for y in [2023, 2024, 2025]:
    g = t[t.year == y]
    p("  %d: %d of %d trusts paid some return of capital" % (y, (g.return_of_capital > 0).sum(), len(g)))
b = t[t.ticker == "BUI"].set_index("year")
p("BUI: return of capital %.0f%% of 2023 distributions, %.0f%% of 2024, %.0f%% of 2025" %
  tuple(b.roc_share.loc[y] for y in [2023, 2024, 2025]))
p("BUI 2026 notices so far: 0% return of capital year to date in every notice from February to October,")
p("but the monthly split labelled part of the February and August payments as return of capital")
open(os.path.join(RES, "section19_platform.txt"), "w").write("\n".join(out) + "\n")
