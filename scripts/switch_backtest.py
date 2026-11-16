"""Does buying UTF over BUI when UTF's discount is unusually wide actually pay?

Signal: UTF discount minus BUI discount, compared with its own trailing
one-year median (no look-ahead). When the spread sits 5 points or more
below that median, UTF is cheap relative to BUI by its own standard.
Outcome: UTF price total return minus BUI price total return over the
next 252 trading days, distributions reinvested at the ex-date close.

Also fits the half-life of each fund's discount gap and of the spread,
and checks November-December seasonality.
"""
import os
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
os.makedirs(RES, exist_ok=True)

bui = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
f = pd.read_csv(os.path.join(DATA, "factors_and_peer_navs_daily.csv"), parse_dates=["date"]).set_index("date")
df = pd.DataFrame({"bui_p": bui.bui_close, "bui_nav": bui.bui_nav,
                   "utf_p": f.utf_price, "utf_nav": f.utf_nav}).dropna()

bd = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])
pdists = pd.read_csv(os.path.join(DATA, "peer_distributions.csv"), parse_dates=["ex_date"])
ud = pdists[pdists.ticker == "UTF"]


def total_return_index(price, dists):
    d = dists.groupby("ex_date").amount.sum()
    d = d[(d.index >= price.index[0]) & (d.index <= price.index[-1])]
    div = pd.Series(0.0, index=price.index)
    for dt, amt in d.items():
        pos = price.index.searchsorted(dt)
        if pos < len(price):
            div.iloc[pos] += amt
    r = (price + div) / price.shift(1) - 1
    return (1 + r.fillna(0)).cumprod()


df["bui_tr"] = total_return_index(df.bui_p, bd)
df["utf_tr"] = total_return_index(df.utf_p, ud)
df["bui_disc"] = (df.bui_p / df.bui_nav - 1) * 100
df["utf_disc"] = (df.utf_p / df.utf_nav - 1) * 100
df["spread"] = df.utf_disc - df.bui_disc
df["norm"] = df.spread.rolling(252, min_periods=200).median()
df["dev"] = df.spread - df["norm"]
H = 252
df["fwd"] = (df.utf_tr.shift(-H) / df.utf_tr - df.bui_tr.shift(-H) / df.bui_tr) * 100

out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

# sanity check on the total return index against a known number
p("BUI price TR since 2016-11-14 (x):", round(df.bui_tr.iloc[-1], 3),
  " UTF:", round(df.utf_tr.iloc[-1], 3))

valid = df.dropna(subset=["dev", "fwd"])
sig = valid[valid.dev <= -5]
p("\n1) SWITCH BACKTEST, spread 5+ pts below trailing 1y median")
p("days with a full 12m forward window:", len(valid), " signal days:", len(sig))
p("unconditional UTF-minus-BUI 12m return, mean %.2f median %.2f, hit %.0f%%" %
  (valid.fwd.mean(), valid.fwd.median(), (valid.fwd > 0).mean() * 100))
if len(sig):
    p("signal days: mean %.2f median %.2f, hit %.0f%%" %
      (sig.fwd.mean(), sig.fwd.median(), (sig.fwd > 0).mean() * 100))

# episodes: a new episode starts when the signal turns on after 20+ days off
on = (df.dev <= -5)
episodes = []
last = None
for dt in df.index[on.fillna(False).values]:
    if last is None or (df.index.get_loc(dt) - df.index.get_loc(last)) > 20:
        episodes.append(dt)
    last = dt
p("\nepisodes (first signal day):")
rows = []
for e in episodes:
    r = df.loc[e]
    fwd = r.fwd
    rows.append({"start": e.date(), "spread": round(r.spread, 2), "norm": round(r["norm"], 2),
                 "dev": round(r.dev, 2), "utf_minus_bui_12m": None if pd.isna(fwd) else round(fwd, 2)})
    p(" ", e.date(), "spread %.2f norm %.2f dev %.2f -> 12m UTF-BUI %s" %
      (r.spread, r["norm"], r.dev, "open" if pd.isna(fwd) else "%.2f" % fwd))
ep = pd.DataFrame(rows)
ep.to_csv(os.path.join(RES, "switch_backtest_episodes.csv"), index=False)
closed = ep.dropna(subset=["utf_minus_bui_12m"])
if len(closed):
    p("closed episodes: %d, mean %.2f, median %.2f, wins %d" %
      (len(closed), closed.utf_minus_bui_12m.mean(), closed.utf_minus_bui_12m.median(),
       (closed.utf_minus_bui_12m > 0).sum()))

