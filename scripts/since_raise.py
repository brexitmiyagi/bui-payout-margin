# What the fund and the utilities ETF did after BUI lifted its payout (declared 5 June 2026, first $0.154 ex-date 15 July).
import datetime as dt
from common import daily, dists, nav_tr_index, at
D = daily(); X = dists(); idx = nav_tr_index(D, X)
a = at(D, dt.date(2026, 6, 30)); b = D[-1]; ia, ib = D.index(a), D.index(b)
print(f"{a['d']} -> {b['d']}: NAV ${a['nav']:.2f} -> ${b['nav']:.2f} ({b['nav']/a['nav']-1:+.1%}), NAV total return {idx[ib]/idx[ia]-1:+.2%}, price ${a['px']:.2f} -> ${b['px']:.2f}")
print(f"XLU price {a['xlu']:.2f} -> {b['xlu']:.2f} ({b['xlu']/a['xlu']-1:+.1%})")
for d in (dt.date(2026, 8, 31), dt.date(2026, 9, 30)):
    x = at(D, d); print(f"  {x['d']}: NAV ${x['nav']:.2f}, XLU {x['xlu']:.2f}")
