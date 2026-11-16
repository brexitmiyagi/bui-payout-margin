"""Out-of-sample check on the UTF switch rule.

Pick the threshold on 2016-2020 only (from 3 to 7 points below the trailing one-year median, best average
12-month UTF-minus-BUI return on signal days), then see how that threshold, and the 5-point rule used in the
post, did from 2021 on.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
d = pd.read_csv(os.path.join(RES, "switch_backtest_daily.csv"), parse_dates=["date"]).set_index("date").dropna(subset=["dev", "fwd"])
ins, oos = d.loc[:"2020-12-31"], d.loc["2021-01-01":]
best = None
for th in [3, 4, 5, 6, 7]:
    s = ins[ins.dev <= -th]
    p("in-sample 2016-2020, threshold %d: %d signal days, mean %.2f, hit %.0f%%" %
      (th, len(s), s.fwd.mean() if len(s) else float("nan"), (s.fwd > 0).mean() * 100 if len(s) else float("nan")))
    if len(s) >= 40 and (best is None or s.fwd.mean() > best[1]):
        best = (th, s.fwd.mean())
p("chosen on 2016-2020: %d points" % best[0])
for th in sorted({best[0], 5}):
    s = oos[oos.dev <= -th]
    p("out of sample 2021 on, threshold %d: %d signal days, mean %.2f, median %.2f, hit %.0f%%; all days mean %.2f, hit %.0f%%" %
      (th, len(s), s.fwd.mean(), s.fwd.median(), (s.fwd > 0).mean() * 100, oos.fwd.mean(), (oos.fwd > 0).mean() * 100))
open(os.path.join(RES, "switch_oos.txt"), "w").write("\n".join(out) + "\n")