# block bootstrap of the signal-day mean against the unconditional mean
rng = np.random.default_rng(7)
n_sig = len(sig)
if n_sig:
    vals = valid.fwd.values
    sims = []
    for _ in range(5000):
        starts = rng.integers(0, len(vals) - 60, size=max(1, n_sig // 60 + 1))
        s = np.concatenate([vals[s0:s0 + 60] for s0 in starts])[:n_sig]
        sims.append(s.mean())
    sims = np.array(sims)
    p("bootstrap: share of random same-size 60-day blocks with mean >= signal mean: %.3f" %
      (sims >= sig.fwd.mean()).mean())

p("\nnow (last row %s): BUI disc %.2f, UTF disc %.2f, spread %.2f, 1y median %.2f, dev %.2f" %
  (df.index[-1].date(), df.bui_disc.iloc[-1], df.utf_disc.iloc[-1], df.spread.iloc[-1],
   df["norm"].iloc[-1], df.dev.iloc[-1]))

# 2) half-lives on weekly data: d(t) - d(t-1) = a + b d(t-1)
p("\n2) HALF-LIFE OF DISCOUNT GAPS (weekly AR(1), Friday closes)")
wk = df[["bui_disc", "utf_disc", "spread", "dev"]].resample("W-FRI").last().dropna()


def half_life(x):
    y = x.diff().dropna()
    xl = x.shift(1).loc[y.index]
    X = np.column_stack([np.ones(len(xl)), xl.values])
    b = np.linalg.lstsq(X, y.values, rcond=None)[0]
    resid = y.values - X @ b
    s2 = resid @ resid / (len(y) - 2)
    se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
    hl = -np.log(2) / np.log(1 + b[1]) if b[1] < 0 else np.inf
    return b[1], se, hl, b[0] / -b[1] if b[1] < 0 else np.nan


hl_rows = []
for col, lab in [("bui_disc", "BUI discount"), ("utf_disc", "UTF discount"), ("spread", "UTF minus BUI spread")]:
    for start in ["2016", "2023"]:
        b, se, hl, mean = half_life(wk[col].loc[start:])
        p("  %-22s since %s: b %.4f (se %.4f), half-life %.1f weeks, long-run level %.2f" %
          (lab, start, b, se, hl, mean))
        hl_rows.append({"series": lab, "since": start, "b": round(b, 4), "se": round(se, 4),
                        "half_life_weeks": round(hl, 1), "long_run_level": round(mean, 2)})
pd.DataFrame(hl_rows).to_csv(os.path.join(RES, "discount_half_lives.csv"), index=False)

# 4) seasonality: change in discount from mid-November to year end, then into late January
p("\n4) SEASONALITY: discount change Nov 16 -> Dec 31 and Dec 31 -> Jan 31 (points)")
srows = []
for y in range(2016, 2026):
    try:
        a = df.loc[:f"{y}-11-16"].iloc[-1]
        b = df.loc[:f"{y}-12-31"].iloc[-1]
        c = df.loc[:f"{y+1}-01-31"].iloc[-1]
    except IndexError:
        continue
    srows.append({"year": y,
                  "bui_nov_dec": round(b.bui_disc - a.bui_disc, 2), "bui_jan": round(c.bui_disc - b.bui_disc, 2),
                  "utf_nov_dec": round(b.utf_disc - a.utf_disc, 2), "utf_jan": round(c.utf_disc - b.utf_disc, 2)})
sea = pd.DataFrame(srows)
sea.to_csv(os.path.join(RES, "seasonality_nov_jan.csv"), index=False)
p(sea.to_string(index=False))
for c in ["bui_nov_dec", "bui_jan", "utf_nov_dec", "utf_jan"]:
    p("  %s mean %.2f, median %.2f, widened in %d of %d" %
      (c, sea[c].mean(), sea[c].median(), (sea[c] < 0).sum(), len(sea)))

# 3) BUI premium lid since the July 1 2026 shelf
p("\n3) BUI PREMIUM LID")
pre = df.loc["2025-07-01":"2026-06-30", "bui_disc"]
post = df.loc["2026-07-01":, "bui_disc"]
for lab, s in [("Jul 2025-Jun 2026", pre), ("since Jul 1 2026", post)]:
    p("  %-18s days %d, max %.2f, mean %.2f, days >= +1%%: %d (%.0f%%), days >= +2%%: %d, days >= 0: %d" %
      (lab, len(s), s.max(), s.mean(), (s >= 1).sum(), (s >= 1).mean() * 100, (s >= 2).sum(), (s >= 0).sum()))
# after a close at or above +1%, where is the premium 5 days later
above = post[post >= 1]
nxt = []
for dt in above.index:
    i = post.index.get_loc(dt)
    if i + 5 < len(post):
        nxt.append(post.iloc[i + 5] - post.iloc[i])
if nxt:
    p("  after a close >= +1%%: average change over next 5 days %.2f pts (n=%d)" % (np.mean(nxt), len(nxt)))
post.to_frame("bui_premium_pct").to_csv(os.path.join(RES, "bui_premium_since_shelf.csv"))

df[["bui_disc", "utf_disc", "spread", "norm", "dev", "fwd"]].round(3).to_csv(
    os.path.join(RES, "switch_backtest_daily.csv"))
open(os.path.join(RES, "switch_backtest.txt"), "w").write("\n".join(out) + "\n")
