"""Data behind the three line charts in the post. Writes CSVs to results/ that go straight into Datawrapper.

premium_history_monthly.csv   BUI's month-end premium or discount to NAV since November 2016, with the +1% trim level
                              and the median since 2023 (Nasdaq closes, BlackRock NAVs)
rights_offering_daily.csv     BUI's and UTF's daily premium, January 20 to June 30, 2026, around the rights offering
nav_gap_cumulative_weekly.csv the fixed-weight NAV residual from nav_gap.py, summed, at week-ends in 2026
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")

b = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
prem = (b.bui_close / b.bui_nav - 1) * 100
med23 = prem.loc["2023":].median()
m = prem.resample("ME").last().dropna()
pd.DataFrame({"BUI premium or discount (%)": m.round(2), "Trim above +1%": 1.0, "Median since 2023": round(med23, 2)}) \
    .rename_axis("Month").to_csv(os.path.join(RES, "premium_history_monthly.csv"), date_format="%Y-%m")

f = pd.read_csv(os.path.join(DATA, "factors_and_peer_navs_daily.csv"), parse_dates=["date"]).set_index("date")
utf = (f.utf_price / f.utf_nav - 1) * 100
w = pd.DataFrame({"BUI premium (%)": prem, "UTF premium (%)": utf}).loc["2026-01-20":"2026-06-30"].dropna().round(2)
w.rename_axis("Date").to_csv(os.path.join(RES, "rights_offering_daily.csv"), date_format="%Y-%m-%d")

g = pd.read_csv(os.path.join(RES, "nav_gap_daily.csv"), parse_dates=[0], index_col=0)
c = g.fixed_resid_cum_pts.resample("W-FRI").last().round(2)
c.rename("Cumulative NAV return the priced holdings don't explain (points)").rename_axis("Week") \
    .to_csv(os.path.join(RES, "nav_gap_cumulative_weekly.csv"), date_format="%Y-%m-%d")
print("median since 2023 %.2f; rows %d / %d / %d" % (med23, len(m), len(w), len(c)))
