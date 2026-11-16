# Checks my rebuilt NAV total return against the numbers BlackRock publishes. Fails loudly if any gap is over 0.15 points.
import datetime as dt
from common import daily, dists, nav_tr_index, at, rows
D = daily(); X = dists(); idx = nav_tr_index(D, X)
def tr(a, b):
    ia, ib = D.index(at(D, a)), D.index(at(D, b))
    return idx[ib] / idx[ia] - 1
s19 = {r['performance_as_of']: r for r in rows('section19_notices_2026.csv')}
fh = {r['period']: r for r in rows('financial_highlights.csv')}
checks = [
    ('5 years to 2026-09-30, a year (Oct 30 Section 19 notice)', (1 + tr(dt.date(2021, 9, 30), dt.date(2026, 9, 30))) ** (1/5) - 1, float(s19['2026-09-30']['five_year_avg_nav_tr_pct']) / 100),
    ('2026 to 2026-09-30 (Oct 30 Section 19 notice)', tr(dt.date(2025, 12, 31), dt.date(2026, 9, 30)), float(s19['2026-09-30']['ytd_cum_nav_tr_pct']) / 100),
    ('first half 2026 (N-CSRS financial highlights)', tr(dt.date(2025, 12, 31), dt.date(2026, 6, 30)), float(fh['H1 2026']['nav_tr_pct']) / 100),
]
for name, mine, theirs in checks:
    print(f"{name}: mine {mine:.2%}, fund {theirs:.2%}, gap {(mine-theirs)*100:+.2f} pts")
    assert abs(mine - theirs) < 0.0015, f"tie-out broke on {name}"
print("all tie-outs within 0.15 pts")
