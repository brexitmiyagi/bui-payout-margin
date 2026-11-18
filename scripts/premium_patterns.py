"""Does BUI's premium to NAV move in ways you could trade?

Three checks on BUI's daily close and NAV since November 2016 (Nasdaq; NAV is BlackRock's, posted as XBUIX):
  1. Snap-back. Regress the next day's (and next five days') change in the premium on today's distance from its
     20-day average. A strongly negative slope means the premium snaps back. Then a plain rule: buy when the premium
     is 1.5 standard deviations under its 60-day average, sell after five days, against holding NAV. It has to clear
     BUI's estimated round-trip spread of about 0.8% (technicals_liquidity.py, Abdi-Ranaldo).
  2. Ex-dates. Price and NAV both drop by the payout on the ex-date. Does the premium move on those days, and around
     the December 2025 special?
  3. Price against same-day NAV. If the price only catches up with the NAV a day later, yesterday's NAV return
     predicts today's price return. The NAV is struck at the same 4 p.m. as the closing price, with foreign stocks
     fair-valued, so in an efficient market it shouldn't.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

b = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
dist = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"]).groupby("ex_date").amount.sum()
b["prem"] = (b.bui_close / b.bui_nav - 1) * 100
b["dv"] = dist.reindex(b.index).fillna(0)
b["rp"] = (b.bui_close + b.dv) / b.bui_close.shift(1) - 1
b["rn"] = (b.bui_nav + b.dv) / b.bui_nav.shift(1) - 1
b["dev20"] = b.prem - b.prem.rolling(20).mean()
b["dprem1"] = b.prem.shift(-1) - b.prem
b["dprem5"] = b.prem.shift(-5) - b.prem
x = b.dropna(subset=["dev20", "dprem1", "dprem5"])

p("1. SNAP-BACK, %s to %s" % (x.index[0].date(), x.index[-1].date()))
for k in ["dprem1", "dprem5"]:
    m = sm.OLS(x[k], sm.add_constant(x.dev20)).fit(cov_type="HAC", cov_kwds={"maxlags": 5 if k == "dprem5" else 1})
    p("   next %s day(s) change in premium on distance from 20-day average: slope %.2f (t %.1f), R2 %.2f" %
      (k[-1], m.params.dev20, m.tvalues.dev20, m.rsquared))
ar = sm.OLS(b.prem.diff().dropna().iloc[1:], sm.add_constant(b.prem.shift(1).loc[b.prem.diff().dropna().index].iloc[1:]
            - b.prem.mean())).fit()
hl = np.log(2) / -np.log(1 + ar.params.iloc[1]) if ar.params.iloc[1] < 0 else np.inf
p("   the premium's own pull toward its long-run average: half-life about %.0f trading days" % hl)
z = (b.prem - b.prem.rolling(60).mean()) / b.prem.rolling(60).std()
fwd = (b.bui_close.shift(-5) + b.dv[::-1].rolling(5).sum()[::-1].shift(-1).fillna(0)) / b.bui_close - 1
fwdn = (b.bui_nav.shift(-5) + b.dv[::-1].rolling(5).sum()[::-1].shift(-1).fillna(0)) / b.bui_nav - 1
sig = z < -1.5
ev, last = [], None
for d in b.index[sig.fillna(False).values]:
    if last is None or (b.index.get_loc(d) - b.index.get_loc(last)) >= 5:
        if pd.notna(fwd.get(d)) and pd.notna(fwdn.get(d)):
            ev.append((fwd[d] - fwdn[d]) * 100)
            last = d
ev = np.array(ev)
p("   rule: buy when the premium is 1.5 sd under its 60-day average, hold five days: %d trades, average gain over NAV"
  " %+.2f points, %d%% positive, before a round-trip spread of about 0.8" % (len(ev), ev.mean(), (ev > 0).mean() * 100))
p("   after the spread: %+.2f points a trade" % (ev.mean() - 0.8))

p("\n2. EX-DATES")
exd = b.index[b.dv > 0]
reg = exd[b.loc[exd, "dv"] < 0.5]
dpe = (b.prem - b.prem.shift(1))
p("   change in premium on regular ex-dates: average %+.2f points, median %+.2f (%d dates); all other days %+.3f" %
  (dpe.loc[reg].mean(), dpe.loc[reg].median(), len(reg), dpe.drop(reg).mean()))
spec = exd[b.loc[exd, "dv"] >= 0.5]
for d in spec:
    i = b.index.get_loc(d)
    w = b.prem.iloc[i - 5:i + 11]
    p("   special ex %s ($%.2f): premium 5 days before %+.2f, day before %+.2f, ex-date %+.2f, 10 days after %+.2f" %
      (d.date(), b.dv[d], w.iloc[0], w.iloc[4], w.iloc[5], w.iloc[-1]))

p("\n3. PRICE AGAINST SAME-DAY NAV")
y = pd.DataFrame({"rp": b.rp, "rn": b.rn, "rn_lag": b.rn.shift(1), "rp_lag": b.rp.shift(1)}).dropna()
m = sm.OLS(y.rp, sm.add_constant(y[["rn", "rn_lag"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
p("   price return on today's NAV return %.2f (t %.1f) and yesterday's %.2f (t %.1f)" %
  (m.params.rn, m.tvalues.rn, m.params.rn_lag, m.tvalues.rn_lag))
y2 = y.loc["2025-11-10":]
m2 = sm.OLS(y2.rp, sm.add_constant(y2[["rn", "rn_lag"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
p("   since BUI dropped calls: today %.2f (t %.1f), yesterday %.2f (t %.1f)" %
  (m2.params.rn, m2.tvalues.rn, m2.params.rn_lag, m2.tvalues.rn_lag))
# is the lag worth trading? after days the NAV beat the price by more than a point, what does the price do next day?
y2 = y2.assign(lag_gap=(y2.rn - y2.rp) * 100, next_rp=b.rp.shift(-1).reindex(y2.index) * 100,
               next_rn=b.rn.shift(-1).reindex(y2.index) * 100).dropna()
for th in (1.0, 1.5):
    e = y2[y2.lag_gap > th]
    p("   since dropping calls, days NAV beat price by more than %.1f point: %d; next day price beat NAV by %+.2f points on"
      " average (%d%% of the time), against a round trip of about 0.8" % (th, len(e), (e.next_rp - e.next_rn).mean(),
      ((e.next_rp - e.next_rn) > 0).mean() * 100))
gap = (y.rp - y.rn).abs() * 100
p("   days the price and NAV returns differ by more than 1 point: %.1f%% of days" % ((gap > 1).mean() * 100))
open(os.path.join(RES, "premium_patterns.txt"), "w").write("\n".join(out) + "\n")
