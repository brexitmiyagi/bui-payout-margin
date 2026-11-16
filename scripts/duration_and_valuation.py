# Treats BUI the way its 2026 behaviour says to: as a rate-sensitive asset. Effective duration from the 2026 weekly
# rate betas, the 10-year note's modified duration, a hedge ratio, how much of BUI's weekly volatility the hedge
# removes, and a 12-month target built from 10-year scenarios:
#   NAV total return = rates-flat return + duration x (-change in 10-year yield)
#   rates-flat return = portfolio dividend yield + EPS growth - expenses (all stated below with sources)
#   10-year scenarios = 12-month forward from the Nov 13 Treasury par curve, +/- 1.41 standard deviations of BUI-era
#   12-month yield changes, weighted 25/50/25 (this keeps the variance of the historical changes)
import csv, os, datetime as dt, math, statistics as st
from common import daily, dists, nav_tr_index
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
D = daily(); idx = nav_tr_index(D, dists())
y = {dt.date.fromisoformat(r['observation_date']): float(r['DGS10']) for r in csv.DictReader(open(os.path.join(DATA, 'dgs10.csv'))) if r['DGS10'] not in ('', '.')}
curve = {r['Date']: r for r in csv.DictReader(open(os.path.join(DATA, 'treasury_par_curve_2026.csv')))}['11/13/2026']
y1, y10, y20 = float(curve['1 Yr']), float(curve['10 Yr']), float(curve['20 Yr'])
# 10-year par note modified duration at today's yield (semiannual coupons)
yy = y10/100; c = yy/2*100; cf = [c]*20; cf[-1] += 100
P = sum(cf[t]/(1+yy/2)**(t+1) for t in range(20)); mac = sum((t+1)/2*cf[t]/(1+yy/2)**(t+1) for t in range(20))/P
dmod = mac/(1+yy/2)
# BUI effective duration: range of 2026 weekly estimates from rate_beta_tests.py (M1 -8.7, M2 -7.2, M3 -10.5; rolling
# 26-week to Nov 6 -6.1). Central 8.
D_lo, D_c, D_hi = 6.0, 8.0, 10.5
print(f"10-year note: yield {y10:.2f}%, modified duration {dmod:.2f}")
print(f"BUI effective rate duration (2026 weekly regressions): central {D_c}, range {D_lo}-{D_hi}")
print(f"hedge: per $100 of BUI, short about ${100*D_c/dmod:.0f} face of 10-year notes (range ${100*D_lo/dmod:.0f}-${100*D_hi/dmod:.0f})")
# hedge effectiveness in 2026 weekly data (note return approximated as -dmod x change in yield)
W = [(x['d'], idx[k]) for k, x in enumerate(D) if x['d'].weekday() == 4 and x['d'] in y and x['d'].year == 2026]
r = [(b[1]/a[1]-1, y[b[0]]-y[a[0]]) for a, b in zip(W, W[1:])]
un = [a for a, _ in r]
hedged = [a - (D_c/dmod)*(-dmod*dy/100) for a, dy in r]
print(f"2026 weekly volatility, annualised: unhedged {st.pstdev(un)*math.sqrt(52):.1%}, hedged {st.pstdev(hedged)*math.sqrt(52):.1%}")
rr = st.correlation(un, [dy for _, dy in r])**2
print(f"share of 2026 weekly NAV variance explained by the 10-year alone (R-squared): {rr:.0%}")
# rates-flat return building blocks
div_yield, eps_growth, expenses = 2.76, 7.0, 1.06    # NII 1.70% + expenses 1.06% (N-CSRS H1 2026); sector EPS growth: Gabelli June 26, 2026 ("consensus EPS CAGR expectations exceeding 7%")
flat = div_yield + eps_growth - expenses
print(f"rates-flat NAV return: {div_yield}% dividends + {eps_growth}% EPS growth - {expenses}% expenses = {flat:.2f}%")
# 12-month forward 10-year: interpolate 11-year between 10 and 20
y11 = y10 + (y20 - y10)*0.1
fwd = (11*y11 - 1*y1)/10
dys = []
for i in range(len(D)-252):
    a, b = D[i]['d'], D[i+252]['d']
    ka = max(k for k in y if k <= a); kb = max(k for k in y if k <= b); dys.append(y[kb]-y[ka])
sd = st.pstdev(dys)
print(f"10-year now {y10:.2f}%, 12-month forward {fwd:.2f}%; s.d. of 12-month changes since Nov 2016 {sd:.2f} pts")
nav0, pay, price0 = D[-1]['nav'], 1.848, D[-1]['px']
cases = [('bull: 10-year falls', fwd - 1.41*sd, 0.25, 1.0), ('base: forward curve', fwd, 0.50, -0.26), ('bear: 10-year rises', fwd + 1.41*sd, 0.25, -5.0)]
tgt = 0
for name, y_end, w, prem in cases:
    dy = y_end - y10
    tr = flat/100 - D_c*dy/100
    nav1 = nav0*(1+tr) - pay; p1 = nav1*(1+prem/100); tgt += w*p1
    print(f"  {name}: 10-year {y_end:.2f}% ({dy:+.2f}), NAV total return {tr:+.1%}, NAV ${nav1:.2f}, premium {prem:+.2f}%, price ${p1:.2f} (weight {w:.0%})")
print(f"weighted 12-month target ${tgt:.2f} vs ${price0:.2f}: {tgt/price0-1:+.1%} on price, {(tgt+pay)/price0-1:+.1%} with distributions")
for Dx in (D_lo, D_hi):
    t2 = sum(w*(nav0*(1 + flat/100 - Dx*(ye-y10)/100) - pay)*(1+pr/100) for _, ye, w, pr in cases)
    print(f"  with duration {Dx}: target ${t2:.2f}")
print(f"hedged carry: rates-flat {flat:.2f}% minus {D_c/dmod:.2f} x 10-year yield {y10:.2f}% = {flat - D_c/dmod*y10:+.2f}% a year before premium changes")
