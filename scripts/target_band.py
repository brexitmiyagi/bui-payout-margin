"""A band around the $26.38 target instead of a point.

Monte Carlo over the inputs I'm least sure of: the 12-month change in the 10-year (normal, centred on the
forward, 1.06 points of implied volatility), rate duration (uniform 6 to 10.5), earnings growth (triangular
5 / 7 / 9.42), the non-rate part of BUI's NAV return (normal, 12.1% a year: the 13.6% weekly volatility with the
21% that rates explain taken out) and the premium a year from now (drawn from BUI's daily premiums since 2023).
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
b = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
prem_hist = ((b.bui_close / b.bui_nav - 1) * 100).loc["2023":].values
rng = np.random.default_rng(3)
N = 200_000
nav0, pay, price0 = 26.38, 1.848, 26.21
dy = rng.normal(5.24 - 5.15, 1.06, N)
D = rng.uniform(6, 10.5, N)
g = rng.triangular(5, 7, 9.42, N)
eps = rng.normal(0, 13.6 * np.sqrt(1 - 0.21), N)
prem = rng.choice(prem_hist, N)
tr = (2.76 + g - 1.06 - D * dy + eps) / 100
px = (nav0 * (1 + tr) - pay) * (1 + prem / 100)
q = np.percentile(px, [10, 25, 50, 75, 90])
p("12-month price, BUI: 10th %.2f, 25th %.2f, median %.2f, 75th %.2f, 90th %.2f; mean %.2f" % (*q, px.mean()))
p("probability price + distributions beats today's $%.2f: %.0f%%; beats 1-year Treasury (4.65%%): %.0f%%" %
  (price0, ((px + pay) > price0).mean() * 100, ((px + pay) / price0 - 1 > 0.0465).mean() * 100))
p("without the non-rate noise (rates, duration, growth, premium only): 10th %.2f, median %.2f, 90th %.2f" %
  tuple(np.percentile((nav0 * (1 + (2.76 + g - 1.06 - D * dy) / 100) - pay) * (1 + prem / 100), [10, 50, 90])))
open(os.path.join(RES, "target_band.txt"), "w").write("\n".join(out) + "\n")
