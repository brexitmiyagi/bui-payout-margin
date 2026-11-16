# BUI against three utility/infrastructure CEFs it could be swapped for: Cohen & Steers Infrastructure (UTF),
# Duff & Phelps Utility and Infrastructure (DPG) and Gabelli Global Utility & Income (GLU). Same tests for each:
# discount now vs its own history, distribution rate, the 5-year NAV return vs payout gap (rebuilt from Nasdaq NAVs and
# distributions reinvested at NAV, the way BlackRock's Section 19 does it), and 2026 weekly rate and equity betas.
# Balance-sheet items (leverage, expenses, income coverage, utility weight) are typed in from each fund's latest
# semi-annual report, with the source next to each number in data/peer_fundamentals.csv.
import csv, os, datetime as dt, statistics as st
import numpy as np, statsmodels.api as sm
from common import daily, dists, nav_tr_index
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
F = list(csv.DictReader(open(os.path.join(DATA, 'factors_and_peer_navs_daily.csv'))))
y = {dt.date.fromisoformat(r['observation_date']): float(r['DGS10']) for r in csv.DictReader(open(os.path.join(DATA, 'dgs10.csv'))) if r['DGS10'] not in ('', '.')}
PD = {}
for r in csv.DictReader(open(os.path.join(DATA, 'peer_distributions.csv'))):
    PD.setdefault(r['ticker'], {})[dt.date.fromisoformat(r['ex_date'])] = float(r['amount'])
def series(tk):
    if tk == 'BUI':
        D = daily(); return [(x['d'], x['nav'], x['px']) for x in D], dists()
    out = []
    for r in F:
        n, p = r[tk.lower()+'_nav'], r[tk.lower()+'_price']
        if n and p: out.append((dt.date.fromisoformat(r['date']), float(n), float(p)))
    return out, PD[tk]
def tr_index(S, X):
    idx = [1.0]
    for a, b in zip(S, S[1:]):
        div = sum(v for k, v in X.items() if a[0] < k <= b[0])
        idx.append(idx[-1]*(b[1]+div)/a[1])
    return idx
def at(S, d): return max(i for i, s in enumerate(S) if s[0] <= d)
fac = {dt.date.fromisoformat(r['date']): r for r in F}
print("fund | discount now | median discount since 2016 / since 2023 | dist rate on NAV / price | 5-yr gap Sep 30 2026 / Oct 30 2026 / 1 yr earlier | 2026 rate beta (t) | 2026 equal-weight equity beta (t)")
for tk in ('BUI', 'UTF', 'DPG', 'GLU'):
    S, X = series(tk); idx = tr_index(S, X)
    last = S[-1]; disc = last[2]/last[1] - 1
    d16 = st.median(s[2]/s[1]-1 for s in S); d23 = st.median(s[2]/s[1]-1 for s in S if s[0].year >= 2023)
    # current annualised regular distribution = latest regular amount x frequency
    exs = sorted(k for k in X if k <= dt.date(2026, 11, 16)); amt = X[exs[-1]]
    freq = 12 if (exs[-1] - exs[-2]).days < 40 else 4
    rate_nav, rate_px = amt*freq/last[1], amt*freq/last[2]
    def gap(e):
        i1 = at(S, e); i0 = at(S, e.replace(year=e.year-5))
        five = (idx[i1]/idx[i0])**0.2 - 1
        ex = sorted(k for k in X if k <= e); a2 = X[ex[-1]]; f2 = 12 if (ex[-1]-ex[-2]).days < 40 else 4
        return (five - a2*f2/S[i1][1])*100
    g = [gap(dt.date(2026, 9, 30)), gap(dt.date(2026, 10, 30)), gap(dt.date(2025, 10, 31))]
    # weekly regressions for 2026: return on 10-year change + RSP + SMH + USO (rate beta) and on 10-year + RSP (equity beta)
    W = [i for i, s in enumerate(S) if s[0].weekday() == 4 and s[0] in y and s[0] in fac and s[0].year >= 2025]
    rows = []
    for a, b in zip(W, W[1:]):
        da, db = S[a][0], S[b][0]
        if da.year < 2025: continue
        fa, fb = fac[da], fac[db]
        rows.append((db, idx[b]/idx[a]-1, y[db]-y[da], float(fb['rsp_close'])/float(fa['rsp_close'])-1,
                     float(fb['smh_close'])/float(fa['smh_close'])-1, float(fb['uso_close'])/float(fa['uso_close'])-1))
    P = [r for r in rows if r[0].year == 2026]
    Y = np.array([r[1] for r in P])
    m3 = sm.OLS(Y, sm.add_constant(np.array([[r[2], r[3], r[4], r[5]] for r in P]))).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
    m2 = sm.OLS(Y, sm.add_constant(np.array([[r[2], r[3]] for r in P]))).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
    print(f"{tk} | {disc:+.2%} | {d16:+.2%} / {d23:+.2%} | {rate_nav:.2%} / {rate_px:.2%} | {g[0]:+.2f} / {g[1]:+.2f} / {g[2]:+.2f} | "
          f"{m3.params[1]*100:+.1f}% ({m3.tvalues[1]:+.1f}) | {m2.params[2]:+.2f} ({m2.tvalues[2]:+.1f})")
print()
for r in csv.DictReader(open(os.path.join(DATA, 'peer_fundamentals.csv'))):
    print(f"{r['ticker']}: leverage {r['leverage_pct_total_assets']}% ({r['leverage_terms']}), expenses {r['expense_ratio_ex_leverage_pct']}% ex-leverage / {r['expense_ratio_total_pct']}% total, "
          f"income covered {r['nii_coverage_pct']}% of distributions ({r['coverage_period']}), utilities {r['utilities_pct_of_investments']}% of investments, payout history: {r['payout_history']}")
