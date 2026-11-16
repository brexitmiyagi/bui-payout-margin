# The core statistics behind the piece. Weekly (Friday to Friday) returns regressed on the change in the 10-year
# yield plus equity controls, with Newey-West (HAC, 4 lags) standard errors:
#   M1: 10-year change + S&P 500 (SPY)
#   M2: 10-year change + equal-weight S&P 500 (RSP), so a mega-cap-led S&P can't drive the result
#   M3: M2 + semiconductors (SMH, a stand-in for the AI trade) + oil (USO)
# Run for BUI's NAV total return, XLU, and the NAVs of three utility/infrastructure CEFs (UTF, UTG, DNP; NAV price
# only, so their distribution weeks add noise). Then: is 2026's rate beta different from earlier years (pooled
# regression with a 2026 interaction), rolling 26-week betas with 95% bands, Dimson-adjusted daily betas for BUI
# (lead and lag terms, since part of the NAV is priced before the US close), and the XLU-SPY correlation with a
# 95% interval.
import csv, os, datetime as dt, math
import numpy as np, statsmodels.api as sm
from common import daily, dists, nav_tr_index
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
D = daily(); idx = nav_tr_index(D, dists())
y = {dt.date.fromisoformat(r['observation_date']): float(r['DGS10'])
     for r in csv.DictReader(open(os.path.join(DATA, 'dgs10.csv'))) if r['DGS10'] not in ('', '.')}
F = {dt.date.fromisoformat(r['date']): r for r in csv.DictReader(open(os.path.join(DATA, 'factors_and_peer_navs_daily.csv')))}
rows = []
for k, x in enumerate(D):
    d = x['d']; f = F.get(d)
    if d not in y or not f or not x['xlu'] or not x['spy'] or '' in (f['rsp_close'], f['smh_close'], f['uso_close'], f['utf_nav'], f['utg_nav'], f['dnp_nav']):
        continue
    rows.append(dict(d=d, bui=idx[k], xlu=x['xlu'], spy=x['spy'], rsp=float(f['rsp_close']), smh=float(f['smh_close']),
                     uso=float(f['uso_close']), utf=float(f['utf_nav']), utg=float(f['utg_nav']), dnp=float(f['dnp_nav']), y10=y[d]))
def changes(R):
    out = []
    for a, b in zip(R, R[1:]):
        c = {'d': b['d'], 'dy': b['y10'] - a['y10']}
        for s in ('bui', 'xlu', 'spy', 'rsp', 'smh', 'uso', 'utf', 'utg', 'dnp'): c[s] = b[s]/a[s] - 1
        out.append(c)
    return out
