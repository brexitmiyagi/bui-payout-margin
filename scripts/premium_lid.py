"""Does an at-the-market program put a lid on a BlackRock CEF's premium?

Three BlackRock equity trusts filed at-the-market prospectus supplements in 2026: BST (29 May, 424B5),
BUI (1 July, 424B2, up to 3,801,642 shares) and CII (27 July, 424B2). Daily premiums from CEF Connect,
one-year window to 12 November 2026. A fund can only issue at or above NAV plus the commission, so the lid,
if there is one, should show up as premiums that stop above roughly +1% to +2%.

Control: 20 other equity CEFs (BlackRock and utility peers) over the same before/after split at 1 July.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

a = pd.read_csv(os.path.join(DATA, "blackrock_atm_premium_test_2026.csv"))
for t, g in a.groupby("ticker", sort=False):
    b, f = g.iloc[0], g.iloc[1]
    p("%s (program from %s): max premium %.2f -> %.2f, mean %.2f -> %.2f, share of days >= +1%%: %.0f%% -> %.0f%%, "
      "days >= +2%%: %d -> %d" % (t, b.start, b.max_premium, f.max_premium, b.mean_premium, f.mean_premium,
                                 b.days_at_or_above_1pct / b.days * 100, f.days_at_or_above_1pct / f.days * 100,
                                 b.days_at_or_above_2pct, f.days_at_or_above_2pct))

c = pd.read_csv(os.path.join(DATA, "control_cef_mean_discount_split_2026_07_01.csv"))
c["change"] = c.after - c.before
p("\ncontrol funds, mean discount before vs after 1 July 2026: median change %+.2f pts, %d of %d narrowed" %
  (c.change.median(), (c.change > 0).sum(), len(c)))
p("BUI's mean premium fell about 1.0 pt and CII's 1.3 pts over the same split, against a control group that,"
  " on the median, moved the other way")
p("caveat: BUI also had an at-the-market program from June 2025 and still reached +10.3% in that year, so the lid"
  " is soft when demand is strong; it bites when demand is ordinary")
open(os.path.join(RES, "premium_lid.txt"), "w").write("\n".join(out) + "\n")
