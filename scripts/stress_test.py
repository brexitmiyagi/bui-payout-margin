# A 2022-type shock on today's BUI: 10-year +150bp and the equal-weight S&P 500 -17.5% (middle of -15% to -20%),
# hitting at once. Two sets of sensitivities: 2026's (rate duration 8, equity beta 0.16) and 2022's (weekly two-factor
# betas that year: rate -2.8% per 100bp, equity 0.69). Then what happens to NAV, the Section 19 gap at the next
# March 31, the rough unrealised-gain cushion and a stressed price. Also the actual 2022 replay for reference.
import datetime as dt
from common import daily, dists, nav_tr_index, at, rows
D = daily(); idx = nav_tr_index(D, dists())
nav0, pay, cushion0, need = D[-1]['nav'], 1.848, 6.34, 1.39   # cushion and gains needed a year from gains_reservoir.py
cases = {'2026 sensitivities (duration 8, equity beta 0.16)': (8.0, 0.16), '2022 sensitivities (rate -2.8%/100bp, equity beta 0.69)': (2.8, 0.69)}
start = idx[D.index(at(D, dt.date(2022, 3, 31)))]
for name, (dur, beq) in cases.items():
    shock = -dur*1.5/100 + beq*(-0.175)
    nav1 = nav0*(1+shock)
    loss = nav0 - nav1
    cushion = cushion0 - loss
    # Section 19 gap at Mar 31, 2027 if the shock is the whole NAV return from here
    five = (idx[-1]*(1+shock)/start)**0.2 - 1
    navm = nav1 - 0.154*4.5
    gap = (five - pay/navm)*100
    print(f"{name}: NAV {shock:+.1%} to ${nav1:.2f}; Mar 31, 2027 Section 19 gap {gap:+.2f} pts; "
          f"unrealised cushion ${cushion0:.2f} -> ${cushion:.2f} a share, about {max(cushion,0)/need:.1f} years of gains-funded payout; "
          f"price at -5% / -10% discount ${nav1*0.95:.2f} / ${nav1*0.90:.2f} (vs ${D[-1]['px']:.2f} now)")
a, b = at(D, dt.date(2021, 12, 31)), at(D, dt.date(2022, 12, 30))
print(f"actual 2022: NAV total return {idx[D.index(b)]/idx[D.index(a)]-1:+.2%}, NAV ${a['nav']:.2f} -> ${b['nav']:.2f}, "
      f"price ${a['px']:.2f} -> ${b['px']:.2f}, SPY {b['spy']/a['spy']-1:+.1%} (price)")
