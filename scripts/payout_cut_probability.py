"""How likely is a cut to BUI's $0.154 monthly payout by the end of 2027, and what would set it off?

There's no formula for when BlackRock cuts, so I use what BlackRock has actually done and tolerated:
  - The six other BlackRock trusts that dropped call writing with BUI pay 6.0% to 7.1% of NAV (CEF Connect, Nov 13).
  - BUI itself paid as much as 8.1% of NAV at the March 2020 low and didn't cut.
  - The two trusts that did cut (BSTZ, BMEZ) cut in October 2025, just before the strategy change, not after a drawdown.
So the trigger I test is the payout running above a given share of NAV at two quarter-ends in a row, with 8.1% (BUI's
own record) as the central case and 7.5% and 9.0% either side. At $0.154 a month, 8.1% of NAV is a NAV of $22.81.

NAV paths: 12-month blocks of BUI's own monthly NAV total returns resampled, the payout taken out each month, run from
the latest NAV to December 2027. Two return pools: every month since November 2016, and the last five years only.
"""
import os, random
import pandas as pd
from common import daily, dists, nav_tr_index

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
random.seed(11)
D = daily(); idx = nav_tr_index(D, dists())
me = {}
for k, x in enumerate(D):
    me[(x['d'].year, x['d'].month)] = idx[k]
keys = sorted(k for k in me if k <= (2026, 10))
monthly = [(keys[i], me[keys[i]] / me[keys[i-1]] - 1) for i in range(1, len(keys))]
pools = {"all months since Nov 2016": [r for _, r in monthly],
         "last five years": [r for k, r in monthly if k >= (2021, 11)]}
PAY = 0.154
nav0 = D[-1]['nav']
# months from Dec 2026 to Dec 2027; quarter-ends at positions of Mar, Jun, Sep, Dec
months = [(2026, 12)] + [(2027, m) for m in range(1, 13)]
qe = [i for i, (y, m) in enumerate(months) if m in (3, 6, 9, 12)]
N = 20000
rows = []
for name, pool in pools.items():
    blocks = [pool[i:i+12] for i in range(0, len(pool) - 11)]
    paths = []
    for _ in range(N):
        rs = []
        while len(rs) < len(months):
            rs += random.choice(blocks)
        nav, path = nav0, []
        for r in rs[:len(months)]:
            nav = nav * (1 + r) - PAY
            path.append(nav)
        paths.append(path)
    for trig in (7.5, 8.1, 9.0):
        level = PAY * 12 / (trig / 100)
        hit = 0
        for path in paths:
            q = [path[i] < level for i in qe]
            if any(q[j] and q[j+1] for j in range(len(q) - 1)):
                hit += 1
        rows.append({"pool": name, "trigger_rate_on_nav": trig, "nav_level": round(level, 2),
                     "fall_from_today_pct": round((level / nav0 - 1) * 100, 1), "p_cut_by_dec_2027_pct": round(hit / N * 100, 1)})
    end = sorted(pt[-1] for pt in paths)
    p("%s: Dec 2027 NAV 10th pct $%.2f, median $%.2f, 90th $%.2f" % (name, end[N//10], end[N//2], end[9*N//10]))
t = pd.DataFrame(rows)
p("\nlatest NAV $%.2f, payout $%.3f a month = %.2f%% of NAV" % (nav0, PAY, PAY * 12 / nav0 * 100))
p(t.to_string(index=False))
t.to_csv(os.path.join(RES, "payout_cut_probability.csv"), index=False)
open(os.path.join(RES, "payout_cut_probability.txt"), "w").write("\n".join(out) + "\n")
