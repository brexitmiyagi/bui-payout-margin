"""Why CEF Connect showed BUI at -0.33% on November 13 when BlackRock's own numbers gave -0.64%.

On the evening of November 13 I saved CEF Connect's live discount for 108 equity CEFs (equity_cef_universe_2026_11_13.csv).
On November 18 I pulled CEF Connect's own one-year pricing history for the same funds
(cef_connect_history_2026_11_18.csv). The history for November 13 has BUI at a $26.38 NAV and -0.64%, the same as
BlackRock. So the -0.33% wasn't a different NAV source. It was the live page before the day's NAV had posted. If
the history is the final number, how often was the live snapshot wrong, by how much, and for which kinds of fund?
Inside the history itself, price, NAV and discount agree with each other on almost every day for every fund.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

u = pd.read_csv(os.path.join(DATA, "equity_cef_universe_2026_11_13.csv")).set_index("ticker")
h = pd.read_csv(os.path.join(DATA, "cef_connect_history_2026_11_18.csv")).set_index("ticker")
x = pd.DataFrame({"snapshot": u.discount_pct, "final": pd.to_numeric(h.discount_2026_11_13_history, errors="coerce"),
                  "category": u.category}).dropna()
x["diff"] = x.snapshot - x.final
p("funds with both numbers: %d" % len(x))
p("snapshot off by more than 0.05 points: %d; more than 0.25: %d; more than 1.0: %d" %
  ((x["diff"].abs() > 0.05).sum(), (x["diff"].abs() > 0.25).sum(), (x["diff"].abs() > 1.0).sum()))
p("mean absolute error %.2f points, largest %.2f" % (x["diff"].abs().mean(), x["diff"].abs().max()))
foreign = x.category.isin(["Asia E", "Emergi", "Single", "Global"])
p("mean absolute error, foreign-equity categories (Asia, emerging, single country, global): %.2f points (%d funds)"
  % (x[foreign]["diff"].abs().mean(), foreign.sum()))
p("mean absolute error, everything else: %.2f points (%d funds)" % (x[~foreign]["diff"].abs().mean(), (~foreign).sum()))
p("\nby category:")
p(x.groupby("category")["diff"].agg(lambda s: s.abs().mean()).round(2).sort_values(ascending=False).to_string())
p("\nlargest misses (snapshot minus final, points):")
p(x.reindex(x["diff"].abs().sort_values(ascending=False).index).head(12)[["category", "snapshot", "final", "diff"]].round(2).to_string())
p("\nBUI: snapshot %.2f, final %.2f" % (x.loc["BUI", "snapshot"], x.loc["BUI", "final"]))
x.to_csv(os.path.join(RES, "cef_connect_timing.csv"))
open(os.path.join(RES, "cef_connect_timing.txt"), "w").write("\n".join(out) + "\n")
