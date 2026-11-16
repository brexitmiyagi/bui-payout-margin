# 12-month target. BUI's price tracks its NAV, so the target is next year's NAV times the usual premium.
# Next year's NAV = today's NAV grown by the portfolio's total return, less the $1.848 the fund pays out.
# Returns come from BUI's own history: every 12-month NAV total return since November 2016 (payout_hurdle.py),
# split into a weak year (25th percentile), a normal year (the last five years' annualised NAV return) and a strong
# year (75th percentile). The median 12-month window ran higher than the 5-year rate, so I use the 5-year rate.
import statistics as st, datetime as dt
from common import daily, dists, nav_tr_index
D = daily(); X = dists(); idx = nav_tr_index(D, X)
r12 = [(D[i]['d'], idx[i+252]/idx[i]-1) for i in range(len(idx)-252)]
allv = sorted(v for _, v in r12)
last5 = [v for d, v in r12 if d >= dt.date(2021, 11, 12)]
pct = lambda s, p: s[int(p*(len(s)-1))]
nav0, px0 = D[-1]['nav'], D[-1]['px']
pay = 0.154 * 12
prem = st.median(x['px']/x['nav']-1 for x in D)          # median since Nov 2016
i5 = [i for i, x in enumerate(D) if x['d'] <= dt.date(2021, 11, 12)][-1]
r5 = (idx[-1]/idx[i5])**(1/5) - 1
cases = [('weak year (25th pct)', pct(allv, .25), .25), ('normal year (5y annualised)', r5, .50), ('strong year (75th pct)', pct(allv, .75), .25)]
tgt = 0
for name, r, w in cases:
    nav1 = nav0 * (1 + r) - pay
    p1 = nav1 * (1 + prem)
    tgt += w * p1
    print(f"{name}: NAV return {r:+.2%} -> NAV ${nav1:.2f}, price ${p1:.2f} ({p1/px0-1:+.1%} price, {(p1+pay)/px0-1:+.1%} with distributions), weight {w:.0%}")
print(f"median premium since Nov 2016 {prem:+.2%}")
print(f"12-month target ${tgt:.2f} vs ${px0:.2f}: {tgt/px0-1:+.1%} on price, {(tgt+pay)/px0-1:+.1%} with ${pay:.3f} of distributions")
print(f"rule: Buy above ${px0*1.15:.2f}, Sell below ${px0*0.85:.2f} (15% either way); NAV return needed to hold NAV flat {pay/nav0:.2%}")
