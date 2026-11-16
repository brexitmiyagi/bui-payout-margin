# The rest of the payout has to come from gains. How much unrealised gain BUI carried at 30 June 2026, and roughly
# how many years of the gains-funded part of the payout that covers. The post-June figure is an estimate.
from common import daily, dists, nav_tr_index, at
import datetime as dt
lt_value, lt_cost, shares = 725_562_730, 516_013_257, 26_548_823   # N-CSRS 30 Jun 2026: long-term investments at value and cost; shares outstanding
res_jun = (lt_value - lt_cost) / shares
nii = 0.23 * 2; pay = 0.154 * 12
need = pay - nii
print(f"unrealised appreciation 30 Jun 2026: ${lt_value-lt_cost:,.0f} = ${res_jun:.2f} a share")
D = daily(); X = dists(); idx = nav_tr_index(D, X)
a = at(D, dt.date(2026, 6, 30)); b = D[-1]
ia, ib = D.index(a), D.index(b)
paid = sum(v for k, v in X.items() if a['d'] < k <= b['d'])
mkt = a['nav'] * (idx[ib]/idx[ia] - 1)
est = res_jun - paid + mkt
print(f"since 30 Jun: distributions ${paid:.3f}, NAV total return {idx[ib]/idx[ia]-1:+.2%} (${mkt:+.2f} a share)")
print(f"estimated unrealised gain now ~${est:.2f} a share; gains needed a year beyond NII ${need:.2f}; ~{est/need:.1f} years at a flat market")
