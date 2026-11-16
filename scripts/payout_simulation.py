# Monte Carlo on BUI's own history: resample 12-month blocks of BUI's monthly NAV total returns (Nov 2016 to Oct 2026)
# and run the $0.154 monthly payout forward three years from the Nov 13, 2026 NAV. Tracks the Section 19 margin
# (5-year NAV return minus payout rate on NAV) at each month-end, NAV, and a rough unrealised-gain reservoir.
# The return pool is every month from Nov 2016 to Oct 2026.
import random, datetime as dt
from common import daily, dists, nav_tr_index
random.seed(7)
D = daily(); idx = nav_tr_index(D, dists())
# month-end index levels
me = {}
for k, x in enumerate(D):
    me[(x['d'].year, x['d'].month)] = (x['d'], idx[k], x['nav'])
keys = sorted(me)
monthly = [(keys[i], me[keys[i]][1] / me[keys[i-1]][1] - 1) for i in range(1, len(keys)) if keys[i] <= (2026, 10)]
hist_levels = [me[k][1] for k in keys if k <= (2026, 10)]
pools = {"all months": [r for _, r in monthly]}
PAY, NII_M, NEED_M = 0.154, 0.46/12, 0.154 - 0.46/12
nav0, res0 = D[-1]['nav'], 6.34      # Nov 13 NAV; estimated unrealised gain a share (gains_reservoir.py)
H, N = 36, 20000
for name, pool in pools.items():
    blocks = [pool[i:i+12] for i in range(0, len(pool)-11)]
    neg_by_dec27 = 0; roc_by_dec27 = 0; nav_end = []; min_margin = []
    for _ in range(N):
        path = []
        while len(path) < H: path += random.choice(blocks)
        path = path[:H]
        lv = list(hist_levels); nav = nav0; res = res0; neg = False; roc = False; mm = 9
        for m, r in enumerate(path):
            lv.append(lv[-1]*(1+r))
            gain = nav*(1+r) - nav            # total return in $ before the payout
            nav = nav*(1+r) - PAY
            res += gain - NII_M - NEED_M      # unrealised moves with the market; realising the gains-funded part draws it down
            if res < 0: roc = roc or m < 14
            five = (lv[-1]/lv[-61])**0.2 - 1
            margin = five - PAY*12/nav
            if m < 14:                        # month-ends through Dec 2027
                mm = min(mm, margin)
                if margin < 0: neg = True
        neg_by_dec27 += neg; roc_by_dec27 += roc; nav_end.append(nav); min_margin.append(mm)
    nav_end.sort()
    print(f"{name}: {len(pool)} months")
    print(f"  P(Section 19 margin negative at some month-end by Dec 2027): {neg_by_dec27/N:.0%}")
    print(f"  P(rough unrealised-gain reservoir runs out by Dec 2027): {roc_by_dec27/N:.0%}")
    print(f"  NAV after 3 years: 10th pct ${nav_end[int(.1*N)]:.2f}, median ${nav_end[N//2]:.2f}, 90th ${nav_end[int(.9*N)]:.2f}; P(below ${nav0:.2f} today) {sum(v < nav0 for v in nav_end)/N:.0%}")
