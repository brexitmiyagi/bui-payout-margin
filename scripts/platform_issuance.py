"""BlackRock's shelf sales across its equity CEFs, lined up against how often each fund traded at a premium.

Shelf shares by fund and year come from the notes to BlackRock's 2024 and 2025 annual reports and the 2026
semi-annual report. Premiums are CEF Connect's weekly history (5-year window, pulled 16 Nov 2026).
The question: does BlackRock sell when premiums show up, and does selling stop them showing up?
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

iss = pd.read_csv(os.path.join(DATA, "blackrock_shelf_issuance_2023_2026.csv"))
prem = pd.read_csv(os.path.join(DATA, "blackrock_weekly_premium_by_year.csv"))
prem["period"] = prem.year.astype(str)
iss_y = iss[iss.period.str.len() == 4].copy()
m = iss_y.merge(prem, on=["ticker", "period"], how="left")
p(m[["ticker", "period", "shelf_shares_issued", "pct_weeks_at_or_above_1", "mean_premium", "max_premium"]]
  .sort_values(["period", "ticker"]).to_string(index=False))
sold = m[m.shelf_shares_issued > 0]
none = m[m.shelf_shares_issued == 0]
p("\nfund-years with sales: %d, median share of weeks at +1%% or more: %.0f%%, median max premium %.2f%%" %
  (len(sold), sold.pct_weeks_at_or_above_1.median(), sold.max_premium.median()))
p("fund-years with no sales: %d, median share of weeks at +1%% or more: %.0f%%" %
  (len(none), none.pct_weeks_at_or_above_1.median()))
big = sold[sold.shelf_shares_issued > 1_000_000]
p("the two big selling years (over 1 million shares): " +
  ", ".join("%s %s: %s shares, premium at +1%%+ in %d%% of weeks, peak %+.2f%%" %
            (r.ticker, r.period, f"{r.shelf_shares_issued:,}", r.pct_weeks_at_or_above_1, r.max_premium)
            for r in big.itertuples()))
p("reading: BlackRock sells when a premium appears and sells most when it lasts. Selling has not stopped premiums"
  " of 5% to 8% appearing in those same years. BUI also sold nothing in the first half of 2026, around its rights"
  " offering, when its weekly premium reached 9.9%.")
p("commission retained by BlackRock Investments in 2025 on BUI's sales: $70,353 (2025 annual report)")
m.to_csv(os.path.join(RES, "platform_issuance.csv"), index=False)
open(os.path.join(RES, "platform_issuance.txt"), "w").write("\n".join(out) + "\n")
