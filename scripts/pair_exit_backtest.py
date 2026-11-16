"""The UTF/BUI pair with the exit rule the post states: enter when UTF's discount minus BUI's is 5 or more points
below its trailing one-year median; exit when the spread is back at or above that day's median, or after 252
trading days, whichever comes first. Return = UTF total return minus BUI total return over the hold (distributions
reinvested), before borrow costs. One position at a time; after an exit, a new entry needs the signal again.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

bui = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
f = pd.read_csv(os.path.join(DATA, "factors_and_peer_navs_daily.csv"), parse_dates=["date"]).set_index("date")
bd = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])
pdist = pd.read_csv(os.path.join(DATA, "peer_distributions.csv"), parse_dates=["ex_date"])


def tr(price, dists):
    div = pd.Series(0.0, index=price.index)
    for dt, a in dists.groupby("ex_date").amount.sum().items():
        i = price.index.searchsorted(dt)
        if 0 < i < len(price):
            div.iloc[i] += a
    return ((price + div) / price.shift(1)).fillna(1).cumprod()


d = pd.DataFrame({"bp": bui.bui_close, "bn": bui.bui_nav, "up": f.utf_price, "un": f.utf_nav}).dropna()
d["btr"] = tr(d.bp, bd)
d["utr"] = tr(d.up, pdist[pdist.ticker == "UTF"])
d["spread"] = (d.up / d.un - d.bp / d.bn) * 100
d["norm"] = d.spread.rolling(252, min_periods=200).median()
d = d.dropna()
idx = d.index
trades = []
i = 0
while i < len(d):
    if d.spread.iloc[i] - d.norm.iloc[i] <= -5:
        j = i + 1
        while j < len(d) and j - i < 252 and d.spread.iloc[j] < d.norm.iloc[j]:
            j += 1
        if j >= len(d):
            trades.append({"entry": idx[i].date(), "exit": None, "days": len(d) - 1 - i, "reason": "open",
                           "utf_minus_bui": round((d.utr.iloc[-1] / d.utr.iloc[i] - d.btr.iloc[-1] / d.btr.iloc[i]) * 100, 2)})
            break
        reason = "back to median" if d.spread.iloc[j] >= d.norm.iloc[j] else "12 months"
        trades.append({"entry": idx[i].date(), "exit": idx[j].date(), "days": j - i, "reason": reason,
                       "utf_minus_bui": round((d.utr.iloc[j] / d.utr.iloc[i] - d.btr.iloc[j] / d.btr.iloc[i]) * 100, 2)})
        i = j + 1
    else:
        i += 1
t = pd.DataFrame(trades)
p(t.to_string(index=False))
c = t[t.reason != "open"]
for lab, s in [("all closed trades", c), ("entries 2016-2020", c[pd.to_datetime(c.entry) < "2021-01-01"]),
               ("entries 2021 on", c[pd.to_datetime(c.entry) >= "2021-01-01"])]:
    if len(s):
        p("%s: %d trades, %d won, mean %+.2f pts, median %+.2f, average hold %.0f trading days (%.1f months)" %
          (lab, len(s), (s.utf_minus_bui > 0).sum(), s.utf_minus_bui.mean(), s.utf_minus_bui.median(),
           s.days.mean(), s.days.mean() / 21))
yrs = c.days.sum() / 252
p("borrow drag at today's 2.42%% fee, net of the 0.66-point yield pickup, over the average hold: about %.2f points per trade"
  % ((2.42 - 0.66) * c.days.mean() / 252))
t.to_csv(os.path.join(RES, "pair_exit_backtest.csv"), index=False)
open(os.path.join(RES, "pair_exit_backtest.txt"), "w").write("\n".join(out) + "\n")
