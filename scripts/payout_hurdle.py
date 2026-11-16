# How much BUI's NAV has to earn every year just to pay its distribution without shrinking, and how often
# it has earned that over any 12 months since late 2016.
import datetime as dt, statistics as st
from common import daily, dists, nav_tr_index, at
D = daily(); X = dists(); idx = nav_tr_index(D, X)
last = D[-1]
monthly = 0.154
hurdle = monthly * 12 / last['nav']
print(f"latest: {last['d']} price ${last['px']:.2f}, NAV ${last['nav']:.2f}, premium {last['px']/last['nav']-1:+.2%}")
print(f"regular distribution ${monthly:.3f} a month = ${monthly*12:.3f} a year = {hurdle:.2%} of NAV, {monthly*12/last['px']:.2%} of price")
# rolling 12-month NAV total return (252 trading days)
r12 = [idx[i+252]/idx[i]-1 for i in range(len(idx)-252)]
s = sorted(r12)
pct = lambda p: s[int(p*(len(s)-1))]
print(f"rolling 12-month NAV total return since {D[0]['d']}: {len(r12)} windows, median {st.median(r12):.2%}, 10th pct {pct(.10):.2%}, 25th {pct(.25):.2%}, 75th {pct(.75):.2%}, 90th {pct(.90):.2%}")
print(f"share of 12-month windows that earned at least the {hurdle:.2%} payout: {sum(v>=hurdle for v in r12)/len(r12):.0%}")
print(f"share of 12-month windows with a negative NAV total return: {sum(v<0 for v in r12)/len(r12):.1%}")
# buckets for the histogram in the post
edges = [None, -.10, -.05, 0, .05, hurdle, .10, .15, .20, .25, .30, None]
for lo, hi in zip(edges, edges[1:]):
    n = sum((lo is None or v >= lo) and (hi is None or v < hi) for v in r12)
    label = f"below {hi:.2%}" if lo is None else f"{lo:.2%} and up" if hi is None else f"{lo:.2%} to {hi:.2%}"
    print(f"  {label}: {n/len(r12):.1%}")
# annualised NAV total return over the full sample and the last 5 years
yrs = (D[-1]['d']-D[0]['d']).days/365.25
print(f"NAV total return {D[0]['d']} to {D[-1]['d']}: {idx[-1]**(1/yrs)-1:.2%} a year")
i5 = [i for i,x in enumerate(D) if x['d'] <= D[-1]['d'].replace(year=D[-1]['d'].year-5)][-1]
print(f"last 5 years: {(idx[-1]/idx[i5])**(1/5)-1:.2%} a year from {D[i5]['d']}")
