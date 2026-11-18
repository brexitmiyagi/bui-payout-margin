"""Do BlackRock's at-the-market share sales line up with premium days?

The shelf can only sell at or above NAV plus the 1% commission, so sales should happen only on days with a premium
of about +1% or more. Two ways to look:
  - between the dated share counts I have (prospectus, semi-annual report, BlackRock's product page), how many
    eligible days were there, and how many shares were sold per eligible day;
  - the daily log of BlackRock's shares-outstanding figure, which I started on November 16, 2026. With a few months
    of rows it can say on which days shares were added. It doesn't have enough rows yet, and I say so.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

b = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
b["prem"] = (b.bui_close / b.bui_nav - 1) * 100
s = pd.read_csv(os.path.join(DATA, "bui_shares_outstanding_points.csv"), parse_dates=["date"]).set_index("date").shares_outstanding
s = s[~s.index.duplicated(keep="last")].sort_index()
p("dated share counts: " + ", ".join("%s %s" % (d.date(), f"{v:,}") for d, v in s.items()))
for (d0, v0), (d1, v1) in zip(s.iloc[:-1].items(), s.iloc[1:].items()):
    w = b.prem.loc[d0:d1].iloc[1:]
    elig = (w >= 1.0).sum()
    p("%s to %s: %+s shares; %d trading days, %d with a premium of +1%% or more (%d at +2%% or more)%s" %
      (d0.date(), d1.date(), f"{v1 - v0:,}", len(w), elig, (w >= 2).sum(),
       "; %s shares per eligible day" % f"{(v1 - v0) / elig:,.0f}" if elig and v1 > v0 else ""))
w = b.prem.loc["2026-07-01":"2026-11-13"]
p("\nJuly 1 to November 13: premium above +1%% on %d days, the last on %s; it was below +1%% on every day after that"
  % ((w >= 1).sum(), w[w >= 1].index.max().date() if (w >= 1).any() else "none"))
p("what the daily log needs: rows on enough days with and without a +1% premium to see whether the count only moves"
  " on premium days. At the current premium (+0.46% on November 17) the shelf can't sell, so the first test is whether"
  " the count stays flat until the premium clears +1%.")
open(os.path.join(RES, "issuance_vs_premium.txt"), "w").write("\n".join(out) + "\n")
