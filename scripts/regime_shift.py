# Did utilities stop trading like equities in 2026? Two-factor regressions, year by year: return on the weekly (and
# daily) change in the 10-year yield and on the S&P 500 (SPY) at the same time. Run for BUI's NAV total return and
# for XLU. Also the plain XLU-SPY correlation. BUI's NAV includes foreign stocks priced earlier in the day, so the
# daily numbers understate its links; the weekly ones are cleaner.
import csv, os, datetime as dt, statistics as st
from common import daily, dists, nav_tr_index
HERE = os.path.dirname(os.path.abspath(__file__))
D = daily(); idx = nav_tr_index(D, dists())
y = {dt.date.fromisoformat(r['observation_date']): float(r['DGS10'])
     for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'dgs10.csv'))) if r['DGS10'] not in ('', '.')}
def ols2(Y, X1, X2):
    n = len(Y); m = lambda a: sum(a)/n
    y_ = [a-m(Y) for a in Y]; a_ = [a-m(X1) for a in X1]; b_ = [a-m(X2) for a in X2]
    saa = sum(a*a for a in a_); sbb = sum(b*b for b in b_); sab = sum(a*b for a, b in zip(a_, b_))
    say = sum(a*c for a, c in zip(a_, y_)); sby = sum(b*c for b, c in zip(b_, y_)); det = saa*sbb - sab*sab
    return (say*sbb - sby*sab)/det, (sby*saa - say*sab)/det
def series(points):
    out = []
    for (d0, i0, x0, s0), (d1, i1, x1, s1) in zip(points, points[1:]):
        out.append((d1, i1/i0-1, x1/x0-1, s1/s0-1, y[d1]-y[d0]))
    return out
pts = [(x['d'], idx[k], x['xlu'], x['spy']) for k, x in enumerate(D) if x['d'] in y and x['xlu'] and x['spy']]
for label, P in (('weekly (Fridays)', series([p for p in pts if p[0].weekday() == 4])), ('daily', series(pts))):
    print(label)
    for yr in range(2017, 2027):
        Q = [p for p in P if p[0].year == yr]
        bn, sn = ols2([q[1] for q in Q], [q[4] for q in Q], [q[3] for q in Q])
        bx, sx = ols2([q[2] for q in Q], [q[4] for q in Q], [q[3] for q in Q])
        c = st.correlation([q[2] for q in Q], [q[3] for q in Q])
        print(f"  {yr}: BUI NAV {bn*100:+.1f}% per +100bp, S&P beta {sn:+.2f} | XLU {bx*100:+.1f}% per +100bp, S&P beta {sx:+.2f} | XLU-SPY corr {c:+.2f}")
