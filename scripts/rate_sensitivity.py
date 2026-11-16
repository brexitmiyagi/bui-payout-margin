# How much BUI's NAV moves when the 10-year Treasury yield moves. Weekly (Friday) NAV total return regressed on the
# weekly change in the 10-year yield (FRED DGS10), year by year. Rates have mattered more in 2026 than in most years.
import csv, os, datetime as dt, statistics as st
from common import daily, dists, nav_tr_index
HERE = os.path.dirname(os.path.abspath(__file__))
D = daily(); idx = nav_tr_index(D, dists())
y = {}
for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'dgs10.csv'))):
    if r['DGS10'] not in ('', '.'):
        y[dt.date.fromisoformat(r['observation_date'])] = float(r['DGS10'])
W = [(D[k]['d'], idx[k], D[k]['spy']) for k in range(len(D)) if D[k]['d'].weekday() == 4 and D[k]['d'] in y]
def slope(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    return sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / sum((a-mx)**2 for a in xs)
def stats(sel):
    pts = [(W[j][1]/W[j-1][1]-1, y[W[j][0]]-y[W[j-1][0]]) for j in range(1, len(W)) if sel(W[j][0])]
    r = [p[0] for p in pts]; dy = [p[1] for p in pts]
    return len(pts), slope(dy, r)*100, st.correlation(r, dy)
for yr in range(2017, 2027):
    n, b, c = stats(lambda d: d.year == yr)
    print(f"{yr}: {n} weeks, NAV move per +100bp in the 10-year {b:+.1f}%, correlation {c:+.2f}")
n, b, c = stats(lambda d: d > dt.date(2026, 6, 30))
print(f"since 30 Jun 2026: {n} weeks, {b:+.1f}% per +100bp, correlation {c:+.2f}")
for d in (dt.date(2026, 6, 30), dt.date(2026, 9, 30), dt.date(2026, 10, 30), max(y)):
    k = max(x for x in y if x <= d); print(f"10-year yield {k}: {y[k]:.2f}%")
