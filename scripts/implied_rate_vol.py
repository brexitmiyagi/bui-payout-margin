"""Swap the historical rate-move size for the one the options market is pricing.

MOVE and swaption vols are not free to pull, so I use listed options on IEF (7-10 year Treasuries) from Cboe's
delayed quotes, close of 13 November 2026. At-the-money implied vol is a price vol; dividing by IEF's own
empirical duration (its 2026 daily sensitivity to the 10-year yield) turns it into a yield vol in percentage points.
Then the rate-scenario target is rerun with that number in place of the 0.92 historical standard deviation.
"""
import os
import re
import json
import datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

d = json.load(open(os.path.join(DATA, "ief_options_cboe_2026_11_13.json")))["data"]
S = d["current_price"]
asof = dt.datetime(2026, 11, 13)
rows = []
for o in d["options"]:
    m = re.match(r"IEF(\d{6})([CP])(\d{8})", o["option"])
    e = dt.datetime.strptime(m.group(1), "%y%m%d")
    rows.append((e, m.group(2), int(m.group(3)) / 1000, o["iv"], o["bid"], o["open_interest"]))
ch = pd.DataFrame(rows, columns=["exp", "cp", "K", "iv", "bid", "oi"])
ch = ch[(ch.iv > 0) & (ch.bid > 0)]
term = []
for e, g in ch.groupby("exp"):
    a = g.iloc[(g.K - S).abs().argsort()[:4]]
    term.append({"expiry": e.date(), "days": (e - asof).days, "atm_iv": a.iv.mean()})
term = pd.DataFrame(term)
term.to_csv(os.path.join(RES, "ief_atm_iv_term.csv"), index=False)
# interpolate to one year
iv1y = float(np.interp(365, term.days, term.atm_iv))
p("IEF close %.2f; ATM implied vol at 1 year (interpolated) %.2f%%" % (S, iv1y * 100))

# IEF empirical duration from 2026 daily data
ief = pd.read_csv(os.path.join(DATA, "ief_daily.csv"), parse_dates=["date"]).set_index("date").close
y = pd.read_csv(os.path.join(DATA, "dgs10.csv"))
y.columns = ["date", "y"]
y["date"] = pd.to_datetime(y.date)
y = y.set_index("date").y.replace(".", np.nan).astype(float)
k = pd.concat([ief.pct_change() * 100, y.diff()], axis=1, sort=True).dropna().loc["2025-11-13":]
k.columns = ["r", "dy"]
dur = -np.polyfit(k.dy, k.r, 1)[0]
sig_y = iv1y * 100 / dur
p("IEF empirical duration (last 12 months, daily) %.2f -> implied 1-year 10-year yield vol %.2f pts (%.0f bp)" %
  (dur, sig_y, sig_y * 100))
p("historical s.d. of 12-month 10-year changes used before: 0.92 pts; implied is %.0f%% %s" %
  (abs(sig_y / 0.92 - 1) * 100, "higher" if sig_y > 0.92 else "lower"))

# rerun the scenario target with implied vol, same inputs as duration_and_valuation.py
y10, fwd, nav0, pay, price0, Dc = 5.07, 5.16, 25.86, 1.848, 25.77, 8.0  # Nov 18 close (Treasury par curve, Nasdaq XBUIX and BUI)
flat = 2.76 + 7.0 - 1.06
tgt = 0
for name, sh, w, prem in [("bull", -1.41, 0.25, 1.0), ("base", 0, 0.5, -0.26), ("bear", 1.41, 0.25, -5.0)]:
    ye = fwd + sh * sig_y
    tr = flat / 100 - Dc * (ye - y10) / 100
    nav1 = nav0 * (1 + tr) - pay
    p1 = nav1 * (1 + prem / 100)
    tgt += w * p1
    p("  %-4s 10-year %.2f%%, NAV total return %+.1f%%, price $%.2f" % (name, ye, tr * 100, p1))
p("weighted target with implied vol $%.2f (vs $25.83 with historical vol)" % tgt)
p("the weighted target barely moves because the scenarios are symmetric and the model is linear in rates;"
  " what changes is the width: the bear case price moves from $22.22 to the figure above")
open(os.path.join(RES, "implied_rate_vol.txt"), "w").write("\n".join(out) + "\n")
