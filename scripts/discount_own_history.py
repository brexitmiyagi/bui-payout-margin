"""Is BUI rich against its own history, not just against other funds?

The cross-section in discount_screen.py says BUI sits about 10 points above where a typical equity CEF with its
payout, size and costs would trade. That can't separate "BUI is rich" from "BUI always trades like this". So here
each fund is compared with itself: month-end discount since 2017 regressed on its own distribution rate on NAV,
the 10-year yield and its trailing 12-month NAV total return. The residual today says whether the discount is
out of line with the fund's own history once those move.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

bui = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
f = pd.read_csv(os.path.join(DATA, "factors_and_peer_navs_daily.csv"), parse_dates=["date"]).set_index("date")
y = pd.read_csv(os.path.join(DATA, "dgs10.csv"))
y.columns = ["date", "y10"]
y["date"] = pd.to_datetime(y.date)
y = y.set_index("date").y10.replace(".", np.nan).astype(float)
bd = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])
pdist = pd.read_csv(os.path.join(DATA, "peer_distributions.csv"), parse_dates=["ex_date"])

funds = {
    "BUI": (bui.bui_close, bui.bui_nav, bd[bd.amount < 0.5]),          # regular payouts only, specials excluded
    "UTF": (f.utf_price, f.utf_nav, pdist[(pdist.ticker == "UTF")]),
}
rows = []
for t, (px, nav, dist) in funds.items():
    dist = dist.groupby("ex_date").amount.sum()
    df = pd.DataFrame({"px": px, "nav": nav}).dropna()
    df["disc"] = (df.px / df.nav - 1) * 100
    # trailing 12-month regular payout as % of NAV
    pay = pd.Series(0.0, index=df.index)
    for dt, a in dist.items():
        i = df.index.searchsorted(dt)
        if i < len(df):
            pay.iloc[i] += a
    df["pay12"] = pay.rolling(252, min_periods=240).sum()
    df["dist_rate"] = df.pay12 / df.nav * 100
    tr = (df.nav + pay) / df.nav.shift(1)
    df["navtr12"] = (tr.fillna(1).cumprod().pct_change(252)) * 100
    df["y10"] = y.reindex(df.index).ffill()
    m = df.resample("ME").last().dropna()
    X = sm.add_constant(m[["dist_rate", "y10", "navtr12"]])
    r = sm.OLS(m.disc, X).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    resid = r.resid
    p("\n%s, month-end %s to %s, n=%d, R2 %.2f" % (t, m.index[0].date(), m.index[-1].date(), int(r.nobs), r.rsquared))
    for k in r.params.index:
        p("  %-10s %+.3f (t %.1f)" % (k, r.params[k], r.tvalues[k]))
    z = resid.iloc[-1] / resid.std()
    p("  latest: discount %.2f, fitted %.2f, residual %+.2f (%.1f standard deviations), residual percentile %.0f" %
      (m.disc.iloc[-1], r.fittedvalues.iloc[-1], resid.iloc[-1], z, (resid <= resid.iloc[-1]).mean() * 100))
    rows.append({"fund": t, "discount": round(m.disc.iloc[-1], 2), "fitted_own_history": round(r.fittedvalues.iloc[-1], 2),
                 "residual": round(resid.iloc[-1], 2), "residual_sd": round(resid.std(), 2), "r2": round(r.rsquared, 2)})
pd.DataFrame(rows).to_csv(os.path.join(RES, "discount_own_history.csv"), index=False)

# The levels regression above puts a trending series (the 10-year) on the right and a mean-reverting one (the
# discount) on the left, which overstates the t-stat. The honest test is changes on changes.
p("\nIS THE 10-YEAR LINK REAL? changes on changes, BUI")
d = pd.DataFrame({"disc": (bui.bui_close / bui.bui_nav - 1) * 100, "y10": y.reindex(bui.index).ffill()}).dropna()
mm = d.resample("ME").last()
p("  unit-root test p-values (monthly levels): discount %.3f, 10-year %.3f" %
  (adfuller(mm.disc)[1], adfuller(mm.y10)[1]))
for freq, lag, lab in [("ME", 6, "monthly"), ("W-FRI", 4, "weekly")]:
    ch = d.resample(freq).last().diff().dropna()
    for start in ["2017", "2023"]:
        c = ch.loc[start:]
        r = sm.OLS(c.disc, sm.add_constant(c.y10)).fit(cov_type="HAC", cov_kwds={"maxlags": lag})
        p("  %-7s since %s: %.2f pts of discount per 1 pt of 10-year (t %.1f), R2 %.3f, n %d" %
          (lab, start, r.params["y10"], r.tvalues["y10"], r.rsquared, int(r.nobs)))
p("  reading: same sign as the levels regression, but weak, and it explains about 1% of moves")
open(os.path.join(RES, "discount_own_history.txt"), "w").write("\n".join(out) + "\n")
