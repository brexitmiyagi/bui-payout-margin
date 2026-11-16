# Premium or discount of BUI's price to its NAV, daily since November 2016 (Nasdaq BUI close vs XBUIX NAV).
import statistics as st
from common import daily
D = daily()
pd = [(x['d'], x['px']/x['nav']-1) for x in D]
v = [p for _, p in pd]
print(f"{D[0]['d']} to {D[-1]['d']}: mean {st.mean(v):+.2%}, median {st.median(v):+.2%}, at a premium {sum(p>0 for p in v)/len(v):.0%} of days")
for y in (2021, 2023, 2025, 2026):
    w = [p for d, p in pd if d.year >= y]
    print(f"  since {y}: mean {st.mean(w):+.2%}, median {st.median(w):+.2%}")
mx = max((p, d) for d, p in pd if d.year == 2026)
print(f"2026 high {mx[0]:+.2%} on {mx[1]}; latest {pd[-1][1]:+.2%} on {pd[-1][0]}")
