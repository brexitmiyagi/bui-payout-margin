# The Section 19 margin (5-year average annual NAV return minus the distribution rate on NAV) rebuilt from daily NAV
# for month-ends the notices haven't reached yet, and what NAV has to do by 31 March 2027 for the margin to go negative.
import datetime as dt
from common import daily, dists, nav_tr_index, at
D = daily(); X = dists(); idx = nav_tr_index(D, X)
pay = 0.154 * 12
def five(e):
    s = e.replace(year=e.year-5)
    a, b = D.index(at(D, s)), D.index(at(D, e))
    return (idx[b]/idx[a])**0.2 - 1
for e in (dt.date(2026, 9, 30), dt.date(2026, 10, 30), D[-1]['d']):
    nav = at(D, e)['nav']
    print(f"{e}: 5-year {five(e):.2%} vs payout {pay/nav:.2%} of NAV ${nav:.2f}, margin {(five(e)-pay/nav)*100:+.2f} pts")
start = idx[D.index(at(D, dt.date(2022, 3, 31)))]; now = idx[-1]; nav0 = D[-1]['nav']
left = 0.154 * 4.5   # roughly four and a half monthly payments between mid-November and 31 March
print("NAV total return from now to 31 Mar 2027 -> 5-year, payout rate, margin")
for g in (-0.10, -0.06, -0.05, -0.04, -0.03, 0.0, 0.03, 0.05, 0.10):
    r5 = (now*(1+g)/start)**0.2 - 1
    nav = nav0*(1+g) - left
    print(f"  {g:+.0%}: {r5:.2%} vs {pay/nav:.2%}, margin {(r5-pay/nav)*100:+.2f} pts")
