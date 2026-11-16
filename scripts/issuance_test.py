"""Does BlackRock actually sell BUI shares into the premium, and does that cap it?

Issuance comes from the annual and semi-annual reports (shelf and dividend-reinvestment shares by period) and,
after June 30 2026, from shares outstanding on BlackRock's product page. There is no daily issuance series, so
the test is by regime: premium behaviour in years when the shelf sold a lot, sold nothing, and since July.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

iss = pd.read_csv(os.path.join(DATA, "bui_share_issuance.csv"))
so = pd.read_csv(os.path.join(DATA, "bui_shares_outstanding_points.csv"), parse_dates=["date"]).set_index("date")
b = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
o = pd.read_csv(os.path.join(DATA, "bui_ohlcv_daily.csv"), parse_dates=["date"]).set_index("date")
prem = (b.bui_close / b.bui_nav - 1) * 100

new = so.shares_outstanding.loc["2026-11-13"] - so.shares_outstanding.loc["2026-06-30"]
p("shares outstanding 30 Jun 2026 -> 13 Nov 2026: +%s (%.2f%% of the June count)" %
  (f"{new:,}", new / so.shares_outstanding.loc["2026-06-30"] * 100))
p("dividend reinvestment added 28,851 shares in the whole first half, so nearly all of the increase is shelf sales")
avg_px = b.bui_close.loc["2026-07-01":].mean()
p("at the average close since July ($%.2f) that is about $%.1fm raised and about $%.0fk of 1%% commission" %
  (avg_px, new * avg_px / 1e6, new * avg_px * 0.01 / 1e3))
months = (pd.Timestamp("2026-11-13") - pd.Timestamp("2026-06-30")).days / 30.4
p("pace: about %s shares a month since July, against %s a month in 2025" %
  (f"{new / months:,.0f}", f"{1373141 / 12:,.0f}"))

rows = []
for lab, a, z, sh in [("2024", "2024-01-01", "2024-12-31", 55243), ("2025", "2025-01-01", "2025-12-31", 1373141),
                      ("H1 2026", "2026-01-01", "2026-06-30", 0), ("Jul-Nov 2026", "2026-07-01", "2026-11-13", new)]:
    x = prem.loc[a:z]
    ch = [x.iloc[i + 5] - x.iloc[i] for i in range(len(x) - 5) if x.iloc[i] >= 1]
    hi = ((o.high.loc[a:z] / b.bui_nav.loc[a:z] - 1) * 100 >= 1)
    vol_elig = o.volume.loc[a:z][hi].sum()
    rows.append({"period": lab, "shelf_shares": sh, "share_of_eligible_day_volume_pct": round(sh / vol_elig * 100, 1),
                 "mean_premium": round(x.mean(), 2), "max_premium": round(x.max(), 2),
                 "days_at_or_above_3pct_pct": round((x >= 3).mean() * 100), "avg_5d_change_after_1pct_close": round(np.mean(ch), 2) if ch else None,
                 "n_after_1pct": len(ch)})
t = pd.DataFrame(rows)
p("\n" + t.to_string(index=False))
p("\nreading: 2025 sold about as many shares a month as the period since July, and the premium still averaged"
  " about 2% with a quarter of days above 3%. Selling trims the premium, it does not cap it. The premium fell"
  " after July because demand fell, with issuance running alongside.")
t.to_csv(os.path.join(RES, "issuance_test.csv"), index=False)
open(os.path.join(RES, "issuance_test.txt"), "w").write("\n".join(out) + "\n")