W = changes([r for r in rows if r['d'].weekday() == 4])
DY = changes(rows)
MODELS = {'M1': ['dy', 'spy'], 'M2': ['dy', 'rsp'], 'M3': ['dy', 'rsp', 'smh', 'uso']}
def fit(P, dep, xs):
    Y = np.array([p[dep] for p in P]); X = sm.add_constant(np.array([[p[x] for x in xs] for p in P]))
    return sm.OLS(Y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
print("Weekly rate beta (% move per +100bp in the 10-year), HAC t-stat in brackets, by year")
for dep in ('bui', 'xlu', 'utf', 'utg', 'dnp'):
    for m, xs in MODELS.items():
        line = []
        for yr in range(2017, 2027):
            P = [p for p in W if p['d'].year == yr]
            r = fit(P, dep, xs)
            line.append(f"{yr}:{r.params[1]*100:+5.1f}[{r.tvalues[1]:+4.1f}]")
        print(f"  {dep.upper():3} {m}: " + " ".join(line))
print("\nEquity betas in M2 (on RSP), 2025 vs 2026, with HAC t-stats")
for dep in ('bui', 'xlu', 'utf', 'utg', 'dnp'):
    out = []
    for yr in (2025, 2026):
        r = fit([p for p in W if p['d'].year == yr], dep, MODELS['M2'])
        out.append(f"{yr} {r.params[2]:+.2f} [{r.tvalues[2]:+.1f}]")
    print(f"  {dep.upper()}: " + ", ".join(out))
print("\nIs the 2026 rate beta different from each earlier year? (M3, pooled with 2026 interaction; p-value of the difference)")
for dep in ('bui', 'xlu'):
    out = []
    for yr in range(2017, 2026):
        P = [p for p in W if p['d'].year in (yr, 2026)]
        Y = np.array([p[dep] for p in P]); z = np.array([1.0 if p['d'].year == 2026 else 0.0 for p in P])
        base = np.array([[p[x] for x in MODELS['M3']] for p in P])
        X = sm.add_constant(np.column_stack([base, z, base * z[:, None]]))
        r = sm.OLS(Y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
        k = 1 + len(MODELS['M3']) + 1   # first interaction term = dy x 2026
        out.append(f"{yr}: diff {r.params[k]*100:+.1f} p={r.pvalues[k]:.2f}")
    print(f"  {dep.upper()}: " + "; ".join(out))
print("\nRolling 26-week rate beta (M3) with 95% band, at quarter-ends")
for dep in ('bui', 'xlu'):
    out = []
    for i in range(26, len(W)+1):
        P = W[i-26:i]; e = P[-1]['d']
        if e.year >= 2024 and (e.month in (3, 6, 9, 12) and e.day >= 24 or i == len(W)):
            r = fit(P, dep, MODELS['M3']); b, s = r.params[1]*100, r.bse[1]*100
            out.append(f"{e}: {b:+.1f} ({b-1.96*s:+.1f} to {b+1.96*s:+.1f})")
    print(f"  {dep.upper()}: " + "; ".join(out))
print("\nDaily Dimson betas for BUI NAV (sum of lead, same-day and lag coefficients), M2")
for yr in (2024, 2025, 2026):
    P = [p for p in DY if p['d'].year == yr]
    n = len(P); Y = np.array([P[i]['bui'] for i in range(1, n-1)])
    cols = []
    for x in ('dy', 'rsp'):
        for sh in (-1, 0, 1):
            cols.append([P[i+sh][x] for i in range(1, n-1)])
    X = sm.add_constant(np.array(cols).T)
    r = sm.OLS(Y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
    R1 = np.zeros(7); R1[1:4] = 1; R2 = np.zeros(7); R2[4:7] = 1
    t1 = r.t_test(R1); t2 = r.t_test(R2)
    print(f"  {yr}: rate {float(t1.effect[0])*100:+.1f}% per +100bp [t {float(t1.tvalue[0][0]):+.1f}], equal-weight equity {float(t2.effect[0]):+.2f} [t {float(t2.tvalue[0][0]):+.1f}]")
print("\nXLU vs SPY correlation with 95% interval (Fisher z)")
for yr in (2024, 2025, 2026):
    for lab, P in (('weekly', W), ('daily', DY)):
        Q = [p for p in P if p['d'].year == yr]; a = [q['xlu'] for q in Q]; b = [q['spy'] for q in Q]
        c = float(np.corrcoef(a, b)[0, 1]); z = math.atanh(c); se = 1/math.sqrt(len(Q)-3)
        print(f"  {yr} {lab:6}: {c:+.2f} ({math.tanh(z-1.96*se):+.2f} to {math.tanh(z+1.96*se):+.2f}), n={len(Q)}")

# chart file: rolling 26-week M3 rate beta with 95% band, every week since 2024
with open(os.path.join(HERE, '..', 'results', 'rolling_rate_beta.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['week_ending', 'bui_beta', 'bui_lo', 'bui_hi', 'xlu_beta', 'xlu_lo', 'xlu_hi'])
    for i in range(26, len(W)+1):
        P = W[i-26:i]; e = P[-1]['d']
        if e.year < 2024: continue
        row = [e.isoformat()]
        for dep in ('bui', 'xlu'):
            r = fit(P, dep, MODELS['M3']); b, s = r.params[1]*100, r.bse[1]*100
            row += [round(b, 2), round(b-1.96*s, 2), round(b+1.96*s, 2)]
        w.writerow(row)
