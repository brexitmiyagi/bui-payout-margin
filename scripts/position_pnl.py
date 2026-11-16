"""What a position looks like in money, with and without a Treasury hedge. Illustrative, not advice.

$100,000 of BUI held for a year. NAV total return = 8.7% rates-flat return minus duration x change in the
10-year (central 8, range 6 to 10.5); premium assumed unchanged. Hedge: short about $103 of 10-year notes per
$100 of BUI (duration 8 over the note's 7.74), which costs the note's 5.15% yield and gains 7.74 x the yield rise.
Sizing: what position, as a share of a portfolio, uses a 1% annual volatility budget.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
pos, flat, y10, dmod, hedge = 100_000, 8.70, 5.15, 7.74, 1.03
rows = []
for bp in [-100, -50, 0, 50, 100]:
    dy = bp / 100
    unh = {D: pos * (flat - D * dy) / 100 for D in (6, 8, 10.5)}
    h = pos * hedge * (-y10 + dmod * dy) / 100       # short notes: pay the yield, gain when yields rise
    rows.append({"10y_move_bp": bp, "unhedged_D6": round(unh[6]), "unhedged_D8": round(unh[8]), "unhedged_D10.5": round(unh[10.5]),
                 "hedged_D8": round(unh[8] + h), "hedged_D6": round(unh[6] + h), "hedged_D10.5": round(unh[10.5] + h)})
t = pd.DataFrame(rows)
p("one-year P&L on $100,000 of BUI, premium unchanged ($):")
p(t.to_string(index=False))
p("\nsizing for a 1%% annual volatility budget: unhedged 13.6%% vol -> %.1f%% of the portfolio; hedged 12.2%% -> %.1f%%" %
  (1 / 13.6 * 100, 1 / 12.2 * 100))
p("the hedge removes the rate bet and about 1.4 points of volatility; what's left is about +3.4% a year of carry before premium changes")
t.to_csv(os.path.join(RES, "position_pnl.csv"), index=False)
open(os.path.join(RES, "position_pnl.txt"), "w").write("\n".join(out) + "\n")
